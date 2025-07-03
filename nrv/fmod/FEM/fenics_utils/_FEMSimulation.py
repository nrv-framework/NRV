"""
NRV-:class:`.FEMSimulation` handling.
"""

import os
import time
import numpy as np
import sys

from dolfinx import default_scalar_type
from dolfinx.fem import (
    Constant,
    Function,
    functionspace,
    assemble_scalar,
    dirichletbc,
    form,
    locate_dofs_topological,
)
from dolfinx.fem.petsc import LinearProblem
from mpi4py.MPI import COMM_WORLD, COMM_SELF, SUM
from petsc4py.PETSc import ScalarType, Viewer
from ufl import (
    Measure,
    TestFunction,
    TrialFunction,
    avg,
    inner,
    nabla_grad,
    CellDiameter,
)
from basix.ufl import element, mixed_element


from ....backend._log_interface import pass_info, rise_error, rise_warning
from ....backend._file_handler import rmv_ext
from ....utils._units import S, V, m
from ._fenics_materials import fenics_material
from ._FEMParameters import FEMParameters
from ._FEMResults import read_gmsh, FEMResults

# Lists of available solvers and conditioners
# go to https://petsc4py.readthedocs.io/en/stable/manual/ksp/ for more info

ksp_type_list = [
    "cg",
    "pipecg",
    "chebyshev",
    "groppcg",
    "pipecgrr",
    "cgne",
    "fcg",
    "cgls",
    "pipefcg",
    "nash",
    "stcg",
    "stcg",
    "qcg",
    "bicg",
    "bcgs",
    "ibcgs",
    "fbcgs",
    "fbcgsr",
    "symmlq",
    "bcgsl",
    "minres",
    "gmres",
    "fgmres",
    "dgmres",
    "pgmres",
    "pipefgmres",
    "lgmres",
    "cr",
    "gcr",
    "pipecr",
    "pipegcr",
    "fetidp",
    "cgs",
    "tfqmr",
    "tcqmr",
    "lsqr",
    "tsirm",
    "python",
    "preonly",
]

pc_type_list = [
    "lu",
    "ilu",
    "gamg",
    "jacobi",
    "sor",
    "eisenstat",
    "icc",
    "asm",
    "gasm",
    "bddc",
    "ksp",
    "composite",
    "cholesky",
    "none",
    "shell",
    "hypre",
]


