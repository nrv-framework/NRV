"""
NRV-Cellular Level postprocessing
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
from collections.abc import Iterable
import matplotlib.pyplot as plt
import numpy as np
from pylab import argmin,argmax
from scipy import signal
from numba import jit
from .file_handler import json_dump, json_load, is_iterable
from .log_interface import rise_error, rise_warning, pass_info
from .CL_postprocessing import *

import json
import os



# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()


#############################
####### File handeler #######
#############################



def ls_axons_results(dir_path):
    '''
    return list of axons simulation result files

    Parameters
    ----------
    dir_path     : str
        path the results directory

    Returns
    -------
    files        :list of str
        list of axons result files
    '''
    list_files = [file for file in os.listdir(dir_path) if file[0:9]=='sim_axon_']
    return(list_files)



def rm_file(file_path, verbose=True):
    """
    Delete file

    Parameters
    ----------
    file_path : str
        path and name of the file to remove
    verbose     : str
        pass information when file is deleted 
    """
    os.remove(file_path)
    pass_info('folowing file removed :' + file_path, verbose=verbose)

def rm_sim_dir(dir_path, verbose=True):
    """
    Delete directory
    Warning: use with caution deleted files cannot be recovered

    Parameters
    ----------
    file_path : str
        path and name of the file to remove
    verbose     : str
        pass information when file is deleted 
    """
    if os.path.exists(dir_path):

        # checking whether the folder is empty or not
        if len(os.listdir(dir_path)) == 0:
            # removing the file using the os.remove() method
            os.rmdir(dir_path)
            pass_info('folowing folder removed :' + dir_path, verbose=verbose)
        else:
            # messaging saying folder not empty
            if os.path.exists(dir_path+"00_Fascicle_config.json",):
                rm_file(dir_path+"00_Fascicle_config.json", verbose)

            for file in ls_axons_results(dir_path):
                rm_file(dir_path+file, verbose)
            if len(os.listdir(dir_path)) == 0:
                os.rmdir(dir_path)
                pass_info('folowing folder removed :' + dir_path, verbose=verbose)
            else:
                pass_info( "Folder contains files or folders which cannot be deleted", verbose=verbose)
    else:
        # file not found message
        pass_info("Folder not found in the directory", verbose=verbose)



#############################
##### Result processing #####
#############################

def fascicular_state(dir_path, save=False, saving_file="facsicular_state.json", delete_files=False,
    verbose=True):
    """
    Return each axon caracteristics (blocked, Onset response, ...)

    Parameters
    ----------
    dir_path     : str
        path the results directory
    save        : bool
        if True save result in json file
    saving_file : str
        if save is True path and name of the saving file

    Returns
    -------
    facsicular_state       : dict

    """

    fascicular = load_simulation_from_json(dir_path+'00_Fascicle_config.json')
    facsicular_state = {'-1': fascicular}

    for file in ls_axons_results(dir_path):
        if 'extra_stim' not in facsicular_state['-1']:
            facsicular_state['-1']['extra_stim'] = extra_stim_properties(dir_path+file)

        axon = axon_state(dir_path + file)
        facsicular_state[axon['ID']]=axon

        if delete_files:
            rm_file(dir_path + file, verbose)
    if save:
        save_axon_results_as_json(facsicular_state, saving_file)


    return facsicular_state



#############################
## VISUALIZATION FUNCTIONS ##
#############################

def plot_fasc_state(facsicular_state, fig, axes, contour_color='k', myel_color='r', unmyel_color='b', num=False):
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

    fasc = facsicular_state['-1']
    colors = []
    alpha = []
    N = 0
    while N in facsicular_state:
        if facsicular_state[N]['block_state']:
            if facsicular_state[N]['onset_state']:
                colors += ['green']
                alpha += [facsicular_state[N]['onset number']]
            else:
                colors += ['bleu']
                alpha += [0]
        elif facsicular_state[N]['block_state'] is None:
            colors += ['red']
            alpha += [facsicular_state[N]['onset number']]
        else:
            if facsicular_state[N]['onset_state']:
                colors += ['orange']
                alpha += [facsicular_state[N]['onset number']]
            else:
                colors += ['lightgray']
                alpha += [0]
        N +=1

    alpha = [1-(i/(1+max(alpha))) for i in alpha]

    ## plot contour
    axes.plot(fasc['y_vertices'], fasc['z_vertices'], linewidth=2, color=contour_color)
    ## plot axons
    circles = []
    for k in range(N):
        if fasc['axons_type'][k] == 1: # myelinated
            circles.append(plt.Circle((fasc['axons_y'][k], fasc['axons_z'][k]),\
                fasc['axons_diameter'][k]/2, color=colors[k], fill=True, alpha=alpha[k]))
        else:
            circles.append(plt.Circle((fasc['axons_y'][k], fasc['axons_z'][k]),\
                fasc['axons_diameter'][k]/2, color=colors[k], fill=True, alpha=alpha[k]))
    for circle in circles:
        axes.add_patch(circle)
    if num:
        for k in range(N):
            axes.text(fasc['axons_y'][k], fasc['axons_z'][k], str(k))
    ## plot electrode(s) if existings
    if 'extra_stim' in fasc:
        electrode = fasc['extra_stim']
        axes.scatter(electrode['y'], electrode['z'], color='red')
