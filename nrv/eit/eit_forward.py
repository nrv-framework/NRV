from ..backend._NRV_Class import NRV_class
from ..backend._log_interface import rise_error


class eit_forward(NRV_class):
    """
    Class allowing to simulate Electircal Impedance Tomography in a nerve
    """

    def __init__(self):
        super().__init__()
        self._nerve = None
        self._protocol = None

    @property
    def nerve(self):
        return self._nerve

    @nerve.setter
    def nerve(self, n):
        self._nerve = n

    @nerve.deleter
    def nerve(self, n):
        self._nerve = None

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, p):
        self._protocol = p

    @protocol.deleter
    def protocol(self, p):
        self._protocol = None

    def simulate():
        rise_error(NotImplementedError)
