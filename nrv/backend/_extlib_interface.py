"""
Module containing functions to ease and addapt the interface with external libraries
"""

import numpy as np
from pandas import DataFrame
from typing import Literal

# ---------------------------------- #
#       Numpy compatibility          #
# ---------------------------------- #


def is_empty_iterable(x):
    """
    check if the object x is an empty iterable

    Parameters
    ----------
    x : any
        object to check.

    Returns
    -------
    bool
    """
    if not np.iterable(x):
        return False
    if len(x) == 0:
        return True
    return False


def set_idxs(_i: np.ndarray | int | tuple | None, _n: int | None) -> np.ndarray:
    """
    convert an object _i into an 1D array of index

    Parameters
    ----------
    _i : np.ndarray | int | tuple | None
        Indexes considered, can be either:
         - None (default): all indexes from 0 to ``_n-1``
         - int: single indexe corresponding to _i
         - tuple: all indexes between _i[0] and _i[1]
    _n : int | None
        _description_

    Returns
    -------
    np.ndarray
    """
    if _i is None and _n is not None:
        _i = np.arange(_n)
    elif not np.iterable(_i):
        _i = np.array([_i])
    elif isinstance(_i, tuple) and len(_i) == 2:
        _i = np.arange(*_i)
    elif isinstance(_i, list):
        _i = np.array(_i)
    if isinstance(_i, np.ndarray) and _n is not None:
        _i = _i[_i < _n]
    return _i


# ---------------------------------- #
#       Pandas compatibility         #
# ---------------------------------- #
def get_query(*args, **kwgs):
    """
    Combine a list of kwargs into a `str` compatible with pandas.DataFrame.query

    """
    queries = []
    for expr in args:
        if isinstance(expr, str):
            queries += [expr]
    for i_lab, i_val in kwgs.items():
        if i_val is not None:
            if isinstance(i_val, str):
                queries += [i_val]
            elif isinstance(i_val, dict):
                queries += [get_query(**i_val)]
            else:
                queries += [f"{i_lab}.isin({set_idxs(i_val, None).tolist()})"]
    if len(queries) == 0:
        return None

    queries = " and ".join(queries)
    return queries


def df_to(
    df: DataFrame, otype: None | Literal["numpy", "list"], *args, **kwgs
) -> object:
    """
    convert a :class:`pandas.DataFrame` to another type.

    Note
    ----
    This function if a generalisation of all  `pandas.DataFrame` methods `to_...`. In other words, if otype is not None, this function returns: `f"df.to_{otype}(*args, **kwgs)"`

    Parameters
    ----------
    df : DataFrame
        :class:`pandas.DataFrame` to convert.
    otype : None | Literal[&quot;numpy&quot;, &quot;list&quot;]
        If None, return as a panda, convert into the corresponding class.

    Returns
    -------
    _type_
        _description_
    """
    if otype is None:
        return df
    else:
        to_any = eval(f"df.to_{otype}")
        return to_any(*args, **kwgs)
