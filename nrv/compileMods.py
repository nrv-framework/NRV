"""
NRV-compileMods
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""

import os


dir_path = os.path.dirname(os.path.realpath(__file__))
path2compiled_mods =  dir_path + '/mods/x86_64'

def NeuronCompile():
    #path2compiled_mods =  dir_path + '/mods/x86_64'
    path2_mods = dir_path + '/mods'
    os.system('cd ' +path2_mods+  '&& nrnivmodl')

if not (os.path.exists(path2compiled_mods)):
    print('Mods files are not compiled, executing nrnivmodl...')
    NeuronCompile()
    print('Compilation done')
