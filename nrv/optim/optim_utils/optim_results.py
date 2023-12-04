from ...backend.NRV_Results import NRV_results
import matplotlib.pyplot as plt

class optim_results(NRV_results):
    def __init__(self, context=None):
        super().__init__({"optimization_parameters": context})



    ############################
    ##    plotting methods    ##
    ############################
    def plot_cost_history(self, fig=None , ax=None, xylabel=True, label=None):
        if ax is None:
            plt.plot(self.cost_history, label=label)
        if xylabel:
            plt.xlabel("iteration number")
            plt.ylabel("cost")