import numpy as np
import os
from mpi4py import MPI 
from petsc4py.PETSc import ScalarType
import time


#from dolfinx import *
from dolfinx.fem import (FunctionSpace, Constant, locate_dofs_topological,\
    dirichletbc, Function, form, assemble_scalar)
from dolfinx.fem.petsc import  LinearProblem
from dolfinx.io.utils import XDMFFile
from ufl import (TestFunction, TrialFunction, as_tensor,\
    nabla_grad, inner, avg, FiniteElement, MixedElement, Measure)

from .fenics_materials import *
from .SimParameters import *
from .SimResult import *
from ....utils.units import *

from ....backend.log_interface import rise_error, rise_warning, pass_info


# Lists of available solvers and conditioners
# go to https://petsc4py.readthedocs.io/en/stable/manual/ksp/ for more info

ksp_type_list = ['cg', 'pipecg', 'chebyshev', 'groppcg', 'pipecgrr', 'cgne', 'fcg', 'cgls',\
    'pipefcg', 'nash', 'stcg', 'stcg', 'qcg', 'bicg', 'bcgs', 'ibcgs', 'fbcgs', 'fbcgsr', 'symmlq',\
    'bcgsl', 'minres', 'gmres', 'fgmres', 'dgmres', 'pgmres', 'pipefgmres', 'lgmres', 'cr', 'gcr',\
    'pipecr', 'pipegcr', 'fetidp', 'cgs', 'tfqmr', 'tcqmr', 'lsqr', 'tsirm', 'python', 'preonly']

pc_type_list = ['lu', 'ilu', 'gamg', 'jacobi', 'sor', 'eisenstat', 'icc', 'asm', 'gasm',\
    'bddc', 'ksp', 'composite', 'cholesky', 'none', 'shell']




