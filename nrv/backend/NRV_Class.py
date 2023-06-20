"""
Access and modify NRV Parameters
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""

from abc import ABCMeta, abstractmethod
from .file_handler import json_dump, json_load

def is_NRV_class(x):
    return isinstance(x, NRV_class)


class NRV_class(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        """
        """
        self.__NRVObject__ = True
        self.type = "nrv_class"

    def save(self,save=False, fname='nrv_save.json', blacklist={}):
        key_dic = self.__dict__
        for key in self.__dict__:
            if key in blacklist:
                key_dic.pop(key)
            elif is_NRV_class(key_dic[key]):
                key_dic[key] = key_dic[key].save()
        if save:
            json_dump(key_dic, fname)
        return key_dic
          
        
    def load(self, data, blacklist={}):
        if type(data) == str:
            key_dic = json_load(data)
        else: 
            key_dic = data
        for key in self.__dict__:
            if key in key_dic and key not in blacklist:
                self.__dict__[key] = key_dic[key]
