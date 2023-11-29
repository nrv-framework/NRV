"""
NRV-Cellular Level postprocessing
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
import os

import matplotlib.pyplot as plt

from ...backend.file_handler import json_load
from ...backend.log_interface import pass_info
from ...fmod.electrodes import is_FEM_electrode
from ..cell.CL_postprocessing import *

# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()


#############################
####### File handeler #######
#############################


def ls_axons_results(dir_path):
    """
    return list of axons simulation result files

    Parameters
    ----------
    dir_path     : str
        path the results directory

    Returns
    -------
    files        :list of str
        list of axons result files
    """
    list_files = [file for file in os.listdir(dir_path) if file[0:9] == "sim_axon_"]
    return list_files

def ls_csv(dir_path):
    """
    return list of axons simulation result files

    Parameters
    ----------
    dir_path     : str
        path the results directory

    Returns
    -------
    files        :list of str
        list of axons result files
    """
    list_files = [file for file in os.listdir(dir_path) if file[-4:] == ".csv"]
    return list_files


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
    pass_info("folowing file removed :" + file_path, verbose=verbose)


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
        # messaging saying folder not empty
        if os.path.exists(
            dir_path + "00_Fascicle_config.json",
        ):
            rm_file(dir_path + "00_Fascicle_config.json", verbose)

        for file in ls_axons_results(dir_path)+ls_csv(dir_path):
            rm_file(dir_path + file, verbose)
        # checking whether the folder is empty or not
        if len(os.listdir(dir_path)) == 0:
            os.rmdir(dir_path)
            pass_info("folowing folder removed :" + dir_path, verbose=verbose)
        else:
            os.rmdir(dir_path)
            pass_info(
                "Folder contains files or folders which cannot be deleted",
                verbose=verbose,
            )
    else:
        # file not found message
        pass_info("Folder not found in the directory", verbose=verbose)

def rm_sim_dir_from_results(results, verbose=True):
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
    fasc_dir = results["save_path"] + "Fascicle_" +str(results["ID"]) + "/"
    rm_sim_dir(dir_path=fasc_dir, verbose=verbose)

def CAP_time_detection(Voltage, t, t_stim=0, stim_duration=0,tol=0.05, myelinated=False,\
    index=True):
    """
    internal use, Return index in the time scale or time of the start and stop of
    a Compound Action Potentiel 

    Parameters
    ----------
    Voltage : list(float)
        list of voltage value
    t     : list(float)
        list of time value
    t_stim : float
        time of the stimulation (to skip the stimulation artefact)
    stim_duration     : list(float)
        list of time value
    tol : float
        absolute tolerence in Volt
    index     : bool
        if true the time index is returned, else the time value
    """
    i_start_unm, i_stop_unm = 0, 0
    i_start_m, i_stop_m = 0, 0
    dt = t[1] - t[0]
    offset = int((t_stim + stim_duration)/dt)+1

    S = Voltage
    N = len(S) - offset

    for i in range(N-1):
        if i_start_unm == 0 and S[i+offset]- S[-1] > tol:
            i_start_unm = i+offset
        if i_stop_unm == 0 and abs(S[len(S)-i-1])- abs(S[-1]) > tol:
            i_stop_unm = len(S) - i - 1

    if myelinated is False: 
        i_max = i_start_unm + np.argmax(Voltage[i_start_unm:i_stop_unm])
        i_min = i_start_unm + np.argmin(Voltage[i_start_unm:i_stop_unm])
        if index:
            return i_start_unm, i_max, i_min, i_stop_unm
        else:
            return t[i_start_unm], t[i_max], t[i_min], t[i_stop_unm]
    else:
        ## No unmyelinated CAP found
        if i_start_unm == 0:
            i_stop_m = i_stop_unm
            for i in range(N-1):
                if i_start_m == 0 and abs(S[i+offset])-abs(S[-1])> tol:
                    i_start_m = i+offset
        else:
            N = i_start_unm - offset
            for i in range(N-1):
                if i_start_m == 0 and abs(S[i+offset])- abs(S[-1]) > tol:
                    i_start_m = i+offset
                if i_stop_m == 0 and abs(S[i_start_unm-i-1])- abs(S[-1]) > tol:
                    i_stop_m = i_start_unm - i - 1
        i_max = np.argmax(Voltage[offset:])
        i_min = i_start_m + np.argmin(Voltage[i_start_m:i_stop_m])

        if index:
            return i_start_m, i_max, i_min, i_stop_m
        else:
            return t[i_start_m], t[i_max], t[i_min], t[i_stop_m]

#############################
##### Result processing #####
#############################
def fascicular_state(
    dir_path,
    save=False,
    saving_file="facsicular_state.json",
    delete_files=False,
    verbose=True,
):
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

    fascicular = json_load(dir_path + "00_Fascicle_config.json")
    facsicular_state = {"-1": fascicular}
    N_ax = fascicular["N"]
    for i in range(N_ax):
        file = "sim_axon_"+ str(i) + ".json"
        if "extra_stim" not in facsicular_state["-1"]:
            facsicular_state["-1"]["extra_stim"] = extra_stim_properties(
                dir_path + file
            )

        axon = axon_state(dir_path + file)
        facsicular_state[axon["ID"]] = axon

        if delete_files:
            rm_file(dir_path + file, verbose)
    if save:
        save_axon_results_as_json(facsicular_state, saving_file)

    return facsicular_state


#############################
## VISUALIZATION FUNCTIONS ##
#############################


def plot_fasc_state(
    facsicular_state,
    fig,
    axes,
    contour_color="k",
    myel_color="r",
    unmyel_color="b",
    num=False,
):
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

    fasc = facsicular_state["-1"]
    colors = []
    alpha = []
    N = 0
    while N in facsicular_state:
        if facsicular_state[N]["block_state"]:
            if facsicular_state[N]["onset_state"]:
                colors += ["green"]
                alpha += [facsicular_state[N]["onset number"]]
            else:
                colors += ["bleu"]
                alpha += [0]
        elif facsicular_state[N]["block_state"] is None:
            colors += ["red"]
            alpha += [facsicular_state[N]["onset number"]]
        else:
            if facsicular_state[N]["onset_state"]:
                colors += ["orange"]
                alpha += [facsicular_state[N]["onset number"]]
            else:
                colors += ["lightgray"]
                alpha += [0]
        N += 1

    alpha = [1 - (i / (1 + max(alpha))) for i in alpha]

    ## plot contour
    axes.plot(fasc["y_vertices"], fasc["z_vertices"], linewidth=2, color=contour_color)
    ## plot axons
    circles = []
    for k in range(N):
        if fasc["axons_type"][k] == 1:  # myelinated
            circles.append(
                plt.Circle(
                    (fasc["axons_y"][k], fasc["axons_z"][k]),
                    fasc["axons_diameter"][k] / 2,
                    color=colors[k],
                    fill=True,
                    alpha=alpha[k],
                )
            )
        else:
            circles.append(
                plt.Circle(
                    (fasc["axons_y"][k], fasc["axons_z"][k]),
                    fasc["axons_diameter"][k] / 2,
                    color=colors[k],
                    fill=True,
                    alpha=alpha[k],
                )
            )
    for circle in circles:
        axes.add_patch(circle)
    if num:
        for k in range(N):
            axes.text(fasc["axons_y"][k], fasc["axons_z"][k], str(k))
    ## plot electrode(s) if existings
    if "extra_stim" in fasc:
        extra_stim = load_any(fasc["extra_stim"])
        for electrode in extra_stim.electrodes:
            if electrode.type == "LIFE":
                circles.append(
                    plt.Circle(
                        (electrode.y, electrode.z),
                        electrode.D / 2,
                        color="gold",
                        fill=True,
                    )
                )
            elif not is_FEM_electrode(electrode):
                axes.scatter(electrode.y, electrode.z, color="gold")