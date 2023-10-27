"""
Access and modify NRV Parameters
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""

# from .log_interface import rise_warning


class NRV_singleton(type):
    """
    Should be used as metaclass to define singleton classes

    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(NRV_singleton, cls).__call__(*args, **kwargs)
        else:
            print("WARNING : Class", cls, "is a sigleton cannot be re-instantiated")
            # rise_warning('Class', cls, 'is a sigleton cannot be re-instantiated')
        return cls._instances[cls]
