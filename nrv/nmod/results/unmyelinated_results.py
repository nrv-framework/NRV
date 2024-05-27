"""
NRV-:class:`.unmyelinated_results` handling.
"""


from .axons_results import axon_results
from ..unmyelinated import unmyelinated

class unmyelinated_results(axon_results):
    """

    """
    def __init__(self, context=None):
        super().__init__(context)


    def generate_axon(self):
        return unmyelinated(**self)

