"""
Access and modify NRV Parameters
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""

from abc import ABCMeta, abstractmethod
import numpy as np
import sys
from copy import deepcopy
from numpy import iterable
from .file_handler import json_dump, json_load
from .parameters import parameters
from .log_interface import rise_error, rise_warning, pass_info

def is_NRV_class(x):
    return isinstance(x, NRV_class)

def is_NRV_class_list(x):
    if iterable(x):
        for xi in x:
            if not is_NRV_class(xi):
                return False
        return True
    return False

def is_NRV_dict(x):
    if isinstance(x, dict):
        if 'nrv_type' in x:
            return True
    return False 

def is_NRV_dict_list(x):
    if iterable(x):
        for xi in x:
            if not (is_NRV_dict(xi)):
                return False
        return True
    return False




class NRV_class(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        """
        """
        self.__NRVObject__ = True
        self.nrv_type = self.__class__.__name__
        if parameters.get_nrv_verbosity()>=4:
            pass_info(self.nrv_type, ' initialized')

    def __del__(self):
        if parameters.get_nrv_verbosity()>=4:
            pass_info(self.nrv_type, ' deleted')        

    def save(self,save=False, fname='nrv_save.json', blacklist={}):
        bl = {}
        for key in blacklist:
            if key in self.__dict__:
                bl[key] = self.__dict__.pop(key)
        key_dic = deepcopy(self.__dict__)
        for key in bl:
            self.__dict__[key] = bl[key]
        for key in key_dic:
            if is_NRV_class(key_dic[key]):
                key_dic[key] = key_dic[key].save()
            elif is_NRV_class_list(key_dic[key]):
                for i in range(len(key_dic[key])):
                    key_dic[key][i] = key_dic[key][i].save()

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
                if is_NRV_dict(key_dic[key]) or is_NRV_dict_list(key_dic[key]):
                    self.__dict__[key] = load_any(key_dic[key])
                elif isinstance(self.__dict__[key], np.ndarray):
                    self.__dict__[key] = np.array(key_dic[key])
                else:
                    self.__dict__[key] = key_dic[key]


def load_any(data, **kwargs):
    if type(data) == str:
        key_dic = json_load(data)
    else: 
        key_dic = data
    
    if is_NRV_class(key_dic) or is_NRV_class_list(key_dic):
        nrv_obj = key_dic
    
    elif is_NRV_dict(key_dic):
        nrv_type = key_dic['nrv_type']
        nrv_obj = eval("sys.modules['nrv']."+nrv_type)()
        nrv_obj.load(key_dic,**kwargs)
    elif is_NRV_dict_list(key_dic):
        nrv_obj = []
        for i in key_dic:
            nrv_obj += [load_any(i, **kwargs)]
    return nrv_obj
