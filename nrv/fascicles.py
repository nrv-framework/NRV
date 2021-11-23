"""
NRV-fascicles
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import spatial

# other NRV2 librairies
from .axons import *
from .unmyelinated import *
from .myelinated import *
from .thin_myelinated import *
from .fascicle_generator import *
from .MCore import *
from .extracellular import *
from .file_handler import *
from .CL_postprocessing import *
from .extracellular import *
from .log_interface import rise_error, rise_warning, pass_info



# verbosity level
verbose = True

# Parallel computing options
if not MCH.is_alone():
    fg_verbose = False
    if MCH.do_master_only_work():
        fg_verbose = True

# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()

OTF_PP_path = os.path.dirname(os.path.realpath(__file__))+'/OTF_PP/'
OTF_PP_library = os.listdir(OTF_PP_path)

#####################
## Fasscicle class ##
#####################
class fascicle():
    """
    Class for Fascicle, defined as a group of axons near one to the other in the same Perineurium Sheath. All axons are independant of each other, no ephaptic coupling.
    """
    def __init__(self, dt=0.001, Nseg_per_sec=0, freq=100, freq_min=0,\
        mesh_shape='plateau_sigmoid', alpha_max=0.3, d_lambda=0.1, T=None, ID=0, threshold=-40,\
        Adelta_limit=6):
        """
        Instrantation of a Fascicle

        Parameters
        ----------
        dt              : float
            simulation time stem for Neuron (ms), by default 1us
        Nseg_per_sec    : float
            number of segment per section in Neuron. If set to 0, the number of segment per section is calculated with the d-lambda rule
        freq            : float
            frequency of the d-lambda rule (Hz), by default 100Hz
        freq_min        : float
            minimum frequency for the d-lambda rule when meshing is irregular, 0 for regular meshing
        v_init          : float
            initial value for the membrane voltage (mV), specify None for automatic model choice of v_init
        T               : float
            temperature (C), specify None for automatic model choice of temperature
        ID              : int
            axon ID, by default set to 0
        threshold       : int
            membrane voltage threshold for spike detection (mV), by default -40mV
        Adelta_limit    : float
            limit diameter between A-delta models (thin myelinated) and myelinated models for axons
        """
        super().__init__()
        self.ID = ID
        self.type = None
        self.L = None
        self.D = None
        # geometric properties
        self.y_grav_center = 0
        self.z_grav_center = 0
        self.N_vertices = 0
        self.y_vertices = np.array([])
        self.z_vertices = np.array([])
        self.A = 0
        # axonal content
        self.N = 0
        self.axons_diameter = np.array([])
        self.axons_type = np.array([])
        self.axons_y = np.array([])
        self.axons_z = np.array([])
        self.NoR_relative_position = np.array([])
        # Axons objects default parameters
        self.dt = dt
        self.Nseg_per_sec = Nseg_per_sec
        self.freq = freq
        self.freq_min = freq_min
        self.mesh_shape = mesh_shape
        self.alpha_max = alpha_max
        self.d_lambda = d_lambda
        self.T = T
        self.threshold = threshold
        self.Adelta_limit = Adelta_limit
        # extra-cellular stimulation
        self.extra_stim = None
        # intra-cellular stimulation
        self.N_intra = 0
        self.intra_stim_position = []
        self.intra_stim_t_start = []
        self.intra_stim_duration = []
        self.intra_stim_amplitude = []
        self.intra_stim_ON = []

    def set_ID(self, ID):
        """
        set the ID of the fascicle

        Parameters
        ----------
        ID : int
            ID number of the fascicle
        """
        self.ID = ID

    def define_length(self, L):
        """
        set the length over the x axis of the fascicle

        Parameters
        ----------
        L   : float
            length of the fascicle in um
        """
        self.L = L

    ## generate stereotypic Fascicle
    def define_circular_contour(self, D, y_c=0, z_c=0, N_vertices=100):
        """
        Define a circular countour to the fascicle

        Parameters
        ----------
        D           : float
            diameter of the circular fascicle contour, in um
        y_c         : float
            y coordinate of the circular contour center, in um
        z_c         : float
            z coordinate of the circular contour center, in um
        N_vertices  : int
            Number of vertice in the compute the contour
        """
        self.type = 'Circular'
        self.D = D
        self.y_grav_center = y_c
        self.z_grav_center = z_c
        self.N_vertices = N_vertices
        theta = np.linspace(-np.pi, np.pi, num=N_vertices)
        self.y_vertices = y_c + (D/2)*np.cos(theta)
        self.z_vertices = z_c + (D/2)*np.sin(theta)
        self.A = np.pi * (D/2)**2

    def fit_circular_contour(self, y_c=0, z_c=0, Delta=0.1, N_vertices=100):
        """
        Define a circular countour to the fascicle

        Parameters
        ----------
        y_c         : float
            y coordinate of the circular contour center, in um
        z_c         : float
            z coordinate of the circular contour center, in um
        D           : float
            distance between farest axon and contour, in um
        N_vertices  : int
            Number of vertice in the compute the contour
        """
        N_axons = len(self.axons_diameter)
        D = 2 * Delta

        if N_axons == 0:
            pass_info('No axon to fit fascicul diameter set to '+str(D)+'um')
        else:
            for axon in range(N_axons):
                dist_max = self.axons_diameter[axon]/2 + ((y_c - self.axons_y[axon])**2 +\
                    (z_c - self.axons_z[axon])**2)**0.5
                D = max(D, 2*(dist_max+Delta))
        self.define_circular_contour(D, y_c=y_c, z_c=z_c, N_vertices=N_vertices)

    def define_ellipsoid_contour(self, a, b, y_c=0, z_c=0, rotate=0):
        """
        Define ellipsoidal contour
        """
        pass

    ## generate Fascicle from histology
    def import_contour(self, smthing_else):
        """
        Define contour from a file
        """
        pass

    ## fill fascicle methods
    def fill(self, parallel=True, percent_unmyel=0.7, FVF=0.55, M_stat='Schellens_1',\
        U_stat='Ochoa_U', ppop_fname=None, pop_fname=None):
        """
        Fill a geometricaly defined contour with axons

        Parameters
        ----------
        parallel        : bool
            if True, the generation process (quite long) is split over multiples cores, if False everything is perfrmed by the master.
        percent_unmyel  : float
            ratio of unmyelinated axons in the population. Should be between 0 and 1.
        FVF             : float
            Fiber Volume Fraction estimated for the area. By default set to 0.55
        M_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for myelinated diameters repartition
        U_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for unmyelinated diameters repartition
        ppop_fname      : str
            optional, if specified, name file to store the placed population generated
        pop_fname       : str
            optional, if specified, name file to store the population generated
        """
        #### AXON GENERATION: parallelization if resquested ####
        Area_to_fill = 0
        # Note: generate a bit too much axons just in case
        if self.type == 'Circular':
            Area_to_fill = np.pi * (self.D/2 + 28)**2
        if parallel:
            if MCH.do_master_only_work():
                pass_info('Generating axons')
            # split the generation over the N cores
            partial_axons_diameter, partial_axons_type, M_diam_list, U_diam_list = \
            fill_area_with_axons(Area_to_fill/MCH.size, percent_unmyel=percent_unmyel, \
                FVF=FVF, M_stat=M_stat, U_stat=U_stat)
            # gather results
            axons_diameter = MCH.gather_jobs_as_array(partial_axons_diameter)
            axons_type = MCH.gather_jobs_as_array(partial_axons_type)
        else:
            if MCH.do_master_only_work():
                axons_diameter, axons_type, M_diam_list, U_diam_list = fill_area_with_axons(\
                    Area_to_fill, percent_unmyel=percent_unmyel, FVF=FVF, M_stat=M_stat,\
                    U_stat=U_stat)
        #### AXON PACKING: never parallel
        if MCH.do_master_only_work():
            N = len(axons_diameter)
            pass_info('\n ... '+str(N)+' axons generated')
            if pop_fname is not None:
                save_axon_population(pop_fname, axons_diameter, axons_type, comment=None)
            pass_info('Axon Packing is starting')
            axons_y, axons_z, iteration, FVF_array, probed_iter = axon_packer(axons_diameter,\
                Delta=0.1, y_gc=self.y_grav_center, z_gc=self.z_grav_center, max_iter=20000,\
                monitor=False)
            # check for remaining collisions and delete problematic axons
            axons_diameter, axons_type, axons_y, axons_z = delete_collisions(axons_diameter,\
                axons_type, axons_y, axons_z)
            N = len(axons_diameter)
            pass_info('... Axon Packing done')
            # check if axons are inside the fascicle
            inside_axons = np.power(axons_y - self.y_grav_center, 2) + np.power(axons_z -\
                self.z_grav_center, 2)  - np.power(np.ones(N)*(self.D/2)-axons_diameter/2, 2)
            axons_to_keep = np.argwhere(inside_axons < 0)
            axons_diameter = axons_diameter[axons_to_keep]
            axons_type = axons_type[axons_to_keep]
            axons_y = axons_y[axons_to_keep]
            axons_z = axons_z[axons_to_keep]
            N = len(axons_diameter)
            # save the good population
            if ppop_fname is not None:
                save_placed_axon_population(ppop_fname, self.axons_diameter, self.axons_type,\
                    self.axons_y, self.axons_z, comment=None)
        else:
            axons_diameter = None
            axons_type = None
            axons_y = None
            axons_z = None
            N = None
        ## BRODCASTING RESULTS TO ALL PARALLEL OBJECTS
        self.axons_diameter = MCH.master_broadcasts_array_to_all(axons_diameter)
        self.axons_type = MCH.master_broadcasts_array_to_all(axons_type)
        self.axons_y = MCH.master_broadcasts_array_to_all(axons_y)
        self.axons_z = MCH.master_broadcasts_array_to_all(axons_z)
        self.N = MCH.master_broadcasts_array_to_all(N)

    def fill_with_population(self, axons_diameter, axons_type, Delta=0.1, ppop_fname=None, FVF=0.55):
        """
        Fill a geometricaly defined contour with an already generated axon population

        Parameters
        ----------
        axons_diameters     : np.array
            Array  containing all the diameters of the axon population
        axons_type          : np.array
            Array containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'
        ppop_fname      : str
            optional, if specified, name file to store the placed population generated
        FVF             : float
            Fiber Volume Fraction estimated for the area. By default set to 0.55
        """
        if MCH.do_master_only_work():
            ## check the population area
            total_ax_area = 0
            for diam in axons_diameter:
                total_ax_area += np.pi*((diam/2)**2)
            if self.A*FVF > total_ax_area:
                rise_warning('Warning: the specified population maybe too small to fill the current fascicle')
            N = len(axons_diameter)
            pass_info('\n ... ' + str(N) + ' axons loaded')
            if ppop_fname is not None:
                save_axon_population(ppop_fname, axons_diameter, axons_type, comment=None)
            pass_info('Axon Packing is starting')
            axons_y, axons_z, iteration, FVF_array, probed_iter = axon_packer(axons_diameter,\
                Delta=Delta, y_gc=self.y_grav_center, z_gc=self.z_grav_center, max_iter=20000,\
                monitor=False)
            # check for remaining collisions and delete problematic axons
            axons_diameter, axons_type, axons_y, axons_z = delete_collisions(axons_diameter,\
                axons_type, axons_y, axons_z)
            N = len(axons_diameter)
            pass_info('... Axon Packing done')
            # check if axons are inside the fascicle
            inside_axons = np.power(axons_y - self.y_grav_center, 2) + np.power(axons_z -\
                self.z_grav_center, 2)  - np.power(np.ones(N)*(self.D/2) - axons_diameter/2, 2)
            axons_to_keep = np.argwhere(inside_axons < 0)
            axons_diameter = axons_diameter[axons_to_keep]
            axons_type = axons_type[axons_to_keep]
            axons_y = axons_y[axons_to_keep]
            axons_z = axons_z[axons_to_keep]
            N = len(axons_diameter)
            # save the good population
            if ppop_fname is not None:
                save_placed_axon_population(ppop_fname, self.axons_diameter, self.axons_type,\
                    self.axons_y, self.axons_z, comment=None)
        else:
            axons_diameter = None
            axons_type = None
            axons_y = None
            axons_z = None
            N = None
        ## BRODCASTING RESULTS TO ALL PARALLEL OBJECTS
        self.axons_diameter = MCH.master_broadcasts_array_to_all(axons_diameter)
        self.axons_type = MCH.master_broadcasts_array_to_all(axons_type)
        self.axons_y = MCH.master_broadcasts_array_to_all(axons_y)
        self.axons_z = MCH.master_broadcasts_array_to_all(axons_z)
        self.N = MCH.master_broadcasts_array_to_all(N)

    def fill_with_placed_population(self, axons_diameter, axons_type, axons_y, axons_z,\
        check_inside=True, check_collision=True, ppop_fname=None):
        """
        Fill a geometricaly defined contour with an already generated axon population

        Parameters
        ----------
        axons_diameters     : np.array
            Array  containing all the diameters of the axon population
        axons_type          : np.array
            Array containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'
        axons_y             : np.array
            y coordinate of the axons, in um
        axons_z             : np.array
            z coordinate of the axons, in um
        check_inside        : bool
            if True the placed axons position are checked to ensure all remaining axons at the end are inside the fascicle
        check_collision     : bool
            if True, possible remaining collisions are check in the loaded population, and thiner axons are deleted
        ppop_fname          : str
            optional, if specified, name file to store the placed population generated
        """
        if MCH.do_master_only_work():
            N = len(axons_diameter)
            if check_collision:
                # check for remaining collisions and delete problematic axons
                axons_diameter, axons_type, axons_y, axons_z = delete_collisions(axons_diameter,\
                    axons_type, axons_y, axons_z)
                N = len(axons_diameter)
            # check if axons are inside the fascicle
            if check_inside:
                inside_axons = np.power(axons_y - self.y_grav_center, 2) +\
                    np.power(axons_z - self.z_grav_center, 2)  - np.power(np.ones(N)*(self.D/2)\
                    -axons_diameter/2, 2)
                axons_to_keep = np.argwhere(inside_axons < 0)
                axons_diameter = axons_diameter[axons_to_keep]
                axons_type = axons_type[axons_to_keep]
                axons_y = axons_y[axons_to_keep]
                axons_z = axons_z[axons_to_keep]
                N = len(axons_diameter)
            # save the good population
            if ppop_fname is not None:
                save_placed_axon_population(ppop_fname, self.axons_diameter, self.axons_type,\
                    self.axons_y, self.axons_z, comment=None)
        else:
            axons_diameter = None
            axons_type = None
            axons_y = None
            axons_z = None
            N = None
        ## BRODCASTING RESULTS TO ALL PARALLEL OBJECTS
        self.axons_diameter = MCH.master_broadcasts_array_to_all(axons_diameter)
        self.axons_type = MCH.master_broadcasts_array_to_all(axons_type)
        self.axons_y = MCH.master_broadcasts_array_to_all(axons_y)
        self.axons_z = MCH.master_broadcasts_array_to_all(axons_z)
        self.N = MCH.master_broadcasts_array_to_all(N)

    ## move methods
    def translate_axons(self, y, z):
        """
        Move axons only in a fascicle by group translation

        Parameters
        ----------
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        """
        self.axons_y += y
        self.axons_z += z

    def translate_fascicle(self, y, z):
        """
        Translate a complete fascicle

        Parameters
        ----------
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        """
        self.y_grav_center += y
        self.z_grav_center += z
        self.y_vertices += y
        self.z_vertices += z
        self.translate_axons(y, z)

    def rotate_axons(self, theta, y_c=0, z_c=0):
        """
        Move axons only in a fascicle by group rotation

        Parameters
        ----------
        theta   : float
            angular value of the translation, in rad
        y_c     : float
            y axis value of the rotation center in um, by default set to 0
        z_c     : float
            z axis value for the rotation center in um, by default set to 0
        """
        self.axons_y = (np.cos(theta) * (self.axons_y - y_c) - np.sin(theta) *\
            (self.axons_z - z_c)) + y_c
        self.axons_z = (np.sin(theta) * (self.axons_y - y_c) + np.cos(theta) *\
            (self.axons_z - z_c)) + z_c

    def rotate_fascicle(self, theta, y_c=0, z_c=0):
        """
        Rotate a complete fascicle

        Parameters
        ----------
        theta   : float
            angular value of the translation, in rad
        y_c     : float
            y axis value of the rotation center in um, by default set to 0
        z_c     : float
            z axis value for the rotation center in um, by default set to 0
        """
        self.y_grav_center = (np.cos(theta) * (self.y_grav_center - y_c) - np.sin(theta) *\
            (self.z_grav_center - z_c)) + y_c
        self.z_grav_center = (np.sin(theta) * (self.y_grav_center - y_c) + np.cos(theta) *\
            (self.z_grav_center - z_c)) + z_c
        self.y_vertices += (np.cos(theta) * (self.y_vertices - y_c) - np.sin(theta) *\
            (self.z_vertices - z_c)) + y_c
        self.z_vertices += (np.sin(theta) * (self.y_vertices - y_c) + np.cos(theta) *\
            (self.z_vertices - z_c)) + z_c
        self.rotate_axons(theta, y_c=y_c, z_c=z_c)

    def remove_axons_electrode_overlap(self, electrode):
        """
        Remove the axons that could overlap an electrode

        Parameters
        ----------
        electrode : object
            electrode instance, see electrodes for more details
        """
        y, z, D = 0, 0, 0
        if is_LIFE_electrode(electrode):
            D = electrode.D
            y = electrode.y_c
            z = electrode.z_c
        elif is_analytical_electrode(electrode):
            y = electrode.y
            z = electrode.z
        else:
            # CUFF electrodes should not affect intrafascicular state
            print('CUFF')
            pass
        # compute the distance of all axons to electrode
        D_vectors = np.sqrt((self.axons_y - y)**2 + (self.axons_z - z)**2) - (self.axons_diameter/2 + D/2)
        colapse = np.argwhere(D_vectors < 0)
        mask = np.ones(len(self.axons_diameter), dtype=bool)
        mask[colapse] = False
        # remove axons colliding the electrode
        if len(colapse)>0:
            pass_info('From Fascicle level: Electrode/Axons overlap, '+str(len(colapse))+' axons will be removed from the fascicle')
        self.N -= len(colapse)
        self.axons_diameter = self.axons_diameter[mask]
        self.axons_type = self.axons_type[mask]
        self.axons_y = self.axons_y[mask]
        self.axons_z = self.axons_z[mask]

    ## representation methods
    def plot(self, fig, axes, contour_color='k', myel_color='r', unmyel_color='b', num=False):
        """
        plot the fascicle in the Y-Z plane (transverse section)

        Parameters
        ----------
        fig     : matplotlib.figure
            figure to display the fascicle
        axes    : matplotlib.axes
            axes of the figure to display the fascicle
        contour_color   : str
            matplotlib color string applied to the contour. Black by default
        myel_color      : str
            matplotlib color string applied to the myelinated axons. Red by default
        unmyel_color    : str
            matplotlib color string applied to the myelinated axons. Blue by default
        num             : bool
            if True, the index of each axon is displayed on top of the circle
        """
        if MCH.do_master_only_work():
            ## plot contour
            axes.plot(self.y_vertices, self.z_vertices, linewidth=2, color=contour_color)
            ## plot axons
            circles = []
            for k in range(self.N):
                if self.axons_type[k] == 1: # myelinated
                    circles.append(plt.Circle((self.axons_y[k], self.axons_z[k]),\
                        self.axons_diameter[k]/2, color=myel_color, fill=True))
                else:
                    circles.append(plt.Circle((self.axons_y[k], self.axons_z[k]),\
                        self.axons_diameter[k]/2, color=unmyel_color, fill=True))
            for circle in circles:
                axes.add_patch(circle)
            if num:
                for k in range(self.N):
                    axes.text(self.axons_y[k], self.axons_z[k], str(k))
            ## plot electrode(s) if existings
            if self.extra_stim is not None:
                for electrode in self.extra_stim.electrodes:
                    axes.scatter(electrode.y, electrode.z, color='gold')

    def plot_x(self, fig, axes, myel_color='r', unmyel_color='b', Myelinated_model='MRG'):
        """
        plot the fascicle's axons along Xline (longitudinal)

        Parameters
        ----------
        fig     : matplotlib.figure
            figure to display the fascicle
        axes    : matplotlib.axes
            axes of the figure to display the fascicle
        myel_color      : str
            matplotlib color string applied to the myelinated axons. Red by default
        unmyel_color    : str
            matplotlib color string applied to the myelinated axons. Blue by default
        Myelinated_model : str
            model use for myelinated axon (use to calulated node position)
        """
        if MCH.do_master_only_work():
            if self.L is None or self.NoR_relative_position != []:
                drange = [min(self.axons_diameter.flatten()),max(self.axons_diameter.flatten())]
                polysize = np.poly1d(np.polyfit(drange, [0.5,5], 1))
                for k in range(self.N):
                    relative_pos = self.NoR_relative_position[k]
                    d = round(self.axons_diameter.flatten()[k],2)
                    if self.axons_type.flatten()[k] == 0.0:
                        color = unmyel_color
                        size = polysize(d)
                        axes.plot([0,self.L],np.ones(2)+k-1,color=color, lw=size)
                    else:
                        color = myel_color
                        size = polysize(d)
                        axon = myelinated(0, 0, d, self.L, model=Myelinated_model,\
                            node_shift=self.NoR_relative_position[k])
                        x_nodes = axon.x_nodes
                        node_number = len(x_nodes)
                        del axon
                        axes.plot([0,self.L],np.ones(2)+k-1,color=color, lw=size)
                        axes.scatter(x_nodes,np.ones(node_number)+k-1,marker='x',color=color)

                ## plot electrode(s) if existings
                if self.extra_stim is not None:
                    for electrode in self.extra_stim.electrodes:
                        axes.plot(electrode.x*np.ones(2), [0,self.N-1], color='gold')
                axes.set_xlabel('x (um)')
                axes.set_ylabel('axon ID')
                axes.set_yticks(np.arange(self.N))
                axes.set_xlim(0,self.L)
                plt.tight_layout()


    ## save/load methods
    def save_fascicle_configuration(self, fname):
        """
        Save a fascicle in a json file

        Parameters
        ----------
        fname : str
            name of the file to save the fascicle
        """
        if MCH.do_master_only_work():
            # copy everything into a dictionnary
            fascicle_config = {}
            fascicle_config['ID'] = self.ID
            fascicle_config['type'] = self.type
            fascicle_config['y_grav_center'] = self.y_grav_center
            fascicle_config['z_grav_center'] = self.z_grav_center
            fascicle_config['N_vertices'] = self.N_vertices
            fascicle_config['y_vertices'] = self.y_vertices
            fascicle_config['z_vertices'] = self.z_vertices
            fascicle_config['A'] = self.A
            fascicle_config['axons_diameter'] = self.axons_diameter
            fascicle_config['axons_type'] = self.axons_type
            fascicle_config['axons_y'] = self.axons_y
            fascicle_config['axons_z'] = self.axons_z
            fascicle_config['NoR_relative_position'] = self.NoR_relative_position
            # save the dictionnary as a json file
            json_dump(fascicle_config, fname)

    def load_fascicle_configuration(self, fname):
        """
        Load a fascicle configuration from a json file

        Parameters
        ----------
        fname : str
            path to the json file describing a fascicle
        """
        results = json_load(fname)
        self.ID = results['ID']
        self.type = results['type']
        self.y_grav_center = results['y_grav_center']
        self.z_grav_center = results['z_grav_center']
        self.N_vertices = results['N_vertices']
        self.y_vertices = np.asarray(results['y_vertices']).flatten()
        self.z_vertices = np.asarray(results['z_vertices']).flatten()
        self.A = results['A']
        self.axons_diameter = np.asarray(results['axons_diameter']).flatten()
        self.N = len(self.axons_diameter)
        self.axons_type = np.asarray(results['axons_type']).flatten()
        self.axons_y = np.asarray(results['axons_y']).flatten()
        self.axons_z = np.asarray(results['axons_z']).flatten()
        self.NoR_relative_position = np.asarray(results['NoR_relative_position']).flatten()

    ## STIMULATION METHODS
    def attach_extracellular_stimulation(self, stimulation):
        """
        attach a extracellular context of simulation for an axon.

        Input:
        ------
            stimulation  : stimulation object, see Extracellular.stimulation help for more details
        """
        if is_extra_stim(stimulation):
            self.extra_stim = stimulation
        # remove everlaping axons
        for electrode in stimulation.electrodes:
            self.remove_axons_electrode_overlap(electrode)

    def insert_I_Clamp(self, position, t_start, duration, amplitude, ax_list=None):
        """
        Insert a IC clamp stimulation

        Parameters
        ----------
        position    : float
            relative position over the fascicle. Note that all thin myelinated and myelinated
            will be stimulated in the nearest node of Ranvier around the clamp specified position
        t_start     : float
            starting time, in ms
        duration    : float
            duration of the pulse, in ms
        amplitude   : float
            amplitude of the pulse (nA)
        ax_list     : list, array, np.array
            list of axons to insert the clamp on, if None, all axons are stimulated
        """
        self.intra_stim_position.append(position)
        self.intra_stim_t_start.append(t_start)
        self.intra_stim_duration.append(duration)
        self.intra_stim_amplitude.append(amplitude)
        self.intra_stim_ON.append(ax_list)
        self.N_intra += 1

    ## SIMULATION HANDLING
    def generate_random_NoR_position(self):
        """
        Generates radom Node of Ranvier shifts to prevent from axons with the same diamters to be aligned.
        """
        # also generated for unmyelinated but the meaningless value won't be used
        self.NoR_relative_position = np.random.uniform(low=0.0, high=1.0, size=len(self.axons_diameter))

    def generate_ligned_NoR_position(self, x=0):
        """
        Generates Node of Ranvier shifts to aligned a node of each axon to x postition.

        Parameters
        ----------
        x    : float
            x axsis value (um) on which node are lined, by default 0
        """
        # also generated for unmyelinated but the meaningless value won't be used
        self.NoR_relative_position = []

        for i in range(self.N):
            if self.axons_type.flatten()[i] == 0.0:
                self.NoR_relative_position += [0.0]
            else:
                d = round(self.axons_diameter.flatten()[i], 2)
                node_length = get_MRG_parameters(d)[5]
                self.NoR_relative_position += [(x - 0.5)% node_length / node_length]
                # -0.5 to be at the node of Ranvier center as a node is 1um long


    def simulate(self, t_sim=2e1, record_V_mem=True, record_I_mem=False, record_I_ions=False,\
        record_particles=False, save_V_mem=False, save_path='', verbose=True,\
        Unmyelinated_model='Rattay_Aberham', Adelta_model='extended_Gaines',\
        Myelinated_model='MRG', Adelta_limit=None, PostProc_Filtering=None, postproc_script=None):
        """
        Simulates the fascicle using neuron framework. Parallel computing friendly. Does not return
        results (possibly too large in memory and complex with parallel computing), but instead 
        creates a folder and store fascicle configuration and all axons results.
        On the fly post processing is possible by specifying an additional script.

        Parameters
        ----------
        t_sim               : float
            total simulation time (ms), by default 20 ms
        record_V_mem        : bool
            if true, the membrane voltage is recorded, set to True by default
        record_I_mem        : bool
            if true, the membrane current is recorded, set to False by default
        record_I_ions       : bool
            if true, the ionic currents are recorded, set to False by default
        record_particules   : bool
            if true, the marticule states are recorded, set to False by default
        save_V_mem          : bool
            if true, all membrane voltages values are stored in results whe basic postprocessing is
            applied. Can be heavy ! False by default
        save_path           : str
            name of the folder to store results of the fascicle simulation.
        Unmyelinated_model  : str
            model for unmyelinated fibers, by default 'Rattay_Aberham'
        Adelta_model        : str
            model for A-delta thin myelinated fibers, by default'extended_Gaines'
        Myelinated_model    : str
            model for myelinated fibers, by default 'MRG'
        Adelta_limit        : float
            limit diameter between A-delta models (thin myelinated) and myelinated models for
            axons. Overwritte the fascicle limit, if unnecessary, specify None. None by default
        PostProc_Filtering  : float, list, array, np.array
            value or iterable values for basic post proc filtering. If None specified, no filtering
            is performed
        postproc_script     : str
            path to a postprocessing file. If specified, the basic post processing is not
            performed, and all postprocessing have to be handled by user. The specified script
            can access global and local variables. Can also be key word ('Vmem' or 'scarter') 
            to use script saved in OTF_PP folder, use with caution
        """
        ##########

        if postproc_script is not None:
            import nrv # not ideal at all but gives direct acces to nrv in the postprocessing script
        if Adelta_limit != self.Adelta_limit and Adelta_limit is not None:
            self.Adelta_limit = Adelta_limit
        if len(self.NoR_relative_position) == 0:
            self.generate_random_NoR_position()
        ## create folder and save fascicle config
        folder_name = save_path + 'Fascicle_' + str(self.ID)
        if MCH.do_master_only_work():
            create_folder(folder_name)
            config_filename = folder_name + '/00_Fascicle_config.json'
            self.save_fascicle_configuration(config_filename)
        else:
            pass
        ## create ID for all axons
        axons_ID = np.arange(len(self.axons_diameter))
        ###### FEM STIMULATION IN PARALLEL: master computes FEM (only one COMSOL licence, other computes axons)####
        if self.extra_stim is not None and not is_analytical_extra_stim(self.extra_stim) and not MCH.is_alone():
            # master solves FEM model
            if MCH.do_master_only_work():
                self.extra_stim.run_model()
            else:
                pass
            # synchronize all process
            sync_Flag = MCH.send_synchronization_flag()
            # split the job
            this_core_mask = MCH.split_job_from_arrays_to_slaves(len(self.axons_diameter))
            if MCH.do_master_only_work():
                ## Master acts as a server, accepting request to compute external potential
                while not np.all(this_core_mask):
                    data = MCH.recieve_data_from_slave()
                    this_core_mask[data['ID']] = True
                    V = self.extra_stim.model.get_potentials(data['x'], data['y'], data['z'])
                    back_data = {'V': V}
                    MCH.send_back_array_to_dest(back_data, data['rank'])
            else:
                ## Slaves computes neurons sending requests to the master from (see FEM_stimulation.compute_electrodes_footprints method)
                for k in this_core_mask:
                    ## test axon axons_type[k]
                    if self.axons_type[k] == 0:
                        axon = unmyelinated(self.axons_y[k], self.axons_z[k],\
                            round(self.axons_diameter[k], 2), self.L, model=Unmyelinated_model,\
                            dt=self.dt, freq=self.freq, freq_min=self.freq_min, mesh_shape=self.mesh_shape,\
                            v_init=None, alpha_max=self.alpha_max, d_lambda=self.d_lambda, T=self.T, ID=k,\
                            threshold=self.threshold)
                    else:
                        ## if myelinated, test the axons_diameter[k],
                        ## if less than Adelta_limit -> A-delta model, else Myelinated
                        if self.axons_diameter[k] < self.Adelta_limit:
                            axon = thin_myelinated(self.axons_y[k], self.axons_z[k],\
                                round(self.axons_diameter[k], 2), self.L, model=Adelta_model,\
                                node_shift=self.NoR_relative_position[k], rec='nodes', dt=self.dt,\
                                freq=self.freq, freq_min=self.freq_min,\
                                mesh_shape=self.mesh_shape, alpha_max=self.alpha_max,\
                                d_lambda=self.d_lambda, v_init=None, T=self.T, ID=k,\
                                threshold=self.threshold)
                        else:
                            axon = myelinated(self.axons_y[k], self.axons_z[k],\
                                round(self.axons_diameter[k], 2), self.L, model=Myelinated_model,\
                                node_shift=self.NoR_relative_position[k], rec='nodes', freq=self.freq,\
                                freq_min=self.freq_min, mesh_shape=self.mesh_shape,\
                                alpha_max=self.alpha_max, d_lambda=self.d_lambda, v_init=None, T=self.T,\
                                ID=k, threshold=self.threshold)
                    ## add extracellular stimulation
                    axon.attach_extracellular_stimulation(self.extra_stim)
                    # add intracellular stim
                    if self.N_intra > 0:
                        for j in range(self.N_intra):
                            if is_iterable(self.intra_stim_ON[j]):
                                # in this case, the stimulation is possibly not for all axons
                                if self.intra_stim_ON[j][k]:
                                    # then stimulation should apply, look for the parameters
                                    # get position
                                    if is_iterable(self.intra_stim_position[j]):
                                        position = self.intra_stim_position[j][k]
                                    else:
                                        position = self.intra_stim_position[j]
                                    # get t_start
                                    if is_iterable(self.intra_stim_t_start[j]):
                                        t_start = self.intra_stim_t_start[j][k]
                                    else:
                                        t_start = self.intra_stim_t_start[j]
                                    # get duration
                                    if is_iterable(self.intra_stim_duration[j]):
                                        duration = self.intra_stim_duration[j][k]
                                    else:
                                        duration = self.intra_stim_duration[j]
                                    # get amplitude
                                    if is_iterable(self.intra_stim_amplitude[j]):
                                        amplitude = self.intra_stim_amplitude[j][k]
                                    else:
                                        amplitude = self.intra_stim_amplitude[j]
                                    # APPLY INTRA CELLULAR STIMULATION
                                    axon.insert_I_Clamp(position, t_start, duration, amplitude)
                            else:
                                # in this case , stimulate all axons
                                if is_iterable(self.intra_stim_position[j]):
                                    position = self.intra_stim_position[j][k]
                                else:
                                    position = self.intra_stim_position[j]
                                # get t_start
                                if is_iterable(self.intra_stim_t_start[j]):
                                    t_start = self.intra_stim_t_start[j][k]
                                else:
                                    t_start = self.intra_stim_t_start[j]
                                # get duration
                                if is_iterable(self.intra_stim_duration[j]):
                                    duration = self.intra_stim_duration[j][k]
                                else:
                                    duration = self.intra_stim_duration[j]
                                # get amplitude
                                if is_iterable(self.intra_stim_amplitude[j]):
                                    amplitude = self.intra_stim_amplitude[j][k]
                                else:
                                    amplitude = self.intra_stim_amplitude[j]
                                # APPLY INTRA CELLULAR STIMULATION
                                axon.insert_I_Clamp(position, t_start, duration, amplitude)
                    ## perform simulation
                    sim_results = axon.simulate(t_sim=t_sim, record_V_mem=record_V_mem,\
                        record_I_mem=record_I_mem, record_I_ions=record_I_ions, record_particles=record_particles)
                    del axon
                    ## postprocessing and data reduction
                    if postproc_script is None:
                        # If no specific postproc. file, then basic operations only are performed (rasterize, destroyV_mem values enventually)
                        if PostProc_Filtering is not None:
                            filter_freq(sim_results, 'V_mem', PostProc_Filtering)
                        rasterize(sim_results, 'V_mem')
                        if not(save_V_mem) and record_V_mem:
                            remove_key(sim_results, 'V_mem')
                    else:
                        with open(postproc_script) as f:
                            code = compile(f.read(), postproc_script, 'exec')
                            exec(code, globals(), locals())
                    ## store results
                    ax_fname = 'sim_axon_'+str(k)+'.json'
                    save_axon_results_as_json(sim_results, folder_name+'/'+ax_fname)
        ###### NO STIM OR ANALYTICAL STIM: all in parallel, OR FEM STIM NO PARALLEL
        else:
            ## split the job between Cores/Computation nodes
            this_core_mask = MCH.split_job_from_arrays(len(self.axons_diameter))
            ## perform simulations
            if MCH.is_alone() and verbose:
                print('Simulating axons in fascicle ' + str(self.ID))
            for k in this_core_mask:
                if MCH.is_alone() and verbose:
                    print('\t Axon ' + f"{k+1}" + '/' + str(self.N), end="\r")
                ## test axon axons_type[k]
                if self.axons_type[k] == 0:
                    axon = unmyelinated(self.axons_y[k], self.axons_z[k],\
                        round(self.axons_diameter[k], 2), self.L, model=Unmyelinated_model,\
                        dt=self.dt, freq=self.freq, freq_min=self.freq_min, mesh_shape=self.mesh_shape,\
                        v_init=None, alpha_max=self.alpha_max, d_lambda=self.d_lambda, T=self.T, ID=k,\
                        threshold=self.threshold)
                else:
                    ## if myelinated, test the axons_diameter[k],
                    ## if less than Adelta_limit -> A-delta model, else Myelinated
                    if self.axons_diameter[k] < self.Adelta_limit:
                        axon = thin_myelinated(self.axons_y[k], self.axons_z[k],\
                            round(self.axons_diameter[k], 2), self.L, model=Adelta_model,\
                            node_shift=self.NoR_relative_position[k], rec='nodes', dt=self.dt,\
                            freq=self.freq, freq_min=self.freq_min,\
                            mesh_shape=self.mesh_shape, alpha_max=self.alpha_max,\
                            d_lambda=self.d_lambda, v_init=None, T=self.T, ID=k,\
                            threshold=self.threshold)
                    else:
                        axon = myelinated(self.axons_y[k], self.axons_z[k],\
                            round(self.axons_diameter[k], 2), self.L, model=Myelinated_model,\
                            node_shift=self.NoR_relative_position[k], rec='nodes', freq=self.freq,\
                            freq_min=self.freq_min, mesh_shape=self.mesh_shape,\
                            alpha_max=self.alpha_max, d_lambda=self.d_lambda, v_init=None, T=self.T,\
                            ID=k, threshold=self.threshold)
                ## add extracellular stimulation
                if self.extra_stim is not None:
                    axon.attach_extracellular_stimulation(self.extra_stim)
                ## add intracellular stim
                if self.N_intra > 0:
                    for j in range(self.N_intra):
                        if is_iterable(self.intra_stim_ON[j]):
                            # in this case, the stimulation is possibly not for all axons
                            if self.intra_stim_ON[j][k]:
                                # then stimulation should apply, look for the parameters
                                # get position
                                if is_iterable(self.intra_stim_position[j]):
                                    position = self.intra_stim_position[j][k]
                                else:
                                    position = self.intra_stim_position[j]
                                # get t_start
                                if is_iterable(self.intra_stim_t_start[j]):
                                    t_start = self.intra_stim_t_start[j][k]
                                else:
                                    t_start = self.intra_stim_t_start[j]
                                # get duration
                                if is_iterable(self.intra_stim_duration[j]):
                                    duration = self.intra_stim_duration[j][k]
                                else:
                                    duration = self.intra_stim_duration[j]
                                # get amplitude
                                if is_iterable(self.intra_stim_amplitude[j]):
                                    amplitude = self.intra_stim_amplitude[j][k]
                                else:
                                    amplitude = self.intra_stim_amplitude[j]
                                # APPLY INTRA CELLULAR STIMULATION
                                axon.insert_I_Clamp(position, t_start, duration, amplitude)
                        else:
                            # in this case , stimulate all axons
                            if is_iterable(self.intra_stim_position[j]):
                                position = self.intra_stim_position[j][k]
                            else:
                                position = self.intra_stim_position[j]
                            # get t_start
                            if is_iterable(self.intra_stim_t_start[j]):
                                t_start = self.intra_stim_t_start[j][k]
                            else:
                                t_start = self.intra_stim_t_start[j]
                            # get duration
                            if is_iterable(self.intra_stim_duration[j]):
                                duration = self.intra_stim_duration[j][k]
                            else:
                                duration = self.intra_stim_duration[j]
                            # get amplitude
                            if is_iterable(self.intra_stim_amplitude[j]):
                                amplitude = self.intra_stim_amplitude[j][k]
                            else:
                                amplitude = self.intra_stim_amplitude[j]
                            # APPLY INTRA CELLULAR STIMULATION
                            axon.insert_I_Clamp(position, t_start, duration, amplitude)
                ## perform simulation
                sim_results = axon.simulate(t_sim=t_sim, record_V_mem=record_V_mem,\
                    record_I_mem=record_I_mem, record_I_ions=record_I_ions, record_particles=record_particles)
                del axon
                ## postprocessing and data reduction

                if postproc_script is None:
                    # If no specific postproc. file, then basic operations only are performed (rasterize, destroyV_mem values enventually)
                    if PostProc_Filtering is not None:
                        filter_freq(sim_results, 'V_mem', PostProc_Filtering)
                    rasterize(sim_results, 'V_mem')
                    if not(save_V_mem) and record_V_mem:
                        remove_key(sim_results, 'V_mem', verbose=verbose)
                elif postproc_script in OTF_PP_library:
                    with open(OTF_PP_path+postproc_script) as f:
                        code = compile(f.read(), OTF_PP_path+postproc_script, 'exec')
                        exec(code, globals(), locals())
                elif postproc_script+'.py' in OTF_PP_library:
                    postproc_script += '.py'
                    with open(OTF_PP_path+postproc_script) as f:
                        code = compile(f.read(), OTF_PP_path+postproc_script, 'exec')
                        exec(code, globals(), locals())
                else:
                    #execfile(postproc_script,globals(),locals())
                    with open(postproc_script) as f:
                        code = compile(f.read(), postproc_script, 'exec')
                        exec(code, globals(), locals())
                ## store results
                ax_fname = 'sim_axon_'+str(k)+'.json'
                save_axon_results_as_json(sim_results, folder_name+'/'+ax_fname)
            if MCH.is_alone() and verbose:
                print('... Simulation done')