class FEMSimulation(FEMParameters):
    r"""
    Class usefull to solve the Static/Quasi-Static electrical current problem using FEM with
    FEniCSx algorithms (https://fenicsproject.org).

    .. math::

        \nabla \mathbf{j}(\mathbf{r}) = 0

    .. math::

        \mathbf{j}(\mathbf{r}) = \mathbf{\sigma} (\mathbf{r}) \nabla V (\mathbf{r}), \forall \mathbf{r} \in \Omega

    Where $\\Omega$ is the simulation space, $\\bf{j}$ the the current density and $V$ the electrical potential

    The problem parameters (domains and boundaries condition) can be define using FEMParameters methods
    Contains methods to setup the matrix sytstem, to solve it and to access the results.

    Parameters
    ----------
    D               : int
        dim of the mesh, by default 3
        NB: only 3 is implemented
    mesh_file       : str
        mesh directory and file name: by default ""
    mesh            : None or MshCreator
        if not None, (MshCreator) from which the mesh sould be used, by default None
    data            : str, dict or FEMParameters
        if not None, load FEMParameters attribute from data, by default None
    elem            :tupple (str, int)
        if None, ("Lagrange", 1), else (element type, element order), by default None
    ummesh          : bool
        if True the scale of mesh space dimensions should be (um), else (m), by default True
        Usefull to link the update materials conductivity as in NRV conductivities are in S/m
        but NerveMshCreator space scale is um)
    comm            : int
        The MPI communicator to use for mesh creation, by default COMM_SELF
    rank            : int
        The rank the Gmsh model is initialized on, by default 0
    """

    def __init__(
        self,
        D=3,
        mesh_file="",
        mesh=None,
        data=None,
        elem=None,
        ummesh=True,
        comm=COMM_SELF,
        rank=0,
    ):
        """
        initialisation of the FEMSimulation
        """
        super().__init__(D=D, mesh_file=mesh_file, data=data)
        if elem is not None:
            self.elem = elem
        else:
            self.elem = ("Lagrange", 1)
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
        self.V_DG = None
        self.dS = None
        self.ds = None
        self.dx = None
        if ummesh:
            self.mat_unit = "S/um"
        else:
            self.mat_unit = "S/m"

        # Multimesh parmeters
        self.Nspace = 1

        # Bilinear and linear forms
        self.a = None
        self.L = None

        self.mat_list_ID = []
        self.sigma_list = []
        self.mat_list = []
        self.mat_list_space = []
        self.mixedvouts = []

        # gather fen_mat name of all domain and internal layer
        self.mat_map = {}
        self.Neuman_list = {}

        # Solver parameters
        self.petsc_opt = {
            "ksp_type": "cg",
            "pc_type": "ilu",
            "ksp_rtol": 1e-4,
            "ksp_atol": 1e-7,
            "ksp_max_it": 1000,
        }
        self.cg_problem = None
        self.dg_problem = None
        self.u = None
        self.v = None
        self.mixedvout = None
        self.vout = None
        self.result = None

        # Mcore attributes
        self.comm = comm
        self.rank = rank

        # Timmers
        self.solving_timer = 0

        self.bcs = []
        # added for overzriting false option
        self.file = []

        self.data_status = True
        self.domain_status = False
        self.material_map_satus = False
        self.dirichlet_BC_status = False
        self.neumann_BC_status = False
        self.bilinear_form_status = False
        self.jump_status = False
        self.linear_form_status = False
        self.setup_status = False
        self.solve_status = False
        self.to_merge = True

    #####################################################
    ########### SimParameter methods overload ###########
    #####################################################

    def add_inboundary(
        self,
        mesh_domain,
        in_domains,
        thickness,
        mat_pty=None,
        mat_file=None,
        mat_perm=None,
        ID=None,
    ):
        super().add_inboundary(
            mesh_domain,
            in_domains,
            thickness,
            mat_pty,
            mat_file,
            mat_perm,
            ID,
        )
        if self.setup_status:
            if mesh_domain in self.mat_map:
                self.mat_map[mesh_domain].update_mat(mat_pty)
            else:
                rise_warning(
                    "Domain not added: new domain cannot be added between 2 simulations,\
                             (set domain before simulation or create a new one)"
                )

    def add_domain(
        self, mesh_domain, mat_pty=None, mat_file=None, mat_perm=None, ID=None
    ):
        super().add_domain(mesh_domain, mat_pty, mat_file, mat_perm, ID)
        if self.setup_status:
            if mesh_domain in self.mat_map:
                self.mat_map[mesh_domain].update_mat(mat_pty)
            else:
                rise_warning(
                    "Domain not added: new domain cannot be added between 2 simulations,\
                             (set domain before simulation or create a new one)"
                )

    #####################################################
    ############ setup the matrix sytstem #############
    #####################################################

    def setup_sim(self, **kwargs):
        """
        setup Bilinear form, Linear form and boundary conditions using paramters and kwargs
        to set the variable defined Neumann boundary conditions (see FEMParameters.add_boundary)
        If FEMSimulation already defined, can be used to modify variable defined NBC
        """
        t0 = time.time()
        if self.data_status:
            self.args = kwargs
            pass_info("Static/Quasi-Static electrical current problem")
            if self.D == 1:
                rise_error("1D not implemented yet")
            else:
                # Initialize the domain
                if not self.domain_status:
                    self.__init_domain()
                # DIRICHLET BOUNDARY CONDITIONS
                if not self.dirichlet_BC_status:
                    self.__set_dirichlet_BC()
                # DEFINING THE VARIATIONAL PROBLEM
                self.v = TrialFunction(self.V)
                self.u = TestFunction(self.V)
                # defining the bilinear form a(vout,u)
                if not self.bilinear_form_status:
                    self.__set_bilinear_form()
                # defining the linear form L(u)
                # NB1: in the case of the current-problem, the source term is nul
                if not self.linear_form_status:
                    self.__set_linear_form()
                # NEUMANN BOUNDARY CONDITIONS
                self.__set_neumann_BC()
            self.setup_status = True
            self.solving_timer += time.time() - t0
        else:
            rise_warning("no parameters are set, Sim can not be setup")

    def __init_domain(self):
        """
        internal use only:
        """
        if not self.domain_status:
            # RECOVERING THE GEOMETRY
            self.domain, self.subdomains, self.boundaries = read_gmsh(
                self.mesh, comm=self.comm, rank=self.rank, gdim=self.D
            )
            # SPACE FOR INTEGRATION
            if self.inbound:
                self.Nspace = self.Ninboundaries + 1
                ME = [
                    element(
                        self.elem[0],
                        self.domain.basix_cell(),
                        self.elem[1],
                        dtype=ScalarType,
                    )
                    for _ in range(self.Nspace)
                ]
                self.multi_elem = mixed_element(ME)
            else:
                self.multi_elem = self.elem
            self.V = functionspace(self.domain, self.multi_elem)
            # MEASURES FOR INTEGRATION
            self.dx = Measure("dx", domain=self.domain, subdomain_data=self.subdomains)
            self.ds = Measure("ds", domain=self.domain, subdomain_data=self.boundaries)
            self.dS = Measure("dS", domain=self.domain, subdomain_data=self.boundaries)
            self.domain_status = True

    def __set_dirichlet_BC(self):
        """
        internal use only: set the Dirichlet boundary condition from parameters
        NB: DBC cannot be change between simulations
        """
        self.bcs = []
        for i in self.dboundaries_list:
            bound = self.dboundaries_list[i]
            condition = bound["condition"]
            if condition.lower() == "dirichlet":
                value = Constant(self.domain, ScalarType(float(bound["value"])))
                label = self.boundaries.find(int(bound["mesh_domain"]))
                if not self.inbound:
                    dofs = locate_dofs_topological(
                        self.V, self.domain.topology.dim - 1, label
                    )
                    self.bcs.append(dirichletbc(value, dofs, self.V))
                else:
                    i_space = self.get_space_of_domain(bound["mesh_domain_3D"])
                    dofs = locate_dofs_topological(
                        self.V.sub(i_space), self.domain.topology.dim - 1, label
                    )
                    self.bcs.append(dirichletbc(value, dofs, self.V.sub(i_space)))
        if not self.bcs:
            rise_warning(
                "no Dirichlet Condition implemented on the Computed Field, Simulation maybe unsuccessful"
            )
        self.dirichlet_BC_status = True

    def __set_neumann_BC(self):
        """
        internal use only: set the Neuman boundary condition from parameters or update
        variable between to simulation
        NB: Only variable NBC (see FEMParameters.add_boundary) can be changed between simulations
        """
        if not self.neumann_BC_status:
            for i_bound in self.nboundaries_list:
                bound = self.nboundaries_list[i_bound]
                condition = bound["condition"]
                if condition.lower() in "neumann":
                    dom = int(bound["mesh_domain"])
                    if "value" in bound:
                        self.Neuman_list[i_bound] = Constant(
                            self.domain, ScalarType(bound["value"])
                        )
                    elif "variable" in bound:
                        self.Neuman_list[i_bound] = Constant(
                            self.domain, ScalarType(self.args[bound["variable"]])
                        )
                    else:
                        rise_error(
                            "A Neuman Boundary condition must be associated with a value or variable"
                        )
                    if not self.inbound:
                        self.L = self.L + self.Neuman_list[i_bound] * self.u * self.ds(
                            dom
                        )
                    else:
                        i_space = self.get_space_of_domain(bound["mesh_domain_3D"])
                        self.L = self.L + self.Neuman_list[i_bound] * self.u[
                            i_space
                        ] * self.ds(dom)
            self.neumann_BC_status = True
        else:
            for i_bound in self.nboundaries_list:
                bound = self.nboundaries_list[i_bound]
                condition = bound["condition"]
                if condition.lower() in "neumann" and "variable" in bound:
                    if bound["variable"] in self.args:
                        self.Neuman_list[i_bound].value = self.args[bound["variable"]]

    def __set_bilinear_form(self):
        """
        internal use only: set the bilinear form a(vout, u) from the parameters
        """
        pass_info("FEN4NRV: setup the bilinear form")
        self.__set_material_map()
        for i_space in range(self.Nspace):
            for i_domain in self.domains_list:
                i_mat = self.get_mixedspace_domain(i_space=i_space, i_domain=i_domain)
                if self.a is None:
                    self.a = self.__get_static_component(i_domain, i_mat, i_space)
                else:
                    self.a += self.__get_static_component(i_domain, i_mat, i_space)
        if self.inbound:
            self.__set_jump()
        self.bilinear_form_status = True

    def __get_static_component(self, i_dom, i_mat, i_space):
        r"""
        Set a static componnent of the bimlinear form:

        .. math::

            a = \nablav[i_{space}] \sigma[i_mat] \nabla u[i_{space}] dx(i_{dom})

        Parameters
        ----------
        i_dom    : int
            id of the domain on which the component should be set
        i_mat       : int
            id of the material corresponding domain on which the component should be set
        i_space     : int
            id of the i_space
        """
        if not self.inbound:
            return inner(
                nabla_grad(self.v),
                self.mat_map[i_mat].sigma_fen * nabla_grad(self.u),
            ) * self.dx(i_dom)
        else:
            return inner(
                nabla_grad(self.v[i_space]),
                self.mat_map[i_mat].sigma_fen * nabla_grad(self.u[i_space]),
            ) * self.dx(i_dom)

    def __set_jump(self):
        """
        internal use only: set the jump for all internale boundary to mimic the thin layers
        """
        for i_ibound in self.inboundaries_list:
            in_space, out_space = self.get_spaces_of_ibound(i_ibound)
            local_thickness = Constant(
                self.domain, ScalarType(self.inboundaries_list[i_ibound]["thickness"])
            )
            jmp_v = avg(self.v[out_space]) - avg(self.v[in_space])
            jmp_u = avg(self.u[out_space]) - avg(self.u[in_space])
            self.a += (
                self.mat_map[i_ibound].sigma_fen
                / local_thickness
                * jmp_u
                * jmp_v
                * self.dS(i_ibound)
            )
        self.jump_status = True

    def __set_material_map(self):
        """
        internal use only: build a dictionnary mat_map containing a material for every domain and layer
        """
        if not self.material_map_satus:
            if self.mat_unit == "S/um":
                UN = S / m
            else:
                UN = 1
            for dom, pty in self.mat_pty_map.items():
                self.mat_map[dom] = fenics_material(pty)
                self.mat_map[dom].update_fenics_sigma(
                    domain=self.domain, elem=self.elem, UN=UN, id=dom
                )
            self.material_map_satus = True

    def __set_linear_form(self):
        """
        internal use only: set the linear form L(u) from the parameters
        """
        pass_info("FEN4NRV: setup the linear form")
        # Check if quicker without
        c_0 = Constant(self.domain, ScalarType(0.0))
        if not self.inbound:
            self.L = c_0 * self.u * self.dx
        else:
            for i_space in range(self.Nspace):
                self.L = c_0 * self.u[i_space] * self.dx
        self.linear_form_status = True

    #####################################################
    ################# Solve the sytstem #################
    #####################################################

    def get_solver_opt(self):
        """
        get krylov solver options
        """
        return self.petsc_opt

    def set_solver_opt(
        self,
        ksp_type=None,
        pc_type=None,
        ksp_rtol=None,
        ksp_atol=None,
        ksp_max_it=None,
        **kwargs,
    ):
        """
        set krylov solver options

        Parameters
        ----------
        ksp_type        : str
            value to set for ksp_type (solver type), if None don"t change, None by default
        pc_type         : str
            value to set for pc_type (preconditioner type), if None don"t change, None by default
            list of possible
        ksp_rtol        : float
            value to set for ksp_rtol (relative tolerance), if None don"t change, None by default
        ksp_atol        : float
            value to set for ksp_atol (absolute tolerance), if None don"t change, None by default
        ksp_max_it      : int
            value to set for ksp_max_it (max number of iterations), if None don"t change, None by default
        """
        if ksp_type is not None:
            if ksp_type in ksp_type_list:
                self.petsc_opt["ksp_type"] = ksp_type
            else:
                rise_warning(ksp_type + " not set, should be in:\n" + ksp_type_list)
        if pc_type is not None:
            if pc_type in pc_type_list:
                self.petsc_opt["pc_type"] = pc_type
            else:
                rise_warning(pc_type + " not set, should be in:\n" + pc_type_list)
        if ksp_rtol is not None:
            self.petsc_opt["ksp_rtol"] = ksp_rtol
        if ksp_atol is not None:
            self.petsc_opt["ksp_atol"] = ksp_atol
        if ksp_max_it is not None:
            self.petsc_opt["ksp_max_it"] = ksp_max_it
        for key in kwargs:
            if "pc" in key and self.petsc_opt["pc_type"] in key:
                self.petsc_opt[key] = kwargs[key]
            elif "ksp" in key and self.petsc_opt["ksp_type"] in key:
                self.petsc_opt[key] = kwargs[key]
            else:
                rise_warning(key + " is not a valid solver option not set")

    def set_result_merging(self, to_merge=None):
        if isinstance(to_merge, bool):
            self.to_merge = to_merge
        else:
            self.to_merge = not self.to_merge

    def solve(self, overwrite=False):
        """
        Assemble and solve the linear problem

        Parameters
        ----------
        overwrite   : bool
            if true modify the existing sim_res value, else create a new one. by default False
        Returns
        -------
        self.results    : FEMResults
            FEMResults containing the result of the resulting field of the FEM simulation
        """
        t0 = time.time()
        pass_info("FEN4NRV: solving electrical potential")
        if self.cg_problem is None:
            self.mixedvout = Function(self.V)
            self.cg_problem = LinearProblem(
                self.a, self.L, bcs=self.bcs, petsc_options=self.petsc_opt
            )
        self.mixedvout.x.array[:] = self.cg_problem.solve().x.array
        self.solve_status = True

        if self.inbound and self.to_merge:
            V_sol = self.__merge_mixed_solutions()
        else:
            self.vout = self.mixedvout.copy()
            V_sol = self.V

        # return simulation result
        self.result = FEMResults()
        if not overwrite:
            vout = Function(V_sol)
            vout.x.array[:] = self.vout.x.array[:]
        else:
            vout = self.vout
        self.result.set_sim_result(
            mesh_file=self.mesh_file,
            domain=self.domain,
            elem=self.multi_elem,
            V=V_sol,
            vout=vout,
            comm=self.domain.comm,
        )
        self.solving_timer += time.time() - t0
        pass_info("FEN4NRV: solved in " + str(self.solving_timer) + " s")
        return self.result

    def __merge_mixed_solutions(self):
        if self.dg_problem is None:
            self.mixedvouts = self.mixedvout.split()
            self.V_DG = functionspace(
                self.domain, ("Discontinuous Lagrange", self.elem[1])
            )
            u_, v_ = TrialFunction(self.V_DG), TestFunction(self.V_DG)
            adg = u_ * v_ * self.dx
            Ldg = 0
            for i_domain in self.domainsID:
                i_space = self.get_space_of_domain(i_domain)
                Ldg += v_ * self.mixedvout[i_space] * self.dx(i_domain)
            self.dg_problem = LinearProblem(
                adg, Ldg, bcs=[], petsc_options=self.petsc_opt
            )
        else:
            mixedvouts = self.mixedvout.split()
            for i in range(len(mixedvouts)):
                self.mixedvouts[i].x.array[:] = mixedvouts[i].x.array
        self.vout = self.dg_problem.solve()
        return self.V_DG

    def compute_conductance(self, order=None):
        self.__init_domain()
        self.__set_material_map()
        V_sigma = self.V
        od = order or self.elem[1]
        V_sigma = functionspace(self.domain, ("DG", od))
        sigma_out = []
        for i_space in range(self.Nspace):
            sigma = Function(V_sigma)
            for i_domain in self.domainsID:
                dom_cells = self.subdomains.find(i_domain)
                dom_dofs = locate_dofs_topological(
                    V_sigma, self.domain.topology.dim - 1, dom_cells
                )
                i_mat = self.get_mixedspace_domain(i_space=i_space, i_domain=i_domain)
                mat = self.mat_map[i_mat].mat
                if mat.is_isotropic():
                    val = np.full_like(dom_dofs, mat.sigma, dtype=default_scalar_type)
                elif not mat.is_func:
                    # val = mat.sigma_fen.value
                    _sig = sum(mat.sigma**2) ** 0.5
                    val = np.full_like(dom_dofs, _sig, dtype=default_scalar_type)
                elif mat.is_func:
                    sig_ = Function(V_sigma)
                    sig_.interpolate(mat.sigma_func)
                    val = sig_.x.array[dom_dofs]
                sigma.x.array[dom_dofs] = val
            self.sigma_results = FEMResults()
            self.sigma_results.set_sim_result(
                mesh_file=self.mesh_file,
                domain=self.domain,
                elem=self.multi_elem,
                V=V_sigma,
                vout=sigma,
                comm=self.domain.comm,
            )
            sigma_out += [self.sigma_results]
        return sigma_out

    #####################################################
    ################ Access the results #################
    #####################################################

    def solver_info(self, txt_fname="solver.txt"):
        solver = self.cg_problem.solver
        viewer = Viewer().createASCII(txt_fname)
        solver.view(viewer)
        solver_output = open(txt_fname, "r")
        for line in solver_output.readlines():
            pass_info(line)

    def solve_and_save_sim(self, filename, save=True):
        if not self.solve_status:
            self.solve()
        fname = rmv_ext(filename)
        self.result.save(fname)
        return self.result

    def get_timers(self):
        return self.solving_timer

    def visualize_mesh(self):
        os.system("gmsh " + self.mesh_file + ".msh")

    def get_surface(self, dom_id):
        S = assemble_scalar(form(1 * self.ds(dom_id)))
        if self.comm == COMM_WORLD:
            S = self.comm.reduce(S, op=SUM, root=0)
            S = self.comm.bcast(S, root=0)
        return S

    def get_domain_potential(self, dom_id, dim=2, space=0, surf=None):
        if dim == 2:
            do = self.ds
        elif dim == 3:
            do = self.dx
        if surf is None:
            surf = self.get_surface(dom_id)
        if self.to_merge:
            v_surf = assemble_scalar(form(self.vout * do(dom_id)))
        else:
            v_surf = assemble_scalar(form(self.vout[space] * do(dom_id)))
        return v_surf / surf
