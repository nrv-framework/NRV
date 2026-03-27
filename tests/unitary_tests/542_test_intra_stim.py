import nrv
import matplotlib.pyplot as plt
import numpy as np
from time import perf_counter


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]
figdir = "unitary_tests/figures/" + test_id + "_"

if __name__ == "__main__":
    intra_stim = nrv.intracellular_context()

    positions = []
    stimuli = []
    stypes = []

    positions += [.1]
    stimuli += [nrv.stimulus()]
    stimuli[-1].pulse(start=2, value=100, duration=0.1)
    stypes += ["i"]
    intra_stim.insert_intra_stim(position=positions[-1], stim=stimuli[-1], stype=stypes[-1])

    positions += [.7]
    stimuli += [nrv.stimulus()]
    stimuli[-1].sinus(start=0, amplitude=1, freq=10, duration=10)
    stypes += ["v"]

    intra_stim.insert_intra_stim(position=positions[-1], stim=stimuli[-1], stype=stypes[-1])

    for _i, (p, s, st) in enumerate(intra_stim):
        print(positions[_i] == p)
        print(stimuli[_i] == s)
        print(stypes[_i] == st)
