"""
Module containing a top class from which all other NRV classes inherit.
This is mainly used to create generic methods such as save and load.
"""

from abc import ABCMeta, abstractmethod
from copy import deepcopy
import sys  # used in an eval
import numpy as np
from pandas import DataFrame
from numpy import iterable

from ._file_handler import json_dump, json_load
from ._log_interface import pass_debug_info
from ._extlib_interface import is_empty_iterable


# ------------------------------------ #
#           check object               #
# ------------------------------------ #
def is_NRV_class(x):
    """
    Check if the object x is a ``NRV_class``.

    Parameters
    ----------
    x   : any
        object to check.

    Returns
    -------
    bool
    """
    return isinstance(x, NRV_class)


def is_NRV_class_list(x):
    """
    check if the object x is a list containing only ``NRV_class``.

    Parameters
    ----------
    x   : any
        object to check.

    Returns
    -------
    bool
    """
    if iterable(x):
        for xi in x:
            if not is_NRV_class(xi):
                return False
        return True
    return False


def is_NRV_class_dict(x):
    """
    check if the object x is a dictionary containing only ``NRV_class``.

    Parameters
    ----------
    x   : any
        object to check.

    Returns
    -------
    bool
    """
    if isinstance(x, dict):
        for xi in x.values():
            if not is_NRV_class(xi):
                return False
        return True
    return False


# ------------------------------------ #
#         check dictionaries           #
# ------------------------------------ #


def is_NRV_dict(x):
    """
    Check if the object x is a dictionary of saved ``NRV_class``.

    Parameters
    ----------
    x : any
        object to check.

    Returns
    -------
    bool
    """
    if isinstance(x, dict):
        if "nrv_type" in x:
            return True
    return False


def is_NRV_dict_list(x):
    """
    Check if the object x is a list of dictionary of saved ``NRV_class``.

    Parameters
    ----------
    x : any
        object to check.

    Returns
    -------
    bool
    """
    if iterable(x):
        if len(x) > 0:
            for xi in x:
                if not (is_NRV_dict(xi)):
                    return False
            return True
    return False


def is_NRV_dict_dict(x):
    """
    Check if the object x is a dictionary containing dictionaries of saved ``NRV_class``.

    Parameters
    ----------
    x : any
        object to check.

    Returns
    -------
    bool
    """
    if isinstance(x, dict):
        for key in x:
            if not (is_NRV_dict(x[key])):
                return False
        return True
    return False


def is_NRV_object_dict(x):
    """
    Check if the object x is_NRV_dict, is_NRV_dict_list or is_NRV_dict_dict.

    Parameters
    ----------
    x : any
        object to check.

    Returns
    -------
    bool
    """
    return is_NRV_dict(x) or is_NRV_dict_list(x) or is_NRV_dict_dict(x)


# --------------------------------- #
#            NRV Class              #
# --------------------------------- #


