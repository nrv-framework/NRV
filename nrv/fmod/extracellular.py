"""
NRV-extracellular contexts
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler

import numpy as np

from ..backend.file_handler import json_load
from ..backend.log_interface import rise_error, rise_warning
from ..backend.MCore import MCH
from ..backend.NRV_Class import NRV_class
from .electrodes import is_analytical_electrode, is_FEM_electrode, check_electrodes_overlap
from .FEM.COMSOL_model import COMSOL_model, COMSOL_Status
from .FEM.FENICS_model import FENICS_model
from .materials import load_material, is_mat
from .stimulus import get_equal_timing_copies

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()


def is_extra_stim(test_stim):
    """
    check if an object is a stimulation, return True if yes, else False
    """
    Flag = (
        isinstance(test_stim, stimulation)
        or isinstance(test_stim, FEM_stimulation)
        or isinstance(test_stim, extracellular_context)
    )
    return Flag


def is_analytical_extra_stim(test_stim):
    """
    check if an object is a stimulation (analytical only), return True if yes, else False
    """
    return isinstance(test_stim, stimulation)


def is_FEM_extra_stim(test_stim):
    """
    check if an object is a FEM stimulation, return True if yes, else False
    """
    return isinstance(test_stim, FEM_stimulation)


def load_any_extracel_context(data):
    """
    return any kind of extracellular context properties from a dictionary or a json file

    Parameters
    ----------
    data    : str or dict
        json file path or dictionary containing extracel_context information
    """
    if type(data) == str:
        context_dic = json_load(data)
    else:
        context_dic = data

    if context_dic["type"] is None:
        extracel = extracellular_context()
    elif context_dic["type"] == "stimulation":
        extracel = stimulation()
    elif context_dic["type"] == "FEM_stim":
        extracel = FEM_stimulation(data["model_fname"], comsol=False)
    else:
        rise_error("extra cellular context type not recognizede")

    extracel.load(context_dic)
    return extracel


class extracellular_context(NRV_class):
    """
    extracellular_context is a class to handle the computation of the extracellular voltage field induced by the electrical stimulation.
    This class should not be used directly by user, but user friendly classes (for Analitycal or FEM based computations) inherits from extracellular_context.
    """

    def __init__(self):
        """
        Instrantiation an extracellular_context object, empty shell to store electrodes and stimuli
        """
        super().__init__()
        self.type = "extracellular_context"
        # empty list to store electrodes and corresponding stimuli
        self.electrodes = []
        self.stimuli = []
        # list for synchronised stimuli
        self.synchronised = False
        self.synchronised_stimuli = []
        self.global_time_serie = []
        self.type = None

    def save_extracel_context(self, save=False, fname="extracel_context.json"):
        rise_warning("save_extracel_context is a deprecated method use save")
        self.save(save=save, fname=fname)

    def load_extracel_context(self, data="extracel_context.json"):
        rise_warning("load_extracel_context is a deprecated method use load")
        self.load(data=data)

    ##
    def is_empty(self):
        """
        check if a stimulation object is empty (No electrodes and stimuli, no external field can be computed).
        Returns True if empty, else False.

        Returns
        -------
        bool
            True if a simulation is empty, else False
        """
        return self.electrodes == []

    def translate(self, x=None, y=None, z=None):
        """
        Move extracellular context electrodes by group translation

        Parameters
        ----------
        x   : float
            x axis value for the translation in um
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        """
        for elec in self.electrodes:
            elec.translate(x=x, y=y, z=z)

    def add_electrode(self, electrode, stimulus):
        """
        Add a stimulation electrode and its stimulus to the stimulation.

        Parameters
        ----------
        electrode   : electrode object
            see Electrode.py or electrode object help for further details
        stimulus    : stimulus object
            see Stimulus.py or stimulus object help for further details
        """
        if self.electrodes == []:
            self.electrodes.append(electrode)
            self.stimuli.append(stimulus)
        else:
            electrode.set_ID_number(self.electrodes[-1].get_ID_number() + 1)
            self.electrodes.append(electrode)
            self.stimuli.append(stimulus)
        self.synchronised = False

    def reset_stimuli(self):
        self.stimuli = []
        self.synchronised_stimuli = []
        self.synchronised = False
        self.global_time_serie = []

    def reset_electrodes(self):
        self.electrodes = []
        self.reset_stimuli()

    def synchronise_stimuli(self, snap_time=False, dt_min=0.001):
        """
        Synchronise all stimuli before simulation. Copies of the stimuli are created with the global number of samples
        from merging all stimuli time samples. Original stimuli are not affected.
        """
        if not (self.synchronised or self.is_empty()):
            if len(self.electrodes) == 1:
                self.synchronised_stimuli.append(self.stimuli[0])
            elif len(self.electrodes) == 2:
                stim_a, stim_b = get_equal_timing_copies(
                    self.stimuli[0], self.stimuli[1]
                )
                self.synchronised_stimuli.append(stim_a)
                self.synchronised_stimuli.append(stim_b)
            else:
                # init : put first two and synchronize them
                stim_a, stim_b = get_equal_timing_copies(
                    self.stimuli[0], self.stimuli[1]
                )
                self.synchronised_stimuli.append(stim_a)
                self.synchronised_stimuli.append(stim_b)
                # remaining stimuli to handle
                unsynchronized_stim = self.stimuli[2:]
                for stimulus in unsynchronized_stim:
                    # synchronise all the previously synchronised with the pending one
                    for s in self.synchronised_stimuli:
                        s.insert_samples(stimulus.t)
                    # synchronise the pending one with the already synchronised and add it to synchronised stim
                    stimulus.insert_samples(self.synchronised_stimuli[0].t)
                    self.synchronised_stimuli.append(stimulus)
            # if snap_time is true synchronised_stimuli overlaping points are removed
            if snap_time:
                for stim in self.synchronised_stimuli:
                    stim.snap_time(dt_min)
            # anyway, take the first stimulus time serie as the global one
            self.global_time_serie = self.synchronised_stimuli[0].t
        self.synchronised = True

    def compute_vext(self, time_index):
        """
        Compute the external potential on a array of coordinate for a time sample of all synchronised stimuli with all
        electrodes.

        Parameters
        ----------
        time_index  : int
            time index of the synchronised stimuli to compute the field at.
            NB: as a safeguard, if the time_index is out of the sample list a null potential is returned

        Returns
        -------
        Vext : np.array
            external potential for the specified positions, in mV (numpy array)
        """
        Vext = np.zeros(len(self.electrodes[0].footprint))
        if not self.synchronised:
            self.synchronise_stimuli()
        if time_index < len(
            self.global_time_serie
        ):  # requested time index is in stimulus range (safeguard)
            for k in range(len(self.electrodes)):
                Istim = self.synchronised_stimuli[k].s[time_index]
                vext_elec = self.electrodes[k].compute_field(Istim)
                Vext = Vext + vext_elec
        return Vext

    def set_electrodes_footprints(self, footprints):
        """
        set the footprints for all electrodes from existing array

        Parameters
        ----------
        footprints  : list of array like
            list footprint for each electode of the extracellular context
        """
        i = 0
        if len(footprints) == len(self.electrodes):
            for i, electrode in enumerate(self.electrodes):
                if i in footprints:
                    electrode.set_footprint(footprints[i])
                else:
                    electrode.set_footprint(footprints[str(i)])
        else:
            rise_error("Footprint number different than electrode number")

    def clear_electrodes_footprints(self):
        """
        clear the footprints for all electrodes from existing array
        """
        for electrode in self.electrodes:
            electrode.clear_footprint()

    def change_stimulus_from_elecrode(self, ID_elec, stimulus):
        """
        Change the stimulus of the ID_elec electrods

        Parameters:
        ----------
            ID_elec  : int
                ID of the electrode which should be changed
            stimulus  : stimulus
                New stimulus to set
        """
        if ID_elec < len(self.stimuli):
            self.stimuli[ID_elec] = stimulus
            self.synchronised_stimuli = []
            self.synchronised = False
        else:
            rise_warning(
                "Only",
                len(self.stimuli),
                "electrode in extracellular_context:",
                ID_elec,
                "is not too big",
            )


class stimulation(extracellular_context):
    """
    Stimulation object are designed to connect all other objects requierd to analyticaly compute the external potential voltage for axons :
    - the material surrounding the axon (only one)
    - a list of electrode(s)
    - a list of corresponding current stimuli
    This class inherits from extracellular_context.
    """

    def __init__(self, material="endoneurium_ranck"):
        """
        Implement a stimulation object.

        Parameters
        ----------
        material    : str or material object
            extracellular medium see Material.py or material object help for further details
        """
        super().__init__()
        if is_mat(material):
            self.material = material
        else:
            self.material = load_material(material)
        self.type = "stimulation"

    def add_electrode(self, electrode, stimulus):
        """
        Add a stimulation electrode and its stimulus to the stimulation, only if the electrode is analytically described.

        Parameters
        ----------
        electrode   : electrode object
            see Electrode.py or electrode object help for further details
        stimulus    : stimulus object
            see Stimulus.py or stimulus object help for further details
        """
        if is_analytical_electrode(electrode):
            if self.electrodes == []:
                self.electrodes.append(electrode)
                self.stimuli.append(stimulus)
            else:
                electrode.set_ID_number(self.electrodes[-1].get_ID_number() + 1)
                self.electrodes.append(electrode)
                self.stimuli.append(stimulus)
            self.synchronised = False

    def compute_electrodes_footprints(self, x, y, z, ID=0):
        """
        Compute the footprints for all electrodes

        Parameters
        ----------
        x           : np.array
            x position at which to compute the field, in um
        y           : float
            y position at which to compute the field, in um
        z           : float
            z position at which to compute the field, in um
        ID          : int
            axon ID, unused here, added to fit FEM_stimulation declaration of same method
        """
        for electrode in self.electrodes:
            electrode.compute_footprint(
                np.asarray(x), np.asarray(y), np.asarray(z), self.material
            )


class FEM_stimulation(extracellular_context):
    """
    FEM_based_simulation object are designed to connect all other objects requierd to compute the external potential voltage for axons using FEM :
    - the materials for the FEM stimulation : endoneurium, perineurium, epineurium and external material
    - a list of electrode(s)
    - a list of corresponding current stimuli
    """

    def __init__(
        self,
        model_fname=None,
        endo_mat="endoneurium_ranck",
        peri_mat="perineurium",
        epi_mat="epineurium",
        ext_mat="saline",
        comsol=True,
        Ncore=None,
    ):
        """
        Implement a FEM_based_stimulation object.

        Parameters
        ----------
        simuluation_fname   : str
            name of the simluation file to compute the field
        endo_mat            : material object
            specification of the endoneurium material, see Material.py or material object help for further details
        peri_mat            : material object
            specification of the perineurium material, see Material.py or material object help for further details
        epi_mat             : material object
            specification of the epineurium material, see Material.py or material object help for further details
        ext_mat             : material object
            specification of the external material (everything but the nerve), see Material.py or material object help for further details
        """
        super().__init__()
        self.electrodes_label = []
        self.model_fname = model_fname
        self.setup = False
        self.is_run = False
        self.Ncore = Ncore
        ## get material properties and add to model

        if is_mat(endo_mat):
            self.endoneurium = endo_mat
            self.endo_mat_file = None
        else:
            self.endoneurium = load_material(endo_mat)
            self.endo_mat_file = endo_mat
        if is_mat(peri_mat):
            self.perineurium = peri_mat
            self.peri_mat_file = None
        else:
            self.perineurium = load_material(peri_mat)
            self.peri_mat_file = peri_mat
        if is_mat(epi_mat):
            self.epineurium = epi_mat
            self.epi_mat_file = None
        else:
            self.epineurium = load_material(epi_mat)
            self.epi_mat_file = epi_mat
        if is_mat(ext_mat):
            self.external_material = ext_mat
            self.ext_mat_file = None
        else:
            self.external_material = load_material(ext_mat)
            self.ext_mat_file = ext_mat

        self.type = "FEM_stim"

        self.comsol = comsol and not (model_fname is None)
        self.fenics = not self.comsol
        ## load model
        if self.comsol:
            if MCH.do_master_only_work():
                self.model = COMSOL_model(self.model_fname, Ncore=self.Ncore)
            else:
                # check that COMSOL is not turned OFF in order to continue
                if not COMSOL_Status:
                    rise_warning(
                        "Slave process abort as axon is supposed to used a COMSOL FEM and COMSOL turned off",
                        abort=True,
                    )
        else:
            self.model = FENICS_model(Ncore=self.Ncore)

    def __del__(self):
        if (
            MCH.do_master_only_work() and COMSOL_Status and self.comsol
        ):  # added for safe del in case of COMSOL status turned OFF
            self.model.close()
            del self.model

    def set_Ncore(self, N):
        """
        Set the number of cores to use for the FEM

        Parameters
        ----------
        N       : int
            Number of cores to set
        """
        self.model.set_Ncore(N=N)

    ## Save and Load mehtods

    def save(self, save=False, fname="extracel_context.json", blacklist=[], **kwargs):
        """
        Return extracellular context as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default "extracel_context.json"

        Returns
        -------
        context_dic : dict
            dictionary containing all information
        """
        if self.comsol:
            blacklist += ["model"]

        return super().save(save=save, fname=fname, blacklist=blacklist, **kwargs)

    def load(self, data, C_model=False, **kwargs):
        """
        Load all extracellular context properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing extracel_context information
        """
        super().load(data, **kwargs)

        if C_model:
            if MCH.do_master_only_work():
                self.model = COMSOL_model(self.model_fname)
            else:
                # check that COMSOL is not turned OFF in order to continue
                if not COMSOL_Status:
                    rise_warning(
                        "Slave process abort as axon is supposed to used a COMSOL FEM and COMSOL turned off",
                        abort=True,
                    )

    def reshape_outerBox(self, Outer_D, res="default"):
        """
        Reshape the size of the FEM simulation outer box

        Parameters
        ----------
        outer_D : float
            FEM simulation outer box diameter, in mm, WARNING, this is the only parameter in mm !
        res         : float or "default"
            mesh resolution for fenics_model cf NerveMshCreator, use with caution, by default "default"
        """
        if MCH.do_master_only_work():
            if self.comsol:
                self.model.set_parameter("Outer_D", str(Outer_D) + "[mm]")
            else:
                self.model.reshape_outerBox(Outer_D, res=res)

    def reshape_nerve(self, Nerve_D, Length, y_c=0, z_c=0, res="default"):
        """
        Reshape the nerve of the FEM simulation

        Parameters
        ----------
        Nerve_D                 : float
            Nerve diameter, in um
        Length                  : float
            Nerve length, in um
        y_c                     : float
            Nerve center y-coordinate in um, 0 by default
        z_c                     : float
            Nerve z-coordinate center in um, 0 by default
        res         : float or "default"
            mesh resolution for fenics_model cf NerveMshCreator, use with caution, by default "default"
        """
        if MCH.do_master_only_work():
            if self.comsol:
                self.model.set_parameter("Nerve_D", str(Nerve_D) + "[um]")
                self.model.set_parameter("Length", str(Length) + "[um]")
                self.model.set_parameter("Nerve_y_c", str(y_c) + "[um]")
                self.model.set_parameter("Nerve_z_c", str(z_c) + "[um]")
            else:
                self.model.reshape_nerve(
                    Nerve_D=Nerve_D, Length=Length, y_c=y_c, z_c=z_c, res=res
                )

    def reshape_fascicle(
        self, Fascicle_D, y_c=0, z_c=0, ID=None, Perineurium_thickness=5, res="default"
    ):
        """
        Reshape a fascicle of the FEM simulation

        Parameters
        ----------
        Fascicle_D  : float
            Fascicle diameter, in um
        y_c         : float
            Fascicle center y-coodinate in um, 0 by default
        z_c         : float
            Fascicle center y-coodinate in um, 0 by default
        Perineurium_thickness   :float
            Thickness of the Perineurium sheet surounding the fascicles in um, 5 by default
        ID          : int
            If the simulation contains more than one fascicles, ID number of the fascicle to reshape as in COMSOL
        res         : float or "default"
            mesh resolution for fenics_model cf NerveMshCreator, use with caution, by default "default"
        """
        if MCH.do_master_only_work():
            if self.comsol:
                if ID is None:
                    self.model.set_parameter("Fascicle_D", str(Fascicle_D) + "[um]")
                    self.model.set_parameter("Fascicle_y_c", str(y_c) + "[um]")
                    self.model.set_parameter("Fascicle_z_c", str(z_c) + "[um]")
                else:
                    self.model.set_parameter(
                        "Fascicle_" + str(ID) + "_D", str(Fascicle_D) + "[um]"
                    )
                    self.model.set_parameter(
                        "Fascicle_" + str(ID) + "_y_c", str(y_c) + "[um]"
                    )
                    self.model.set_parameter(
                        "Fascicle_" + str(ID) + "_z_c", str(z_c) + "[um]"
                    )
                self.model.set_parameter(
                    "Perineurium_thickness", str(Perineurium_thickness) + "[um]"
                )
            else:
                self.model.reshape_fascicle(
                    Fascicle_D=Fascicle_D,
                    y_c=y_c,
                    z_c=z_c,
                    ID=ID,
                    Perineurium_thickness=Perineurium_thickness,
                    res=res,
                )

    def remove_fascicles(self, ID=None):
        """
        remove a fascicle of the FEM simulation

        Parameters
        ----------
        ID          : int, None
            ID number of the fascicle to remove, if None, remove all fascicles, by default None
        """
        if MCH.do_master_only_work():
            self.model.remove_fascicles(ID=ID)

    def add_electrode(self, electrode, stimulus):
        """
        Add a stimulation electrode and its stimulus to the stimulation, only it the electrode is FEM based.

        Parameters
        ----------
        electrode   : electrode object
            see Electrode.py or electrode object help for further details
        stimulus    : stimulus object or list[stimulus]
            see Stimulus.py or stimulus object help for further details, for Multipolar electrode:
            if stimulus a list of situmulus one stimulus set for each active site
            else
        """
        is_overlaping = False
        for elec in self.electrodes:
            is_overlaping = is_overlaping or check_electrodes_overlap(elec, electrode)

        if is_overlaping:
            rise_warning("overlaping electrod: not added to context")
        else:
            if is_FEM_electrode(electrode):
                if not electrode.is_multipolar:
                    if not self.electrodes == []:
                        electrode.set_ID_number(self.electrodes[-1].get_ID_number() + 1)
                    self.electrodes.append(electrode)
                    self.electrodes_label.append(electrode.label)
                    self.stimuli.append(stimulus)
                else:
                    if np.iterable(stimulus):
                        stimuli = stimulus
                    else:
                        rise_warning(
                            "Only one stimulus for a multipolar electrode, it will be set for all active sites"
                        )
                        stimuli = [stimulus for k in range(electrode.N_contact)]
                    for E in range(electrode.N_contact):
                        if not self.electrodes == []:
                            electrode.set_ID_number(
                                self.electrodes[-1].get_ID_number() + 1
                            )
                        self.electrodes.append(electrode)
                        self.electrodes_label.append(electrode.label + "_" + str())
                        self.stimuli.append(stimuli[E])

                if self.fenics and MCH.do_master_only_work():
                    electrode.parameter_model(self.model)
                self.synchronised = False
                self.setup = False
                self.is_run = False

    def setup_FEM(self):
        """
        Parameter a model with all added electrodes parameters, material parameters, build geometry and mesh
        """
        # parameter electrodes
        if self.comsol:
            for electrode in self.electrodes:
                electrode.parameter_model(self.model)
                # parameter materials
                self.model.set_parameter(
                    "Outer_conductivity", str(self.external_material.sigma) + "[S/m]"
                )
                self.model.set_parameter(
                    "Epineurium_conductivity", str(self.epineurium.sigma) + "[S/m]"
                )
                self.model.set_parameter(
                    "Perineurium_conductivity", str(self.perineurium.sigma) + "[S/m]"
                )
                if self.endoneurium.is_isotropic():
                    self.model.set_parameter(
                        "Endoneurium_conductivity_xx",
                        str(self.endoneurium.sigma) + "[S/m]",
                    )
                    self.model.set_parameter(
                        "Endoneurium_conductivity_yy",
                        str(self.endoneurium.sigma) + "[S/m]",
                    )
                    self.model.set_parameter(
                        "Endoneurium_conductivity_zz",
                        str(self.endoneurium.sigma) + "[S/m]",
                    )
                else:
                    self.model.set_parameter(
                        "Endoneurium_conductivity_xx",
                        str(self.endoneurium.sigma_xx) + "[S/m]",
                    )
                    self.model.set_parameter(
                        "Endoneurium_conductivity_yy",
                        str(self.endoneurium.sigma_yy) + "[S/m]",
                    )
                    self.model.set_parameter(
                        "Endoneurium_conductivity_zz",
                        str(self.endoneurium.sigma_zz) + "[S/m]",
                    )
                ## create geometry and mesh
                self.model.build_and_mesh()
        else:
            self.model.build_and_mesh()
            self.model.set_materials(
                Endoneurium_mat=self.endo_mat_file,
                Outer_mat=self.ext_mat_file,
                Perineurium_mat=self.peri_mat_file,
                Epineurium_mat=self.epi_mat_file,
            )
            self.model.setup_simulations()
        self.setup = True

    def run_model(self):
        """
        Set materials properties, build geometry and mesh if not already done and solve the FEM model all in one.
        """
        if MCH.do_master_only_work() or self.model.is_multi_proc:
            if not self.setup:
                self.setup_FEM()
            if not self.is_run:
                self.model.solve()
                self.is_run = True

    def compute_electrodes_footprints(self, x, y, z, ID):
        """
        Compute the footprints for all electrodes

        Parameters
        ----------
        x           : np.array
            x position at which to compute the field, in um
        y           : float
            y position at which to compute the field, in um
        z           : float
            z position at which to compute the field, in um
        ID          : int
            ID of the axon
        """

        if MCH.do_master_only_work() or (self.fenics and self.model.is_multi_proc):
            # test if the model is not solve and run simulation
            if not self.model.is_computed:
                self.run_model()
            # get all potentials
            V = self.model.get_potentials(x, y, z)
        else:
            # send a request to the master to get all potentials
            data = {"rank": MCH.rank, "x": x, "y": y, "z": z, "ID": ID}
            MCH.send_data_to_master(data)
            # listen to the master to get V
            V = MCH.recieve_potential_array_from_master()["V"]
        if len(self.electrodes) > 1:
            # sort electrodes by alphabetical order (COMSOL files should perform the parametric sweep by alphabetical order)
            sorter = np.argsort(self.electrodes_label)
            self.electrodes_label = list(np.asarray(self.electrodes_label)[sorter])
            self.electrodes = list(np.asarray(self.electrodes)[sorter])
            self.stimuli = list(np.asarray(self.stimuli)[sorter])
            # set the footprints
            for k, electrode in enumerate(self.electrodes):
                self.electrodes[k].set_footprint(V[:, k])
                # electrode.set_footprint(V[:, k])
        else:
            self.electrodes[0].set_footprint(V)
