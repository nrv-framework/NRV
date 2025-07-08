"""
NRV-:class:`.recorder` handling.
"""

import faulthandler

import numpy as np
import matplotlib.pyplot as plt

from ..backend._log_interface import rise_error, rise_warning
from ..backend._NRV_Class import NRV_class, is_empty_iterable
from ..utils._units import cm, m
from ..utils._misc import rotate_2D
from ._materials import load_material

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()

MRG_fiberD = np.asarray([1, 2, 5.7, 7.3, 8.7, 10.0, 11.5, 12.8, 14.0, 15.0, 16.0])
MRG_nodeD = np.asarray([0.7, 1.4, 1.9, 2.4, 2.8, 3.3, 3.7, 4.2, 4.7, 5.0, 5.5])


def is_recording_point(point):
    """
    Check if the specified object is a recording point
    """
    return isinstance(point, recording_point)


def is_recorder(rec):
    """
    Check if the specified object is a recorder
    """
    return isinstance(rec, recorder)


def NodeD_interpol(diameter):
    """
    Compute the MRG Node diameters

    Parameters
    ----------
    diameter    : float
        diameter of the unmylinated axon to implement, in um
    Returns
    -------
    nodeD       : float
    """
    if diameter in MRG_fiberD:
        index = np.where(MRG_fiberD == diameter)[0]
        nodeD = MRG_nodeD[index]
    else:
        # create fiting polynomyals
        nodeD_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_nodeD, 3))
        nodeD = nodeD_poly(diameter)
    return float(nodeD)


