"""
NRV-:class:`nrv_function` handling.
"""

from abc import abstractmethod

import numpy as np
from scipy.interpolate import (
    CubicHermiteSpline,
    CubicSpline,
    Akima1DInterpolator,
    PchipInterpolator,
    make_interp_spline,
)
from scipy.special import erf

from ..backend._file_handler import json_dump, json_load
from ..backend._log_interface import rise_warning, rise_error
from ..backend._NRV_Class import NRV_class, is_empty_iterable

#############################
## sigma functions classes ##
#############################
spy_interp1D_kind = {
    "linear": {"f": make_interp_spline, "kwgs": {"k": 1}},
    "akima": {"f": Akima1DInterpolator, "kwgs": {"extrapolate": True}},
    "pchip": {"f": PchipInterpolator, "kwgs": {"extrapolate": True}},
    "slinear": {"f": make_interp_spline, "kwgs": {"k": 1}},
    "quadratic": {"f": make_interp_spline, "kwgs": {"k": 4}},
    "cubic": {"f": CubicSpline, "kwgs": {"extrapolate": True}},
    "previous": {"f": make_interp_spline, "kwgs": {"k": 0}},
}


class nrv_function(NRV_class):
    """
    Class containg all comon method of fonction used in nrv
    """

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.f_type = "nrv_function"
        self.dim = 0

    def __call__(self, *X):
        return self.call_method(*X)

    @staticmethod
    def call_method(self, X):
        return X

    def __compatible(self, b):
        if not callable(b):
            return True
        elif "dim" in self.__dir__() and "dim" in b.__dir__():
            if self.dim == b.dim:
                return True
        else:
            rise_warning("Type not compatible for operation", type(self), type(b))
            return False

    def __neg__(self):
        c = eval(self.f_type)()
        c.call_method = lambda *X: -self(*X)
        return c

    def __abs__(self):
        c = eval(self.f_type)()
        c.call_method = lambda *X: abs(self(*X))
        return c

    def __add__(self, b):
        if self.__compatible(b):
            c = eval(self.f_type)()
            if callable(b):
                c.call_method = lambda *X: self(*X) + b(*X)
            else:
                c.call_method = lambda *X: self(*X) + b
            return c

    def __radd__(self, b):
        if self.__compatible(b):
            c = eval(self.f_type)()
            if callable(b):
                c.call_method = lambda *X: b * (X) + self(*X)
            else:
                c.call_method = lambda *X: b + self(*X)
            return c

    def __sub__(self, b):
        if self.__compatible(b):
            c = eval(self.f_type)()
            if callable(b):
                c.call_method = lambda *X: self(*X) - b(*X)
            else:
                c.call_method = lambda *X: self(*X) - b
            return c

    def __rsub__(self, b):
        if self.__compatible(b):
            c = eval(self.f_type)()
            if callable(b):
                c.call_method = lambda *X: b(*X) - self(*X)
            else:
                c.call_method = lambda *X: b - self(*X)
            return c

    def __mul__(self, b):
        if self.__compatible(b):
            c = eval(self.f_type)()
            if callable(b):
                c.call_method = lambda *X: self(*X) * b(*X)
            else:
                c.call_method = lambda *X: self(*X) * b
            return c

    def __rmul__(self, b):
        if self.__compatible(b):
            c = eval(self.f_type)()
            if callable(b):
                c.call_method = lambda *X: b(*X) * self(*X)
            else:
                c.call_method = lambda *X: b * self(*X)
            return c


###############################################################
####################### 1D functions ##########################
###############################################################


class function_1D(nrv_function):
    """
    class containing function from IR to IR
    Such function can be call either on 1 value or on a ndarray (and applied on each value)
    """

    def __init__(self):
        super().__init__()
        self.f_type = "function_1D"
        self.dim = 1

    # @staticmethod
    def call_method(self, X):
        # Composition with N dim function
        if isinstance(X, nrv_function):
            c_type = "function_" + str(X.dim) + "D"
            c = eval(c_type)()
            c.call_method = lambda *x: self(X(*x))
            return c
        else:
            return None


