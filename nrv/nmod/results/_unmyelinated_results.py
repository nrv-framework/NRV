"""
NRV-:class:`.unmyelinated_results` handling.
"""

import numpy as np
import matplotlib.pyplot as plt
from ._axons_results import axon_results


class unmyelinated_results(axon_results):
    """ """

    def __init__(self, context=None):
        super().__init__(context)

    def generate_axon(self):
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
        **kwgs
    ) -> None:
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
            **kwgs
        )
