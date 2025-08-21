from dolfinx.fem.petsc import LinearProblem
from ufl import TestFunction, TrialFunction, grad, inner, Measure
from basix.ufl import element
from dolfinx.fem import (
    Constant,
    functionspace,
    Function,
    assemble_scalar,
    form,
    locate_dofs_topological,
    dirichletbc,
)
from dolfinx.io.utils import VTXWriter


from petsc4py.PETSc import ScalarType
from mpi4py import MPI
import gmsh
import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter

from ..utils import _units as uni

from ._eit_forward import eit_forward
from .utils._misc import (
    compute_sigma_2D_old,
    compute_sigma_2D,
    in_circle,
    in_bbox,
    compute_mye_sigma_2D,
)

from ..backend import pass_info, rmv_ext
from ..fmod.FEM.mesh_creator import get_mesh_domid
from ..fmod.FEM.fenics_utils import read_gmsh, layered_material
from ..nmod.results import axon_results
from ..utils import convert
from ..utils.geom import CShape

sig_2D_method_list = [
    "single_val",
    "avg_ind",
    "avg_inter",
    "avg_inter_approx",
]

sig_2D_method_list_deprecated = {
    "mean": "avg_ind",
    "convolve": "avg_inter",
}


class EIT2DProblem(eit_forward):
    """
    End-used class for Electrical Impedance Tomography (EIT) forward simulation in neural contexts solved with a 2D approximation.

    This class extends `eit_forward` to provide specialized methods for setting up, meshing, and solving EIT problems in a 2D (Oyz) plan. It supports:
      - mesh generation with axons
      - physical domain assignment
      - finite element method (FEM) initialization
      - conductivity updates during the simulation.

    Warning
    -------
    For now the 2D approximation isn't well documented. Further explaination will be added to the doc in the future.


    Note
    ----
    - Mesh generation and FEM setup rely on GMSH and FEniCS/Dolfinx libraries with interface integrated into this class classes.
    - Conductivity calculations support various methods, including myelinated and unmyelinated axons.
    """

    def __init__(
        self,
        nervefile: str,
        res_dname: str | None = None,
        label: str = "2deit_1",
        **parameters
    ):
        self.sigma_method: str = "avg_ind"
        super().__init__(nervefile, res_dname=res_dname, label=label, **parameters)

    @property
    def dim(self) -> int:
        return 2

    @property
    def x_bounds_fem(self):
        if self.sigma_method in ["mean", "avg_ind"] or "inter" in self.sigma_method:
            return (self.x_rec - self.l_elec / 2, self.x_rec + self.l_elec / 2)
        # elif "inter"  in self.sigma_method:
        #     return (self.x_rec-self.l_fem/2, self.x_rec+self.l_fem/2)
        return self.x_rec

    def _setup_problem(self):
        super()._setup_problem()
        self.r_cir = self.nerve_results.D / 2

        self.n_fa = self.nerve_results.n_fasc

        self.r_ax = self.axnod_d / 2
        self.y_ax = self._axons_pop_ppts["y"].to_numpy(dtype=float)
        self.z_ax = self._axons_pop_ppts["z"].to_numpy(dtype=float)
        self.UN = uni.S / uni.m
        self.unaligned_axons = np.array([])

    def set_ncore_gmsh(self, ncore_meshing):
        gmsh.option.setNumber("General.NumThreads", ncore_meshing)
        if ncore_meshing > 1:
            gmsh.option.set_number("Mesh.Algorithm3D", 10)
        else:
            gmsh.option.set_number("Mesh.Algorithm3D", 1)

    def get_info(self, verbose=False):
        entities = gmsh.model.getEntities()
        nodeTags = gmsh.model.mesh.getNodes()[0]
        elemTags = gmsh.model.mesh.getElements()[1]

        n_entities = len(entities)
        n_nodes = len(nodeTags)
        n_elements = sum(len(i) for i in elemTags)
        n_proc = self.get_nproc("mesh")
        if verbose:
            pass_info("Mesh properties:")
            pass_info("Number of processes : " + str(n_proc))
            pass_info("Number of entities : " + str(n_entities))
            pass_info("Number of nodes : " + str(n_nodes))
            pass_info("Number of elements : " + str(n_elements))
        return n_proc, n_entities, n_nodes, n_elements

    def __add_from_cshape(
        self,
        shape: CShape,
        n_pts_trace: int = 100,
        x: float = 0,
        dx: float = 10,
        res: None | float = None,
    ):
        """
        genertate a volume by extruding a :class:`....utils.geom._cshape.CShape` along

        Warining
        --------
        Not fully implemented

        Parameters
        ----------
        shape       : CShape
            shape to set as initial
        n_pts_trace       : float
            z position of the x-min face center
        x       : float
            x position of the x-min face center
        dx       : float
            Cylinder length along x

        Returns
        -------
        cyl    : int
            id of the added object
        """
        if res is not None:
            # NOTE TC - alpha is arbitrarily set to 5 see if it needs to be access
            alpha = 5
            n_pts_trace = alpha * round(shape.perimeter / res)
        pt_tags = []
        y_trace, z_trace = shape.get_trace(n_theta=n_pts_trace)

        # Create OCC points
        for y, z in zip(y_trace, z_trace):
            pt_tags.append(gmsh.model.occ.addPoint(x, y, z))

        # Connect with a periodic B-spline curve (closed loop)
        curve = gmsh.model.occ.addBSpline(pt_tags + [pt_tags[0]])

        # Make curve loop and surface
        loop = gmsh.model.occ.addCurveLoop([curve])
        surf = gmsh.model.occ.addPlaneSurface([loop])
        gmsh.model.occ.synchronize()
        return surf

    def build_mesh(self, with_axons: bool = True):
        """
        creation of mesh file

        Parameters
        ----------
        mesh_file: str | None, optional
            filename of the mesh, by default None
            if true output .msh saved in a .json

        """
        super().build_mesh()
        __ts = perf_counter()
        # check if problem is defined
        if not self.defined_pb:
            self._setup_problem()

        if with_axons:
            __n_ax = self.n_c
        else:
            __n_ax = 0
        # MESH JOB
        _zaxis = [0, 0, 1]
        _xaxis = [-1, 0, 0]
        gmsh.initialize()
        gmsh.option.setNumber("General.Verbosity", 2)
        gmsh.model.add("self.circle")
        self.set_ncore_gmsh(self.get_nproc("mesh"))

        ## Geometry
        all_ids = []
        cir = gmsh.model.occ.addDisk(
            0, 0, 0, self.r_cir, self.r_cir, zAxis=_zaxis, xAxis=_xaxis, tag=1
        )
        all_ids += [(2, cir)]

        self.c_fa_ids = []
        fasc_bbox = []
        for i_fa in self.fasc_geometries:
            cir = self.__add_from_cshape(self.fasc_geometries[i_fa])
            self.c_fa_ids += [(2, cir)]
            fasc_bbox += [np.round(gmsh.model.occ.getBoundingBox(2, cir), 4)]

        self.c_in_ids = []
        for i_c in range(__n_ax):
            cir = gmsh.model.occ.addDisk(
                -self.z_ax[i_c],
                self.y_ax[i_c],
                0,
                self.r_ax[i_c],
                self.r_ax[i_c],
                tag=self.n_fa + 2 + i_c,
                zAxis=_zaxis,
                xAxis=_xaxis,
            )
            all_ids += [(2, cir)]
            self.c_in_ids += [(2, cir)]

        bar_ids = []
        CoF_arc = self.w_elec / (2 * np.arcsin(self.w_elec / (2 * self.r_cir)))
        elec_coms = np.zeros((self.n_elec, 2))

        for i in range(self.n_elec):
            bar = gmsh.model.occ.addRectangle(
                0, -self.w_elec / 2, 0, self.r_cir * 1.1, self.w_elec
            )
            angle = (np.pi / 2) - ((2 * np.pi * i) / (self.n_elec))
            gmsh.model.occ.rotate([(2, bar)], 0, 0, 0, 0, 0, 1, angle)
            bar_ids += [(2, bar)]

            # Compute the electrode center of map to ecover the line id
            z_elec_com = CoF_arc * np.exp(1j * angle)
            elec_coms[i][0] = np.real(z_elec_com)
            elec_coms[i][1] = np.imag(z_elec_com)

        dis3 = gmsh.model.occ.addDisk(
            0, 0, 0, self.r_cir, self.r_cir, zAxis=_zaxis, xAxis=_xaxis
        )
        elec = gmsh.model.occ.cut(bar_ids, [(2, dis3)])[0]
        all_ids += elec
        gmsh.model.occ.rotate(all_ids, 0, 0, 0, 0, 1, 0, np.pi / 2)

        gmsh.model.occ.fragment([(2, 1)], elec + self.c_fa_ids + self.c_in_ids)
        gmsh.model.occ.synchronize()

        ## Physical Domains
        # recover the 1D geometrical ID to set the physical domain
        lines = gmsh.model.occ.getEntities(dim=1)
        line_elec = [[] for _ in range(self.n_elec)]
        for line in lines:
            _, x, y = gmsh.model.occ.getCenterOfMass(line[0], line[1])
            if np.isclose(y, CoF_arc):
                line_elec[0] += [line[1]]
            for i in range(self.n_elec):
                if np.allclose([x, y], elec_coms[i]):
                    line_elec[i] += [line[1]]

        surfs = gmsh.model.occ.getEntities(dim=2)
        id_elt_ne = []
        id_elt_fa = [[] for _ in range(self.n_fa)]
        id_elt_ax = [[] for _ in range(__n_ax)]
        for surf in surfs:
            _, y, z = gmsh.model.occ.getCenterOfMass(surf[0], surf[1])
            bbox = gmsh.model.occ.getBoundingBox(surf[0], surf[1])
            dx, dy = abs(bbox[1] - bbox[4]), abs(bbox[2] - bbox[5])
            # Nerve surface
            if np.allclose([dx, dy], [self.nerve_results.D, self.nerve_results.D]):
                id_elt_ne += [surf[1]]
            # Fascicles surfaces
            for i in range(self.n_fa):
                bb_mask = np.allclose(np.round(bbox, 4), fasc_bbox[i])
                if bb_mask:
                    id_elt_fa[i] += [surf[1]]
            # Axons surfaces
            for i in range(__n_ax):
                __y_dom, __z_dom = self.y_ax[i], self.z_ax[i]
                bb_mask = np.allclose([dx, dy], [self.r_ax[i] * 2, self.r_ax[i] * 2])
                com_mask = np.allclose([y, z], [__y_dom, __z_dom])
                if bb_mask & com_mask:
                    id_elt_ax[i] += [surf[1]]

        # set 1D physical groups
        for i_elec in range(self.n_elec):
            id_ph = get_mesh_domid("e", i_elec, is_surf=True)
            gmsh.model.addPhysicalGroup(1, line_elec[i_elec], id_ph)

        # set 2D physical groups

        gmsh.model.addPhysicalGroup(2, id_elt_ne, 1)
        for i_fa, id_elt in enumerate(id_elt_fa):
            id_ph = get_mesh_domid("f", i_fa)
            gmsh.model.addPhysicalGroup(2, id_elt, id_ph)
        for i_ax, id_elt in enumerate(id_elt_ax):
            id_ph = get_mesh_domid("a", i_ax)
            gmsh.model.addPhysicalGroup(2, id_elt, id_ph)

        ## Resolution
        n_field = 0
        for i_fa, id_elt in enumerate(id_elt_fa):
            gmsh.model.mesh.field.add("Constant", n_field)
            gmsh.model.mesh.field.setNumbers(n_field, "SurfacesList", id_elt)
            gmsh.model.mesh.field.setNumber(n_field, "IncludeBoundary", True)
            gmsh.model.mesh.field.setNumber(n_field, "VIn", self.res_f[i_fa])
            gmsh.model.mesh.field.setNumber(n_field, "VOut", self.res_n)
            n_field += 1

        for i_ax, id_elt in enumerate(id_elt_ax):
            gmsh.model.mesh.field.add("Constant", n_field)
            gmsh.model.mesh.field.setNumbers(n_field, "SurfacesList", id_elt)
            gmsh.model.mesh.field.setNumber(n_field, "IncludeBoundary", True)
            gmsh.model.mesh.field.setNumber(n_field, "VIn", self.res_a[i_ax])
            gmsh.model.mesh.field.setNumber(n_field, "VOut", self.res_n)
            n_field += 1

        for i_elec, id_elt in enumerate(line_elec):
            gmsh.model.mesh.field.add("Constant", n_field)
            gmsh.model.mesh.field.setNumbers(n_field, "CurvesList", id_elt)
            gmsh.model.mesh.field.setNumber(n_field, "IncludeBoundary", True)
            gmsh.model.mesh.field.setNumber(n_field, "VIn", self.res_e)
            gmsh.model.mesh.field.setNumber(n_field, "VOut", self.res_n)
            n_field += 1

        gmsh.model.mesh.field.add("Min", n_field)
        gmsh.model.mesh.field.setNumbers(
            n_field, "FieldsList", [i_f for i_f in range(n_field)]
        )

        gmsh.model.mesh.field.setAsBackgroundMesh(n_field)
        # gmsh.option.setNumber('Mesh.MeshSizeMin', 1)
        # gmsh.option.setNumber('Mesh.MeshSizeMax', 1)
        gmsh.option.setNumber("Geometry.NumSubEdges", 100)

        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)
        gmsh.write(self.nerve_mesh_file)
        # Store info
        self.mesh_info["fname"] = self.nerve_mesh_file
        (
            self.mesh_info["n_proc"],
            self.mesh_info["n_entities"],
            self.mesh_info["n_nodes"],
            self.mesh_info["n_elements"],
        ) = self.get_info(verbose=True)
        gmsh.finalize()
        self.mesh_built = True
        self.fem_initialized = False
        __tf = perf_counter()
        self.mesh_timer += __tf - __ts

    def _init_fem(self):
        """
        initialization of fem

        Parameters
        ----------
        mesh_file: str | None, optional
            filename of the mesh, by default None

        """
        if not self.mesh_built:
            self.build_mesh()
        # load mesh

        self.domain, self.ct, self.ft = read_gmsh(
            self.nerve_mesh_file, comm=MPI.COMM_SELF, gdim=3
        )
        # FEM INIT HERE
        # FEM domain definition
        self.element = element("CG", self.domain.basix_cell(), 2)
        self.V = functionspace(self.domain, self.element)

        # Integration tools
        dx = Measure("dx", domain=self.domain, subdomain_data=self.ct)
        self.ds = Measure("ds", domain=self.domain, subdomain_data=self.ft)

        f = Constant(self.domain, ScalarType(0))
        Gnd = Constant(self.domain, ScalarType(0))
        self.sigepi = Constant(self.domain, ScalarType(self.sigma_epi))  # *self.UN))
        self.sigendo = Constant(self.domain, ScalarType(self.sigma_endo))  # *self.UN))
        self.sigax = [Constant(self.domain, ScalarType(0)) for _ in range(self.n_c)]
        bcs = []
        if self.use_gnd_elec:
            e_dom = get_mesh_domid("e", self.gnd_elec_id, is_surf=True)
            label = self.ft.find(e_dom)
            dofs = locate_dofs_topological(self.V, 1, label)
            bcs.append(dirichletbc(Gnd, dofs, self.V))

        # Static Laplace equations (weak formulation)
        u = TrialFunction(self.V)
        v = TestFunction(self.V)
        a = self.sigepi * inner(grad(u), grad(v)) * dx(1)
        for i_fa in range(self.n_fa):
            id_ph = get_mesh_domid("f", i_fa)
            a += self.sigendo * inner(grad(u), grad(v)) * dx(id_ph)
        for i_ax in range(self.n_c):
            id_ph = get_mesh_domid("a", i_ax)
            a += self.sigax[i_ax] * inner(grad(u), grad(v)) * dx(id_ph)
        L = inner(f, v) * dx

        # Set Neumann boundary condition for each electrode
        self.j_elecs = []
        self.s_elec = []
        for i_elec in range(self.n_elec):
            id_ph = get_mesh_domid("e", i_elec, is_surf=True)
            self.j_elecs += [Constant(self.domain, ScalarType(0))]
            L += inner(self.j_elecs[-1], v) * self.ds(id_ph)
            self.s_elec += [assemble_scalar(form(1 * self.ds(id_ph)))]

        # Compute solution
        self.problem = LinearProblem(a, L, bcs=bcs, petsc_options=self.petsc_opt)
        self.fem_initialized = True

    def _clear_fem(self):
        if self.fem_initialized:
            del (
                self.domain,
                self.ct,
                self.ft,
                self.element,
                self.V,
                self.ds,
                self.sigepi,
                self.sigax,
                self.problem,
            )
            self.fem_initialized = False

    def __get_mat_axon_mem(
        self, ax_res: axon_results, i_t: int, method: str | None = None
    ) -> float | complex:
        """
        Computes the axonal membrane admittance or conductivity for a given time index and method.

        Parameters
        ----------
        ax_res : axon_results
            The results object containing axon properties and methods for retrieving membrane parameters.
        i_t : int
            The time index at which to compute the membrane property.
        method : str or None, optional
            The method to use for computation. If None, uses `self.sigma_method`. Supported methods include:
            - "mye": Myelinated axon calculation.
            - "mean", "avg_ind": Mean or average individual calculation.
            - "inter", "convolve": Interpolated or convolved calculation (with optional "old" variant).
            - Other methods default to direct calculation at `self.x_rec`.

        Returns
        -------
        float or complex
            The computed membrane admittance or conductivity, depending on the frequency and method.
        """

        if method is None:
            method = self.sigma_method.lower()
        if "mye" in method:
            if len(ax_res["x_rec"]) > 0:
                if self.current_freq == 0:
                    Y_mem_t = ax_res.get_membrane_conductivity(
                        x=None, i_t=i_t, mem_th=self.ax_mem_th, unit="S/m"
                    )
                else:
                    Y_mem_t = ax_res.get_membrane_complexe_admitance(
                        f=self.current_freq,
                        x=None,
                        i_t=i_t,
                        mem_th=self.ax_mem_th,
                        unit="S/m",
                    )
            else:
                Y_mem_t = np.array([])
        elif method in ["mean", "avg_ind"]:
            if self.current_freq == 0:
                Y_mem_t = np.mean(
                    ax_res.get_membrane_conductivity(
                        x=None, i_t=i_t, mem_th=self.ax_mem_th, unit="S/m"
                    )
                )
            else:
                Y_mem_t = np.mean(
                    ax_res.get_membrane_complexe_admitance(
                        f=self.current_freq,
                        x=None,
                        i_t=i_t,
                        mem_th=self.ax_mem_th,
                        unit="S/m",
                    )
                )
        elif "inter" in method or "convolve" in method:
            if self.current_freq == 0:
                Y_m_t = ax_res.get_membrane_conductivity(
                    x=None, i_t=i_t, mem_th=self.ax_mem_th, unit="S/m"
                )
            else:
                Y_m_t = ax_res.get_membrane_complexe_admitance(
                    f=self.current_freq,
                    x=None,
                    i_t=i_t,
                    mem_th=self.ax_mem_th,
                    unit="S/m",
                )
            if "old" in method:
                Y_mem_t = compute_sigma_2D_old(
                    Y_m_t,
                    ax_res["x_rec"],
                    sig_in=self.sigma_axp,
                    sig_out=self.sigma_endo,
                    l_elec=self.l_elec,
                )
            else:
                Y_mem_t = compute_sigma_2D(
                    Y_m_t,
                    ax_res["x_rec"],
                    sig_in=self.sigma_axp,
                    sig_out=self.sigma_endo,
                    d_ax=ax_res["d"],
                    th_mem=self.ax_mem_th,
                    l_elec=self.l_elec,
                    method=method,
                )
        else:
            if self.current_freq == 0:
                Y_mem_t = ax_res.get_membrane_conductivity(
                    x=self.x_rec, i_t=i_t, mem_th=self.ax_mem_th, unit="S/m"
                )
            else:
                Y_mem_t = ax_res.get_membrane_complexe_admitance(
                    f=self.current_freq,
                    x=self.x_rec,
                    i_t=i_t,
                    mem_th=self.ax_mem_th,
                    unit="S/m",
                )
        return Y_mem_t

    def _update_mat_axons(self, i_t: int, i_t_1: int = -1) -> bool:
        """
        problem is already defined, update sigma axons between time steps

        Parameters
        ----------
        t : float , the time step
            if t is different from 0, by default False


        Returns
        -------
        Bool , by default True

        """
        has_changed = i_t_1 > 0
        for i_ax, (i_ax_pop, _ax_ppts) in enumerate(self._axons_pop_ppts.iterrows()):
            ax_res = self.nerve_results[_ax_ppts["fkey"]][_ax_ppts["akey"]]
            if "d" not in ax_res.keys():
                ax_res["d"] = _ax_ppts["diameters"]

            # Myelinated axon
            if _ax_ppts["types"]:
                if ax_res["rec"] == "nodes":
                    Y_mem_t = self.__get_mat_axon_mem(
                        ax_res=ax_res, i_t=i_t, method="mye"
                    )
                    # ax_res.get_membrane_conductivity(x=None, i_t=i_t, mem_th=self.ax_mem_th, unit="S/m")
                    sigma_ax = compute_mye_sigma_2D(
                        Y_mem_t,
                        x_rec=ax_res["x_rec"],
                        sig_mye=self.myelin_mat[i_ax],
                        sig_in=self.sigma_axp,
                        sig_out=self.sigma_endo,
                        d_ax=ax_res["d"],
                        d_node=self.axnod_d[i_ax],
                        alpha_th=self.alpha_in_c[i_ax],
                        l_elec=self.l_elec,
                    )
                    if i_t == -1 and len(ax_res["x_rec"]) == 0:
                        np.append(self.unaligned_axons, i_ax)
                    self.sigax[i_ax].value = sigma_ax
                    # ax_mat = layered_material(mat_in=self.sigma_axp, mat_lay=sigma_ax, alpha_lay=)
                    # frac_l_node = 1. * len(ax_res["x_rec"])/self.l_elec
                    # self.sigax[i_ax].value = frac_l_node*ax_mat.sigma +(1-frac_l_node)*self.myelin_mat #*self.UN
                else:
                    frac_l_node = 1.0 * len(ax_res["x_rec"]) / self.l_elec
                    Y_mem_t = np.mean(
                        self.__get_mat_axon_mem(ax_res=ax_res, i_t=i_t, method="mye")
                    )
                    ax_node_mat = layered_material(
                        mat_in=self.sigma_axp,
                        mat_lay=Y_mem_t,
                        alpha_lay=self.alpha_in_c[i_ax],
                    )

                    self.sigax[i_ax].value = (
                        ax_node_mat.sigma + (1 - frac_l_node) * self.myelin_mat[i_ax]
                    )
            # Unmyelinated axon
            else:
                Y_mem_t = self.__get_mat_axon_mem(ax_res=ax_res, i_t=i_t)
                ax_mat = layered_material(
                    mat_in=self.sigma_axp,
                    mat_lay=Y_mem_t,
                    alpha_lay=self.alpha_in_c[i_ax],
                )
                self.sigax[i_ax].value = ax_mat.sigma  # *self.UN
                if not has_changed:
                    Y_mem_t_1 = self.__get_mat_axon_mem(ax_res=ax_res, i_t=i_t_1)
                    has_changed = not np.isclose(
                        Y_mem_t, Y_mem_t_1, rtol=1e-7, atol=1.0e-13
                    )
        return has_changed

    def _compute_v_elec(self, sfile: None | str = None, i_t: int = 0) -> np.ndarray:
        __v = np.zeros(self.n_elec, dtype=ScalarType)
        for i_elec, e_str in enumerate(self.electrodes):
            self.j_elecs[i_elec].value = self.electrodes[e_str] / self.l_elec
            # if self.sigma_method != "avg_inter":
            #     self.j_elecs[i_elec].value /= self.l_elec
        # FEM simulation
        u_n = Function(self.V)
        u_n = self.problem.solve()
        # extract single ended measurements
        for i_rec in range(self.n_elec):
            id_ph = get_mesh_domid("e", i_rec, is_surf=True)
            __v[i_rec] = (
                assemble_scalar(form(u_n * self.ds(id_ph))) / self.s_elec[i_rec]
            )
        if sfile is not None:
            fname = rmv_ext(sfile) + ".bp"
            with VTXWriter(self.domain.comm, fname, u_n, "bp4") as f:
                f.write(self.times[i_t])
            return self.V, u_n, __v
        del u_n

        # Conversion: (mesh unit:= [um])
        # sigma ∇ __v = j -> [__v] = [j]([∇][sigma])^-1
        # [__v] = [A].[um]-2 . [um].[m][S]^-1 = [A]([S].10^-6)^-1 = [MV]
        __v = convert(__v, unitin="MV", unitout="V")
        return __v