class recording_point(NRV_class):
    """
    Object equivalent to a point source electrode for extracellular potential recording only (No stimulation)
    """

    def __init__(self, x=0, y=0, z=0, ID=0, method="PSA"):
        """
        Instantiation of a recording point.

        Parameters
        ----------
        x       : float
            x position of the recording point, in um
        y       : float
            y position of the recording point, in um
        z       : float
            z position of the recording point, in um
        ID      : int
            electrode identification number, set to 0 by default
        method  : string
            electrical potential approximation method, can be "PSA" (Point Source Approximation)
            or "LSA" (Line Source Approximation).
            set to "PSA" by default. Note that if LSA is requested with an anisotropic material, computation
            will automatically be performed using "PSA"
        """
        super().__init__()
        self.type = "recording_point"
        # properties
        self.ID = ID
        self.x = x
        self.y = y
        self.z = z
        self.method = method
        # footprints
        self.footprints = (
            {}
        )  # footprints are stored for each axon with the key beeing the axon's ID
        self.init = False
        self.recording = None

    def save_recording_point(self, save=False, fname="recording_point.json"):
        rise_warning("save_recording_point is a deprecated method use save")
        self.save(save=save, fname=fname)

    def load_recording_point(self, data="recording_point.json"):
        rise_warning("load_recording_point is a deprecated method use load")
        self.load(data=data)

    def translate(self, x=None, y=None, z=None):
        """
        Move recording point by translation

        Parameters
        ----------
        x   : float
            x axis value for the translation in um
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        """
        if x is not None:
            self.x += x
        if y is not None:
            self.y += y
        if z is not None:
            self.z += z

    def rotate(
        self, angle: float, center: tuple[float, float] = (0, 0), degree: bool = False
    ):
        """
        rotate recording point around x-axis

        Parameters
        ----------
        angle : float
            Rotation angle
        center : bool, optional
            Center of the rotation, by default (0,0)
        degree : bool, optional
            if True `angle` is in degree, if False in radian, by default False
        """
        self.y, self.z = rotate_2D(
            point=(self.y, self.z), angle=angle, degree=degree, center=center
        )

    def get_ID(self):
        """
        get the ID of a recording point

        Returns
        -------
        id : int
            ID number of the recording point
        """
        return self.ID

    def get_method(self):
        """
        get the method for a recording point

        Returns
        -------
        method : str
            name of the method, either "PSA" for point source approximation or "LSA" for line Source Approximation
        """
        return self.method

    def set_method(self, method):
        """
        Set the approximation to compute the extracellular potential

        Parameters
        ----------
        method : str
            name of the method, either "PSA" for point source approximation or "LSA" for line Source Approximation
        """
        self.method = method

    def compute_PSA_isotropic_footprint(
        self,
        x_axon,
        y_axon,
        z_axon,
        d,
        ID,
        sigma,
        myelinated=False,
    ):
        """
        Compute the footprint for Point Source approximation an isotropic material

        Parameters
        ----------
        x_axon  : array
            array of the positions of the axon along the x-axis at which there is a current source, in [um]
        y_axon  : float
            y-axis position of the axon, in [um]
        z-axon  : float
            z-axis position of the axon, in [um]
        d       : float
            diameter of the axon, in [um]
        ID      : int
            axon ID number
        sigma   : float
            conductivity of the isotropic extracellular material, in [S.m]
        """
        if myelinated:
            d = NodeD_interpol(d)
            surface = np.pi * (d / cm) * (1 / cm)
        else:
            surface = np.pi * (d / cm) * (np.gradient(x_axon) / cm)
        electrical_distance = (
            4
            * np.pi
            * sigma
            * (
                ((self.x - x_axon) / m) ** 2
                + ((self.y - y_axon) / m) ** 2
                + ((self.z - z_axon) / m) ** 2
            )
            ** 0.5
        )
        self.footprints[str(ID)] = np.divide(surface, electrical_distance)

    def compute_PSA_anisotropic_footprint(
        self,
        x_axon,
        y_axon,
        z_axon,
        d,
        ID,
        sigma_xx,
        sigma_yy,
        sigma_zz,
        myelinated=False,
    ):
        """
        Compute the footprint for Point Source approximation an anisotropic material

        Parameters
        ----------
        x_axon      : array
            array of the positions of the axon along the x-axis at which there is a current source, in [um]
        y_axon      : float
            y-axis position of the axon, in [um]
        z-axon      : float
            z-axis position of the axon, in [um]
        d           : float
            diameter of the axon, in [um]
        ID          : int
            axon ID number
        sigma_xx    : float
            conductivity of the isotropic extracellular material alog the x-axis, in [S.m]
        sigma_yy    : float
            conductivity of the isotropic extracellular material alog the y-axis, in [S.m]
        sigma_zz    : float
            conductivity of the isotropic extracellular material alog the z-axis, in [S.m]
        """
        if myelinated:
            d = NodeD_interpol(d)
            surface = np.pi * (d / cm) * (1 / cm)
            d_internode = np.gradient(x_axon)
        else:
            surface = surface = np.pi * (d / cm) * (np.gradient(x_axon) / cm)
            d_internode = np.gradient(x_axon)

        #!! Modified tc 12/12/24 added **0.5
        sx = (sigma_yy * sigma_zz) ** 0.5
        sy = (sigma_xx * sigma_zz) ** 0.5
        sz = (sigma_xx * sigma_yy) ** 0.5

        electrical_distance = (
            4
            * np.pi
            * (
                (sx * (self.x - x_axon) / m) ** 2
                + (sy * (self.y - y_axon) / m) ** 2
                + (sz * (self.z - z_axon) / m) ** 2
            )
            ** 0.5
        )
        self.footprints[str(ID)] = np.divide(surface, electrical_distance)

    def compute_LSA_isotropic_footprint(
        self,
        x_axon,
        y_axon,
        z_axon,
        d,
        ID,
        sigma,
        myelinated=False,
    ):
        """
        Compute the footprint for Linear Source approximation an isotropic material

        Parameters
        ----------
        x_axon  : array
            array of the positions of the axon along the x-axis at which there is a current source, in [um]
        y_axon  : float
            y-axis position of the axon, in [um]
        z-axon  : float
            z-axis position of the axon, in [um]
        d       : float
            diameter of the axon, in [um]
        ID      : int
            axon ID number
        sigma   : float
            conductivity of the isotropic extracellular material, in [S.m]
        """
        if myelinated:
            d = NodeD_interpol(d)
            surface = np.pi * (d / cm) * (1 / cm)
            d_internode = np.gradient(x_axon)
        else:
            surface = surface = np.pi * (d / cm) * (np.gradient(x_axon) / cm)
            d_internode = np.gradient(x_axon)

        dist = (((self.x - x_axon) / m) ** 2 + ((self.y - y_axon) / m) ** 2) ** 0.5
        electrical_distance = (4 * np.pi * (d_internode / m) * sigma) / np.log(
            abs(
                (dist - (self.x - x_axon) / m)
                / (
                    (
                        (
                            (d_internode + (self.x - x_axon)) ** 2
                            + (self.y - y_axon) ** 2
                        )
                        ** 0.5
                    )
                    / m
                    - (d_internode + (self.x - x_axon)) / m
                )
            )
        )
        self.footprints[str(ID)] = np.divide(surface, electrical_distance)

    def init_recording(self, N_points):
        """
        Initializes the recorded extracellular potential. if a recording already exists,
        nothing is performed (usefull at the multi-axons level for instance)

        Parameters
        ----------
        N_points : int
            length of the extracellular potential vector along temporal dimension
        """
        if not self.init:
            self.recording = np.zeros(N_points)
            self.init = True
        else:
            if len(self.recording) != N_points:
                rise_error(
                    "Trying to compute an extracellular potential of a wrong temporal size"
                )

    def reset_recording(self, N_points):
        """
        Sets the recorded extracellular potential to zero whatever the conditions

        Parameters
        ----------
        N_points : int
            length of the extracellular potential vector along temporal dimension
        """
        self.recording = np.zeros(N_points)

    def add_axon_contribution(self, I_membrane, ID):
        """
        Adds the and axon extracellular potential to the recording computed as the matrix product of
        I_membrane computed from neuron with the footprint computed below and stored in the object
        for a specific axons ID.

        Parameters
        ----------
        I_membrane  : array
            membrane current as a matrix over times (columns) and position (lines)
            in mA/cm2
        ID          : int
            axon ID as footprint are stored in a dictionnary with their ID as key
        """
        self.recording += np.matmul(np.transpose(I_membrane), self.footprints[str(ID)])


