
from time import perf_counter
import numpy as np

from ._eit_forward import eit_forward

from ..backend import pass_info
from ..fmod import CUFF_MP_electrode, CUFF_electrode
from ..fmod.FEM import check_sim_dom
from ..fmod.FEM.fenics_utils import FEMSimulation, layered_material
from ..fmod.FEM.mesh_creator import ENT_DOM_offset, get_mesh_domid, get_node_physical_id
from ..ui import mesh_from_nerve, mesh_from_electrode


ScalarType = np.float64


class EIT3DProblem(eit_forward):
    def __init__(self, nervefile, res_dname=None, label="3deit_1", **parameters):
        super().__init__(nervefile, res_dname=res_dname, label=label, **parameters)

    @property
    def x_bounds_fem(self):
        return (self.x_rec - self.l_fem/2, self.x_rec + self.l_fem/2)

    def _define_problem(self):
        super()._define_problem()
        if self.use_gnd_elec and (self.gnd_elec_id < 0 or self.n_elec < 0):
            self.eit_elec = CUFF_MP_electrode(N_contact=self.n_elec, x_center=self.l_fem/2-self.l_elec,contact_width=self.w_elec, contact_length=self.l_elec, insulator=False)
            self.gnd_elec = CUFF_electrode(x_center=self.l_fem/2+self.l_elec, contact_length=self.l_elec/2, insulator=False)
            self.gnd_elec_id = self.n_elec
        else:
            self.eit_elec = CUFF_MP_electrode(N_contact=self.n_elec, x_center=self.l_fem/2,contact_width=self.w_elec, contact_length=self.l_elec, insulator=False)
            self.gnd_elec = None

    def build_mesh(self, with_axons:bool=True):
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
            self._define_problem()
        # MESH JOB
        self.mesh = mesh_from_nerve(self.nerve, length=self.l_fem, x_shift=self.x_bounds_fem[0], add_axons=with_axons,res_nerve=self.res_n, res_fasc=self.res_f, res_ax=self.res_a)
        self.mesh.n_core = self.get_nproc("mesh")
        self.mesh = mesh_from_electrode(elec=self.eit_elec, mesh=self.mesh, res=self.res_e)
        if self.gnd_elec is not None:
            self.mesh = mesh_from_electrode(elec=self.gnd_elec, mesh=self.mesh)
        self.mesh.set_verbosity(4)
        pass_info("... start meshing")
        self.mesh.compute_mesh()
        self.mesh.save(self.nerve_mesh_file)
        pass_info("... meshing done")
        # Store info
        self.mesh_info["fname"] = self.nerve_mesh_file
        self.mesh_info["n_proc"], self.mesh_info["n_entities"], self.mesh_info["n_nodes"], self.mesh_info["n_elements"] = self.mesh.get_info(verbose=True)
        # Update sim status
        self.mesh_built = True
        self.fem_initialized = False
        del self.mesh
        self.mesh = None
        __tf = perf_counter()
        self.mesh_timer +=  __tf - __ts

    def _init_fem(self):
        """
        initialization of fem 

        Parameters 
        ----------
        mesh_file: str | None, optional
            filename of the mesh, by default None
            
        """
        if not self.fem_initialized:
            self.sim = FEMSimulation(D=3, mesh_file=self.nerve_mesh_file, elem=("Lagrange", 2), ummesh=True)
            self.sim.set_solver_opt(**self.petsc_opt)
            self.__set_domains()
            # TO ADD :SETTING INTERNAL BOUNDARY CONDITION (for perineuriums)
            # improvement label: 
            # TODO fasc_peri
            self.__set_iboundaries()
            # SETTING BOUNDARY CONDITION
            # Ground (to the external ring of Outerbox)
            self.__set_boundaries()
            # print(check_sim_dom(self.sim, self.mesh))
            if self.mesh is not None:
                assert check_sim_dom(self.sim, self.mesh), "all domains are not set. Please check parameters of your simulation"
            self.sim.setup_sim(**self.electrodes)
            self.s_elec = []
            for i_elec in range(self.n_elec):
                e_dom = ENT_DOM_offset["Surface"] + ENT_DOM_offset["Electrode"]+2*i_elec
                #print(e_dom)
                self.s_elec += [self.sim.get_surface(e_dom)]
            self.fem_initialized = True
            #print(self.s_elec)

    def _clear_fem(self):
        if self.fem_initialized:
            del self.sim
            self.fem_initialized = False


    def __set_domains(self):
        """
        Internal use only: set the material properties of physical domains
        """
        # self.sim.add_domain(
        #     mesh_domain=ENT_DOM_offset["Outerbox"], mat_pty=self.outer_mat
        # )
        # Nerve domain
        self.sim.add_domain(
            mesh_domain=ENT_DOM_offset["Nerve"], mat_pty=self.sigma_epi
        )
        for i in range(self.nerve_results.n_fasc):
            self.sim.add_domain(
                mesh_domain=ENT_DOM_offset["Fascicle"] + (2 * i),
                mat_pty=self.sigma_endo,
            )
        # for _, (i, elec) in enumerate(self.electrodes.items()):
        #     if not elec["type"] == "LIFE":
        #         self.sim.add_domain(
        #             mesh_domain=ENT_DOM_offset["Electrode"] + (2 * i),
        #             mat_pty=self.electrodes_mat,
        #         )
        self._update_mat_axons(i_t=-1)

    # TODO fasc_peri: to complete
    def __set_iboundaries(self):
        """
        Internal use only: set internam boundaries
        """
        pass
        # for i in self.fascicles:
        #     thickness = self.Perineurium_thickness[i]
        #     f_dom = ENT_DOM_offset["Fascicle"] + (2 * i)
        #     self.sim.add_inboundary(
        #         mesh_domain=ENT_DOM_offset["Surface"] + f_dom,
        #         mat_pty=self.Perineurium_mat,
        #         thickness=thickness,
        #         in_domains=[f_dom],
        #     )

    def __set_boundaries(self):
        """
        Internal use only: set ground DBC and current injection NBC for electrodes
        """
        # GND DBS
        if self.use_gnd_elec:
            gnd_dom = get_mesh_domid("e", self.gnd_elec_id, is_surf=True)
            self.sim.add_boundary(mesh_domain=gnd_dom, btype="Dirichlet", value=0)
        else:
            gnd_dom = 1
            self.sim.add_boundary(mesh_domain=gnd_dom, btype="Dirichlet", value=0)
        for E in range(self.n_elec):
            E_label = "E"+str(E)
            e_dom = ENT_DOM_offset["Surface"] + ENT_DOM_offset["Electrode"]+2*E
            self.sim.add_boundary(mesh_domain=e_dom, btype="Neuman", variable=E_label)
            # print(E_label, "linked with ", e_dom)

    def __find_elec_subdomain(self, elec) -> int:
        """
        Internal use only:
        """
        if elec["type"] == "LIFE":
            y_e, z_e = elec["kwargs"]["y_c"], elec["kwargs"]["z_c"]
            for i in self.fascicles:
                fascicle = self.fascicles[i]
                d_f, y_f, z_f = fascicle["d"], fascicle["y_c"], fascicle["z_c"]
                if (y_e - y_f) ** 2 + (z_e - z_f) ** 2 < (d_f / 2) ** 2:
                    return 10 + 2 * i
        return 0


    def _update_mat_axons(self, i_t: float, i_t_1:float=-1) -> bool:
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
        for i_ax , (i_ax_pop, _ax_ppts) in enumerate(self._axons_pop_ppts.iterrows()):
            i_dom =ENT_DOM_offset["Axon"] + (2 * i_ax)
            ax_res = self.nerve_results[_ax_ppts["fkey"]][_ax_ppts["akey"]]
            # print(i_ax, len(ax_res["x_rec"]), ax_res["x_rec"], self.x_bounds_fem)
            if len(ax_res["x_rec"])>0:
                if self.current_freq == 0:
                    Y_mem_t = ax_res.get_membrane_conductivity(x=None, i_t=max(i_t, 0), mem_th=self.ax_mem_th, unit="S/m")
                else:
                    Y_mem_t = ax_res.get_membrane_complexe_admitance(x=None, i_t=max(i_t, 0), mem_th=self.ax_mem_th, unit="S/m")
            else:
                Y_mem_t = []
            # Myelinated
            if _ax_ppts["types"]:
                if ax_res["rec"]=="nodes":
                    # set myelin mat only the first time 
                    if i_t == -1:
                        self.sim.add_domain(
                            i_dom,
                            mat_pty=self.myelin_mat[i_ax],
                        )
                    for i_node, g_node in enumerate(Y_mem_t):
                        node_mat = layered_material(mat_in=self.sigma_axp, mat_lay=g_node, alpha_lay=self.alpha_in_c[i_ax])
                        id_node = get_node_physical_id(id_ax=i_dom, i_node=i_node)
                        # print(i_node, id_node)
                        self.sim.add_domain(mesh_domain=id_node,mat_pty=node_mat)
                else:
                    print("NotImplemented")
                    raise NotImplementedError
            # Unmyelinated
            else:
                Y_mem_t = np.vstack((
                    ax_res["x_rec"]-ax_res["x_rec"][0],
                    Y_mem_t
                ))
                ax_mat = layered_material(mat_in=self.sigma_axp, mat_lay=Y_mem_t, alpha_lay=self.alpha_in_c[i_ax])
                self.sim.add_domain(
                    mesh_domain=i_dom, mat_pty=ax_mat
                )
                # X_ = np.array([[x, 0, 0] for x in Y_mem_t[0,:]]).T
                # fig = plt.figure()
                # plt.plot(Y_mem_t[0,:], Y_mem_t[1,:])
            #     plt.plot(Y_mem_t[0,:], ax_mat.sigma(X_))
            #     print(max(ax_mat.sigma(X_)))
            #     if t == -1:
            #         plt.savefig(f"{int(1e4*perf_counter())}test.png")
            #     else:
            #         plt.savefig(f"{t}test.png")
            # # plt.show()
            # exit()
        return True

    def _compute_v_elec(self, sfile:None|str=None, i_t:int=0)->np.ndarray:
        __v = np.zeros(self.n_elec, dtype=ScalarType)
        # FEM simulation
        self.sim.setup_sim(**self.electrodes)
        res = self.sim.solve()
        # extract single ended measurements
        for i_rec in range(self.n_elec):
            id_ph = get_mesh_domid("e", i_rec, is_surf=True)
            __v[i_rec] = self.sim.get_domain_potential(id_ph ,surf=self.s_elec[i_rec])
        if sfile is not None:
            res.save(sfile, t=self.times[i_t])
            return res.V, res.vout, __v
        del res
        return __v