"""
NRV-:class:`.electrode` handling.
"""

import faulthandler

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

from ..backend._file_handler import json_load
from ..backend._log_interface import rise_error, rise_warning
from ..backend._NRV_Class import NRV_class, abstractmethod
from ..utils._misc import rotate_2D

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()


def is_FEM_electrode(elec):
    """
    Check if the electrode is a FEM based electrode
    """
    return issubclass(type(elec), FEM_electrode)


def is_CUFF_electrode(elec):
    """
    Check if the electrode is a LIFE electrode
    """
    return isinstance(elec, CUFF_electrode)


def is_LIFE_electrode(elec):
    """
    Check if the electrode is a LIFE electrode
    """
    return isinstance(elec, LIFE_electrode)


def is_analytical_electrode(elec):
    """
    Check if the electrode is an analytical based electrode
    """
    return not issubclass(type(elec), FEM_electrode)


def load_any_electrode(data):
    """
    return any kind of electrod context properties from a dictionary or a json file

    Parameters
    ----------
    data    : str or dict
        json file path or dictionary containing extracel_context information
    """
    if type(data) == str:
        elec_dic = json_load(data)
    else:
        elec_dic = data

    if elec_dic["type"] == "electrode":
        elec = electrode()
    elif elec_dic["type"] == "point source":
        elec = point_source_electrode(0, 0, 0)
    elif elec_dic["type"] == "FEM":
        elec = FEM_electrode("")
    elif elec_dic["type"] == "LIFE":
        elec = LIFE_electrode("", 0, 0, 0, 0, 0)
    elif elec_dic["type"] == "CUFF":
        elec = CUFF_electrode()
    elif elec_dic["type"] == "CUFF MP":
        elec = CUFF_MP_electrode()
    else:
        rise_error("Electrode type not recognizede")

    elec.load(elec_dic)
    return elec


def check_electrodes_overlap(elec1, elec2):
    """
    check if two FEM electrodes are overlaping

    Parameters
    ----------
    elec1:      FEM_electrode
        first electrode
    elec2:      FEM_electrode
        second electrode

    Returns
    -------
    test:           bool
        True if elec1 and elec2 are overlaping
    """
    if not is_FEM_electrode(elec1) or not is_FEM_electrode(elec2):
        return False
    if is_CUFF_electrode(elec1) and is_CUFF_electrode(elec2):
        dist_e = abs(elec1.x - elec2.x)
        len_min = (elec1.contact_length + elec2.contact_length) / 2
        if dist_e < len_min:
            return True
        else:
            return False
    elif is_LIFE_electrode(elec1) and is_LIFE_electrode(elec2):
        dist_e_x = abs(elec1.x - elec2.x)
        len_min_x = (elec1.length + elec2.length) / 2
        dist_e_yz = (elec1.y - elec2.y) ** 2 + (elec1.z - elec2.z) ** 2
        len_min_yz = ((elec1.D + elec2.D) / 2) ** 2
        if dist_e_x < len_min_x and dist_e_yz < len_min_yz:
            return True
        else:
            return False
    return False


class electrode(NRV_class):
    """
    Objet for generic electrode description. Each electrode has an ID and a position.
    """

    @abstractmethod
    def __init__(self, ID=0):
        """
        Instantiation of a generic electrode

        Parameters
        ----------
        ID  : int
            electrode identification number, set to 0 by default
        """
        super().__init__()
        self.ID = ID
        self.footprint = np.asarray([])
        self.type = "electrode"
        self.is_multipolar = False
        self.x = None
        self.y = None
        self.z = None

    def save_electrode(self, save=False, fname="electrode.json"):
        rise_warning("save_electrode is a deprecated method use save")
        self.save(save=save, fname=fname)

    def load_electrode(self, data="electrode.json"):
        rise_warning("load_electrode is a deprecated method use load")
        self.load(data=data)

    def get_ID_number(self):
        """
        get the ID of a electrode

        Returns
        -------
        ID : int
            identification number of the electrode
        """
        return self.ID

    def set_ID_number(self, ID):
        """
        set the identification number of an electrode

        Parameters
        ----------
        ID  : int
            electrode identification number
        """
        self.ID = ID

    def get_footprint(self):
        """
        get the footprint of a electrode

        Returns
        -------
        footprint : np.array
            identification number of the electrode
        """
        return self.footprint

    def set_footprint(self, footprint):
        """
        set the footprint of a electrode

        Parameters
        ----------
        footprint : np.array
            array contaning the electrod linear footprint (electrode response at 1mA)
            on several space points
        """
        self.footprint = np.array(footprint)

    def clear_footprint(self):
        """
        clear the footprint of a electrode
        """
        self.footprint = np.array([])

    def compute_field(self, I):
        """Compute the external field using the Point source approximation

        Parameters
        ----------
        I       : float
            current value, in uA

        Returns
        -------
        v_ext   : np.array
            external voltage field value at specified coordinates with the specified material in mV
        """
        # convert uA in mA
        I_mA = I * 1e-3
        v_ext = I_mA * self.footprint
        return v_ext

    def translate(self, x=None, y=None, z=None):
        """
        Move electrode by translation

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
        self.clear_footprint()

    def rotate(
        self, angle: float, center: tuple[float, float] = (0, 0), degree: bool = False
    ):
        """
        rotate electrode around x-axis

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

    @abstractmethod
    def plot(self, axes: plt.axes, color: str = "gold", **kwgs) -> None:
        pass


