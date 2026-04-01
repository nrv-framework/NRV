"""
NRV-:class:`NRV_singleton` handling.
"""


class NRV_singleton(type):
    """
    Should be used as metaclass to define singleton classes

    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Return the unique instance associated with the singleton class.

        Parameters
        ----------
        *args
            Positional arguments used when creating the instance for the first time.
        **kwargs
            Keyword arguments used when creating the instance for the first time.

        Returns
        -------
        object
            Singleton instance of ``cls``.
        """
        # with cls._lock:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
