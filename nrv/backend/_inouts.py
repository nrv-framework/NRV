from collections.abc import Callable
from inspect import getcallargs
from copy import deepcopy
import inspect

from ._log_interface import rise_warning


def set_attributes(my_object, attributes_dict):
    for key, value in attributes_dict.items():
        if key in my_object.__dict__:
            setattr(my_object, key, value)
        else:
            rise_warning(
                "trying to set a non existing attribute "
                + str(key)
                + " in "
                + str(type(my_object))
            )
    return 0


def check_function_kwargs(func: Callable, kwargs: dict) -> dict:
    """
    check that the keys of a dictionnary are arguments of a function and return an updated dictionnary with only valide keys

    Parameters
    ----------
    func : function
        function to check
    kwargs : dict
        dictionnary of arguments to check

    Returns
    -------
    dict
        updated kwargs dictionnary
    """
    func_kwargs_set = set(func.__code__.co_varnames[: func.__code__.co_argcount])
    kwargs_set = set(kwargs.keys())
    not_valid_kwargs_set = kwargs_set - func_kwargs_set
    for k in not_valid_kwargs_set:
        kwargs.pop(k)
    return kwargs


def function_to_str(func: Callable) -> str:
    lines = inspect.getsource(func)
    return lines


def str_to_function(lines: str) -> Callable:
    lines
    return lines
