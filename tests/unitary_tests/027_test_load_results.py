import nrv
import matplotlib.pyplot as plt

fname = './unitary_tests/sources/26_test_svg.json'

results = nrv.load_any(fname)

print('d_lambda' in results.keys())
print('ID' not in results.keys())
print(results['myelinated'] == False)

plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/27_A.png')
#plt.show()