"""
NRV-electrodes
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
import numpy as np
from ..backend.log_interface import rise_error, rise_warning, pass_info
from ..backend.file_handler import *

# enable faulthandler to ease 'segmentation faults' debug
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

    if elec_dic["type"] is None:
        elec = electrode()
    elif elec_dic["type"] == "point source":
        elec = point_source_electrode(0,0,0)
    elif elec_dic["type"] == "FEM":
        elec = FEM_electrode("")
    elif elec_dic["type"] == "LIFE":
        elec = LIFE_electrode("",0,0,0,0,0)
    elif elec_dic["type"] == "CUFF":
        elec = CUFF_electrode()
    elif elec_dic["type"] == "CUFF MP":
        elec = CUFF_MP_electrode()
    else:
        rise_error("Electrode type not recognizede")

    elec.load_electrode(elec_dic)
    return elec


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
        self.type = None
        self.is_multipolar = False

    ## Save and Load mehtods

    def save_electrode(self, save=False, fname='electrode.json'):
        """
        Return electrode as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default 'electrode.json'

        Returns
        -------
        elec_dic : dict
            dictionary containing all information
        """
        elec_dic = {}
        elec_dic['ID'] = self.ID
        elec_dic['footprint'] = self.footprint
        elec_dic['type'] = self.type
        elec_dic['is_multipolar'] = self.is_multipolar
        if save:
            json_dump(elec_dic, fname)
        return elec_dic

    def load_electrode(self, data):
        """
        Load all electrode properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing electrode information
        """
        if type(data) == str:
            elec_dic = json_load(data)
        else: 
            elec_dic = data

        self.ID = elec_dic['ID']
        self.footprint = np.asarray(elec_dic['footprint'])
        self.type = elec_dic['type']
        self.is_multipolar = elec_dic['is_multipolar']


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

    def get_footptint(self):
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
        super().__init__(ID)
        self.x = x
        self.y = y
        self.z = z

        self.type = "point source"

    ## Save and Load mehtods

    def save_electrode(self, save=False, fname='electrode.json'):
        """
        Return electrode as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default 'electrode.json'

        Returns
        -------
        elec_dic : dict
            dictionary containing all information
        """
        elec_dic = super().save_electrode()
        elec_dic['x'] = self.x
        elec_dic['y'] = self.y
        elec_dic['z'] = self.z
        if save:
            json_dump(elec_dic, fname)
        return elec_dic


    def load_electrode(self, data):
        """
        Load all electrode properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing electrode information
        """
        if type(data) == str:
            elec_dic = json_load(data)
        else: 
            elec_dic = data
        super().load_electrode(data)
        self.x = elec_dic['x']
        self.y = elec_dic['y']
        self.z = elec_dic['z']


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

    ## Save and Load mehtods

    def save_electrode(self, save=False, fname='electrode.json'):
        """
        Return electrode as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default 'electrode.json'

        Returns
        -------
        elec_dic : dict
            dictionary containing all information
        """
        elec_dic = super().save_electrode()
        elec_dic['label'] = self.label
        elec_dic['is_volume'] = self.is_volume
        if save:
            json_dump(elec_dic, fname)
        return elec_dic

    def load_electrode(self, data):
        """
        Load all electrode properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing electrode information
        """
        if type(data) == str:
            elec_dic = json_load(data)
        else: 
            elec_dic = data
        super().load_electrode(data)
        self.label = elec_dic['label']
        self.is_volume = elec_dic['is_volume']

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
        self.type = "LIFE"

    ## Save and Load mehtods

    def save_electrode(self, save=False, fname='electrode.json'):
        """
        Return electrode as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default 'electrode.json'

        Returns
        -------
        elec_dic : dict
            dictionary containing all information
        """
        elec_dic = super().save_electrode()
        elec_dic['D'] = self.D
        elec_dic['length'] = self.length
        elec_dic['x_shift'] = self.x_shift
        elec_dic['y_c'] = self.y_c
        elec_dic['z_c'] = self.z_c
        if save:
            json_dump(elec_dic, fname)
        return elec_dic


    def load_electrode(self, data):
        """
        Load all electrode properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing electrode information
        """
        if type(data) == str:
            elec_dic = json_load(data)
        else: 
            elec_dic = data
        super().load_electrode(data)
        self.D = elec_dic['D']
        self.length = elec_dic['length']
        self.x_shift = elec_dic['x_shift']
        self.y_c = elec_dic['y_c']
        self.z_c = elec_dic['z_c']


    def parameter_model(self, model):
        """
        Parameter the model electrode with user specified dimensions

        Parameters
        ----------
        model : obj
            FEM COMSOL or Fenics simulation to parameter, se FEM or Extracellular for more details
        """
        if model.type == 'COMSOL':
            model.set_parameter(self.label+'_D', str(self.D)+'[um]')
            model.set_parameter(self.label+'_Length', str(self.length)+'[um]')
            model.set_parameter(self.label+'_y_c', str(self.y_c)+'[um]')
            model.set_parameter(self.label+'_z_c', str(self.z_c)+'[um]')
            model.set_parameter(self.label+'_x_offset', str(self.x_shift)+'[um]')
        else:
            model.add_electrode(elec_type=self.type, x_c=self.x_shift+(self.length/2),\
            y_c=self.y_c, z_c=self.z_c, length=self.length, D=self.D, is_volume=self.is_volume)



class CUFF_electrode(FEM_electrode):
    """
    CUFF electrode for FEM models
    """
    def __init__(self, label="", contact_length=100, is_volume=False, contact_thickness=None,\
        insulator_length=None, insulator_thickness=None,x_center=0, ID=0):
        """
        Instantiation of a LIFE electrode

        Parameters
        ----------
        label               : str
            name of the electrode in the COMSOL file
        x_center            :float
            x-position of the CUFF center in um, by default 0
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
        super().__init__(label, ID)
        self.insulator_length = insulator_length
        self.insulator_thickness = insulator_thickness
        self.contact_length = contact_length
        self.contact_thickness = contact_thickness
        self.x_center = x_center
        self.is_volume = is_volume
        self.type = "CUFF"

    ## Save and Load mehtods

    def save_electrode(self, save=False, fname='electrode.json'):
        """
        Return electrode as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default 'electrode.json'

        Returns
        -------
        elec_dic : dict
            dictionary containing all information
        """
        elec_dic = super().save_electrode()
        elec_dic['insulator_length'] = self.insulator_length
        elec_dic['insulator_thickness'] = self.insulator_thickness
        elec_dic['contact_length'] = self.contact_length
        elec_dic['contact_thickness'] = self.contact_thickness
        elec_dic['x_center'] = self.x_center
        elec_dic['is_volume'] = self.is_volume
        if save:
            json_dump(elec_dic, fname)
        return elec_dic


    def load_electrode(self, data):
        """
        Load all electrode properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing electrode information
        """
        if type(data) == str:
            elec_dic = json_load(data)
        else: 
            elec_dic = data
        super().load_electrode(data)
        self.insulator_length = elec_dic['insulator_length']
        self.insulator_thickness = elec_dic['insulator_thickness']
        self.contact_length = elec_dic['contact_length']
        self.contact_thickness = elec_dic['contact_thickness']
        self.x_center = elec_dic['x_center']
        self.is_volume = elec_dic['is_volume']

    def parameter_model(self, model):
        """
        Parameter the model electrode with user specified dimensions

        Parameters
        ----------
        model : obj
            FEM COMSOL or Fenics simulation to parameter, se FEM or Extracellular for more details
        """
        if model.type == 'COMSOL':
            model.set_parameter(self.label+'_insulator_length', str(self.insulator_length)+'[um]')
            model.set_parameter(self.label+'_insulator_thickness', str(self.insulator_thickness)+'[um]')
            model.set_parameter(self.label+'_contact_length', str(self.contact_length)+'[um]')
            model.set_parameter(self.label+'_contact_thickness', str(self.contact_thickness)+'[um]')
            model.set_parameter(self.label+'_x_center', str(self.x_center)+'[um]')
        else:
            model.add_electrode(elec_type=self.type, insulator_length=self.insulator_length, is_volume=self.is_volume,\
                insulator_thickness=self.insulator_thickness, contact_length=self.contact_length,\
                contact_thickness=self.contact_thickness, x_c=self.x_center)

