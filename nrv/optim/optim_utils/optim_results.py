from ...backend.NRV_Results import NRV_results

class optim_results(NRV_results):
    def __init__(self, context=None):
        super().__init__({"optimization_parameters": context})