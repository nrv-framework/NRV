"""
NRV-:class:`.unmyelinated_results` handling.
"""

import numpy as np
import matplotlib.pyplot as plt
from ._axons_results import axon_results


class unmyelinated_results(axon_results):
    """ """

    def __init__(self, context=None):
        """
        Initialize an unmyelinated-axon results container.

        Parameters
        ----------
        context : Any, optional
            Serialized context or existing results used to populate the object.
        """
        super().__init__(context)

    def generate_axon(self):
        """
        Recreate an unmyelinated axon object from the stored result parameters.

        Returns
        -------
        unmyelinated
            Reconstructed axon instance.
        """
        if "unmyelinated" not in globals():
            from .._unmyelinated import unmyelinated
        return unmyelinated(**self)

    def plot_x_t(
        self,
        axes: plt.Axes,
        key: str = "V_mem",
        color: str = "k",
        n_lines: int = 20,
        n_jumped_lines: int | None = None,
        switch_axes=False,
        norm=None,
        **kwgs,
    ) -> None:
        """
        Plot time traces at a subset of recording positions along the axon.

        Parameters
        ----------
        axes : matplotlib.axes.Axes
            Target axes.
        key : str, optional
            Result key to display.
        color : str, optional
            Line color.
        n_lines : int, optional
            Number of traces to sample when ``n_jumped_lines`` is not provided.
        n_jumped_lines : int | None, optional
            Fixed stride used to subsample recording positions.
        switch_axes : bool, optional
            If ``True``, swap time and position axes.
        norm : Any, optional
            Optional normalization passed to the parent implementation.
        **kwgs : dict
            Additional plotting keyword arguments.
        """
        if n_jumped_lines is not None:
            x_index = np.arange(len(self.x_rec))
            x_index = x_index[x_index % n_jumped_lines == 0]
        else:
            x_index = np.int32(np.linspace(0, len(self.x_rec) - 1, n_lines))
        x_pos = self.x_rec[x_index]
        super().plot_x_t(
            axes=axes,
            x_pos=x_pos,
            x_index=x_index,
            key=key,
            color=color,
            switch_axes=switch_axes,
            norm=norm,
            **kwgs,
        )
