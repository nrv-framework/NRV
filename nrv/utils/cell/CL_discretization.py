"""
NRV-Cellular Level discretization methods
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS


todo:
 - Blocking vs dt
 - Blocking vs nseg
 - Onset_response vs dt (ou pas)
 - Onset_response vs dt (ou pas)
 - Velocity vs nseg 
 - Spike th vs nseg unmyelinated

"""
import numpy as np
from scipy.optimize import minimize

from ...backend.log_interface import rise_error, rise_warning

calibrated_unmyelinated_models = ["Rattay_Aberham", "Sundt", "Tigerholm"]
calibrated_myelinated_models = ["MRG", "Gaines_motor", "Gaines_sensory"]
# calibrated_simulation = ['Velocity','Spike_threshold','Blocking_threshold','Onset_response']
calibrated_simulation = ["Velocity", "Spike_threshold"]


def _diff_nseg_spike_threshold_myelinated(nseg, tol):
    """
    Computes the norm to minimize for a specified nseg - Spike Threshold Simulation - Myelinated models

    Parameters
    ----------
    nseg : int
        number of segment

    tol:
        desired tolerance

    Returns
    -------
    float
        norm to minimize
    """
    nseg_log = np.log(nseg)
    tol_log = np.log(tol)
    poly_coeff = [0.08914346, -1.2569447, 3.12523366]
    poly = np.poly1d(poly_coeff)
    val = np.exp(poly(nseg_log))
    return (val - tol) ** 2


def _diff_dt_ratio_spike_threshold_myelinated(dt_ratio, tol):
    """
    Computes the norm to minimize for a specified dt - Spike Threshold Simulation - Myelinated models

    Parameters
    ----------
    dt_ratio : float
        dt ratio

    tol:
        desired tolerance

    Returns
    -------
    float
        norm to minimize
    """
    dt_log = np.log(dt_ratio)
    tol_log = np.log(tol)
    poly_coeff = [-0.05832062, 0.95287425, -5.45710455, 12.26637458, -7.04848512]
    poly = np.poly1d(poly_coeff)
    val = np.exp(poly(dt_log))
    return (val - tol) ** 2


def _diff_dt_ratio_spike_threshold_unmyelinated(dt_ratio, tol):
    """
    Computes the norm to minimize for a specified dt - Spike Threshold Simulation - Unmyelinated models

    Parameters
    ----------
    dt_ratio : float
        dt ratio

    tol:
        desired tolerance

    Returns
    -------
    float
        norm to minimize
    """
    dt_log = np.log(dt_ratio)
    tol_log = np.log(tol)
    poly_coeff = [0.01751393, -0.25108173, 1.23328312, -3.34147125, 6.57882033]
    poly = np.poly1d(poly_coeff)
    val = np.exp(poly(dt_log))
    return (val - tol) ** 2


def _diff_dt_velocity_myelinated(dt, tol):
    """
    Computes the norm to minimize for a specified dt - Velocity estimation - Myelinated models

    Parameters
    ----------
    dt : float
        time discretization in ms

    tol:
        desired tolerance

    Returns
    -------
    float
        norm to minimize
    """
    poly_coeff = [3.65238002e05, -4.13999358e04, 2.16625888e03, -2.75739556e-01]
    poly = np.poly1d(poly_coeff)
    return (poly(dt) - tol) ** 2


def _diff_dt_velocity_sundt_tigerholm(dt, tol):
    """
    Computes the norm to minimize for a specified dt - Velocity estimation - Sundt-Tigerholm unmyelinated models

    Parameters
    ----------
    dt : float
        time discretization in ms

    tol:
        desired tolerance

    Returns
    -------
    float
        norm to minimize
    """

    poly_coeff = [1.70847637e05, -1.40276023e04, 5.26842025e02, 1.27772606e-01]
    poly = np.poly1d(poly_coeff)
    return (poly(dt) - tol) ** 2


