"""
NRV-:class:`.nerve_results` handling.
"""


from ...backend.NRV_Results import sim_results
from .fascicles_results import fascicle_results
from ...backend.log_interface import rise_error, rise_warning, pass_info

class nerve_results(sim_results):
    """

    """

    def __init__(self, context=None):
        super().__init__(context)


    def get_fascicle_results(self, ID: int) -> fascicle_results:
        if ID not in self.fascicles_IDs:
            rise_error(("Fascicle ID does not exists."))
        else:
            return(self[f'fascicle{ID}'])




