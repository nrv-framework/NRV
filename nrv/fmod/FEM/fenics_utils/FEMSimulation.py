import os
import time

from dolfinx.fem import (
    Constant,
    Function,
    FunctionSpace,
    assemble_scalar,
    dirichletbc,
    form,
    locate_dofs_topological,
)
from dolfinx.fem.petsc import LinearProblem
from dolfinx.io.utils import XDMFFile
from mpi4py import MPI
from petsc4py.PETSc import ScalarType, Viewer
from ufl import (
    FiniteElement,
    Measure,
    MixedElement,
    TestFunction,
    TrialFunction,
    avg,
    inner,
    nabla_grad,
)

from ....backend.log_interface import pass_info, rise_error, rise_warning
from ....backend.file_handler import rmv_ext
from ....utils.units import S, V, m
from .fenics_materials import load_fenics_material
from .SimParameters import SimParameters
from .SimResult import read_gmsh, SimResult

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


class FEMSimulation(SimParameters):
    """
    Class usefull to solve the Static/Quasi-Static electrical current problem using FEM with
    FEniCSx algorithms (https://fenicsproject.org).

    / add equation /

    The problem parameters (domains and boundaries condition) can be define using SimParameters methods
    Contains methods to prepare the matrix sytstem, to solve it and to access the results.

    Inherit from SimParameters class. see SimParameters for further detail
    """

    def __init__(
        self,
        D=3,
        mesh_file="",
        mesh=None,
        data=None,
        elem=None,
        ummesh=True,
        comm=MPI.COMM_SELF,
        rank=0,
    ):
        """
        initialisation of the FEMSimulation:

        Parameters
        ----------
        D               : int
            dim of the mesh, by default 3
            NB: only 3 is implemented
        mesh_file       : str
            mesh directory and file name: by default ""
        mesh            : None or MshCreator
            if not None, MshCreator from which the mesh sould be used, by default None
            (see MshCreator and NerveMshCreator for more details)
        data            : str, dict or SimParameters
            if not None, load SimParameters attribute from data, by default None
            (see SimParameters.load)
        elem            :tupple (str, int)
            if None, ("Lagrange", 1), else (element type, element order), by default None
        ummesh          : bool
            if True the scale of mesh space dimensions should be (um), else (m), by default True
            Usefull to link the update materials conductivity as in NRV conductivities are in S/m
            but NerveMshCreator space scale is um)
        comm            : int
            The MPI communicator to use for mesh creation, by default MPI.COMM_SELF
        rank            : int
            The rank the Gmsh model is initialized on, by default 0
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
        self.dirichlet_BC_status = False
        self.neumann_BC_status = False
        self.bilinear_form_status = False
        self.jump_status = False
        self.linear_form_status = False
        self.prepared_status = False
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
        if self.prepared_status:
            if mesh_domain in self.mat_map:
                mat = load_fenics_material(mat_pty)
                self.mat_map[mesh_domain].load_from_mat(mat)
            else:
                rise_warning(
                    "Domain not added: new domain cannot be added between 2 simulations,\
                             (set domain before simulation or create a new one)"
                )

    def add_domain(
        self, mesh_domain, mat_pty=None, mat_file=None, mat_perm=None, ID=None
    ):
        super().add_domain(mesh_domain, mat_pty, mat_file, mat_perm, ID)
        if self.prepared_status:
            if mesh_domain in self.mat_map:
                mat = load_fenics_material(mat_pty)
                self.mat_map[mesh_domain].load_from_mat(mat)
            else:
                rise_warning(
                    "Domain not added: new domain cannot be added between 2 simulations,\
                             (set domain before simulation or create a new one)"
                )

    #####################################################
    ############ Prepare the matrix sytstem #############
    #####################################################

    def prepare_sim(self, **kwargs):
        """
        Prepare Bilinear form, Linear form and boundary conditions using paramters and kwargs
        to set the variable defined Neumann boundary conditions (see SimParameters.add_boundary)
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
                self.mixedvout = TrialFunction(self.V)
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
            self.prepared_status = True
            self.solving_timer += time.time() - t0
        else:
            rise_warning("no parameters are set, Sim can not be prepared")

    def __init_domain(self):
        """
        internal use only:
        """
        if not self.domain_status:
            # RECOVERING THE GEOMETRY
            self.domain, self.subdomains, self.boundaries = read_gmsh(
                self.mesh, comm=self.comm, rank=self.rank, gdim=3
            )
            # SPACE FOR INTEGRATION
            if self.inbound:
                self.Nspace = self.Ninboundaries + 1
                ME = [
                    FiniteElement(self.elem[0], self.domain.ufl_cell(), self.elem[1])
                    for k in range(self.Nspace)
                ]
                self.multi_elem = MixedElement(ME)
            else:
                self.multi_elem = self.elem
            self.V = FunctionSpace(self.domain, self.multi_elem)
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
        for i in self.boundaries_list:
            bound = self.boundaries_list[i]
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
        NB: Only variable NBC (see SimParameters.add_boundary) can be changed between simulations
        """
        if not self.neumann_BC_status:
            for i_bound in self.boundaries_list:
                bound = self.boundaries_list[i_bound]
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
            for i_bound in self.boundaries_list:
                bound = self.boundaries_list[i_bound]
                condition = bound["condition"]
                if condition.lower() in "neumann" and "variable" in bound:
                    if bound["variable"] in self.args:
                        self.Neuman_list[i_bound].value = self.args[bound["variable"]]

    def __set_bilinear_form(self):
        """
        internal use only: set the bilinear form a(vout, u) from the parameters
        """
        pass_info("FEN4NRV: preparing the bilinear form")
        self.__set_material_map()
        for i_space in range(self.Nspace):
            for i_domain in self.domains_list:
                dom = self.get_mixedspace_domain(i_space=i_space, i_domain=i_domain)
                if self.a is None:
                    self.a = self.__get_static_component(i_domain, dom, i_space)
                else:
                    self.a += self.__get_static_component(i_domain, dom, i_space)
        if self.inbound:
            self.__set_jump()
        self.bilinear_form_status = True

    def __get_static_component(self, i_dom, i_mat, i_space):
        """
        Set a static componnent of the bimlinear form:
        a = ∇v[i_space] x 𝜎[i_mat]∇u[i_space] dx(i_dom)
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
                nabla_grad(self.mixedvout),
                self.mat_map[i_mat].sigma_fen * nabla_grad(self.u),
            ) * self.dx(i_dom)
        else:
            return inner(
                nabla_grad(self.mixedvout[i_space]),
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
            jmp_v = avg(self.mixedvout[out_space]) - avg(self.mixedvout[in_space])
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
        if self.mat_unit == "S/um":
            UN = S / m
        else:
            UN = 1
        for dom, pty in self.mat_pty_map.items():
            self.mat_map[dom] = load_fenics_material(pty)
            self.mat_map[dom].update_fenics_sigma(
                domain=self.domain, elem=self.elem, UN=UN, id=dom
            )

    def __set_linear_form(self):
        """
        internal use only: set the linear form L(u) from the parameters
        """
        pass_info("FEN4NRV: preparing the linear form")
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
        self, ksp_type=None, pc_type=None, ksp_rtol=None, ksp_atol=None, ksp_max_it=None
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
        self.results    : SimResult
            SimResult containing the result of the resulting field of the FEM simulation
        """
        t0 = time.time()
        pass_info("FEN4NRV: solving electrical potential")
        if self.cg_problem is None:
            self.cg_problem = LinearProblem(
                self.a, self.L, bcs=self.bcs, petsc_options=self.petsc_opt
            )
        self.mixedvout = self.cg_problem.solve()
        self.solve_status = True

        if self.inbound and self.to_merge:
            V_sol = self.__merge_mixed_solutions()
        else:
            self.vout = self.mixedvout.copy()
            V_sol = self.V

        # return simulation result
        self.result = SimResult()
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
            self.V_DG = FunctionSpace(
                self.domain, ("Discontinuous Lagrange", self.elem[1])
            )
            u, v = TrialFunction(self.V_DG), TestFunction(self.V_DG)
            adg = u * v * self.dx
            Ldg = 0
            for i_domain in self.domainsID:
                i_space = self.get_space_of_domain(i_domain)
                Ldg += v * self.mixedvout[i_space] * self.dx(i_domain)
            self.dg_problem = LinearProblem(
                adg, Ldg, bcs=[], petsc_options=self.petsc_opt
            )
        else:
            mixedvouts = self.mixedvout.split()
            for i in range(len(mixedvouts)):
                self.mixedvouts[i].x.array[:] = mixedvouts[i].x.array
        self.vout = self.dg_problem.solve()
        return self.V_DG

    #####################################################
    ################ Access the results #################
    #####################################################

    def solver_info(self, txt_fname="solver.txt"):
        solver = self.cg_problem.solver
        viewer = Viewer().createASCII(txt_fname)
        solver.view(viewer)
        solver_output = open(txt_fname, "r")
        for line in solver_output.readlines():
            print(line)

    def solve_and_save_sim(self, filename, save=True):
        if not self.solve_status:
            self.solve()

        fname = rmv_ext(filename)
        if not (fname == filename or fname + ".xdmf" == filename):
            rise_warning("Extension of solution will be save in xdmf files")
        with XDMFFile(self.domain.comm, fname + ".xdmf", "w") as file:
            file.write_mesh(self.domain)
            file.write_function(self.vout)
        return self.result

    def get_timers(self):
        return self.solving_timer

    def visualize_mesh(self):
        os.system("gmsh " + self.mesh_file + ".msh")

    def get_domain_potential(self, dom_id, dim=2, space=0):
        if dim == 2:
            do = self.ds
        elif dim == 3:
            do = self.dx
        Surf = assemble_scalar(form(1 * do(dom_id)))
        if self.to_merge:
            return assemble_scalar(form(self.vout * do(dom_id))) / Surf * V
        else:
            return assemble_scalar(form(self.vout[space] * do(dom_id))) / Surf * V
