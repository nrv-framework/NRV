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

    def plot_x_t(
        self,
        axes: plt.axes,
        key: str = "V_mem",
        color: str = "k",
        n_lines: int = 20,
        **kwgs
    ) -> None:
        x_index = np.int32(np.linspace(0, len(self.x_rec) - 1, n_lines))
        x_pos = self.x_rec[x_index]
        dx = np.abs(x_pos[1] - x_pos[0])
        norm_fac = dx / (np.max(abs(self[key])) * 1.1)
        offset = np.abs(np.min(self[key][0] * norm_fac))
        for x, x_idx in zip(x_pos, x_index):
            axes.plot(
                self["t"], self[key][x_idx] * norm_fac + x + offset, color=color, **kwgs
            )
