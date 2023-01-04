import numpy as np
import matplotlib.pyplot as plt
import os
from mpi4py import MPI 
from petsc4py.PETSc import ScalarType
from petsc4py import PETSc

from dolfinx import *
from dolfinx.fem import (FunctionSpace, Constant, locate_dofs_topological,\
    dirichletbc, Function)
from dolfinx.fem.petsc import  LinearProblem
from dolfinx.io.gmshio import read_from_msh
from dolfinx.io.utils import XDMFFile
from ufl import (TestFunction, TrialFunction, as_tensor, jump,\
    grad, nabla_grad, inner, avg, dot, FiniteElement, MixedElement, Measure)

from ...materials import *
from .SimParameters import *
from .SimResult import *


def return_2Dscalar_value(field,x,y):
    np_value = np.array([0.0],dtype=np.float_)
    field.eval(np_value, np.array([x,y]))
    return float(np_value[0])

def return_3Dscalar_value(field,x,y,z):
    np_value = np.array([0.0],dtype=np.float_)
    field.eval(np_value, np.array([x,y,z]))
    return float(np_value[0])

class FEMSimulation(SimParameters):
    def __init__(self, D=3, mesh_file="", data=None, elem=None):
        super().__init__(D=D, mesh_file=mesh_file, data=data)
        if elem is not None:
            self.elem = elem
        else:
            self.elem = ('Lagrange', 1)

        # Mesh and Meshtag
        self.mesh = None
        self.subdomains = None
        self.boundaries = None

        # Space and mesure
        self.V = None
        self.dS = None
        self.ds = None
        self.dx = None

        # Multimesh parmeters
        self.Nspace = 1

        # Bilinear and linear forms
        self.a = None
        self.L = None

        # Solver parameter
        self.petsc_opt = None
        self.cg_problem = None
        self.u = None
        self.mixedvout = None
        self.vout = None
        self.result = SimResult()

        self.bcs = []
        # added for overzriting false option 
        self.file = []

        if data is not None:
            self.data_status = True


    def prepare_sim(self, **kwargs):
        if self.data_status :
            self.args = kwargs
            print('Info : Static/Quasi-Static electrical current problem')
            if self.D == 1:
                print('Error : 1D not implemented yet')
            else:
                # RECOVERING THE GEOMETRY
                self.mesh, self.subdomains, self.boundaries = read_from_msh(self.mesh_file+".msh", comm=MPI.COMM_WORLD, gdim=3)
                # SPACE FOR INTEGRATION 
                if self.inbound:
                    self.Nspace = self.Ninboundaries + 1
                    ME = [FiniteElement('Lagrange', self.mesh.ufl_cell(), 1) for k in range(self.Nspace)]
                    self.elem = MixedElement(ME)
                self.V = FunctionSpace(self.mesh,self.elem)
                # MEASURES FOR INTEGRATION
                self.dx = Measure("dx", domain=self.mesh, subdomain_data=self.subdomains)
                self.ds = Measure("ds", domain=self.mesh, subdomain_data=self.boundaries)
                self.dS = Measure("dS", domain=self.mesh, subdomain_data=self.boundaries)                
                # DIRICHLET BOUNDARY CONDITIONS
                self._set_dirichlet_BC()
                # DEFINING THE VARIATIONAL PROBLEM
                self.mixedvout = TrialFunction(self.V)
                self.u = TestFunction(self.V)
                # defining the bilinear form a(vout,u)
                self._set_bilinear_form()
                # defining the linear form L(u)
                # NB1: in the case of the current-problem, the source term is nul
                # NB2: all Neuman Conditions are specified in the linear form
                print('Info : ... preparing the linear form')
                # Check if quicker without
                if not self.inbound:
                    self.L = Constant(self.V, ScalarType(0.0))*self.u*self.dx
                else:
                    for i_space in range(self.Nspace): 
                        self.L = Constant(self.V, ScalarType(0.0))*self.u[i_space]*self.dx
                self._set_neuman_BC()
        else: 
            print("Warning: no parameters are set, Sim can not be prepared")


    def _set_dirichlet_BC(self):
        """
        internal use only: set the Dirichlet boundary condition from parameters
        """
        self.bcs = []
        for i in self.boundaries_list:
            bound = self.boundaries_list[i]
            condition = bound['condition']
            if condition =='Dirichlet':
                value = Constant(self.V, ScalarType(float(bound["value"]))) 
                label = self.boundaries.find(int(bound["mesh_domain"]))
                if not self.inbound:
                    id_subspace = self.boundaries_list
                    dofs = locate_dofs_topological(self.V, self.mesh.topology.dim-1, label)
                    self.bcs.append(dirichletbc(value, dofs, self.V))
                if self.inbound:
                    i_space = self.get_space_of_domain(bound['mesh_domain_3D'])
                    dofs = locate_dofs_topological(self.V.sub(i_space), self.mesh.topology.dim-1, label)
                    self.bcs.append(dirichletbc(value, dofs, self.V.sub(i_space)))
        if not self.bcs:
            print('Warning: no Dirichlet Condition implemented on the Computed Field, Simulation maybe unsuccessful')

    def _set_neuman_BC(self):
        """
        internal use only: set the Neuman boundary condition from parameters
        """
        labelL_list = []
        Neuman_list = []
        for i in self.boundaries_list:
            bound = self.boundaries_list[i]
            condition = bound['condition']
            if condition== 'Neuman':
                labelL_list.append(int(bound['mesh_domain']))
                if 'value' in bound:
                    Neuman_list.append(Constant(self.V, ScalarType(bound['value'])))
                elif 'variable' in bound:
                    Neuman_list.append(Constant(self.V, ScalarType(self.args[bound['variable']])))
                else:
                    print('Error: A Neuman Boundary condition must be associated with a value or variable')
                if not self.inbound:
                    self.L = self.L + Neuman_list[-1]*self.u*self.ds(labelL_list[-1])
                else:
                    i_space = self.get_space_of_domain(bound['mesh_domain_3D'])
                    self.L = self.L + Neuman_list[-1]*self.u[i_space]*self.ds(labelL_list[-1])

    def _set_bilinear_form(self):
        """
        internal use only: set the bilinear form a(vout, u) from the parameters
        """
        print('Info: ... preparing the bilinear form')
        #for dom in self.domains_list:
        if not self.inbound:
            label_list = []
            sigma_list = []
            for i_domain in self.domains_list:
                dom = self.domains_list[i_domain]
                # Recovering the label and the path to the material file
                label_list.append(dom["mesh_domain"])
                mat_path = str(dom["mat_file"])
                # Recovering the material properties for the domain
                mat = load_material(mat_path)
                if mat.is_isotropic():
                    # isotropic material, sigma is a scalar
                    local_sigma = Constant(self.V, ScalarType(mat.sigma))
                else:
                    # anisotropic material, sigma is a 2-order tensor
                    local_sigma = as_tensor([\
                        [mat.sigma_xx, 0, 0],\
                        [0, mat.sigma_yy, 0],\
                        [0, 0, mat.sigma_zz],\
                        ])
                sigma_list.append(local_sigma)
                if self.a is None:
                    self.a = inner(nabla_grad(self.mixedvout), sigma_list[0]*nabla_grad(self.u))*self.dx(label_list[0])
                else:
                    self.a = self.a + inner(nabla_grad(self.mixedvout), sigma_list[-1]*nabla_grad(self.u))*self.dx(label_list[-1])
        else:
            for i_space in range(self.Nspace):
                label_list = []
                sigma_list = []
                for i_domain in self.domains_list:
                    dom = self.get_mixedspace_domain(i_space=i_space, i_domain=i_domain)
                    # Recovering the label and the path to the material file
                    label_list.append(self.get_mixedspace_domain(i_space=i_space, i_domain=i_domain))
                    mat_path = str(self.mat_file_map[label_list[-1]])
                    # Recovering the material properties for the domain
                    mat = load_material(mat_path)
                    if mat.is_isotropic():
                        # isotropic material, sigma is a scalar
                        local_sigma = Constant(self.V, ScalarType(mat.sigma))
                    else:
                        # anisotropic material, sigma is a 2-order tensor
                        local_sigma = as_tensor([\
                            [mat.sigma_xx, 0, 0],\
                            [0, mat.sigma_yy, 0],\
                            [0, 0, mat.sigma_zz],\
                            ])
                    sigma_list.append(local_sigma)
                    if self.a is None:
                        self.a = inner(nabla_grad(self.mixedvout[i_space]), sigma_list[0]*nabla_grad(self.u[i_space]))*self.dx(i_domain)
                    else:
                        self.a = self.a + inner(nabla_grad(self.mixedvout[i_space]), sigma_list[-1]*nabla_grad(self.u[i_space]))*self.dx(i_domain)
            self._set_jump()
            
    def _set_jump(self):
        """
        internal use only: set the bilinear form a(vout, u) from the parameters
        """
        i_space = 0
        for i_ibound in self.inboundaries_list:
            mat_path = str(self.mat_file_map[i_ibound])
            mat = load_material(mat_path)
            if mat.is_isotropic():
                # isotropic material, sigma is a scalar
                local_sigma = Constant(self.V, ScalarType(mat.sigma))
            else: 
                print("Error: internal boundary should be isotropic")
            local_thickness = Constant(self.V, ScalarType(self.inboundaries_list[i_ibound]['thickness']))
            jmp_v = avg(self.mixedvout[i_space]) - avg(self.mixedvout[i_space+1])
            jmp_u = avg(self.u[i_space]) - avg(self.u[i_space+1])
            self.a  += local_sigma/local_thickness * jmp_u * jmp_v * self.dS(i_ibound)
            i_space += 1

    def reset_LinearForm_sim(self, **kwargs):
        self.args = kwargs
        self.mixedvout = TrialFunction(self.V)
        print('... reseting the linear form')
        self.L = Constant(self.V, ScalarType(Constant(0.0)))*self.u*self.dx
        labelL_list = []
        Neuman_list = []
        for bound in self.boundaries_list:
            condition = bound.getElementsByTagName('condition')
            if condition[0].childNodes[0].nodeValue =='Neuman':
                labelL_list.append(int(bound.getElementsByTagName('label')[0].childNodes[0].nodeValue))
                value_list = bound.getElementsByTagName('value')
                variable_list = bound.getElementsByTagName('variable')
                if value_list:
                    Neuman_list.append(Constant(self.V, ScalarType(value_list[0].childNodes[0].nodeValue)))
                elif variable_list:
                    Neuman_list.append(Constant(self.V, ScalarType(self.args[variable_list[0].childNodes[0].nodeValue])))
                else:
                    print('Error: A Neuman Boundary condition must be associated with a value or variable')
                self.L = self.L + Neuman_list[-1]*self.u*self.ds(labelL_list[-1])


    def solve_and_save_sim(self,filename, save=True, plot=False, overwrite=True):
        print('Info : ... solving electrical potential')
        if not save:
            print('Warning: the result will not be saved, be sure you use or save it later')
        if self.petsc_opt is None:
            self.petsc_opt={"ksp_type": "cg", "pc_type": "ilu", "ksp_rtol":1e-4, "ksp_atol":1e-7, "ksp_max_it": 1000}
        self.cg_problem = LinearProblem(self.a, self.L, bcs=self.bcs, petsc_options=self.petsc_opt)
        self.mixedvout = self.cg_problem.solve()
        if self.inbound:
            self._merge_mixed_solutions()
        else:
            self.vout = self.mixedvout
            
        # Dump solution to file in VTK format
        if save:
            if (not self.file) or overwrite==True:
                fname = rmv_ext(filename)
                if not (fname == filename or fname+".xdmf" == filename):
                    print('Warning: extension of solution will be save in xdmf files')
                with XDMFFile(self.mesh.comm, fname+".xdmf", "w") as file:
                    file.write_mesh(self.mesh)
                    file.write_function(self.vout)

        # return simulation result
        self.result.set_sim_result(mesh_file=self.mesh_file, domain=self.mesh, elem=self.elem, V=self.V, vout=self.vout, comm=self.mesh.comm)
        return self.result

    def _merge_mixed_solutions(self):
        self.mixedvout = self.mixedvout.split()
        V_DG = FunctionSpace(self.mesh, ("DG", 1))
        u, v = TrialFunction(V_DG), TestFunction(V_DG)
        u_dg = Function(V_DG)
        adg = u*v * self.dx
        Ldg = 0
        for i_domain in self.domainsID:
            i_space = self.get_space_of_domain(i_domain)
            Ldg += v*self.mixedvout[i_space]*self.dx(i_domain)
        problem = fem.petsc.LinearProblem(adg, Ldg,bcs=[], petsc_options=self.petsc_opt)
        self.vout = problem.solve()



    def visualize_mesh(self):
        os.system('gmsh '+ self.mesh_file +'.msh')