class gaussian(function_1D):
    r"""
    gaussian function define as:

    .. math::

        f(x) = e^{-\frac{(x-\mu)^2}{2*\sigma^2}}
    """

    def __init__(self, mu=0, sigma=1):
        """ """
        super().__init__()
        self.mu = mu
        self.sigma = sigma

    def call_method(self, X):
        res = super().call_method(X)
        if res is None:
            res = np.exp(
                -(((X - self.mu) / self.sigma) ** 2) / 2
            )  # /(self.sigma*(2*np.pi)**0.5)
        return res


class gate(function_1D):
    def __init__(self, mu=0, sigma=1, kind="Rational", N=None):
        """ """
        super().__init__()
        # self.kind =
        self.mu = mu
        self.sigma = sigma
        self.N = N
        self.kind = kind

    def call_method(self, X):
        res = super().call_method(X)
        if res is None:
            X_eff = (X - self.mu) / self.sigma
            if self.N is None:
                res = (np.sign(X_eff + 0.5) - np.sign(X_eff - 0.5)) / 2
            elif self.kind.lower() == "rational":
                res = 1 / ((2 * X_eff) ** (2 * self.N) + 1)
            else:
                res = (
                    erf((X_eff + (0.5 * self.sigma) / self.mu) / self.N)
                    - erf((X_eff - (0.5 * self.sigma) / self.mu) / self.N)
                ) / 2
        return res


###############################################################
####################### 2D functions ##########################
###############################################################


class function_2D(nrv_function):
    """
    class containing function from IR^2 to IR
    Such function can be call either on 1 value or on a ndarray (and applied on each value)
    """

    def __init__(self):
        super().__init__()
        self.f_type = "function_2D"
        self.dim = 2

    @staticmethod
    def call_method(self, X):
        return 1


class ackley(function_2D):
    """
    Bi-dimensional Ackley function
    """

    def __init__(self):
        super().__init__()

    def call_method(self, x: np.array, y: np.array) -> np.array:
        return (
            -20 * np.exp(-0.2 * np.sqrt(0.5 * (x**2 + y**2)))
            - np.exp(0.5 * (np.cos(2 * np.pi * x) + np.cos(2 * np.pi * y)))
            + np.e
            + 20
        )


class beale(function_2D):
    """
    Bi-dimensional Beale function
    """

    def __init__(self):
        super().__init__()

    def call_method(self, x: np.array, y: np.array) -> np.array:
        return (
            (1.5 - x + x * y) ** 2
            + (2.25 - x + x * y**2) ** 2
            + (2.625 - x + x * y**3) ** 2
        )


class goldstein_price(function_2D):
    """
    Bi-dimensional Goldstein function
    """

    def __init__(self):
        super().__init__()

    def call_method(self, x: np.array, y: np.array) -> np.array:
        return (
            1
            + (x + y + 1) ** 2
            * (19 - 14 * x + 3 * x**2 - 14 * y + 6 * x * y + 3 * y**2)
        ) * (
            30
            + (2 * x - 3 * y) ** 2
            * (18 - 32 * x + 12 * x**2 + 48 * y - 36 * x * y + 27 * y**2)
        )


class booth(function_2D):
    """
    Bi-dimensional Booth function
    """

    def __init__(self):
        super().__init__()

    def call_method(self, x: np.array, y: np.array) -> np.array:
        return (x + 2 * y - 7) ** 2 + (2 * x + y - 5) ** 2


class bukin6(function_2D):
    """
    Bi-dimensional Booth function
    """

    def __init__(self):
        super().__init__()

    def call_method(self, x: np.array, y: np.array) -> np.array:
        return 100 * np.sqrt(np.abs(y - 0.01 * x**2)) + 0.01 * np.abs(x + 10)


###############################################################
####################### ND functions ##########################
###############################################################
class function_ND(nrv_function):
    """
    class containing function from IR^n to IR
    Such function can be call either on 1 value or on a ndarray (and applied on each value)
    """

    def __init__(self):
        super().__init__()
        self.f_type = "function_ND"
        self.dim = "N"

    @staticmethod
    def call_method(self, *X):
        return 1


class Id(function_ND):
    """ """

    def __init__(self):
        super().__init__()

    def call_method(self, *x: np.array) -> np.array:
        if len(x) == 1 and np.iterable(x[0]):
            x = x[0]
        return x


