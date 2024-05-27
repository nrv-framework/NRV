import nrv
import numpy as np
import matplotlib.pyplot as plt



nerve_results = nrv.load_any("./unitary_tests/sources/518_nerve_results.json")
fig, ax = plt.subplots(figsize=(8, 8))
nerve_results.plot_recruited_fibers(ax)
fig.savefig('./unitary_tests/figures/518_plot_nerve1.png')

nerve_results = nrv.load_any("./unitary_tests/sources/518_nerve_results2.json")
fig, ax = plt.subplots(figsize=(8, 8))
nerve_results.plot_recruited_fibers(ax)
fig.savefig('./unitary_tests/figures/518_plot_nerve2.png')