class NRV_class(metaclass=ABCMeta):
    """
    Instanciate a basic NRV class
    NRV Class are empty shells, defined as abstract classes of which every class in NRV
    should inherite. This enable automatic context backup with save and load methods.
    """

    @abstractmethod
    def __init__(self):
        """
        Init method for ``NRV_class``
        """
        self.__NRVObject__ = True
        self.nrv_type = self.__class__.__name__
        self.nrv_module = self.__module__
        pass_debug_info(self.nrv_type, " initialized")

    def __del__(self):
        """
        Destructor for ``NRV_class``
        """
        pass_debug_info(self.nrv_type, " deleted")
        keys = list(self.__dict__.keys())
        for key in keys:
            del self.__dict__[key]

    def save(self, save=False, fname="nrv_save.json", blacklist=[], **kwargs) -> dict:
        """
        Generic saving method for ``NRV_class`` instance.

        Parameters
        ----------
        save: bool, optional
            If True, saves the NRV object in a json file, by default False.
        fname : str, optional
            Name of the json file
        blacklist : dict, optional
            Dictionary containing the keys to be excluded from the saving.
        **kwargs : dict, optional
            Additional arguments to pass to the ``save`` method of the NRV object.

        Returns
        -------
        key_dict : dict
            dictionary containing the original instance data in a `jsonisable` format.

        Note
        ----
        - This ``save`` method does not save the object to a `json` file by default: It only\
            returns a dictionary containing the original instance data in a jsonisable format.\
            However, this is the simplest way to do it by setting the ``save`` parameter to ``True``.
        - The dictionary returned by this `save` method can be modified without having any impact on the\
            the original instance (the items are deep copies of the instance's attributes).
        """
        key_dic = {}
        for key in self.__dict__:
            if key not in blacklist:
                if is_NRV_class(self.__dict__[key]):
                    key_dic[key] = self.__dict__[key].save(save=False, **kwargs)
                elif is_NRV_class_list(self.__dict__[key]):
                    key_dic[key] = []
                    for i in range(len(self.__dict__[key])):
                        key_dic[key] += [
                            self.__dict__[key][i].save(save=False, **kwargs)
                        ]
                elif is_NRV_class_dict(self.__dict__[key]):
                    key_dic[key] = {}
                    for i in self.__dict__[key]:
                        key_dic[key][i] = self.__dict__[key][i].save(
                            save=False, **kwargs
                        )
                else:
                    key_dic[key] = deepcopy(self.__dict__[key])
        if save:
            json_dump(key_dic, fname)
        return key_dic

    def load(self, data, blacklist={}, **kwargs) -> None:
        """
        Generic loading method for ``NRV_class`` instance

        Parameters
        ----------
        data : str, dict, nrv_class
            data from which the object should be generated:

                - if str, data will be loaded from the corresponding json file
                - if dict, data will be loaded from a dictionnary
                - if nrv_class, same object will be returned
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
                elif isinstance(self.__dict__[key], DataFrame):
                    self.__dict__[key] = DataFrame(key_dic[key])
                elif isinstance(self.__dict__[key], set):
                    self.__dict__[key] = set(key_dic[key])
                elif is_empty_iterable(key_dic[key]):
                    self.__dict__[key] = eval(self.__dict__[key].__class__.__name__)()
                else:
                    self.__dict__[key] = key_dic[key]

    def set_parameters(self, **kawrgs) -> None:
        """
        Generic method to set any attribute of ``NRV_class`` instance

        Parameters
        ----------
        ***kwargs
            Key arguments containing one or multiple parameters to set.

        Examples
        --------
        As the :class:`~nrv.nmod._myelinated.myelinated` inherits from NRV_class-class parameters, such as diameter and lenght can be set with `set_parameters`.

        >>> ax = nrv.myelinated()
        >>> print(ax.d, ax.L)
        10, 10000
        >>> ax.set_parameters(d=6, L=1000)
        >>> print(ax.d, ax.L)
        6, 1000
        """
        for key in kawrgs:
            if key in self.__dict__:
                self.__dict__[key] = kawrgs[key]

    def get_parameters(self):
        """
        Generic method returning all the atributes of an NRV_class instance

        Returns
        -------
            dict : dictionnary of all atributes of ``NRV_class`` instance
        """
        return self.__dict__


def load_any(data, **kwargs) -> NRV_class:
    """
    loads any type of NRV object from a json file or a dictionary generated with NRV_class.save

    Parameters
    ----------
    data : str, dict, nrv_class
        data from which the object should be generated:

            - if str, data will be loaded from the corresponding json file
            - if dict, data will be loaded from a dictionnary
            - if nrv_class, same object will be returned
    **kwargs
        additionnal argument to use for the loading

    Returns
    -------
    nrv_obj: any (NRV_class)


    """
    if isinstance(data, str):
        key_dic = json_load(data)
    else:
        key_dic = data
    # test if NRV class
    if is_NRV_class(key_dic) or is_NRV_class_list(key_dic):
        nrv_obj = key_dic
    # test if NRV dict
    elif is_NRV_object_dict(key_dic):
        key_dic = deepcopy(key_dic)
        if is_NRV_dict(key_dic):
            nrv_type = key_dic["nrv_type"]
            nrv_module = "nrv"
            if "nrv_module" in key_dic:
                nrv_module = key_dic["nrv_module"]
            nrv_obj = eval(f"sys.modules['{nrv_module}'].{nrv_type}")()
            nrv_obj.load(key_dic, **kwargs)
        elif is_NRV_dict_dict(key_dic):
            nrv_obj = {}
            for key in key_dic:
                nrv_obj[key] = load_any(key_dic[key], **kwargs)
        elif is_NRV_dict_list(key_dic):
            nrv_obj = []
            for i in key_dic:
                nrv_obj += [load_any(i, **kwargs)]
    else:
        nrv_obj = key_dic
    return nrv_obj
