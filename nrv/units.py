"""
NRV-Units
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""

###################
## defaulf units ##
###################
mV = 1			# default unit for Voltage is mV, as neuron
ms = 1			# default unit for time is ms, as neuron
um = 1			# default unit for length is um, as neuron
uA = 1			# default unit for current is uA, UNLESS NEURON who is by default in nA
S = 1			# default unit for conductance is S

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
uS = 1e-3 * mS
