"""
Access and modify NRV Parameters
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
from .NRV_Class import NRV_class, abstractmethod, is_NRV_class, load_any
from .file_handler import json_load


def generate_results(obj: str, **kwargs):
    """
    generate the proper results object depending of the obj simulated

    Parameters
    ----------
    obj      : any
    """
    nrv_obj = load_any(obj)
    if "nrv_type" in nrv_obj.__dict__():
        nrv_type = nrv_obj.nrv_type
        if "myelinated" in nrv_type:
            nrv_type = ""
        return eval('sys.modules["nrv"].' + nrv_type + "_results")(context=obj)


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
        if isinstance(data, str):
            key_dic = json_load(data)
        else:
            key_dic = data
        for key, item in key_dic.items():
            if key not in self.__dict__:
                self.__dict__[key] = item

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
        self.pop("__NRVObject__")
