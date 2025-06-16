from typing import List, Tuple, Type
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame

from ...backend._NRV_Class import NRV_class, abstractmethod
from ._cshape import CShape

class BShape(NRV_class):
    """
    Abstract base class for bumble-shaped geometries gathering sub-shapes.
    """
    @abstractmethod
    def __init__(self):
        """
        Initializes the CShape with a specified number of points for angular resolution.

        
        Parameters
        ----------
        """
        super().__init__()
        self.geom:None|Type[CShape] = None
        self._pop:None|DataFrame = None


        # Shape Status
        #:bool: 
        
    @property
    def has_geom(self)->bool:
        """
        Shape Status: True if the instance has a geometry

        Returns
        -------
        bool
        """
        return self.geom is not None
    
    @property
    def has_pop(self)->bool:
        """
        Population Status: True if the instance has an population

        Returns
        -------
        bool
        """
        
        return self._pop is not None
    
    @property
    def has_placed_pop(self)->bool:
        """
        Placed Population Status: True if the instance has an population with fixed position for each member

        Returns
        -------
        bool
        """
        if not self.has_pop:
            return False
        keys_to_have = {"y", "z", "is_placed"} - set(self._pop.keys())
        if not len(keys_to_have): 
            return self._pop["is_placed"].sum()
        return False
    
    def __len__(self)->int:
        if not self.has_pop:
            return 0
        return len(self._pop)

    def set_geometry(self, **kwgs):
        pass

    def clear_geometry(self):
        self.geom = None


    def create_population(self, **kwgs):
        pass

    def clear_population(self):
        self._pop = None

    def clear_population_placement(self):
        if self.has_placed_pop:
            self._pop["y"] = 0
            self._pop["z"] = 0
            self._pop["is_placed"] = False


    def place_population(self, **kwgs):
        pass


    def plot(self, ax:plt.Axes, **kwgs):
        """
        Plot the population and its geometry :class:`matplotlib.pyplot.Axes`

        Parameters
        ----------
        ax : plt.Axes
            axes where population should be ploted
        """
        pass