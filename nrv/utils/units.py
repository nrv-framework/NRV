"""
NRV-Units
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""

###################
## defaulf units ##
###################
mV = 1  # default unit for Voltage is mV, as neuron
ms = 1  # default unit for time is ms, as neuron
um = 1  # default unit for length is um, as neuron
uA = 1  # default unit for current is uA, UNLESS NEURON who is by default in nA
S = 1  # default unit for conductance is S
kHz = 1  # default unit for frequency is kHz
uF = 1  # default unit for capacitance is uF

######################
## voltage prefixes ##
######################
uV = 1e-3 * mV
V = 1e3 * mV

#############################
## time prefixes and units ##
#############################
us = 1e-3 * ms
s = sec = 1e3 * ms
minute = 60 * sec
hour = 60 * minute
day = 24 * hour

########################
## frequency prefixes ##
########################

Hz = 1e-3 * kHz
MHz = 1e3 * kHz
GHz = 1e6 * kHz

#####################
## length prefixes ##
#####################
mm = 1e3 * um
cm = 1e1 * mm
dm = 1e1 * cm
m = 1e1 * dm

######################
## current prefixes ##
######################
nA = 1e-3 * uA
mA = 1e3 * uA
A = 1e3 * mA

###########################
## conductance prefixes ##
###########################
kS = 1e3 * S
mS = 1e-3 * S
uS = 1e-6 * S

###########################
## capacitance prefixes ##
###########################
F = 1e6 * uF
mF = 1e3 * uF
pF = 1e-3 * uF
nF = 1e-6 * uF

#############################
####  Usefull functions ####
#############################


def sci_round(number, digits=3):
    power = "{:e}".format(number).split("e")[1]
    return round(number, -(int(power) - digits))