class recorder(NRV_class):
    """
    Object for recording extracellular potential of axons.
    """

    def __init__(self, material=None):
        """
        Instantiation of an extracellular potential recording mechanism. A mecanism can store recording points,
        be associated with a material and properties. The mechanism will perform the extracellular potential
        computation at each point for an axon when a simulation is performed.
        """
        super().__init__()
        self.type = "recorder"
        self.material = None
        self.is_isotropic = True
        self.t = None
        self.t_init = False
        # if no material specified, sigma is 1S/m, else everything is loaded from signal
        if material == None:
            self.sigma = 1
            self.isotropic = True
            self.material = None
            self.sigma_xx = None
            self.sigma_yy = None
            self.sigma_zz = None
        else:
            self.material = material
            temporary_material = load_material(self.material)
            if temporary_material.is_isotropic():
                self.isotropic = True
                self.sigma = temporary_material.sigma
                self.sigma_xx = None
                self.sigma_yy = None
                self.sigma_zz = None
            else:
                self.isotropic = False
                self.sigma = None
                self.sigma_xx = temporary_material.sigma_xx
                self.sigma_yy = temporary_material.sigma_yy
                self.sigma_zz = temporary_material.sigma_zz
        # for internal use
        self.recording_points: list[recording_point] = []

    def save_recorder(self, save=False, fname="recorder.json"):
        rise_warning("save_recorder is a deprecated method use save")
        self.save(save=save, fname=fname)

    def load_recorder(self, data="recorder.json"):
        rise_warning("load_recorder is a deprecated method use load")
        self.load(data=data)

    def is_empty(self):
        """
        check if a recorder has no recording points (empty) or not.

        Returns
        -------
        """
        return is_empty_iterable(self.recording_points)

    def translate(self, x=None, y=None, z=None):
        """
        Move recorder rec points by group translation

        Parameters
        ----------
        x   : float
            x axis value for the translation in um
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        """
        for rec_p in self.recording_points:
            rec_p.translate(x=x, y=y, z=z)

    def rotate(
        self, angle: float, center: tuple[float, float] = (0, 0), degree: bool = False
    ):
        """
        Rotate rec points by group rotation around x-axis

        Parameters
        ----------
        angle : float
            Rotation angle
        center : bool, optional
            Center of the rotation, by default (0,0)
        degree : bool, optional
            if True `angle` is in degree, if False in radian, by default False
        """
        for rec_p in self.recording_points:
            rec_p.rotate(angle=angle, center=center, degree=degree)

    def set_time(self, t_vector):
        """
        set the time vector of a recorder

        t_vector : array
            array of recording times, in ms
        """
        if not self.t_init:
            self.t = t_vector
            self.t_init = True

    def add_recording_point(self, point):
        """
        add an object of type recording_point to the list of recording points.

        Parameters
        ----------
        point : recording_point
            recording point to add to the recording points list
        """
        if is_recording_point(point):
            self.recording_points.append(point)

    def set_recording_point(self, x, y, z, method="PSA"):
        """
        Set a recording point at a given location and add to the recording points list

        Parameters
        ----------
        x       : float
            x position of the recording point, in um
        y       : float
            y position of the recording point, in um
        z       : float
            z position of the recording point, in um
        Parameters
        method  : string
            electrical potential approximation method, can be "PSA" (Point Source Approximation)
            or "LSA" (Line Source Approximation).
            set to "PSA" by default. Note that if LSA is requested with an anisotropic material,
            computation
            will automatically be performed using "PSA"
        """
        if self.is_empty():
            new_point = recording_point(x, y, z, method=method)
        else:
            lowest_ID = self.recording_points[-1].get_ID()
            new_point = recording_point(x, y, z, ID=lowest_ID + 1, method=method)
        self.add_recording_point(new_point)

    def set_recording_zplane(
        self, x_min, x_max, y_min, y_max, z, dx=10, dy=10, method="PSA"
    ):
        """
        Generate equaly spaced recording points in the z plane

        Parameters
        ----------
        x_min   : float
            minimal x postion for recording points, in um
        x_max   : float
            maximal x postion for recording points, in um
        y_min   : float
            minimal y postion for recording points, in um
        y_max   : float
            maximal y postion for recording points, in um
        z       : float
            fixed z position for recording points
        dx      : float
            distance between recording points on the x coordinate, in um
        dy      : float
            distance between recording points on the y coordinate, in um
        method  : string
            electrical potential approximation method, can be "PSA" (Point Source Approximation)
            or "LSA" (Line Source Approximation).
            set to "PSA" by default. Note that if LSA is requested with an anisotropic material,
            computation
            will automatically be performed using "PSA"
        """
        if np.abs(x_max - x_min) < dx:
            dx = np.abs(x_max - x_min) / 10
            rise_warning("dx too large, changed automatically to " + str(dx) + " um")
        if np.abs(y_max - y_min) < dy:
            dy = np.abs(y_max - y_min) / 10
            rise_warning("dy too large, changed automatically to " + str(dy) + " um")
        x_positions = np.arange(x_min, x_max, dx)
        y_positions = np.arange(y_min, y_max, dy)
        for x in x_positions:
            for y in y_positions:
                self.set_recording_point(x, y, z, method=method)

    def set_recording_yplane(
        self, x_min, x_max, y, z_min, z_max, dx=10, dz=10, method="PSA"
    ):
        """
        Generate equaly spaced recording points in the y plane

        Parameters
        ----------
        x_min   : float
            minimal x postion for recording points, in um
        x_max   : float
            maximal x postion for recording points, in um
        y       : float
            fixed y position for recording points
        z_min   : float
            minimal z postion for recording points, in um
        z_max   : float
            maximal z postion for recording points, in um
        dx      : float
            distance between recording points on the x coordinate, in um
        dz      : float
            distance between recording points on the z coordinate, in um
        method  : string
            electrical potential approximation method, can be "PSA" (Point Source Approximation)
            or "LSA" (Line Source Approximation). set to "PSA" by default.
            Note that if LSA is requested with an anisotropic material,computation
            will automatically be performed using "PSA"
        """
        if np.abs(x_max - x_min) < dx:
            dx = np.abs(x_max - x_min) / 10
            rise_warning("dx too large, changed automatically to " + str(dx) + " um")
        if np.abs(z_max - z_min) < dz:
            dz = np.abs(z_max - z_min) / 10
            rise_warning("dz too large, changed automatically to " + str(dz) + " um")
        x_positions = np.arange(x_min, x_max, dx)
        z_positions = np.arange(z_min, z_max, dz)
        for x in x_positions:
            for z in z_positions:
                self.set_recording_point(x, y, z, method=method)

    def set_recording_volume(
        self,
        x_min,
        x_max,
        y_min,
        y_max,
        z_min,
        z_max,
        dx=10,
        dy=10,
        dz=10,
        method="PSA",
    ):
        """
        Generate equaly spaced recording points in the y plane

        Parameters
        ----------
        x_min   : float
            minimal x postion for recording points, in um
        x_max   : float
            maximal x postion for recording points, in um
        y_min   : float
            minimal y postion for recording points, in um
        y_max   : float
            maximal y postion for recording points, in um
        z_min   : float
            minimal z postion for recording points, in um
        z_max   : float
            maximal z postion for recording points, in um
        dx      : float
            distance between recording points on the x coordinate, in um
        dy      : float
            distance between recording points on the y coordinate, in um
        dz      : float
            distance between recording points on the z coordinate, in um
        method  : string
            electrical potential approximation method, can be "PSA" (Point Source Approximation)
            or "LSA" (Line Source Approximation).
            set to "PSA" by default. Note that if LSA is requested with an anisotropic material, computation
            will automatically be performed using "PSA"
        """
        if np.abs(x_max - x_min) < dx:
            dx = np.abs(x_max - x_min) / 10
            rise_warning("dx too large, changed automatically to " + str(dx) + " um")
        if np.abs(y_max - y_min) < dy:
            dy = np.abs(y_max - y_min) / 10
            rise_warning("dy too large, changed automatically to " + str(dy) + " um")
        if np.abs(z_max - z_min) < dz:
            dz = np.abs(z_max - z_min) / 10
            rise_warning("dz too large, changed automatically to " + str(dz) + " um")
        x_positions = np.arange(x_min, x_max, dx)
        y_positions = np.arange(y_min, y_max, dy)
        z_positions = np.arange(z_min, z_max, dz)
        for x in x_positions:
            for y in y_positions:
                for z in z_positions:
                    self.set_recording_point(x, y, z, method=method)

    def compute_footprints(self, x_axon, y_axon, z_axon, d, ID, myelinated=False):
        """
        compute all footprints for a given axon on all recording points of the recorder

        Parameters
        ----------
        x_axon      : array
            array of the positions of the axon along the x-axis at which there is a current source, in [um]
        y_axon      : float
            y-axis position of the axon, in [um]
        z-axon      : float
            z-axis position of the axon, in [um]
        d           : float
            diameter of the axon, in [um]
        ID          : int
            axon ID number
        """
        if not self.is_empty():
            for point in self.recording_points:
                if myelinated:
                    if point.method == "PSA":
                        if self.isotropic:
                            point.compute_PSA_isotropic_footprint(
                                x_axon,
                                y_axon,
                                z_axon,
                                d,
                                ID,
                                self.sigma,
                                True,
                            )
                        else:
                            point.compute_PSA_anisotropic_footprint(
                                x_axon,
                                y_axon,
                                z_axon,
                                d,
                                ID,
                                self.sigma_xx,
                                self.sigma_yy,
                                self.sigma_zz,
                                True,
                            )
                    if point.method == "LSA":
                        if self.isotropic:
                            point.compute_LSA_isotropic_footprint(
                                x_axon,
                                y_axon,
                                z_axon,
                                d,
                                ID,
                                self.sigma,
                                True,
                            )
                        else:
                            rise_warning(
                                "LSA not implemented for anisotropic material return isotropic by default"
                            )
                            point.compute_LSA_isotropic_footprint(
                                x_axon, y_axon, z_axon, d, ID, self.sigma
                            )
                else:
                    surface = np.pi * (d / cm) * (np.gradient(x_axon) / cm)
                    if point.method == "PSA":
                        if self.isotropic:
                            point.compute_PSA_isotropic_footprint(
                                x_axon,
                                y_axon,
                                z_axon,
                                d,
                                ID,
                                self.sigma,
                            )
                        else:
                            point.compute_PSA_anisotropic_footprint(
                                x_axon,
                                y_axon,
                                z_axon,
                                d,
                                ID,
                                self.sigma_xx,
                                self.sigma_yy,
                                self.sigma_zz,
                            )
                    if point.method == "LSA":
                        if self.isotropic:
                            point.compute_LSA_isotropic_footprint(
                                x_axon, y_axon, z_axon, d, ID, self.sigma
                            )
                        else:
                            rise_warning(
                                "LSA not implemented for anisotropic material return isotropic by default"
                            )
                            point.compute_LSA_isotropic_footprint(
                                x_axon, y_axon, z_axon, d, ID, self.sigma
                            )

    def init_recordings(self, N_points):
        """
        Initializes the recorded extracellular potential for all recodgin points.
        If a potential already exists,nothing will be performed

        Parameters
        ----------
        N_points : int
            length of the extracellular potential vector along temporal dimension
        """
        if not self.is_empty():
            for point in self.recording_points:
                point.init_recording(N_points)

    def reset_recordings(self, N_points):
        """
        Sets the recorded extracellular potential to zero whatever the conditions for all
        recording points

        Parameters
        ----------
        N_points : int
            length of the extracellular potential vector along temporal dimension
        """
        if not self.is_empty():
            for point in self.recording_points:
                point.reset_recording(N_points)

    def add_axon_contribution(self, I_membrane, ID):
        """
        Add one axon contribution to the extracellular potential of all recording points.

        Parameters
        ----------
        I_membrane  : array
            membrane current as a matrix over times (columns) and position (lines)
            in mA/cm2
        ID          : int
            axon ID as footprint are stored in a dictionnary with their ID as key
        """
        if not self.is_empty():
            for point in self.recording_points:
                point.add_axon_contribution(I_membrane, ID)

    def gather_all_recordings(self, results: list[dict]):
        """
        Gather all recordings computed by each cores in case of parallel simulation (fascicle
        level), sum de result and propagate final extracellular potential to each core.
        """
        if not self.is_empty():
            reclist = [res["recorder"] for res in results]
            self.t = reclist[0]["t"]
            for i, point in enumerate(self.recording_points):
                if point.recording is None:
                    point.recording = 0.0
                for rec in reclist:
                    point.recording += np.array(rec["recording_points"][i]["recording"])

    def plot(
        self,
        axes: plt.axes,
        points: int | np.ndarray | None = None,
        color: str = "k",
        **kwgs,
    ) -> None:
        if self.t is None:
            rise_warning("empty recorder canot be ploted")
        else:
            if points is None:
                points = np.arange(len(self.recording_points))
            if np.iterable(points):
                for i_pts in points:
                    self.plot(axes=axes, points=i_pts, color=color, **kwgs)
            else:
                if points > len(self.recording_points):
                    rise_warning(
                        f"recording point {points} does not exits in recorder, and so canot be ploted"
                    )
                else:
                    axes.plot(
                        self.t,
                        self.recording_points[points].recording,
                        color=color,
                        **kwgs,
                    )