class point_source_electrode(electrode):
    """
    Point source electrode. Inherite from electrode. The electrode is punctual and act as a\
    monopole.
    """

    def __init__(self, x=0, y=0, z=0, ID=0):
        """
        Instantiation of a Point source electrode

        Parameters
        ----------
        x   : float
            x position of the electrode, in um
        y   : float
            y position of the electrode, in um
        z   : float
            z position of the electrode, in um
        ID  : int
            electrode identification number, set to 0 by default
        """
        super().__init__(ID)
        self.x = x
        self.y = y
        self.z = z

        self.type = "point source"

    def compute_footprint(self, x, y, z, mat):
        """
        Compute the linear footprint (electrode response at 1mA)

        Parameters
        ----------
        x       : float
            array like, x corrdinates where to compute the field, in um
        y       : float
            array like, y coordinates where to compute the field, in um
        z       : float
            array like, y coordinates where to compute the field, in um
        mat     : float
            material object, see Material help for more detail
        """
        if mat.is_isotropic():
            # 1e-6  on distances to stay in m (condivtivity specified in S/m
            self.footprint = 1.0 / (
                4
                * np.pi
                * np.sqrt(
                    (1e-6 * (self.x - x)) ** 2
                    + (1e-6 * (self.y - y)) ** 2
                    + (1e-6 * (self.z - z)) ** 2
                )
                * mat.sigma
            )
        else:
            sx = mat.sigma_yy * mat.sigma_zz
            sy = mat.sigma_xx * mat.sigma_zz
            sz = mat.sigma_xx * mat.sigma_yy
            # 1e-6  on distances to stay in m (condivtivity specified in S/m)
            self.footprint = 1.0 / (
                4
                * np.pi
                * np.sqrt(
                    sx * (1e-6 * (self.x - x)) ** 2
                    + sy * (1e-6 * (self.y - y)) ** 2
                    + sz * (1e-6 * (self.z - z)) ** 2
                )
            )

    def plot(self, axes: plt.axes, color: str = "gold", **kwgs) -> None:
        if "nerve_d" in kwgs:
            del kwgs["nerve_d"]
        axes.plot(self.y, self.z, ".", color=color, **kwgs)


class FEM_electrode(electrode):
    """
    Electrode located in Finite Element Model in Comsol
    """

    @abstractmethod
    def __init__(self, label, ID=0):
        """
        Instrantiation of a FEM electrode
        """
        super().__init__(ID)
        self.label = label
        self.ID = ID
        self.footprint = np.asarray([])
        self.is_volume = False
        self.type = "FEM"

    def set_footprint(self, V_1mA):
        """
        set the footprin of a FEM electrode

        Parameters
        ----------
        V_1mA : list, array, numpy array
            Voltage response at 1mA
        """
        self.footprint = np.asarray(V_1mA)