class rosenbock(function_ND):
    """
    Multi-dimensional Rosenbock function
    """

    def __init__(self):
        super().__init__()

    def call_method(self, *x: np.array) -> np.array:
        if len(x) == 1 and np.iterable(x[0]):
            x = x[0]
        result = 0
        for i in range(1, len(x)):
            result += 100 * (x[i] - x[i - 1] ** 2) ** 2 + (1 - x[i - 1]) ** 2
        return result


class rastrigin(function_ND):
    """
    Multi-dimensional Rastrigin function
    """

    def __init__(self):
        super().__init__()

    def call_method(self, *x: np.array) -> np.array:
        if len(x) == 1 and np.iterable(x[0]):
            x = x[0]
        A = 10.0
        n = len(x)
        result = A * n
        for xi in x:
            result += xi**2 - A * np.cos(2 * np.pi * xi)
        return result


class sphere(function_ND):
    """
    Multi-dimensional Sphere function
    """

    def __init__(self, Xc=None):
        super().__init__()
        self.Xc = Xc
        if self.Xc is None:
            self.Xc = []

    def call_method(self, *X):
        if len(X) == 1 and np.iterable(X[0]):
            X = X[0]
        Nc = len(self.Xc)
        res = 0
        for i, xi in enumerate(X):
            if i < Nc:
                xc = self.Xc[i]
            else:
                xc = 0
            res += (xi - xc) ** 2
        return res**0.5


###########################################################
####################  cost_evaluation  #####################
###########################################################
class cost_evaluation(nrv_function):
    def __init__(self):
        super().__init__()
        self.f_type = "cost_evaluation"

    @staticmethod
    def call_method(self, static_sim) -> float:
        return 1

    def __call__(self, results, **kwargs) -> float:
        return self.call_method(results)


