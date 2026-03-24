from abc import abstractmethod
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool, Manager
from rich import progress
from itertools import product

from ..backend._extlib_interface import set_idxs
from .results import eit_forward_results


class eit_inverse:
    """
    Abstract base class for solving the Electrical Impedance Tomography (EIT) inverse problem.

    This class provides the interface for solving EIT problems inverse problem on nerve models :class:`eit_forward_results` simulation results

    .. seealso::
    :doc:`EIT users guide </usersguide/eit>` --- For generic description.

    :doc:`Tutorial 6 </tutorials/6_play_with_eit>` --- For usage description.

    Note
    ----
    This class is abstract and cannot be instantiated directely. For now only the following daughter class can be used:
        - :class:`nrv.eit.pyeit_inverse`:  Interface EIT of inverse problem solving using PyEIT methods.

    Note
    ----
    In future version additional solver could be add to NRV.
    """

    @abstractmethod
    def __init__(self, data: None | eit_forward_results = None, **kwgs):
        """
        Initialize an inverse EIT solver.

        Parameters
        ----------
        data : eit_forward_results | None, optional
            Forward EIT results used as reconstruction input.
        **kwgs : dict
            Additional subclass-specific keyword arguments.
        """
        self.data = data  # TODO [NRV] load_any(data) for merge with nrv
        self.n_proc: int = 1
        self.results = []
        self.results_ppt = []

    # ---------------------- #
    # Properties and setters #
    # ---------------------- #
    @property
    def has_data(self) -> bool:
        """
        Check if the object contains data.

        Returns
        -------
            bool: True if data is present, False otherwise.
        """
        return self.data is not None

    @property
    def data(self) -> None | eit_forward_results:
        """
        Forward EIT data used by the inverse solver.

        Returns
        -------
        eit_forward_results | None
            Current input dataset.
        """
        return self._data

    @data.setter
    def data(self, data: None | eit_forward_results):
        """
        Set the forward EIT dataset used by the inverse solver.

        Parameters
        ----------
        data : eit_forward_results | None
            New input dataset.
        """
        self._data = data

    @data.deleter
    def data(self):
        """
        Remove the current forward EIT dataset.
        """
        self._data = None

    def fromat_data(data: None | eit_forward_results = None) -> np.ndarray:
        """
        Convert forward EIT data into the format expected by the inverse solver.

        Parameters
        ----------
        data : eit_forward_results | None, optional
            Input data or solver state to format.

        Returns
        -------
        np.ndarray
            Formatted data vector.
        """
        pass

    def _get_i_to_solve(
        self, i_to_solve=None, i_t: int = 0, i_f: int = 0, i_res: int = 0
    ) -> tuple[int]:
        """
        Resolve explicit or queued indices for one inverse reconstruction.

        Parameters
        ----------
        i_to_solve : int | None, optional
            Index into ``self.to_solve`` when batch solving is enabled.
        i_t : int, optional
            Time index.
        i_f : int, optional
            Frequency index.
        i_res : int, optional
            Result index.

        Returns
        -------
        tuple[int, int, int]
            Time, frequency, and result indices to reconstruct.
        """
        if i_to_solve is not None and self.to_solve is not None:
            _to_solve = self.to_solve[i_to_solve]
            if len(_to_solve) == 3:
                i_t, i_f, i_res = _to_solve
            else:
                i_t, i_f = _to_solve
        return i_t, i_f, i_res

    # ---------------------- #
    # Reconstruction methods #
    # ---------------------- #
    def __set_pbar_label(self, kwgs):
        """
        Build the progress-bar label used during batch reconstruction.

        Parameters
        ----------
        kwgs : dict
            Additional keyword arguments provided to :meth:`solve`.

        Returns
        -------
        str
            Progress-bar description.
        """
        __label = f"Solving inverse problem"
        if self.n_proc > 1:
            __label += f" - {self.n_proc} procs"
        return __label

    def _run_inverse(i_to_solve=None, i_t: int = 0, i_f: int = 0, i_res: int = 0):
        """
        Run one inverse reconstruction.

        Parameters
        ----------
        i_to_solve : int | None, optional
            Optional index into the queued reconstructions.
        i_t : int, optional
            Time index.
        i_f : int, optional
            Frequency index.
        i_res : int, optional
            Result index.
        """
        pass

    def solve(
        self,
        i_t: np.ndarray | int | None = 0,
        i_f: np.ndarray | int | None = 0,
        i_res: np.ndarray | int | None = 0,
        **kwgs,
    ):
        """
        Solve one or several inverse problems and cache the results.

        Parameters
        ----------
        i_t, i_f, i_res : np.ndarray | int | None, optional
            Time, frequency, and result indices to reconstruct.
        **kwgs : dict
            Additional solver-specific options.

        Returns
        -------
        list
            List of reconstructed images or fields accumulated in ``self.results``.
        """
        _msolve = np.iterable(i_t) or np.iterable(i_f) or np.iterable(i_res)
        if not _msolve:
            _res, _ppt = self._run_inverse(i_t=i_t, i_f=i_f, i_res=i_res)
            self.results.append(_res)
            self.results_ppt.append(_ppt)
        else:
            self.to_solve = list(
                product(
                    set_idxs(i_t, self.data.n_t),
                    set_idxs(i_f, self.data.n_f),
                )
            )
            _n_sim = len(self.to_solve)
            sim_list = np.arange(_n_sim)
            with progress.Progress(
                "[progress.description]{task.description}",
                "{task.completed} / {task.total}",
                progress.BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                progress.TimeRemainingColumn(),
                progress.TimeElapsedColumn(),
            ) as pg:
                __label = self.__set_pbar_label(**kwgs)
                task_id = pg.add_task(f"[cyan]{__label}:", total=_n_sim)
                # with mp.get_context('spawn').Pool(parameters.get_nmod_ncore()) as pool:  #forces spawn mode
                with Pool(self.n_proc) as pool:
                    for _res, _ppt in pool.imap(self._run_inverse, sim_list):
                        self.results.append(_res)
                        self.results_ppt.append(_ppt)
                        self.results.append(sim_list)
                        pg.advance(task_id)
                        pg.refresh()
                    pool.close()  # LR: Apparently this avoid PETSC Terminate ERROR
                    pool.join()
        return self.results

    def get_results(self, i_t: int = 0, i_f: int = 0, i_res: int = 0) -> np.ndarray:
        """
        Retrieves the computed result for the specified time, frequency, and result indices.
        If the result is not already computed, it triggers the computation.

        Parameters
        ----------
        i_t : int, optional
            Index for the time corresponding to the result, default is 0.
        i_f : int, optional
            Index for the frequency corresponding to the result, default is 0.
        i_res : int, optional
            Index for the result corresponding to the result, default is 0.

        Returns
        -------
        np.ndarray
            The result corresponding to the specified indices.

        Note
        ----
        If the requested result is not found in `self.results_ppt`, the method will
        call `self.solve` to compute it before returning.
        """

        res_id = i_t, i_f, i_res
        if not res_id in self.results_ppt:
            print("Result not found. Computing...")
            self.solve(*res_id)
        return self.results[self.results_ppt.index(res_id)]

    def clear_results(self, i_t: int = 0, i_f: int = 0, i_res: int = 0):
        """
        Removes the result entry corresponding to the specified indices from the results.

        Parameters
        ----------
        i_t : int, optional
            Index for time (default is 0).
        i_f : int, optional
            Index for frequency (default is 0).
        i_res : int, optional
            Index for result (default is 0).

        Note
        ----
        If the specified result identifier exists in `self.results_ppt`, the corresponding
        result is removed from both `self.results` and `self.results_ppt`.
        """
        res_id = i_t, i_f, i_res
        if res_id in self.results_ppt:
            _idx = self.results_ppt.index(res_id)
            self.results.pop(_idx)
            self.results_ppt.pop(_idx)

    def clear_all_results(self):
        """
        Clears all stored results by resetting the `results` and `results_ppt` attributes to empty lists.
        """
        self.results = []
        self.results_ppt = []

    def get_results_range(self, i_t: int = 0, i_f: int = 0, i_res: int = 0) -> tuple:
        """
        Return the value range of one reconstructed result.

        Parameters
        ----------
        i_t : int, optional
            Time index.
        i_f : int, optional
            Frequency index.
        i_res : int, optional
            Result index.

        Returns
        -------
        tuple
            Minimum and maximum values of the selected reconstruction.
        """
        _dv = self.get_results(i_t=i_t, i_f=i_f, i_res=i_res)
        return np.min(_dv), np.max(_dv)

    def plot(ax: plt.Axes, **kwgs):
        """
        Plot one reconstructed inverse result.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Target axes.
        **kwgs : dict
            Plotting options defined by subclasses.
        """
        pass
