"""
NRV-compileMods
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""

import os


dir_path = os.environ['NRVPATH'] + '/_misc/mods/'
ls = os.listdir(dir_path)
test_mods = False
i=0
while (not test_mods) and i<len(ls):
    test_mods = not '.' in ls[i]
    i += 1

def NeuronCompile():
    #path2compiled_mods =  dir_path + '/mods/x86_64'
    path2_mods = dir_path
    os.system('chmod +x '+ os.environ['NRVPATH'] +'/nrv2calm')
    os.system('cd ' +path2_mods+  '&& nrnivmodl')

if not test_mods:
    print('Mods files are not compiled, executing nrnivmodl...')
    NeuronCompile()
    print('Compilation done')
