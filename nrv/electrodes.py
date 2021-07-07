"""
NRV-electrodes
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
import numpy as np
from .log_interface import rise_error, rise_warning, pass_info

# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()

def is_FEM_electrode(elec):
    """
    Check if the electrode is a FEM based electrode
    """
    return issubclass(type(elec), FEM_electrode)

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

class electrode():
    """
    Objet for generic electrode description. Each electrode has an ID and a position.

    """
    def __init__(self, ID=0):
        """
        Instantiation of a generic electrode

        Parameters
        ----------
        ID  : int
            electrode identification number, set to 0 by default
        """
        super(electrode, self).__init__()
        self.ID = ID
        self.footprint = np.asarray([])

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
        ------
        ID  : int
            electrode identification number
        """
        self.ID = ID

    def compute_field(self, I):
        """ Compute the external field using the Point source approximation

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
        I_mA = I*1e-3
        v_ext = I_mA*self.footprint
        return v_ext

class point_source_electrode(electrode):
    """
    Point source electrode. Inherite from electrode. The electrode is punctual and act as a\
    monopole.
    """
    def __init__(self, x, y, z, ID=0):
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
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.ID = ID

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
            self.footprint = 1./(4*np.pi*np.sqrt((1e-6*(self.x-x))**2 + (1e-6*(self.y-y))**2 +\
                (1e-6*(self.z-z))**2)*mat.sigma)
        else:
            sx = mat.sigma_yy * mat.sigma_zz
            sy = mat.sigma_xx * mat.sigma_zz
            sz = mat.sigma_xx * mat.sigma_yy
            # 1e-6  on distances to stay in m (condivtivity specified in S/m)
            self.footprint = 1./(4*np.pi*np.sqrt(sx*(1e-6*(self.x-x))**2 + \
                sy*(1e-6*(self.y-y))**2 + sz*(1e-6*(self.z-z))**2))

class FEM_electrode(electrode):
    """
    Electrode located in Finite Element Model in Comsol
    """
    def __init__(self, label, ID):
        """
        Instrantiation of a FEM electrode
        """
        super().__init__()
        self.label = label
        self.ID = ID
        self.footprint = np.asarray([])

    def set_footprint(self, V_1mA):
        """
        set the footprin of a FEM electrode

        Parameters:
        -----------
        V_1mA : list, array, numpy array
            Voltage response at 1mA
        """
        self.footprint = np.asarray(V_1mA)

class LIFE_electrode(FEM_electrode):
    """
    Longitudinal IntraFascicular Electrode for FEM models
    """
    def __init__(self, label, D, length, x_shift, y_c, z_c, ID=0):
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
        self.x_shift = x_shift
        self.y_c = y_c
        self.z_c = z_c

    def parameter_model(self,model):
        """
        Parameter the model electrode with user specified dimensions

        Parameters
        ----------
        model : obj
            FEM COMSOL simulation to parameter, se FEM or Extracellular for more details
        """
        model.set_parameter(self.label+'_D', str(self.D)+'[um]')
        model.set_parameter(self.label+'_Length', str(self.length)+'[um]')
        model.set_parameter(self.label+'_y_c', str(self.y_c)+'[um]')
        model.set_parameter(self.label+'_z_c', str(self.z_c)+'[um]')
        model.set_parameter(self.label+'_x_offset', str(self.x_shift)+'[um]')