class FEMSimulation(SimParameters):
    def __init__(self, D=3, mesh_file="", mesh=None, data=None, elem=None, \
        ummesh=True, comm=MPI.COMM_SELF, rank=0):
        """

        """
        super().__init__(D=D, mesh_file=mesh_file, data=data)
        if elem is not None:
            self.elem = elem
        else:
            self.elem = ('Lagrange', 1)
        self.multi_elem = None

        # Mesh and Meshtag
        self.mesh = mesh
  
        if self.mesh is None:
            self.mesh = self.mesh_file
        self.domain = None
        self.subdomains = None
        self.boundaries = None

        # Space and mesure
        self.V = None
        self.dS = None
        self.ds = None
        self.dx = None
        if ummesh:
            self.mat_unit = 'S/um'
        else:
            self.mat_unit = 'S/m'

        # Multimesh parmeters
        self.Nspace = 1

        # Bilinear and linear forms
        self.a = None
        self.L = None

        # Solver parameters
        self.petsc_opt = {"ksp_type":"cg", "pc_type":"ilu", "ksp_rtol":1e-4, "ksp_atol":1e-7, "ksp_max_it":1000}
        self.cg_problem = None
        self.u = None
        self.mixedvout = None
        self.vout = None
        self.result = SimResult()

        # Mcore attributes
        self.comm = comm
        self.rank = rank

        # Timmers
        self.solving_timer = 0

        self.bcs = []
        # added for overzriting false option 
        self.file = []

        #if data is not None:
        self.data_status = True
        self.solve_status = False

        

    #####################################################
    ############ Prepare the matrix sytstem #############
    #####################################################

    def prepare_sim(self, **kwargs):
        t0 = time.time()
        if self.data_status :
            self.args = kwargs
            pass_info('Static/Quasi-Static electrical current problem')
            if self.D == 1:
                rise_error('1D not implemented yet')
            else:
                # RECOVERING THE GEOMETRY
                self.domain, self.subdomains, self.boundaries = read_gmsh(self.mesh, comm=self.comm, rank=self.rank, gdim=3)
                # SPACE FOR INTEGRATION 
                if self.inbound:
                    self.Nspace = self.Ninboundaries + 1
                    ME = [FiniteElement(self.elem[0], self.domain.ufl_cell(), self.elem[1]) for k in range(self.Nspace)]
                    self.multi_elem = MixedElement(ME)
                else:
                    self.multi_elem = self.elem
                self.V = FunctionSpace(self.domain,self.multi_elem)
                # MEASURES FOR INTEGRATION
                self.dx = Measure("dx", domain=self.domain, subdomain_data=self.subdomains)
                self.ds = Measure("ds", domain=self.domain, subdomain_data=self.boundaries)
                self.dS = Measure("dS", domain=self.domain, subdomain_data=self.boundaries)                
                # DIRICHLET BOUNDARY CONDITIONS
                self.__set_dirichlet_BC()
                # DEFINING THE VARIATIONAL PROBLEM
                self.mixedvout = TrialFunction(self.V)
                self.u = TestFunction(self.V)
                # defining the bilinear form a(vout,u)
                self.__set_bilinear_form()
                # defining the linear form L(u)
                # NB1: in the case of the current-problem, the source term is nul
                # NB2: all Neuman Conditions are specified in the linear form
                pass_info('FEN4NRV: preparing the linear form')
                # Check if quicker without
                if not self.inbound:
                    self.L = Constant(self.domain, ScalarType(0.0))*self.u*self.dx
                else:
                    for i_space in range(self.Nspace): 
                        self.L = Constant(self.domain, ScalarType(0.0))*self.u[i_space]*self.dx
                self.__set_neuman_BC()
            self.solving_timer += time.time() - t0
        else: 
            rise_warning("no parameters are set, Sim can not be prepared")

    def __set_dirichlet_BC(self):
        """
        internal use only: set the Dirichlet boundary condition from parameters
        """
        self.bcs = []
        for i in self.boundaries_list:
            bound = self.boundaries_list[i]
            condition = bound['condition']
            if condition.lower() =='dirichlet':
                value = Constant(self.domain, ScalarType(float(bound["value"]))) 
                label = self.boundaries.find(int(bound["mesh_domain"]))
                if not self.inbound:
                    id_subspace = self.boundaries_list
                    dofs = locate_dofs_topological(self.V, self.domain.topology.dim-1, label)
                    self.bcs.append(dirichletbc(value, dofs, self.V))
                if self.inbound:
                    i_space = self.get_space_of_domain(bound['mesh_domain_3D'])
                    dofs = locate_dofs_topological(self.V.sub(i_space), self.domain.topology.dim-1, label)
                    self.bcs.append(dirichletbc(value, dofs, self.V.sub(i_space)))
        if not self.bcs:
            rise_warning('no Dirichlet Condition implemented on the Computed Field, Simulation maybe unsuccessful')

    def __set_neuman_BC(self):
        """
        internal use only: set the Neuman boundary condition from parameters
        """
        labelL_list = []
        Neuman_list = []
        for i in self.boundaries_list:
            bound = self.boundaries_list[i]
            condition = bound['condition']
            if condition.lower()== 'neuman':
                labelL_list.append(int(bound['mesh_domain']))
                if 'value' in bound:
                    Neuman_list.append(Constant(self.domain, ScalarType(bound['value'])))
                elif 'variable' in bound:
                    Neuman_list.append(Constant(self.domain, ScalarType(self.args[bound['variable']])))
                else:
                    rise_error('A Neuman Boundary condition must be associated with a value or variable')
                if not self.inbound:
                    self.L = self.L + Neuman_list[-1]*self.u*self.ds(labelL_list[-1])
                else:
                    i_space = self.get_space_of_domain(bound['mesh_domain_3D'])
                    self.L = self.L + Neuman_list[-1]*self.u[i_space]*self.ds(labelL_list[-1])

    def __set_bilinear_form(self):
        """
        internal use only: set the bilinear form a(vout, u) from the parameters
        """
        pass_info('FEN4NRV: preparing the bilinear form')
        #for dom in self.domains_list:
        if not self.inbound:
            label_list = []
            sigma_list = []
            for i_domain in self.domains_list:
                dom = self.domains_list[i_domain]
                # Recovering the label and the path to the material file
                label_list.append(dom["mesh_domain"])
                mat_path = dom["mat_pty"]
                # Recovering the material properties for the domain
                local_sigma = self.__get_permitivity(mat_path,unit=self.mat_unit)
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
                    label_list.append(dom)
                    mat_path = self.mat_pty_map[label_list[-1]]
                    # Recovering the material properties for the domain
                    local_sigma = self.__get_permitivity(mat_path,unit=self.mat_unit)
                    sigma_list.append(local_sigma)
                    if self.a is None:
                        self.a = inner(nabla_grad(self.mixedvout[i_space]), sigma_list[0]*nabla_grad(self.u[i_space]))*self.dx(i_domain)
                    else:
                        self.a = self.a + inner(nabla_grad(self.mixedvout[i_space]), sigma_list[-1]*nabla_grad(self.u[i_space]))*self.dx(i_domain)
            self.__set_jump()
            
    def __set_jump(self):
        """
        internal use only: set the jump for all internale boundary to mimic the thin layers
        """

        for i_ibound in self.inboundaries_list:
            in_space, out_space = self.get_spaces_of_ibound(i_ibound)
            mat_path = self.mat_pty_map[i_ibound]
            local_sigma = self.__get_permitivity(mat_path,unit=self.mat_unit)
            local_thickness = Constant(self.domain, ScalarType(self.inboundaries_list[i_ibound]['thickness']))
            jmp_v = avg(self.mixedvout[out_space]) - avg(self.mixedvout[in_space])
            jmp_u = avg(self.u[out_space]) - avg(self.u[in_space])
            self.a  += local_sigma/local_thickness * jmp_u * jmp_v * self.dS(i_ibound)

    def __get_permitivity(self, X, unit='S/m'):
        """
        Extract permitivity from an object X and convert it in dolfinx 
        constant or tensor

        Parameters
        ----------
            X       : str, mat, float, list[3]
            unit    : 'S/m' or 'S/um'
                unit into witch the permitivity should be converted, by default S/m

        Returns
        -------
            sigma   :   dolfinx.fem.Constant or ufl.as_tensor
                permitivity 
        """
        if unit == 'S/um':
            UN = S/m
        else:
            UN = 1

        mat = None
        if isinstance(X, str):
            mat = load_fenics_material(X)
        elif is_fen_mat(X):
            mat = X
        elif is_mat(X):
            mat = fenics_material(X)
        
        if mat is not None:
            sigma = mat.get_fenics_sigma(domain=self.domain,elem=self.elem,UN=UN)
        elif isinstance(X, (float, int)):
            sigma = Constant(self.domain, ScalarType(X*UN))
        elif np.iterable(X) and len(X)==3:
                sigma = as_tensor([\
                    [X[0] * UN, 0, 0],\
                    [0, X[1] * UN, 0],\
                    [0, 0, X[2] * UN],\
                    ]) 
        else:
            rise_error(('get_permitivity: X should be either an str, mat, float, list[3]'))
        return sigma

    #####################################################
    ################# Solve the sytstem #################
    #####################################################

    def get_solver_opt(self):
        """
        get krylov solver options
        """
        return self.petsc_opt

    def set_solver_opt(self, ksp_type=None, pc_type=None, ksp_rtol=None, ksp_atol=None, ksp_max_it=None):
        """
        set krylov solver options
        
        Parameters
        ----------
        ksp_type        : str
            value to set for ksp_type (solver type), if None don't change, None by default
        pc_type         : str
            value to set for pc_type (preconditioner type), if None don't change, None by default
            list of possible
        ksp_rtol        : float
            value to set for ksp_rtol (relative tolerance), if None don't change, None by default
        ksp_atol        : float
            value to set for ksp_atol (absolute tolerance), if None don't change, None by default
        ksp_max_it      : int
            value to set for ksp_max_it (max number of iterations), if None don't change, None by default
        """
        if ksp_type is not None:
            if ksp_type in ksp_type_list:
                self.petsc_opt['ksp_type'] = ksp_type
            else:
                rise_warning(ksp_type+' not set, should be in:\n'+ksp_type_list)
        if pc_type is not None:
            if pc_type in pc_type_list:
                self.petsc_opt['pc_type'] = pc_type
            else:
                rise_warning(pc_type+' not set, should be in:\n'+pc_type_list)
        if ksp_rtol is not None:
            self.petsc_opt['ksp_rtol'] = ksp_rtol
        if ksp_atol is not None:
            self.petsc_opt['ksp_atol'] = ksp_atol
        if ksp_max_it is not None:
            self.petsc_opt['ksp_max_it'] = ksp_max_it


    def solve(self):
        t0 = time.time()
        pass_info('FEN4NRV: solving electrical potential')
        #rise_warning('The result will not be saved, be sure you use or save it later')
        self.cg_problem = LinearProblem(self.a, self.L, bcs=self.bcs, petsc_options=self.petsc_opt)
        self.mixedvout = self.cg_problem.solve()
        if self.inbound:
            V_sol = self.__merge_mixed_solutions()
        else:
            self.vout = self.mixedvout
            V_sol = self.V

        # return simulation result
        self.result.set_sim_result(mesh_file=self.mesh_file, domain=self.domain, elem=self.multi_elem, V=V_sol, vout=self.vout, comm=self.domain.comm)
        
        self.solving_timer += time.time() - t0
        pass_info('FEN4NRV: solved in ' + str(self.solving_timer) + ' s')
        return self.result

    def __merge_mixed_solutions(self):
        self.mixedvout = self.mixedvout.split()
        V_DG = FunctionSpace(self.domain, ('Discontinuous Lagrange', self.elem[1]))
        u, v = TrialFunction(V_DG), TestFunction(V_DG)
        adg = u*v * self.dx
        Ldg = 0
        for i_domain in self.domainsID:
            i_space = self.get_space_of_domain(i_domain)
            Ldg += v*self.mixedvout[i_space]*self.dx(i_domain)
        problem = LinearProblem(adg, Ldg,bcs=[], petsc_options=self.petsc_opt)
        self.vout = problem.solve()
        return V_DG

    #####################################################
    ################ Access the results #################
    #####################################################

    def solve_and_save_sim(self, filename, save=True):
        if not self.solve_status:
            self.solve()

        fname = rmv_ext(filename)
        if not (fname == filename or fname+".xdmf" == filename):
            rise_warning('Extension of solution will be save in xdmf files')
        with XDMFFile(self.domain.comm, fname+".xdmf", "w") as file:
            file.write_mesh(self.domain)
            file.write_function(self.vout)
        return self.result

    def get_timers(self):
        return self.assembling_timer, self.solving_timer

    def visualize_mesh(self):
        os.system('gmsh '+ self.mesh_file +'.msh')


    def get_domain_potential(self, dom_id, dim=2):
        if dim == 2:
            do = self.ds
        elif dim == 3:
            do = self.dx

        S= assemble_scalar(form(1*do(dom_id)))
        return assemble_scalar(form(self.vout*do(dom_id)))/S