class CUFF_MP_electrode(CUFF_electrode):
    """
    MultiPolar CUFF electrode for FEM models
    """
    def __init__(self, label="CUFF_MP", N_contact=4, contact_width=None, contact_length=100, is_volume=False,\
        contact_thickness=None, insulator_length=None, insulator_thickness=None, x_center=0, ID=0):
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
        super().__init__(label=label,contact_length=contact_length,is_volume=is_volume,\
            contact_thickness=contact_thickness, insulator_length=insulator_length,\
            insulator_thickness=insulator_thickness, x_center=x_center, ID=ID)
        self.N_contact = N_contact
        self.contact_width = contact_width
        self.type = "CUFF MP"
        self.is_multipolar = True


    ## Save and Load mehtods

    def save_electrode(self, save=False, fname='electrode.json'):
        """
        Return electrode as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default 'electrode.json'

        Returns
        -------
        elec_dic : dict
            dictionary containing all information
        """
        elec_dic = super().save_electrode()
        elec_dic['N_contact'] = self.N_contact
        elec_dic['contact_width'] = self.contact_width
        if save:
            json_dump(elec_dic, fname)
        return elec_dic


    def load_electrode(self, data):
        """
        Load all electrode properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing electrode information
        """
        if type(data) == str:
            elec_dic = json_load(data)
        else: 
            elec_dic = data
        super().load_electrode(data)
        self.N_contact = elec_dic['N_contact']
        self.contact_width = elec_dic['contact_width']



    def parameter_model(self, model):
        """
        Parameter the model electrode with user specified dimensions

        Parameters
        ----------
        model : obj
            FEM COMSOL or Fenics simulation to parameter, se FEM or Extracellular for more details
        """
        if model.type == 'COMSOL':
            rise_warning('Multipolar CUFF not implemented on comsol')
        else:
            model.add_electrode(elec_type=self.type, N=self.N_contact, is_volume=self.is_volume,\
                contact_width=self.contact_width, insulator_length=self.insulator_length,\
                insulator_thickness=self.insulator_thickness, contact_length=self.contact_length,\
                contact_thickness=self.contact_thickness, x_c=self.x_center)
