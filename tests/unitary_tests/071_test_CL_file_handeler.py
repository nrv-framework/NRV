import nrv
import matplotlib.pyplot as plt
import os

DIR1 = './unitary_tests/figures/Fascicle_70/'
DIR2 = './unitary_tests/figures/'

nrv.rm_sim_dir('./unitary_tests/figures/Fascicle_70/', verbose=True)
os.replace(DIR1+"70_Facsicular_state.json",DIR2+"70_Facsicular_state.json")
nrv.rm_sim_dir('./unitary_tests/figures/Fascicle_70/', verbose=True)
