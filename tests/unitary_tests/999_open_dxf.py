import nrv
import matplotlib.pyplot as plt
import numpy as np

x_list = []
y_list = []
color_list = []

test = nrv.load_dxf_file('../nrv/geom/smoothed_edges_white.dxf')
if test != None:
	print(True)

msp = test.modelspace()
spline_counter = 0
lwpolyline_counter = 0
color_counter = 0

c_list = ['black', 'dimgray','brown','orange', 'cyan', 'peru', 'lime', 'blue', 'violet','teal', 'crimson', 'greenyellow', 'darkkhaki', 'sienna',
'red', 'darkseagreen', 'tan', 'dodgerblue','gold', 'midnightblue', 'fuchsia', 'tomato', 'darkgray', 'mediumseagreen','slategray', 'olive', 'purple','goldenrod']


k = 0

#for e in msp:
start = 0
stop = 27
N = len(msp)
while (k<N):
	e = msp[k]
	k += 1
	if e.dxftype() == 'SPLINE':
		spline_counter += 1
		#print(e.control_points)
		if start <= lwpolyline_counter <= stop:
			x_list.append(e.control_points[0][0])
			y_list.append(e.control_points[0][1])
			color_list.append(c_list[lwpolyline_counter])
		#if e.closed:
		#print(e.knot_count())
		#print(e.knots)
	elif e.dxftype() == 'LWPOLYLINE':
		lwpolyline_counter += 1
		#print(lwpolyline_counter)
		#for k in range(e.__len__()):
		#	x_list.append(e.__getitem__(k)[0])
		#	y_list.append(e.__getitem__(k)[1])
		#	color_list.append(c_list[color_counter])
		#	#print(e.__getitem__(k))
		color_counter += 1
	else:
		print(e.dxftype())
print(str(spline_counter)+' splines')
print(str(lwpolyline_counter)+ ' LWPOLYLINEs')

plt.figure()
plt.scatter(x_list, y_list, c = color_list)
plt.savefig('./unitary_tests/figures/999.png')
#plt.show()
