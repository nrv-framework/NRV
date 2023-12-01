"""
Access and modify NRV Parameters
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
from abc import ABCMeta, abstractmethod
from copy import deepcopy

# sys used in an eval
import sys
import numpy as np
from numpy import iterable

from .file_handler import json_dump, json_load
from .log_interface import pass_debug_info

########################################
#           check object               #
########################################


def is_NRV_class(x):
    return isinstance(x, NRV_class)


def is_NRV_class_list(x):
    if iterable(x):
        for xi in x:
            if not is_NRV_class(xi):
                return False
        return True
    return False


def is_NRV_class_dict(x):
    if isinstance(x, dict):
        for xi in x.values():
            if not is_NRV_class(xi):
                return False
        return True
    return False


##########################################
#           check dictionaries           #
##########################################

def is_NRV_object_dict(x):
    return is_NRV_dict(x) or is_NRV_dict_list(x) or is_NRV_dict_dict(x)


def is_NRV_dict(x):
    if isinstance(x, dict):
        if "nrv_type" in x:
            return True
    return False


def is_NRV_dict_list(x):
    if iterable(x):
        if len(x) > 0:
            for xi in x:
                if not (is_NRV_dict(xi)):
                    return False
            return True
    return False


def is_NRV_dict_dict(x):
    if isinstance(x, dict):
        for key in x:
            if not (is_NRV_dict(x[key])):
                return False
        return True
    return False


class NRV_class(metaclass=ABCMeta):
    """
    Instanciate a basic NRV class
    NRV Class are empty shells, defined as abstract classes of which every class in NRV
    should inherite. This enable automatic context backup with save and load methods
    """

    @abstractmethod
    def __init__(self):
        """
        Init method for NRV class
        """
        self.__NRVObject__ = True
        self.nrv_type = self.__class__.__name__
        pass_debug_info(self.nrv_type, " initialized")

    def __del__(self):
        """
        Destructor for NRV class
        """
        pass_debug_info(self.nrv_type, " deleted")


    def save(self, save=False, fname="nrv_save.json", blacklist=[], **kwargs):
        """
        Generic saving method for NRV class instance

        Parameters
        ----------
        save : bool, optional
            If True, save the NRV object in a json file
        fname : str, optional
            Name of the json file
        blacklist : dict, optional
            Dictionary containing the keys to be excluded from the save
        **kwargs : dict, optional
            Additional arguments to be passed to the save method of the NRV object
        """
        key_dic = {}
        for key in self.__dict__:
            if key not in blacklist:
                if is_NRV_class(self.__dict__[key]):
                    key_dic[key] = self.__dict__[key].save(**kwargs)
                elif is_NRV_class_list(self.__dict__[key]):
                    key_dic[key] = []
                    for i in range(len(self.__dict__[key])):
                        key_dic[key] += [self.__dict__[key][i].save(**kwargs)]
                elif is_NRV_class_dict(self.__dict__[key]):
                    key_dic[key] = {}
                    for i in self.__dict__[key]:
                        key_dic[key][i] = self.__dict__[key][i].save(**kwargs)
                else:
                    key_dic[key] = deepcopy(self.__dict__[key])
        if save:
            json_dump(key_dic, fname)
        return key_dic

    def load(self, data, blacklist={}, **kwargs):
        """
        Generic loading method for NRV class instance

        Parameters
        ----------
        data : dict
            Dictionary containing the NRV object
        blacklist : dict, optional
            Dictionary containing the keys to be excluded from the load
        **kwargs : dict, optional
            Additional arguments to be passed to the load method of the NRV object
        """
        if isinstance(data, str):
            key_dic = json_load(data)
        else:
            key_dic = data
        for key in self.__dict__:
            if key in key_dic and key not in blacklist:
                if is_NRV_object_dict(key_dic[key]):
                    self.__dict__[key] = load_any(key_dic[key], **kwargs)
                elif isinstance(self.__dict__[key], np.ndarray):
                    self.__dict__[key] = np.array(key_dic[key])
                elif key_dic[key] == []:
                    self.__dict__[key] = eval(self.__dict__[key].__class__.__name__)()
                else:
                    self.__dict__[key] = key_dic[key]

    def set_parameters(self,**kawrgs):
        for key in kawrgs:
            if key in self.__dict__:
                self.__dict__[key] = kawrgs[key]

    def get_parameters(self):
        return self.__dict__

def load_any(data, **kwargs):
    """loads an object of any kind from a json file

    Args:
        data : _description_

    Returns:
        _type_: _description_
    """
    if isinstance(data, str):
        key_dic = json_load(data)
    else:
        key_dic = data
    # test if NRV class
    if is_NRV_class(key_dic) or is_NRV_class_list(key_dic):
        nrv_obj = key_dic
    # test if NRV dict
    elif is_NRV_dict(key_dic):
        nrv_type = key_dic["nrv_type"]
        nrv_obj = eval('sys.modules["nrv"].' + nrv_type)()
        nrv_obj.load(key_dic, **kwargs)
    elif is_NRV_dict_dict(key_dic):
        nrv_obj = {}
        for key in key_dic:
            nrv_obj[key] = load_any(key_dic[key], **kwargs)
    elif is_NRV_dict_list(key_dic):
        nrv_obj = []
        for i in key_dic:
            nrv_obj += [load_any(i, **kwargs)]
    return nrv_obj