class LIFE_electrode(FEM_electrode):
    """
    Longitudinal IntraFascicular Electrode for FEM models
    """

    def __init__(
        self,
        label="LIFE_1",
        D=25,
        length=1000,
        x_shift=0,
        y_c=0,
        z_c=0,
        ID=0,
    ):
        """
        Instantiation of a LIFE electrode

        Parameters
        ----------
        label   : str
            name of the electrode in the COMSOL file
        D       : float
            diameter of the electrode, in um
        length  : float
            length of the electrode, in um
        x_shift : float
            geometrical offset from the start (x=0) of the simulation
        y_c     : float
            y-coordinate of the center of the electrode, in um
        z_c     : float
            z-coordinate of the center of the electrode, in um
        """
        super().__init__(label, ID)
        self.D = D
        self.length = length
        self.x = x_shift
        self.y = y_c
        self.z = z_c
        self.type = "LIFE"

    def parameter_model(self, model, res="default"):
        """
        Parameter the model electrode with user specified dimensions

        Parameters
        ----------
        model : obj
            FEM COMSOL or Fenics simulation to parameter, se FEM or Extracellular for more details
        """
        if model.type == "COMSOL":
            model.set_parameter(self.label + "_D", str(self.D) + "[um]")
            model.set_parameter(self.label + "_Length", str(self.length) + "[um]")
            model.set_parameter(self.label + "_y_c", str(self.y) + "[um]")
            model.set_parameter(self.label + "_z_c", str(self.z) + "[um]")
            model.set_parameter(self.label + "_x_offset", str(self.x) + "[um]")
        else:
            model.add_electrode(
                elec_type=self.type,
                x_c=self.x + (self.length / 2),
                y_c=self.y,
                z_c=self.z,
                length=self.length,
                d=self.D,
                is_volume=self.is_volume,
                res=res,
            )

    def plot(self, axes: plt.axes, color: str = "gold", **kwgs) -> None:
        axes.add_patch(
            plt.Circle(
                (self.y, self.z),
                self.D / 2,
                color=color,
                fill=True,
            )
        )


class CUFF_electrode(FEM_electrode):
    """
    CUFF electrode for FEM models
    """

    def __init__(
        self,
        label="",
        contact_length=100,
        is_volume=False,
        contact_thickness=None,
        insulator=True,
        insulator_length=None,
        insulator_thickness=None,
        x_center=0,
        insulator_offset=0,
        ID=0,
    ):
        """
        Instantiation of a LIFE electrode

        Parameters
        ----------
        label               : str
            name of the electrode in the COMSOL file
        x_center            :float
            x-position of the CUFF center in um, by default 0
        contact_length      :float
            length along x of the contact site in um, by default 100
        is_volume   : bool
            if True the contact is kept on the mesh as a volume, by default True
        contact_thickness   :float
            thickness of the contact site in um, by default 5
        insulator            :bool
            remove insulator ring from the mesh (no conductivity), by default True
        insulator_thickness :float
            thickness of the insulator ring in um, by default 20
        insulator_length    :float
            length along x of the insulator ring in um, by default 1000
        """
        super().__init__(label, ID)
        self.contact_length = contact_length
        self.contact_thickness = contact_thickness
        self.x = x_center
        self.is_volume = is_volume
        self.insulator = insulator
        self.insulator_length = insulator_length
        self.insulator_thickness = insulator_thickness
        self.insulator_offset = insulator_offset
        self.type = "CUFF"

    def translate(self, x=None, y=None, z=None):
        """
        Move electrode by translation

        Parameters
        ----------
        x   : float
            x axis value for the translation in um
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        """
        super().translate(x)

    def parameter_model(self, model, res="default"):
        """
        Parameter the model electrode with user specified dimensions

        Parameters
        ----------
        model : obj
            FEM COMSOL or Fenics simulation to parameter, se FEM or Extracellular for more details
        """
        if model.type == "COMSOL":
            model.set_parameter(
                self.label + "_contact_length", str(self.contact_length) + "[um]"
            )
            model.set_parameter(self.label + "_x_center", str(self.x) + "[um]")
            if self.contact_thickness is not None:
                model.set_parameter(
                    self.label + "_contact_thickness",
                    str(self.contact_thickness) + "[um]",
                )
            if self.insulator_thickness is not None:
                model.set_parameter(
                    self.label + "_insulator_thickness",
                    str(self.insulator_thickness) + "[um]",
                )
            if self.insulator_length is not None:
                model.set_parameter(
                    self.label + "_insulator_length",
                    str(self.insulator_length) + "[um]",
                )
        else:
            model.add_electrode(
                elec_type=self.type,
                insulator_length=self.insulator_length,
                is_volume=self.is_volume,
                insulator=self.insulator,
                insulator_thickness=self.insulator_thickness,
                contact_length=self.contact_length,
                contact_thickness=self.contact_thickness,
                insulator_offset=self.insulator_offset,
                x_c=self.x,
                res=res,
            )

    def plot(self, axes: plt.axes, color: str = "gold", **kwgs) -> None:
        if "nerve_d" in kwgs:
            rad = kwgs["nerve_d"] / 2
            del kwgs["nerve_d"]
            if "linewidth" not in kwgs:
                kwgs["linewidth"] = 2
            axes.add_patch(plt.Circle((0, 0), rad, color=color, fill=False, **kwgs))
        else:
            rise_warning("Diameter has to be specifie to plot CUFF electrodes")


