"""
NRV-nrv_function
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""

from scipy.interpolate import interp1d, CubicHermiteSpline
import numpy as np

from ..backend.log_interface import rise_error, rise_warning, pass_info
from ..backend.file_handler import json_dump, json_load
#############################
## sigma functions classes ##
#############################
spy_interp1D_kind = ['linear', 'nearest', 'nearest-up', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next']

class nrv_function:
    """
    Class containg all comon method of fonction used in nrv
    """
    def __init__(self):
        self.type = 'nrv_function'
    
    def __call__(self, *arg):
        return 1
    
    def save_field_function(self, save=False, fname='nrv_function.json'):
        """
        Return feild function as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default 'nrv_function.json'

        Returns
        -------
        mat_dic : dict
            dictionary containing all information
        """
        ff_dic = {}
        ff_dic['type'] = self.type
        if save:
            json_dump(ff_dic, fname)
        return ff_dic

    def load_field_function(self, data):
        """
        Load function properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing function information
        """
        if type(data) == str:
            ff_dic = json_load(data)
        else: 
            ff_dic = data
        self.type = ff_dic['type']

class nrv_interp(nrv_function):
    def __init__(self, X_values, Y_values, kind="linear", dx=0.01, interpolator=None, dxdy=None,\
        scale=None, columns=[]):
        """
        Interpolator based on scipy.interpolate
        Parameters
        ----------
        X_values    : (N,) array_like
            A 1-D array of real values
        Y_values    :(…,N,…) array_like
            A N-D array of real values. The length of y along the interpolation 
            axis must be equal to the length of x.
        kind        : str
            kind of interpolation which should be used, by default "linear"
            possible values:    - scipy interp1d kinds (see nrv.spy_interp1D_kind)
                                - {'hermite', 'cardinal', 'catmull-rom'} for respective 
                                  cubic spline interpollation
        dx
            if minimal distance between 2 consecutive points, by default 0.01
        interpolator
            custumize intepolation function if None kind is use to set the interpolator,
            by default None
        dxdy
            if kind is 'hermite', derivative vector (see scipy.interpolate.CubicHermiteSpline),
            by default None
        scale
            if kind is 'cardinal', scale to use for derivative vector, by default None
        columns       : int or array_like
            columns on which apply the interpolation when class called
            if [] iterpolation done on the whole vector,by default []

        Returns
        -------
        output  :  tuple(3)
            (domain, cell_tag, facet_tag)
        """
        super().__init__()
        self.type = "interp"
        # General parameters
        self.X_values = X_values
        self.Y_values = Y_values
        self.N_pts = len(Y_values)
        self.interpolator = interpolator
        self.kind = kind
        self.dx = dx

        # CubicHermiteSpline parameters
        self.dxdy = dxdy

        # Cardinal Spline parameters
        self.scale = scale

        self.columns = columns
        self.__set_interp()


    def __set_interp(self):
        """
        Internal use only, set interpolator
        """
        self.N_pts = len(self.X_values)
        self.__check_X_values()
        self.update_interpolator()

    def __check_X_values(self, dx=None):
        """

        """
        S = self.X_values.argsort()
        self.X_values = self.X_values[S]
        self.Y_values = self.Y_values[S]
        if dx is not None:
            self.dx = dx
        for i, x in enumerate(self.X_values):
            if i >0:
                while x<self.X_values[i-1]:
                    x += dx
                self.X_values[i] = x

    def update_interpolator(self, kind=None, interpolator=None, dxdy=None, scale=None):
        """
        
        """
        if kind is not None:
            self.kind = kind

        if interpolator is not None:
            self.interpolator = interpolator
        elif self.kind.lower() in spy_interp1D_kind:
            self.interpolator = interp1d(self.X_values, self.Y_values, kind=self.kind, fill_value="extrapolate")
        elif self.kind.lower() in ['hermite', 'cardinal', 'catmull-rom']:
            if self.scale is None or self.kind == 'catmull-rom':
                self.scale = 0.5
            if self.dxdy is None:
                self.dxdy = np.array([(self.Y_values[1]-self.Y_values[0])/self.X_values[1]-self.X_values[0]]\
                        + [(self.Y_values[k+2]-self.Y_values[k])/(self.X_values[k+2]-self.X_values[k]) for k in range(self.N_pts-2)]\
                        + [(self.Y_values[-1]-self.Y_values[-2])/(self.X_values[-1]-self.X_values[-2])])
            if self.kind.lower() == 'hermite' and dxdy is not None:
                self.dxdy = dxdy
                self.scale = 1
            if self.kind.lower() == 'cardinal' and scale is not None:
                self.scale = scale
                    
            self.interpolator = CubicHermiteSpline(self.X_values, self.Y_values, self.scale*self.dxdy)

        
    def __call__(self, X):
        if self.columns == []:
            return self.interpolator(X)
        try:
            return self.interpolator(X[self.columns])
        except:
            rise_warning('nrv_interpol: columns out of bound, intepolation done on the whole vector')
            return self.interpolator(X)
    




