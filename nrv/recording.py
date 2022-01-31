"""
NRV-extracellular contexts
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
import numpy as np
from .materials import *
from .units import *
from .log_interface import rise_error, rise_warning, pass_info

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

class recording_point():
    """
    Object equivalent to a point source electrode for extracellular potential recording only (No stimulation)
    """
    def __init__(self, x, y, z, ID=0, method='PSA'):
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
            electrical potential approximation method, can be 'PSA' (Point Source Approximation)
            or 'LSA' (Line Source Approximation).
            set to 'PSA' by default. Note that if LSA is requested with an anisotropic material, computation
            will automatically be performed using 'PSA'
        """
        # properties
        self.ID = ID
        self.x = x
        self.y = y
        self.z = z
        self.method = method
        # footprints
        self.footprints = dict()    #
        self.recording = None

    def get_ID(self):
        """
        get the ID of a recordin point

        Returns
        -------
        id : int
            ID number of the recording point
        """
        return self.ID

    def get_method(self):
        return self.method

    def set_method(self,method):
        self.method = method

    def compute_PSA_isotropic_footprint(self, x_axon, y_axon, z_axon, D, ID, sigma):
        electrical_distance = 4*np.pi*sigma*(((self.x - x_axon)*m)**2 + ((self.y - y_axon)*m)**2+ ((self.z - z_axon)*m)**2)**0.5
        surface = np.pi * (D*cm) * (np.gradient(x_axon)*cm)
        self.footprints[str(ID)] = np.divide(surface,electrical_distance)

    def init_recording(self, N_points):
        """
        Initializes the recorded extracellular potential. if a recording already exists,
        nothing is performed (usefull at the multi-axons level for instance)

        Parameters
        ----------
        N_points : int
            length of the extracellular potential vector along temporal dimension
        """
        if self.recording == None:
            self.recording = np.zeros(N_points)
        else:
            if len(self.recording)!=N_points:
                rise_error('Trying to compute an extracellular potential of a wrong temporal size')

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
        print('... compute')
        print(np.shape(I_membrane))
        print(len(self.footprints[str(ID)]))
        print(len(self.recording))
        #print(np.shape(I_membrane*np.transpose(self.footprints[str(ID)])))
        #self.recording +=

class recorder():
    """
    Object for recording extracellular potential of axons.
    """
    def __init__(self, material=None):
        """
        Instantiation of an extracellular potential recording mechanism. A mecanism can store recording points,
        be associated with a material and properties. The mechanism will perform the extracellular potential
        computation at each point for an axon when a simulation is performed.
        """
        self.material = None
        self.is_isotropic = True
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
        self.recording_points = []

    def is_empty(self):
        """
        check if a recorder has no recording points (empty) or not.

        Returns
        -------
        """
        return self.recording_points == []

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

    def set_recording_point(self, x, y, z, method='PSA'):
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
        method  : string
            electrical potential approximation method, can be 'PSA' (Point Source Approximation)
            or 'LSA' (Line Source Approximation).
            set to 'PSA' by default. Note that if LSA is requested with an anisotropic material, computation
            will automatically be performed using 'PSA'
        """
        if self.is_empty():
            new_point = recording_point(x, y, z, method=method)
        else:
            lowest_ID = self.recording_points[-1].get_ID()
            new_point = recording_point(x, y, z, ID=lowest_ID+1, method=method)
        self.add_recording_point(new_point)

    def compute_footprints(self, x_axon, y_axon, z_axon, D, ID):
        if not self.is_empty():
            print('computing footprints')
            for point in self.recording_points:
                print('... new footprint')
                point.compute_PSA_isotropic_footprint(x_axon, y_axon, z_axon, D, ID, self.sigma)

    def init_recordings(self, N_points):
        if not self.is_empty():
            for point in self.recording_points:
                point.init_recording(N_points)

    def reset_recordings(self, N_points):
        if not self.is_empty():
            for point in self.recording_points:
                point.reset_recording(N_points)

    def add_axon_contribution(self, I_membrane, ID):
        if not self.is_empty():
            for point in self.recording_points:
                point.add_axon_contribution(I_membrane, ID)

