"""
Everything about the configuration, gathers :in a singleton:
* Macine configuration,
* NRV parameters,
* ...
"""

from ._NRV_Singleton import NRV_singleton
from ._machine_config import MachineConfig
from ._parameters import nrv_parameters


class nrv_config(metaclass=NRV_singleton):
    """A unique class to handle all the configuration"""

    def __init__(self):
        self.machine_config = MachineConfig()
        self.framework_parameters = nrv_parameters()

    def display_machine_config(self):
        print(self.machine_config)
