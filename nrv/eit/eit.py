from ..backend.NRV_Class import NRV_class



class eit(NRV_class):
    """
    Class allowing to simulate Electircal Impedance Tomography in a nerve
    """
    def __init__():
        _nerve = None
        _protocol = None

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

