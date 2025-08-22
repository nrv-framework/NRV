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
        return self._data

    @data.setter
    def data(self, data: None | eit_forward_results):
        self._data = data

    @data.deleter
    def data(self):
        self._data = None

    def fromat_data(data: None | eit_forward_results = None) -> np.ndarray:
        pass

    def _get_i_to_solve(
        self, i_to_solve=None, i_t: int = 0, i_f: int = 0, i_res: int = 0
    ) -> tuple[int]:
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
        __label = f"Solving inverse problem"
        if self.n_proc > 1:
            __label += f" - {self.n_proc} procs"

    def _run_inverse(i_to_solve=None, i_t: int = 0, i_f: int = 0, i_res: int = 0):
        pass

    def solve(
        self,
        i_t: np.ndarray | int | None = 0,
        i_f: np.ndarray | int | None = 0,
        i_res: np.ndarray | int | None = 0,
        **kwgs,
    ):
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
        res_id = i_t, i_f, i_res
        if not res_id in self.results_ppt:
            print("Result not found. Computing...")
            self.solve(*res_id)
        return self.results[self.results_ppt.index(res_id)]

    def plot(ax: plt.Axes, **kwgs):
        pass