def _diff_dt_velocity_rattay_aberham(dt, tol):
    """
    Computes the norm to minimize for a specified dt - Velocity estimation - Rattay-Aberham unmyelinated models

    Parameters
    ----------
    dt : float
        time discretization in ms

    tol:
        desired tolerance

    Returns
    -------
    float
        norm to minimize
    """

    poly_coeff = [2.79799924e05, -1.18439668e04, 7.14708491e02, -1.43308070e-01]
    poly = np.poly1d(poly_coeff)
    return (poly(dt) - tol) ** 2


def _get_dt_velocity_myelinated(tol, model):
    """
    returns the dt value for requested tolerance - myelinated models - velocity estimation

    Parameters
    ----------
    tol : float
        tolerance

    model: str
        simulated model
    Returns
    -------
    dt
        time discretization in ms
    """
    if tol > 50:
        rise_warning(
            "Requested tolerance is out of calibration range. Returned value might be inacurate."
        )
    res = minimize(
        _diff_dt_velocity_myelinated, 1.0, args=(tol), method="Nelder-Mead", tol=1e-6
    )
    return res.x[0]


def _get_dt_velocity_unmyelinated(tol, model):
    """
    returns the dt value for requested tolerance - unmyelinated models - velocity estimation

    Parameters
    ----------
    tol : float
        tolerance

    model: str
        simulated model
    Returns
    -------
    dt
        time discretization in ms
    """
    if model == "Rattay_Aberham":
        if tol > 40:
            rise_warning(
                "Requested tolerance is out of calibration range. Returned value might be inacurate."
            )
        res = minimize(
            _diff_dt_velocity_rattay_aberham,
            1.0,
            args=(tol),
            method="Nelder-Mead",
            tol=1e-6,
        )
    if (model == "Sundt") or (model == "Tigerholm"):
        if tol > 10:
            rise_warning(
                "Requested tolerance is out of calibration range. Returned value might be inacurate."
            )
        res = minimize(
            _diff_dt_velocity_sundt_tigerholm,
            1.0,
            args=(tol),
            method="Nelder-Mead",
            tol=1e-6,
        )
    return res.x[0]


def _get_dt_spike_threshold_myelinated(tol, model):
    """
    returns the dt value for requested tolerance - myelinated models - Spike threshold

    Parameters
    ----------
    tol : float
        tolerance

    model: str
        simulated model
    Returns
    -------
    dt_ratio
        time discretization ratio
    """
    if tol > 10:
        rise_warning(
            "Requested tolerance is out of calibration range. Returned value might be inacurate."
        )
    res = minimize(
        _diff_dt_ratio_spike_threshold_myelinated,
        10.0,
        args=(tol),
        method="Nelder-Mead",
        tol=1e-6,
    )
    return res.x[0]


def _get_dt_spike_threshold_unmyelinated(tol, model):
    """
    returns the dt value for requested tolerance - unmyelinated models - Spike threshold

    Parameters
    ----------
    tol : float
        tolerance

    model: str
        simulated model
    Returns
    -------
    dt_ratio
        time discretization ratio
    """
    if tol > 40:
        rise_warning(
            "Requested tolerance is out of calibration range. Returned value might be inacurate."
        )
    res = minimize(
        _diff_dt_ratio_spike_threshold_unmyelinated,
        1.0,
        args=(tol),
        method="Nelder-Mead",
        tol=1e-6,
    )
    return res.x[0]


def _get_nseg_spike_threshold_myelinated(tol, model):
    """
    returns the number of segment for the requested tolerance - myelinated models - Spike threshold

    Parameters
    ----------
    tol : float
        tolerance

    model: str
        simulated model
    Returns
    -------
    nseg: int
        number of segment
    """
    if tol > 25:
        rise_warning(
            "Requested tolerance is out of calibration range. Returned value might be inacurate."
        )
    res = minimize(
        _diff_nseg_spike_threshold_myelinated,
        1.0,
        args=(tol),
        method="Nelder-Mead",
        tol=1e-6,
    )
    return res.x[0]


