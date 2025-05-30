"""
NRV-:class:`NRV_singleton` handling.
"""

# from .log_interface import rise_warning
from multiprocessing import Lock

class NRV_singleton(type):
    """
    Should be used as metaclass to define singleton classes

    """
    _instances = {}

    # _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        # with cls._lock:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

