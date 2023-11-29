"""
Access and modify NRV Parameters
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
from .NRV_Class import NRV_class, abstractmethod, is_NRV_class


class NRV_results(NRV_class, dict):
    """
    Results class for NRV
    """
    @abstractmethod
    def __init__(self, context=None):
        super().__init__()
        if context is None:
            context = {}
        elif is_NRV_class(context):
            context.save(save=False)

        if "nrv_type" in context:
            context["result_type"] = context.pop("nrv_type")
        self.update(context)
        self.__sync()


    def save(self, save=False, fname="nrv_save.json", blacklist=[], **kwargs):
        self.__sync()
        return super().save(save, fname, blacklist, **kwargs)


    def load(self, data, blacklist=[], **kwargs):
        super().load(data, blacklist, **kwargs)
        self.__sync()


    def __setitem__(self, key, value):
        if not key == "nrv_type":
            self.__dict__[key] = value
        super().__setitem__(key, value)

    def __delitem__(self, key):
        if not key == "nrv_type":
            del self.__dict__[key]
        super().__delitem__(key)

    def update(self, __m, **kwargs) -> None:
        """
        overload of dict update method to update both attibute and items
        """
        self.__dict__.update(__m, **kwargs)
        super().update(__m, **kwargs)
    
    def __sync(self):
        self.update(self.__dict__)
        self.pop('__NRVObject__')