def _get_dt_velocity(tol, model):
    """
    returns the dt value for requested tolerance - Velocity estimation

    Parameters
    ----------
    tol : float
        tolerance

    model: str
        simulated model
    Returns
    -------
    dt
        time discretization in ms
    """

    if model in calibrated_myelinated_models:
        return _get_dt_velocity_myelinated(tol, model)
    if model in calibrated_unmyelinated_models:
        return _get_dt_velocity_unmyelinated(tol, model)
    if model not in (calibrated_myelinated_models) and model not in (
        calibrated_unmyelinated_models
    ):
        rise_error("Selected model is not calibrated yet.")
        return 0


def _get_dt_spike_threshold(tol, model):
    """
    returns the dt value for requested tolerance - Spike threshold

    Parameters
    ----------
    tol : float
        tolerance

    model: str
        simulated model
    Returns
    -------
    dt
        time discretization ratio
    """

    if model in calibrated_myelinated_models:
        return _get_dt_spike_threshold_myelinated(tol, model)
    if model in calibrated_unmyelinated_models:
        return _get_dt_spike_threshold_unmyelinated(tol, model)
    if model not in (calibrated_myelinated_models) and model not in (
        calibrated_unmyelinated_models
    ):
        rise_error("Selected model is not calibrated yet.")


def _get_nseg_spike_threshold(tol, model, L=None, d=None):
    """
    returns the number of segment for requested tolerance - Spike threshold

    Parameters
    ----------
    tol : float
        tolerance

    model: str
        simulated model

    d: float
        axon diameter in um (only for unmyelinated models)

    L: float
        Axon length in um (only for unmyelinated models)
    Returns
    -------
    nseg
        number of segment
    """

    if model in calibrated_myelinated_models:
        return _get_nseg_spike_threshold_myelinated(tol, model)
    if model in calibrated_unmyelinated_models:
        rise_error("Not implemented yet.")
    if model not in (calibrated_myelinated_models) and model not in (
        calibrated_unmyelinated_models
    ):
        rise_error("Selected model is not calibrated yet.")


def Get_nseg(tol, model, simulation_category, d=None, L=None):
    """
    Returns the number of segment for the requested tolerance

    Parameters
    ----------
    tol : float
        desired tolerance

    model: str
        simulated

    simulation_category: str
        Simulation to perform

    d: float
        axon diameter in um (only for unmyelinated models)

    L: float
        axon length in um (only for unmyelinated models)

    Returns
    -------
    nseg number of segments
    """

    if simulation_category not in (calibrated_simulation):
        rise_error("Selected simulation is not calibrated yet.")
    else:
        if simulation_category == "Velocity":
            rise_error("Not implemented yet.")

        if simulation_category == "Spike_threshold":
            nseg = _get_nseg_spike_threshold(tol, model)
            return np.int32(np.round(nseg))


def Get_dt(tol, model, simulation_category, stim_pw=None):
    """
    Estimates the dt value for requested tolerance

    Parameters
    ----------
    tol : float
        desired tolerance

    model: str
        simulated

    simulation_category: str
        Simulation to perform

    stim_pw: float
        Stimulation characteristic pulse width in ms (not required for velocity simulation)

    Returns
    -------
    dt
        time discretization value
    """

    if simulation_category not in (calibrated_simulation):
        rise_error("Selected simulation is not calibrated yet.")
    else:
        if simulation_category == "Velocity":
            return _get_dt_velocity(tol, model)

        if simulation_category == "Spike_threshold":
            if stim_pw > 250e-3:
                rise_warning(
                    "Characteristic pulse width is out of calibration range. Returned value might be inacurate."
                )
            dt_ratio = stim_pw / _get_dt_spike_threshold(tol, model)
            return dt_ratio
