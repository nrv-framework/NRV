"""
NRV-:class:`.NRV_simulable` handling.

A generic class for all NRV simulable classes (:class:`~nrv.nmod.nerve`, :class:`~nrv.nmod._fascicle`, :class:`~nrv.nmod.myelinated`)
"""

from ._NRV_Class import NRV_class
from ._NRV_Results import generate_results, sim_results


def is_NRV_simulable(x):
    """
    Check if the object x is a :class:`.NRV_simulable`.

    Parameters
    ----------
    x   : any
        object to check.

    Returns
    -------
    bool
    """
    return isinstance(x, NRV_simulable)


def simulable(x):
    """
    Check if the object x is a :class:`.NRV_simulable`.

    Parameters
    ----------
    x   : any
        object to check.

    Returns
    -------
    bool
    """
    return isinstance(x, NRV_simulable)


class NRV_simulable(NRV_class):
    """
    Generic class for all NRV simulable classes (:class:`~nrv.nmod.nerve`, :class:`~nrv.nmod.fascicle`, :class:`~nrv.nmod.myelinated`).
    This class gather commun features to all the simulable object, in particular the :func:`.NRV_simulable.simulate` method.

    Note
    ----
    -   All NRV_simulable instance are callable object. When called, the instance :func:`.NRV_simulable.simulate` method is called.

    Parameters
    ----------
    t_sim : float
        duration of the simulation in `ms`
    dt : float
        Time step of the simulation in `ms`
    record_V_mem : bool
        if true, the membrane voltage of each cell is recorded, by default True
    record_I_mem : bool
        if true, the membrane current of each cell is recorded, by default False
    record_I_ions : bool
        if true, the ionic currents of each cell are recorded, by default False
    record_particles : bool
        if true, the marticule states of each cell are recorded, by default False
    record_g_mem : bool
        if true, the membrane coductivity of each cell is recorded, by default False
    record_g_ions : bool
        if true, the ionic conductivities of each cell are recorded, by default False
    loaded_footprints : bool
        Dictionnary composed of extracellular footprint array, the keys are int value
        of the corresponding electrode ID, if None, footprints calculated during the simulation,
        set to None by default

    Note
    ----
    -   All the above parameters can either be set when the instance is initialized, or later in the script.
    """

    def __init__(
        self,
        t_sim=2e1,
        dt=0.001,
        record_V_mem=True,
        record_I_mem=False,
        record_I_ions=False,
        record_particles=False,
        record_g_mem=False,
        record_g_ions=False,
        loaded_footprints=None,
        **kwargs
    ):
        super().__init__()
        self.t_sim = t_sim
        self.record_V_mem = record_V_mem
        self.record_I_mem = record_I_mem
        self.record_I_ions = record_I_ions
        self.record_particles = record_particles
        self.record_g_mem = record_g_mem
        self.record_g_ions = record_g_ions
        self.loaded_footprints = loaded_footprints

        self.dt = dt

    @property
    def has_FEM_extracel(self) -> bool:
        # return self.extracel_status() and issubclass(self.extra_stim.nrv_type == "FEM_stimulation")
        return self.extracel_status() and self.extra_stim.nrv_type == "FEM_stimulation"

    def extracel_status(self):
        """
        Check if an extracellular context is attached to the instance

        Returns
        -------
        bool
        """
        if "extra_stim" in self.__dict__:
            if self.__dict__["extra_stim"] is not None:
                return True
        else:
            return False

    def intracel_status(self):
        """
        Check if an intracellular context is attached to the instance

        Returns
        -------
        bool
        """
        if "intra_current_stim" in self.__dict__:
            if (
                self.__dict__["intra_current_stim"] != []
                and self.__dict__["intra_current_stim"] is not None
            ):
                return True
        elif "intra_voltage_stim" in self.__dict__:
            if self.__dict__["intra_voltage_stim"] is not None:
                return True
        else:
            return False

    def rec_status(self):
        """
        Check if a recording context is attached to the instance

        Returns
        -------
        bool
        """
        if "recorder" in self.__dict__:
            if self.__dict__["recorder"] is not None:
                return True
        else:
            return False

    def __call__(self, **kwds):
        return self.simulate(**kwds)

    def simulate(self, **kwargs) -> sim_results:
        """
        Generic start of the simulate method. At this level the method does only two things:

        -   update instance attribues from the kwargs
        -   generate the sim_results dictionary

        Parameters
        ----------
        **kwargs
            Key arguments containing one or multiple parameters to set.

        Returns
        -------
        sim_results:
            Empty results containing only the simulation parameters.
        """
        self.set_parameters(**kwargs)
        context = self.save(
            save=False,
            extracel_context=self.extracel_status(),
            intracel_context=self.intracel_status(),
            rec_context=self.rec_status(),
        )
        results = generate_results(context)
        return results