class CUFF_MP_electrode(CUFF_electrode):
    """
    MultiPolar CUFF electrode for FEM models
    """

    def __init__(
        self,
        label="CUFF_MP",
        N_contact=4,
        contact_width=None,
        contact_length=100,
        is_volume=False,
        contact_thickness=None,
        insulator=True,
        insulator_length=None,
        insulator_thickness=None,
        x_center=0,
        insulator_offset=0,
        ID=0,
    ):
        """
        Instantiation of a LIFE electrode

        Parameters
        ----------
        label               : str
            name of the electrode in the COMSOL file
        x_center            :float
            x-position of the CUFF center in um, by default 0
        N_contact           :int
            Number of contact site of the electrode, by default 4
            length of the CUFF electrod in um, by default 100
        contact_length      :float
            length along x of the contact site in um, by default 100
        is_volume   : bool
            if True the contact is kept on the mesh as a volume, by default True
        contact_thickness   :float
            thickness of the contact site in um, by default 5
        inactive            :bool
            remove insulator ring from the mesh (no conductivity), by default True
        insulator_thickness :float
            thickness of the insulator ring in um, by default 20
        insulator_length    :float
            length along x of the insulator ring in um, by default 1000
        """
        super().__init__(
            label=label,
            contact_length=contact_length,
            is_volume=is_volume,
            contact_thickness=contact_thickness,
            insulator_length=insulator_length,
            insulator=insulator,
            insulator_thickness=insulator_thickness,
            x_center=x_center,
            insulator_offset=insulator_offset,
            ID=ID,
        )
        self.N_contact = N_contact
        self.contact_width = contact_width
        self.type = "CUFF MP"
        self.is_multipolar = True

    def parameter_model(self, model, res="default"):
        """
        Parameter the model electrode with user specified dimensions

        Parameters
        ----------
        model : obj
            FEM COMSOL or Fenics simulation to parameter, se FEM or Extracellular for more details
        """
        if model.type == "COMSOL":
            rise_warning("Multipolar CUFF not implemented on comsol")
        else:
            model.add_electrode(
                elec_type=self.type,
                N=self.N_contact,
                is_volume=self.is_volume,
                contact_width=self.contact_width,
                insulator_length=self.insulator_length,
                insulator_thickness=self.insulator_thickness,
                contact_length=self.contact_length,
                insulator=self.insulator,
                contact_thickness=self.contact_thickness,
                x_c=self.x,
                insulator_offset=self.insulator_offset,
                res=res,
            )

    def plot(
        self, axes: plt.axes, color: str = "gold", list_e=None, e_label=True, **kwgs
    ) -> None:
        if "nerve_d" in kwgs:
            rad = kwgs["nerve_d"] / 2
            del kwgs["nerve_d"]
            if list_e is None:
                list_e = np.arange(self.N_contact)
            elif not np.iterable(list_e):
                list_e = [list_e]
            # elec_theta = 0.9 * 2 * np.pi / self.N_contact
            elec_theta = 180 * (self.contact_width / (rad)) / np.pi
            for i in list_e:
                theta_ = np.pi / 2 - (2 * i * np.pi / self.N_contact)
                theta_deg = 180 * theta_ / np.pi
                axes.add_patch(
                    Wedge(
                        (0, 0),
                        1.025 * rad,
                        theta1=theta_deg - elec_theta / 2,
                        theta2=theta_deg + elec_theta / 2,
                        color=color,
                        width=0.05 * rad,
                        **kwgs,
                    )
                )
                if e_label:
                    z_ = 1.2 * rad * np.exp(1j * theta_)
                    axes.text(z_.real, z_.imag, f"E{i}", va="center", ha="center")

        else:
            rise_warning("Diameter has to be specifie to plot CUFF MP electrodes")