###############################################################
####################### interpolation ######################
###############################################################
class nrv_interp(nrv_function):
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
        kind of interpolation which should be used, by default "linear" possible values:
            - scipy interp1d kinds (see nrv.spy_interp1D_kind)
            - {'hermite', 'cardinal', 'catmull-rom'} for respective
              cubic spline interpollation
    dx
        if minimal distance between 2 consecutive points, by default 0.01 interpolator
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

    def __init__(
        self,
        X_values,
        Y_values,
        kind="linear",
        dx=0.01,
        interpolator=None,
        dxdy=None,
        scale=None,
        columns=[],
    ):
        super().__init__()
        self.f_type = "nrv_interp"
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
        """ """
        S = self.X_values.argsort()
        self.X_values = self.X_values[S]
        self.Y_values = self.Y_values[S]
        if dx is not None:
            self.dx = dx
        for i, x in enumerate(self.X_values):
            if i > 0:
                while x < self.X_values[i - 1]:
                    x += dx
                self.X_values[i] = x

    def update_interpolator(self, kind=None, interpolator=None, dxdy=None, scale=None):
        """ """
        if kind is not None:
            self.kind = kind
        if interpolator is not None:
            self.interpolator = interpolator
        elif self.kind.lower() in spy_interp1D_kind:
            __interp_type = spy_interp1D_kind[self.kind.lower()]["f"]
            __kwgs = spy_interp1D_kind[self.kind.lower()]["kwgs"]
            self.interpolator = __interp_type(self.X_values, self.Y_values, **__kwgs)
        elif self.kind.lower() in ["hermite", "cardinal", "catmull-rom"]:
            if self.scale is None or self.kind == "catmull-rom":
                self.scale = 0.5
            if self.dxdy is None:
                self.dxdy = np.array(
                    [
                        (self.Y_values[1] - self.Y_values[0]) / self.X_values[1]
                        - self.X_values[0]
                    ]
                    + [
                        (self.Y_values[k + 2] - self.Y_values[k])
                        / (self.X_values[k + 2] - self.X_values[k])
                        for k in range(self.N_pts - 2)
                    ]
                    + [
                        (self.Y_values[-1] - self.Y_values[-2])
                        / (self.X_values[-1] - self.X_values[-2])
                    ]
                )
            if self.kind.lower() == "hermite" and dxdy is not None:
                self.dxdy = dxdy
                self.scale = 1
            if self.kind.lower() == "cardinal" and scale is not None:
                self.scale = scale

            self.interpolator = CubicHermiteSpline(
                self.X_values, self.Y_values, self.scale * self.dxdy
            )

    # Mathematical operations
    def __add__(self, b):
        if isinstance(b, nrv_interp):
            if np.allclose(b.X_values, self.X_values):
                Y = b.Y_values + self.Y_values
                # TO ADD: computation of dxdy when both are set
            else:
                rise_error(
                    "Not implemented: operations of nrv_iterp with different X_scale"
                )
        else:
            Y = self.Y_values + b
        return nrv_interp(
            X_values=self.X_values,
            Y_values=Y,
            interpolator=self.interpolator,
            kind=self.kind,
            dx=self.dx,
            dxdy=None,
            scale=self.scale,
            columns=self.columns,
        )

    def __mul__(self, b):
        if isinstance(b, nrv_interp):
            if np.allclose(b.X_values, self.X_values):
                Y = self.Y_values * b.Y_values
                # TO ADD: computation of dxdy when both are set
            else:
                rise_error(
                    "Not implemented: operations of nrv_iterp with different X_scale"
                )
        else:
            Y = self.Y_values * b
        return nrv_interp(
            X_values=self.X_values,
            Y_values=Y,
            interpolator=self.interpolator,
            kind=self.kind,
            dx=self.dx,
            dxdy=None,
            scale=self.scale,
            columns=self.columns,
        )

    def __truediv__(self, b):
        if isinstance(b, nrv_interp):
            if np.allclose(b.X_values, self.X_values):
                if np.isclose(b.Y_values, 0).any():
                    rise_error(ZeroDivisionError, "float division by zero in Python")
                Y = self.Y_values / b.Y_values
                # TO ADD: computation of dxdy when both are set
            else:
                rise_error(
                    NotImplementedError,
                    "operations of nrv_iterp with different X_scale",
                )
        else:
            Y = self.Y_values / b
        return nrv_interp(
            X_values=self.X_values,
            Y_values=Y,
            interpolator=self.interpolator,
            kind=self.kind,
            dx=self.dx,
            dxdy=None,
            scale=self.scale,
            columns=self.columns,
        )

    def __rtruediv__(self, b):
        if np.isclose(self.Y_values, 0).any():
            rise_error(ZeroDivisionError, " float division by zero in Python")
        if isinstance(b, nrv_interp):
            if np.allclose(b.X_values, self.X_values):
                Y = b.Y_values / self.Y_values
                # TO ADD: computation of dxdy when both are set
            else:
                rise_error(
                    NotImplementedError,
                    "operations of nrv_iterp with different X_scale",
                )
        else:
            Y = b / self.Y_values
        return nrv_interp(
            X_values=self.X_values,
            Y_values=Y,
            interpolator=self.interpolator,
            kind=self.kind,
            dx=self.dx,
            dxdy=self.dxdy,
            scale=self.scale,
            columns=self.columns,
        )

    def __radd__(self, b):
        return self.__add__(b)

    def __rmul__(self, b):
        return self.__mul__(b)

    def __sub__(self, b):
        return self.__add__(-b)

    def __rsub__(self, b):
        return self.__sub__(b)

    def __call__(self, X):
        if is_empty_iterable(self.columns):
            return self.interpolator(X)
        try:
            return self.interpolator(X[self.columns])
        except:
            rise_warning(
                "nrv_interpol: columns out of bound, intepolation done on the whole vector"
            )
            return self.interpolator(X)


class MeshCallBack(nrv_function):
    """ """

    def __init__(self, f=None, axis="x"):
        super().__init__()
        self.f_type = "MeshCallBack"
        self.f = None
        self.axis = axis

        self.set_function(f)

    def set_function(self, f=None):
        if f is None:
            self.f = lambda *x: 1
        elif callable(f):
            self.f = f
        elif isinstance(f, str):
            self.f = lambda x: eval(f)
        else:
            rise_warning(type(f), "Not recognized for MeshCallBack function")

    def __call__(self, dim, tag, x, y, z, lc):
        X = []
        if "x" in self.axis:
            X += [x]
        if "y" in self.axis:
            X += [y]
        if "z" in self.axis:
            X += [z]
        return lc * self.f(*X)
