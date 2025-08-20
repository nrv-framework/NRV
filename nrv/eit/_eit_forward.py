from multiprocessing import Pool, Manager
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TimeElapsedColumn, track, MofNCompleteColumn
from typing import Iterable, Literal

from petsc4py.PETSc import ScalarType
from time import perf_counter
from abc import abstractmethod
from math import isnan
from pandas import DataFrame
import numpy as np
import os
import traceback

from .utils._misc import split_job_from_arrays, compute_myelin_ppt, sample_nerve_results, touch, sample_keys_mdt
from .results import eit_forward_results

from ..backend import NRV_class, json_dump, load_any, parameters, rise_warning
from ..nmod import nerve
from ..nmod.results import nerve_results
from ..fmod import load_material, recorder
from ..utils import convert, get_MRG_parameters
from ..utils.geom import CShape

static_env = np.dtype(ScalarType).kind != 'c'

class eit_forward(NRV_class):
    """
    Abstract base class for Electrical Impedance Tomography (EIT) forward simulation in neural contexts.

    This class provides the interface and core logic for simulating EIT problems on nerve models, including
    nerve simulation, mesh generation, FEM problem definition, and result management. It supports multi-core
    parallelization, custom electrode protocols, and backup/retry mechanisms for failed simulation steps.
    
    Attributes
    ----------
    label : str
        Simulation label.
        Nerve data source.
    parameters : dict
        Simulation parameters.
    res_dir : str
        Directory for saving results.
    nerve : nerve
        Loaded nerve object.
    is_nerve_res : bool
        Indicates if nerve data is a results object.
    l_nerve : float or None
        Nerve length.
    x_rec : float
        Electrode recording position (um).
    n_elec : int
    inj_offset : int
        Electrode offset for current injection.
    inj_protocol_type : str or list
        Injection protocol type or custom protocol.
    i_drive : float
        Current amplitude injected (uA).
    l_elec : float
        Electrode length (um).
    gnd_elec_id : int
        Ground electrode index.
    use_gnd_elec : bool
        Use ground electrode.
    freqs : np.ndarray
        Array of simulation frequencies (kHz).
    times : np.ndarray
        Array of simulation time points (ms).
    current_freq : float
        Current simulation frequency.
    dt_fem : float
        FEM time step.
    t_start_fem : float
        FEM simulation start time.
    t_stop_fem : float
        FEM simulation stop time.
    n_fem_step : int or None
        Number of FEM steps.
    aplha_fem_step : float
        Alpha parameter for FEM step.
    l_fem : float
        FEM domain length.
    use_pbar : bool
        Use progress bar in simulation.
    ax_mem_th : float
        Axon membrane thickness (um).
    sigma_epi : float
        Epineurium conductivity (S/m).
    sigma_endo : float
        Endoneurium conductivity (S/m).
    sigma_axp : float
        Axoplasm conductivity (S/m).
    myelin_mat : float
        Myelin material property.
    n_proc_global : int or None
        Global number of processes.
    n_proc_nerve : int or None
        Number of processes for nerve simulation.
    n_proc_mesh : int or None
        Number of processes for mesh generation.
    n_proc_fem : int or None
        Number of processes for FEM simulation.
    nerve_timer : float
        Timer for nerve simulation.
    mesh_timer : float
        Timer for mesh generation.
    fem_timer : float
        Timer for FEM simulation.
    use_backup : bool
        Enable backup saving during simulation.
    __backup_fname : str
        Backup file name.
    n_elt_r, f_elt_r, a_elt_r, e_elt_r : float
        Mesh resolution rates for nerve, fascicle, axon, and electrode.
    v_elecs : np.ndarray or None
        Simulated electrode voltages.
    __nerve_res_file : str or None
        Nerve results file path.
    __nerve_mesh_file : str or None
        Nerve mesh file path.
    __fem_res_file : str or None
        FEM results file path.
    nerve_results : nerve_results or None
        Results of nerve simulation.
    mesh : object or None
        FEM mesh object.
    mesh_info : dict
        Mesh information.
    fem_results : eit_forward_results
        Results of FEM simulation.
    mesh_built : bool
        Indicates if mesh is built.
    defined_pb : bool
        Indicates if FEM problem is defined.
    fem_initialized : bool
        Indicates if FEM is initialized.
    petsc_opt : dict
        PETSc solver options.

    Methods
    -------
    timers_dict : dict
        Returns timers for nerve, mesh, and FEM simulation.
    nerve_res_file : str
        Returns nerve results file path.
    nerve_mesh_file : str
        Returns nerve mesh file path.
    fem_res_file : str
        Returns FEM results file path.
    x_bounds_fem : tuple of float
        Returns x bounds of FEM domain.
    i_drive_A : float
        Returns injected current in Amperes.
    n_e : int
        Returns number of electrodes.
    n_t : int
        Returns number of time steps.
    n_f : int
        Returns number of frequency steps.
    n_p : int
        Returns number of injection patterns.
    v_shape : tuple of int
        Returns shape of voltage results array.
    inj_protocol : list of tuple
        Returns injection protocol.
    is_multi_patern : bool
        Returns True if multiple injection patterns.
    get_nproc(which="") : int
        Returns number of processes for a simulation step.
    simulate_nerve(...)
        Simulates neural context and returns nerve results.
    simulate_recording(...)
        Deprecated. Use simulate_nerve.
    _setup_problem()
        Defines FEM problem from nerve results.
    build_mesh(with_axons=True)
        Builds FEM mesh.
    _init_fem()
        Initializes FEM problem.
    _clear_fem()
        Clears FEM problem state.
    clear_fem_res()
        Clears FEM results and resets result file.
    _update_mat_axons(t)
        Updates axon material properties for time step.
    _compute_v_elec(sfile=None, i_t=0)
        Computes electrode voltages for a time step.
    __check_v_elec(v_elecs, task_id, i_t)
        Checks and handles failed FEM steps.
    run_fem(task_info)
        Runs FEM simulation for all time steps of a task.
    run_fem_1core(task_info)
        Runs FEM simulation on a single core.
    run_all_fem(task_info)
        Runs FEM simulation for all frequencies and patterns.
    simulate_eit(save=True, sim_list=None)
        Runs EIT simulation for all time steps and saves results.
    rerun_failed_steps(eit_results=None, save=True)
        Reruns failed FEM simulation steps.
    run_and_savefem(sfile, sim_list=[0], with_axons=True)
        Computes and saves electric field for selected time steps.

    Notes
    -----
    - This class is abstract and requires implementation of certain methods in subclasses.
    - Designed for extensibility to support custom electrode configurations and protocols.
    - Uses numpy array formalism for simulation data.
    - Supports multiprocessing for large-scale simulations.
    """
    @abstractmethod
    def __init__(self, nervedata, res_dname=None, label="eit_1",**parameters):
        """
        Initialize the EIT forward simulation class.

        Parameters
        ----------
        nervedata : str or nerve
            Path to nerve data file or nerve object.
        res_dname : str, optional
            Directory name for saving results, by default None.
        label : str, optional
            Label for the simulation, by default "eit_1".
        **parameters : dict
            Additional simulation parameters.
        """
        super().__init__()
        self.label = label
        self.nervedata = nervedata
        self.parameters = parameters
        if res_dname is None:
            self.res_dir = f"./{self.label}"
        else:
            self.res_dir = res_dname

        # sanity checks
        if isinstance(self.nervedata,str):
            if not os.path.isfile(self.nervedata):
                raise IOError(f"No such file for nerve description: '{self.nervedata}'")
        assert isinstance(self.parameters, dict)
        if not os.path.isdir(self.res_dir):
            print(f"No such directory {self.res_dir}. Creating it to save the results")
            os.mkdir(self.res_dir)

        # loading nerve files
        self.nerve:nerve = load_any(self.nervedata)
        self.is_nerve_res = "results" in self.nerve.nrv_type
        self.l_nerve:None|float = None
        ## default parameters

        # Electrodes context
        # (supposed to be CUFF_MP See if it can be generalised)
        # improvement label: 
        # TODO custom_eit_elec
        self.x_rec:float = 2000
        self.n_elec:int = 8
        self.inj_offset:int = 5
        self.inj_protocol_type = "single"
        #:float: current amplitude injected in uA. for impedance meau
        self.i_drive = 1 # uA
        self.l_elec = 30 # um
        self.gnd_elec_id = 0
        self.use_gnd_elec = False

        self.freqs:np.ndarray = np.ones(1) # kHz
        self.times:np.ndarray = np.zeros(1) # ms
        self.current_freq:float = 0

        # FEM simulation Parameters
        self.dt_fem:float = 0.02
        self.t_start_fem:float = 0
        self.t_stop_fem:float = -1
        self.n_fem_step:None|int = None
        self.aplha_fem_step:bool = 0.001
        self.l_fem:bool = 10 * self.l_elec
        self.use_pbar:bool = True

        # Material properties
        self.ax_mem_th:float = convert(10, unitin="nm", unitout="um")  # um 
        #! changed from m to um 04/02/25 as all other length are in um
        self.sigma_epi:float = convert(load_material("epineurium").sigma, unitin="S/m", unitout="S/m")  # S/m
        self.sigma_endo:float = convert(load_material("endoneurium_bhadra").sigma, unitin="S/m", unitout="S/m")  # S/m
        # self.sigma_endo = self.sigma_epi  # S/m
        self.sigma_axp:float = convert(1.83, unitin="S/m", unitout="S/m")  # S/m


        self.myelin_mat:float = compute_myelin_ppt(d=10)
        # print(self.myelin_mat)

        self.n_proc_global:None|int = None
        self.n_proc_nerve:None|int = None
        self.n_proc_mesh:None|int = None
        self.n_proc_fem:None|int = None

        self.nerve_timer:float = 0
        self.mesh_timer:float = 0
        self.fem_timer:float = 0

        #: bool: if true simulation resutls are save on the fligth 
        self.use_backup:bool = False
        self.__backup_fname: str = "./." + f"_BCKP_Store_{perf_counter()}".replace(".", "")

        # mesh resolution rate
        self.n_elt_r:float = 0.2
        self.f_elt_r:float = 0.1
        self.a_elt_r:float = 0.3
        self.e_elt_r:float = 0.2

        # overwriting parameters
        self.set_parameters(**parameters)

        # Simulations Outputs
        self.v_elecs:None|np.ndarray = None
        # fnames
        self.__nerve_res_file:None|str = None
        self.__nerve_mesh_file:None|str = None
        self.__fem_res_file:None|str = None

        # current results
        self.nerve_results:None|nerve_results = None
        self.mesh = None
        self.mesh_info:dict = {}
        self.fem_results:eit_forward_results = eit_forward_results()
        # EIT FEM simulation steps
        self.mesh_built:bool = False
        self.defined_pb:bool = False
        self.fem_initialized:bool = False


        if static_env:
            self.petsc_opt = {
                "ksp_type": "cg",
                "pc_type": "ilu",
                "ksp_rtol": 1e-16,
                "ksp_atol": 1e-18,
                "ksp_max_it": int(1e7),
            }
        else:
            self.petsc_opt = {
                "ksp_type": "cg",
                "pc_type": "lu",
                "ksp_rtol": 1e-16,
                "ksp_atol": 1e-18,
                "ksp_max_it": int(1e7),
            }

    @property
    def timers_dict(self)->dict:
        """
        Duration of all the simulations

        Returns
        -------
        dict
            Dictionary with timers for nerve, mesh, and FEM simulation.
        """
        return {
            "nerve_timer":self.nerve_timer,
            "mesh_timer":self.mesh_timer,
            "fem_timer":self.fem_timer,
        }

    @property
    def nerve_res_file(self)->str:
        """
        File where the nerve simulation results are saved

        Note
        ----
        The file name is construct from intance ``res_dir`` and ``label`` as: "{res_dir}/{label}_rec.json"

        Returns
        -------
        str
        """
        if self.__nerve_res_file is None:
            self.__nerve_res_file = f"{self.res_dir}/{self.label}_rec.json"
        return self.__nerve_res_file

    @property
    def nerve_mesh_file(self)->str:
        """
        File where the nerve mesh is saved

        Note
        ----
        The file name is construct from intance ``res_dir`` and ``label`` as: "{res_dir}/{label}_mesh.msh"

        Returns
        -------
        str
        """
        if self.__nerve_mesh_file is None:
            self.__nerve_mesh_file = f"{self.res_dir}/{self.label}_mesh.msh"
        return self.__nerve_mesh_file

    @property
    def fem_res_file(self)->str:
        """
        File where the fem results are saved

        Note
        ----
        The file name is construct from intance ``res_dir`` and ``label`` as: "{res_dir}/{label}_fem.json"

        Returns
        -------
        str
        """
        if self.__fem_res_file is None:
            self.__fem_res_file = f"{self.res_dir}/{self.label}_fem.json"
        return self.__fem_res_file

    @property
    def x_bounds_fem(self)->tuple[float]:
        """
        x bounds of the nerve section over which FEM is simulated

        Returns
        -------
        tuple[float]
        """
        pass

    @property
    def i_drive_A(self)->float:
        """
        Injected current in A

        Returns
        -------
        float
        """

        return convert(self.i_drive, unitin="uA", unitout="A")

    @property
    def dim(self)->Literal[None,2,3]:
        """
        Spatial dimension number of the problem.

        Returns
        -------
        int
        """
        return self.n_elec

    @property
    def n_e(self)->int:
        """
        Number of electrodes.

        Returns
        -------
        int
        """
        return self.n_elec

    @property
    def n_t(self)->int:
        """
        Number of time step in the EIT simulation.

        Returns
        -------
        int
        """
        return len(self.times)

    @property
    def n_f(self)->int:
        """
        Number of frequency step in the EIT simulation.

        Returns
        -------
        int
        """
        if static_env:
            return 1
        return len(self.freqs)
    

    @property
    def n_p(self)->int:
        """
        Number of injection paterns in the protocol.

        Returns
        -------
        int
        """
        return len(self.inj_protocol)
    
    def v_shape(self)->tuple[int]:
        """
        Get the shape of the voltage results array.

        Returns
        -------
        tuple of int
            Shape of the voltage results array.
        """
        _s = [self.n_p, self.n_f, self.n_t, self.n_e]
        return tuple([_n for _n in _s if _n > 1])


    @property
    def inj_protocol(self)->list[tuple]:
        """
        Injection protocole.

        Note
        ----
        Computed from ``self.inj_protocol_type`` if:
            - `"single"`: only one injection: `0` -> `self.injection_offset`.
            - `"simple"`: the paterns loop over all electrodes with a constant injection offset:
            `0` -> `self.injection_offset`; `1` -> `self.injection_offset+1`; ...; `self.n_elec` -> `self.injection_offset-1`
            - type is ``list``: custom injection protocole.

        Returns
        -------
        list[tuple]

        Raises
        ------
        ValueError
            For unrecognized injection protocole type
        """
        if isinstance(self.inj_protocol_type, list):
            __inj_prot = self.inj_protocol_type
        elif self.inj_protocol_type == "simple":
            __inj_prot = [(i_inj, (i_inj + self.inj_offset) % self.n_elec) for i_inj in range(self.n_elec)]
        elif self.inj_protocol_type == "single":
            __inj_prot = [(i_inj, (i_inj + self.inj_offset) % self.n_elec) for i_inj in range(1)]
        else:
            raise ValueError(f"Unrecognized injection protocole type: {self.inj_protocol_type}")
        return __inj_prot

    @property
    def is_multi_patern(self)->bool:
        """
        Check if the injection protocol contains more than one pattern.

        Returns
        -------
        bool
            True if multiple patterns, False otherwise.
        """
        return len(self.inj_protocol)>1

    def get_nproc(self, which:str="")->int:
        """
        return the number of process of a given simualtion step

        Note
        ----
        Simulation step are: nerve simulation, meshing and fem simulation

        Parameters
        ----------
        which : str, optional
            label of the step ("nerve", "mesh" or "fem") else or if corresponding `n_proc` attribute not set, `n_proc_global` is used, by default ""

        Returns
        -------
        int
            Number of processes.
        """
        n_proc = 1
        if "nerve" in which and self.n_proc_nerve is not None:
            n_proc = self.n_proc_nerve
        elif "mesh" in which and self.n_proc_mesh is not None:
            n_proc = self.n_proc_mesh
        elif "fem" in which and self.n_proc_fem is not None:
            n_proc = self.n_proc_fem
        elif self.n_proc_global is not None:
            n_proc = self.n_proc_global
        return n_proc


    def __check_geometry(self):
        """
        Check the geometry consistency for the simulation.

        Raises
        ------
        AssertionError
            If geometry parameters are inconsistent.
        """
        # assert self.dt_fem >= self.nerve.dt, "Nerve simulation dt should be smaller than dt_fem, please check you parameters before lanching simulation"
        assert self.dim == 2 or (self.l_fem >= self.l_elec), "elec out of FEM x-boundaries, please check you parameters before lanching simulation"
        assert self.x_rec + self.l_fem/2 <= self.nerve_results.L, "FEM x-boundaries out of the nerve, please check you parameters before lanching simulation"


    # TODO: rename method: simulate_nerve
    def simulate_nerve(
        self,
        t_start:float=1,
        duration:float=0.2,
        amplitude:float=5,
        expr: str | None = None,
        mask_labels: None | Iterable[str] | str = [],
        ax_list: None | list = None,
        fasc_list: None | list = None,
        sim_param:dict={},
        ax_param:dict={},
        save:bool=False
    ):
        """
        Simulate the neural context: fibres conductivity and extracellular context.

        Parameters
        ----------
        t_start     : float
            Time to start current clamp in ms, by default 1.
        duration    : float
            Duration of current clamp in ms, by default 0.2.
        amplitude   : float
            Current amplitude of the clamp in uA, by default 5.
        expr : str | None, optional
            To select a subpopulation of axon for the clamp, If not None mask is generated using :meth:`pandas.DataFrame.eval` of this expression, by default None
        mask_labels : None | Iterable[str] | str, optional
            To select a subpopulation of axon for the clamp, Label or list of labels already added to the axon populations population, by default []
        ax_list     : None | list
            To select a subpopulation of axon for the clamp, list of axons to insert the clamp on, if None, all axons are stimulated, by default None
        fasc_list     : None | list
            To select a subpopulation of axon for the clamp, list of fascicle to insert the clamp on, if None, all fascicle are stimulated, by default None
        sim_param : dict, optional
            Nerve parameters to change before simulation, by default {}.
        ax_param : dict, optional
            Axon parameters to change before simulation, by default {}.
        save : bool, optional
            If True, save the simulation result, by default True.

        Returns
        -------
        nerve_results
            Results of the nerve simulation.
        """
        __ts = perf_counter()
        if not self.is_nerve_res:
            parameters.set_ncores(n_nrv=self.get_nproc("nerve"), n_nmod=self.n_proc_nerve)
            if self.l_nerve is not None:
                self.nerve.define_length(self.l_nerve)

            self.nerve.set_parameters(**sim_param)
            self.nerve.set_axons_parameters(**ax_param)
            self.parameters.update(sim_param)
            self.parameters.update(ax_param)

            # TODO: idealy reset Iclamps... need new methods in axon
            # current clamp
            self.nerve.insert_I_Clamp(position=0, t_start=t_start, duration=duration, amplitude=amplitude,expr=expr, mask_labels=mask_labels, ax_list=ax_list,fasc_list=fasc_list)
            # Analitical recorder
            __testrec = recorder('endoneurium_ranck')
            for i_elec in range(self.n_elec):
                z_elec = self.nerve.D/2 * np.exp(2j*i_elec*np.pi/self.n_elec)
                __testrec.set_recording_point(self.x_rec, z_elec.real, z_elec.imag)
            self.nerve.attach_extracellular_recorder(__testrec)

            pp_kwg = {"keys_to_sample":"g_mem", "x_bounds": self.x_bounds_fem, "t_start_rec":self.t_start_fem, "t_stop_rec":self.t_stop_fem}
            if self.n_fem_step is None:
                pp_kwg["sample_dt"] = self.dt_fem
            else:
                pp_kwg["sample_dt"] = None
            # run simulation
            self.nerve_results = self.nerve.simulate(
                record_g_mem=True,
                return_parameters_only=False,
                save_results=False,
                postproc_script=sample_keys_mdt,
                postproc_kwargs=pp_kwg,
            )
            if self.n_fem_step is not None:
                d_iclamp = duration
                if self.x_rec >10000:
                    d_iclamp = 0
                self.nerve_results = sample_nerve_results(self.nerve_results, self.n_fem_step, alpha=self.aplha_fem_step, t_iclamp=t_start, d_iclamp=d_iclamp)
            self.nerve_results.save(save=save, fname=self.nerve_res_file, rec_context=True)
        else:
            self.nerve_results = self.nerve
        __tf = perf_counter()
        self.nerve_timer +=  __tf - __ts
        self.defined_pb = False
        return self.nerve_results


    def simulate_recording(
        self,
        t_start=1,
        duration=0.2,
        amplitude=5,
        sim_param={},
        ax_param={},
        save=True
    ):
        """
        Simulate the neural context: fibres conductivity and extracelullar context.

        Warning
        -------
        Deprecated. Use :meth:`simulate_nerve` instead.

        Parameters
        ----------
        t_start : int, optional
            Time to start current clamp in ms, by default 1.
        duration : float, optional
            Duration of current clamp in ms, by default 0.2.
        amplitude : int, optional
            Current amplitude of the clamp in uA, by default 5.
        sim_param : dict, optional
            Nerve parameters to change before simulation, by default {}.
        ax_param : dict, optional
            Axon parameters to change before simulation, by default {}.
        save : bool, optional
            If True, save the simulation result, by default True.

        Returns
        -------
        nerve_results
            Results of the nerve simulation.
        """
        rise_warning("Deprecated: simulate_recording is deprecated use simulate_nerve method instead")
        return self.simulate_nerve(
            t_start=t_start,
            duration=duration,
            amplitude=amplitude,
            sim_param=sim_param,
            ax_param=ax_param,
            save=save,
        )

    def _setup_problem(self):
        """
        Setup FEM problem parameters from nerve simulation results.
        """
        self.__check_geometry()

        # Recovering nerve pties from nrvsim
        self.times = self.nerve_results[self.nerve_results.fascicle_keys[0]].axon0.t
        self.fasc_geometries:dict[str, CShape] = self.nerve_results.fasc_geometries

        self._axons_pop_ppts:DataFrame = self.nerve_results.axons

        self.n_c = self._axons_pop_ppts.shape[0]
        i_mye = self._axons_pop_ppts["types"].to_numpy( dtype=bool)
        self.axnod_d = self._axons_pop_ppts["diameters"].copy(deep=True).to_numpy(dtype=float)
        self.axnod_d[i_mye]= get_MRG_parameters(self.axnod_d[i_mye])[2]
        self.myelin_mat = compute_myelin_ppt(self.axnod_d)
        self.alpha_in_c = (
            self.ax_mem_th / (self.axnod_d/2)
        )
        # Setting electrode properties
        self.w_elec = 0.5 * np.pi * self.nerve_results.D / self.n_elec
        self.electrodes = {}

        for E in range(self.n_elec):
            E_label = "E"+str(E)
            self.electrodes[E_label] = 0
        # TODO custom_eit_elec
        # change line bellow by an attach_electrode method(elec:FEM_electrode) method ?
        if self.inj_offset == 1:
            self.n_rec_per_inj = self.n_elec - 3
        else:
            self.n_rec_per_inj = self.n_elec - 4
        self.defined_pb = True

        # Setting mesh resolution
        self.res_n = self.nerve_results.D * self.n_elt_r
        self.res_f = [2 * np.min(g.radius) * self.f_elt_r for g in self.fasc_geometries.values()]
        self.res_a = self._axons_pop_ppts["diameters"].to_numpy(dtype=float) * self.a_elt_r
        self.res_e = self.w_elec * self.e_elt_r

    def _define_problem(self):
        rise_warning("Deprecated: _define_problem is deprecated use _setup_problem method instead")
        self._setup_problem()

    def build_mesh(self, with_axons:bool=True):
        """
        Create the mesh for FEM simulation.

        Parameters
        ----------
        with_axons : bool, optional
            Include axons in the mesh, by default True.
        """
        if not self.defined_pb:
            self._setup_problem()


    def _init_fem(self):
        """
        initialization of FEM problem
        """
        pass

    def clear(self):
        """
        Clear all simulations outputs.
        """
        pass

    def _clear_fem(self):
        """
        Clear FEM problem state.
        """
        pass

    def clear_fem_res(self):
        """
        Clear FEM results and reset result file.
        """
        self.__fem_res_file = None
        self.fem_results = eit_forward_results()


    def _update_mat_axons(self, t: float) -> bool:
        """
        Update axon material properties between time steps.

        Parameters
        ----------
        t : float
            Time step.

        Returns
        -------
        bool
            True if update successful.
        """
        return True

    def _compute_v_elec(self, sfile:None|str=None, i_t:int=0)->np.ndarray|None:
        """
        Compute electrode voltages for a given time step.

        Parameters
        ----------
        sfile : str or None, optional
            File to save results, by default None.
        i_t : int, optional
            Time step index, by default 0.

        Returns
        -------
        np.ndarray or None
            Computed electrode voltages.
        """
        pass

    def __check_v_elec(self, v_elecs:np.ndarray, task_id:int, i_t:int)->np.ndarray:
        """
        Internal use only: check if an FEM step did not fail (i.e. corresponding v_elec are not NaN). In such cases set the voltage value to 0 and reset the FEM. Additionally, if backup saving is activated, save the results in backup file. 

        Parameters
        ----------
        v_elecs : np.ndarray(self.n_elec,)
            Computed voltage simulated of one simulation step
        task_id : int
            id of the current task (process)
        i_t : int
            time step of the simulation

        Returns
        -------
        np.ndarray(self.n_elec,)
        """

        if isnan(v_elecs[0]):
            v_elecs = np.zeros(self.n_elec)
            self._clear_fem()
            self._init_fem()
        if self.use_backup and os.path.isfile(self.__backup_fname):
            line = f"{task_id}\t{self.current_freq}\t{i_t}"
            for __v in v_elecs:
                line += f"\t{__v}"
            line += f"\t{int(v_elecs[0]!=0)}\n"
            file_object = open(self.__backup_fname, "a")
            file_object.write(line)
            file_object.close()
        return v_elecs

    def run_fem(self, task_info:list)->np.ndarray:
        """
        Run the FEM simulation for all time step of a given task (process). Depending of the problem definition, the simulation is run for all injection partens and only for the current frequency.

        Note
        ----
        By contrast with `self.run_fem` is that 

        Parameters
        ----------
        task_info : list
            list of four elements containing:
             - the task_name: `str`
             - the task_id: `int`
             - the total: `int`
             - the progress_dict: `dict`

        Returns
        -------
        np.ndarray(self.n_p, self.n_t, self.n_e) |
        np.ndarray(self.n_t, self.n_e)
        """
        task_name, task_id, total, progress_dict = task_info
        parameters.set_nrv_verbosity(2)
        _sim_list = self.sim_list[task_id]
        # print(task_id, _sim_list)

        v_elecs = np.zeros((self.n_p, self.n_t, self.n_e), dtype=ScalarType)
        # if task_id!=7 and task_id!=6:
        #     return v_elecs
        v_str = ""
        if self.use_pbar:
            progress = Progress(
                "[progress.description]{task.description}",
                MofNCompleteColumn(),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
                TimeElapsedColumn(),
            )
            task = progress.add_task(task_name, total=total)
            progress.advance(task, 0)
            progress_dict[task_id] = progress.get_renderable()
        if len(_sim_list)>0 and not self.fem_initialized:
            try:
                self._init_fem()
            except TimeoutError:
                print()
                print()
                print("TimeoutError")
                self._clear_fem()
                self._init_fem()
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                rise_warning(
                    f"Simulation induced an error at initialisation"
                    + traceback.format_exc()
                )
        for i_, i_t in enumerate(_sim_list):
            # update and solve
            if i_ == 0:
                i_t_1 = -1
            else:
                i_t_1 = _sim_list[i_-1]
            self._update_mat_axons(i_t, i_t_1)
            for i_p, inj_pat in enumerate(self.inj_protocol):
                # Set current injection
                for i_elec, e_str in enumerate(self.electrodes):
                    if "E"+str(inj_pat[0]) == e_str:
                        self.electrodes[e_str] = self.i_drive_A / self.s_elec[i_elec]
                    elif "E"+str(inj_pat[1]) == e_str:
                        self.electrodes[e_str] = -self.i_drive_A / self.s_elec[i_elec]
                    else:
                        self.electrodes[e_str] = 0
                try:
                    v_elecs[i_p, i_t, :] = self._compute_v_elec()
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except:
                    rise_warning(
                        f"Simulation induced an error computing for {self.current_freq}kHz at {self.times[i_t]}ms\n"
                        + traceback.format_exc()
                    )
                v_elecs[i_p, i_t, :] = self.__check_v_elec(v_elecs[i_p, i_t, :], task_id, i_t)
                # Update the shared progress state
                if self.use_pbar:
                    progress.update(task, advance=1 ,value=v_str)
                    progress_dict[task_id] = progress.get_renderable()
        return v_elecs

    def run_fem_1core(self, task_info):
        """
        
        """
        task_name, task_id, total, progress_dict = task_info
        parameters.set_nrv_verbosity(2)
        _sim_list = self.sim_list[task_id]
        v_elecs = np.zeros((self.n_p, self.n_t, self.n_e), dtype=ScalarType)
        if not self.fem_initialized:
            self._init_fem()
        for i_ in track(range(len(_sim_list))):
            # update and solve
            i_t = _sim_list[i_]
            # update and solve
            if i_ == 0:
                i_t_1 = -1
            else:
                i_t_1 = _sim_list[i_-1]
            self._update_mat_axons(i_t, i_t_1)
            for i_p, inj_pat in enumerate(self.inj_protocol):
                # Set current injection
                for i_elec, e_str in enumerate(self.electrodes):
                    if "E"+str(inj_pat[0]) == e_str:
                        self.electrodes[e_str] = self.i_drive_A / self.s_elec[i_elec]
                    elif "E"+str(inj_pat[1]) == e_str:
                        self.electrodes[e_str] = -self.i_drive_A / self.s_elec[i_elec]
                    else:
                        self.electrodes[e_str] = 0
                try:
                    v_elecs[i_p, i_t, :] = self._compute_v_elec()
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except:
                    rise_warning(
                        f"Simulation induced an error computing{i_t, self.current_freq} \n"
                        + traceback.format_exc()
                    )
                v_elecs[i_p, i_t, :] = self.__check_v_elec(v_elecs[i_p, i_t, :], task_id, i_t)
        return v_elecs
    
    def run_all_fem(self, task_info:list)->np.ndarray:
        """
        Run the FEM simulation for all time step of a given task (process). Depending of the problem definition, the simulation if run for all injection frequencies and over the whole frequency.

        Note
        ----
        By contrast with `self.run_fem` is that 

        Parameters
        ----------
        task_info : list
            list of four elements containing:
             - the task_name: `str`
             - the task_id: `int`
             - the total: `int`
             - the progress_dict: `dict`

        Returns
        -------
        np.ndarray(self.n_p,self.n_f, self.n_t, self.n_e) |
        np.ndarray(self.n_f, self.n_t, self.n_e) |
        np.ndarray(self.n_t, self.n_e)
        """
        if static_env:
            self.current_freq = 0
            if self.get_nproc("fem") == 1:
                v_elecs = self.run_fem_1core(task_info=task_info)
            else:
                v_elecs = self.run_fem(task_info=task_info)
        else:
            v_elecs = np.zeros((self.n_p,self.n_f, self.n_t, self.n_e), dtype=ScalarType)
            task_info[0] = task_info[0]+f"freq 0/{self.n_f}"
            for i_f in range(self.n_f):
                self.current_freq = self.freqs[i_f]
                self.myelin_mat = compute_myelin_ppt(self.axnod_d, f=self.current_freq)
                task_info[0] = task_info[0].replace(f"{i_f}/", f"{i_f+1}/")
                if self.get_nproc("fem") == 1:
                    v_elecs[:, i_f, :, :] = self.run_fem_1core(task_info)
                else:
                    v_elecs[:, i_f, :, :] = self.run_fem(task_info)
        self._clear_fem()
        return v_elecs


    def simulate_eit(self, save:bool=True, sim_list:np.ndarray|None=None)->eit_forward_results:
        """
        Run the eit problem for all time steps

        Parameters
        ----------
        save : bool, optional
            if true output dict saved in a json, by default True
        res_file : str | None, optional
            filename of the saving, by default None

        Returns
        -------
        eit_forward_results
            EIT simulation results.
        """
        if not self.defined_pb:
            self._setup_problem()
        __ts = perf_counter()
        if self.use_backup:
            touch(self.__backup_fname)
        n_proc = self.get_nproc("fem")
        if sim_list is None:
            self.sim_list = split_job_from_arrays(self.n_t, n_split=n_proc, stype="default")
        else:
            if len(sim_list) < n_proc:
                self.n_proc_fem = len(sim_list)
            n_proc = self.get_nproc("fem")
            self.sim_list = np.array_split(sim_list, n_proc, axis=0)

        # Set each process task property
        tasks = [{"task_name": f"process {i+1} -- {n_proc} :", "total": self.n_p*len(self.sim_list[i]), "task_id": i} for i in range(n_proc)]
        manager = Manager()
        progress_dict = manager.dict()
        task_info_list = [
            [task["task_name"], task["task_id"], task["total"], progress_dict]
            for task in tasks
        ]
        if n_proc == 1:
            print("single core")
            self.v_elecs = self.run_all_fem(task_info_list[0])
        else:
            with Pool(n_proc) as pool:
                with Live(refresh_per_second=10) as live:
                    async_results = [pool.apply_async(self.run_all_fem, args=(task_info,)) for task_info in task_info_list]
                    while any(not result.ready() for result in async_results):
                        table = Table.grid()
                        for task_id, progress in progress_dict.items():
                            table.add_row(progress)
                        live.update(table)
                    for result in async_results:
                        result.wait()
                    # results = list(pool.imap(self.run_fem, np.arange(n_proc)))
                    arrays = [result.get() for result in async_results]
                pool.close()
                pool.join()
            self.v_elecs = np.sum(arrays, axis=0).squeeze()
        #print(self.v_elecs, type(self.v_elecs))
        self.fem_results["res_dir"] = self.res_dir
        self.fem_results["label"] = self.label
        self.fem_results["parameters"] = self.parameters

        if isinstance(self.nervedata,str):
            self.fem_results["nervefile"] = self.nervedata
        
        
        self.fem_results["mesh_info"] = self.mesh_info
        self.fem_results["t"] = self.times
        self.fem_results["p"] = self.inj_protocol
        self.fem_results["i_off"] = self.inj_offset

        if static_env:
            self.fem_results["f"] = 0
        elif len(self.freqs) == 1:
            self.fem_results["f"] = self.freqs[0]
        else:
            self.fem_results["f"] = self.freqs

        # compute dv
        self.fem_results["v_eit"] = abs(self.v_elecs)
        self.fem_results["v_eit_phase"] = np.angle(self.v_elecs)
        __tf = perf_counter()
        self.fem_timer +=  __tf - __ts

        self.fem_results["computation_time"] = self.timers_dict
        self.fem_results.incorporate_nerve_res(self.nerve_results)

        if save:
            # Saving
            json_dump(self.fem_results, self.fem_res_file)
        if self.use_backup and os.path.isfile(self.__backup_fname):
            os.remove(self.__backup_fname)
        return self.fem_results


    # ----------------------------------------- #
    # Complementary and debug simulation method #
    # ----------------------------------------- #


    def rerun_failed_steps(self, eit_results:eit_forward_results|str|None=None, save:bool=True)->eit_forward_results:
        """
        Rerun failed FEM simulation steps.

        Parameters
        ----------
        eit_results : eit_forward_results, str, or None, optional
            EIT results object or file path, by default None.
        save : bool, optional
            If True, save updated results, by default True.

        Returns
        -------
        eit_forward_results
            Updated EIT simulation results.
        """
        if eit_results is None:
            eit_results = self.fem_res_file
        if isinstance(eit_results, str):
            eit_results = eit_forward_results(data=eit_results)
        if "res_dir" in eit_results and "label" in eit_results:
            assert eit_results["res_dir"] == self.res_dir and eit_results["label"] == self.label

        if not eit_results.has_failed_test:
            print("All good, nothing to retry")
            self.fem_results = eit_results
        else:
            sim_list = eit_results.fail_results
            self.freqs = eit_results["f"]
            self.times = eit_results["t"]
            print(f"...following simulation steps will be restarted\n{sim_list}")
            self.simulate_eit(save=False, sim_list=sim_list)
            #updating results
            print("...updating results")

            eit_results["computation_time"]["fem_timer"] += self.fem_results["computation_time"]["fem_timer"]

            eit_results.update_failed_results(
                _v_eit=self.fem_results["v_eit"],
                _v_eit_phase=self.fem_results["v_eit_phase"]
            )
            self.fem_results = eit_results

        if save:
            # Saving
            json_dump(self.fem_results, self.fem_res_file)
        return self.fem_results

    def run_and_savefem(self, sfile:str, sim_list:list[int]=[0], with_axons:bool=True)->np.ndarray:
        """
        Compute only a few time step of the EIT simulation and save the computed electric field in the whole domain

        Parameters
        ----------
        sfile : str
            saving file name
        sim_list : list[int], optional
            List of time step to compute, by default [0]
        with_axons : bool, optional
            include axon in the EIT simulation, by default True

        Returns
        -------
        np.ndarray
        """
        parameters.set_nrv_verbosity(2)
        if not self.defined_pb:
            self._setup_problem()
        self.build_mesh(with_axons=with_axons)

        if len(sim_list)>0 and not self.fem_initialized:
            self._init_fem()
        for i_, i_t in enumerate(sim_list):
            # update and solve
            if i_ == 0:
                i_t_1 = -1
            else:
                i_t_1 = sim_list[i_-1]
            self._update_mat_axons(i_t, i_t_1)
            for inj_pat in self.inj_protocol:
                # Set current injection
                for i_elec, e_str in enumerate(self.electrodes):
                    if "E"+str(inj_pat[0]) == e_str:
                        self.electrodes[e_str] = self.i_drive_A / self.s_elec[i_elec]
                    elif "E"+str(inj_pat[1]) == e_str:
                        self.electrodes[e_str] = -self.i_drive_A / self.s_elec[i_elec]
                    else:
                        self.electrodes[e_str] = 0
                v = self._compute_v_elec(sfile=sfile, i_t=i_t)
        self._clear_fem()
        return v
