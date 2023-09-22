"""
NRV-compileMods
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""

import os

# test if neuron correctly installed
# warning: difficult as neuron can be 'mocked' on github and rtd for delploy and help
try:
    import neuron as nrn  # this still work with fake neuron (mock)

    nrn_version = nrn.__version__  # this fails :)
except AttributeError:
    from .log_interface import rise_warning

    # no Neuron or fake neuron
    rise_warning(
        "No mods compiled as the environnement variable NRVPATH does not exist"
    )
else:
    # if true neuron installation
    dir_path = os.environ["NRVPATH"] + "/_misc/mods/"
    ls = os.listdir(dir_path)
    test_mods = False
    i = 0
    while (not test_mods) and i < len(ls):
        test_mods = "." not in ls[i]
        i += 1

    def NeuronCompile():
        # path2compiled_mods =  dir_path + "/mods/x86_64"
        path2_mods = dir_path
        os.system("chmod +x " + os.environ["NRVPATH"] + "/nrv2calm")
        os.system("cd " + path2_mods + "&& nrnivmodl")

    if not test_mods:
        print("Mods files are not compiled, executing nrnivmodl...")
        NeuronCompile()
        print("Compilation done")
