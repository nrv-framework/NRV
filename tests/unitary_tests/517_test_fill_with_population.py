import nrv
import numpy as np
import matplotlib.pyplot as plt

if 1:#nrv.MCH.do_master_only_work():
    N = 200
    axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(N, M_stat="Ochoa_M")
    y_axons, z_axons = nrv.axon_packer(axons_diameters,delta = 10)
    d_fasc = nrv.get_circular_contour(axons_diameters,y_axons,z_axons,delta = 10)

    L = 10000 			# length, in um

    #Axon pop is already packed
    fascicle_1 = nrv.fascicle(diameter=d_fasc)
    fascicle_1.define_length(L)
    fascicle_1.fill_with_population(axons_diameters, axons_type, y_axons=y_axons, z_axons=z_axons, delta = 10)
    fascicle_1.generate_random_NoR_position()
    fig, ax = plt.subplots(figsize=(8, 8))
    fascicle_1.plot(ax)
    fig.savefig('./unitary_tests/figures/517_external_packing.png')

    #Axon pop is not packed
    fascicle_2 = nrv.fascicle(diameter=d_fasc)
    fascicle_2.define_length(L)
    fascicle_2.fill_with_population(axons_diameters, axons_type, delta = 10)
    fascicle_2.generate_random_NoR_position()
    fig, ax = plt.subplots(figsize=(8, 8))
    fascicle_2.plot(ax)
    fig.savefig('./unitary_tests/figures/517_internal_packing.png')

    #Fascicle is smaller than packet pop size
    fascicle_3 = nrv.fascicle(diameter=d_fasc/2)
    fascicle_3.define_length(L)
    fascicle_3.fill_with_population(axons_diameters, axons_type, y_axons=y_axons, z_axons=z_axons, delta = 10)
    fascicle_3.generate_random_NoR_position()
    fig, ax = plt.subplots(figsize=(8, 8))
    fascicle_3.plot(ax)
    fig.savefig('./unitary_tests/figures/517_shrinking_pop.png')

    #Fascicle is larger than packet pop size
    fascicle_4 = nrv.fascicle(diameter=d_fasc*3)
    fascicle_4.define_length(L)
    fascicle_4.fill_with_population(axons_diameters, axons_type, y_axons=y_axons, z_axons=z_axons, delta = 10,fit_to_size=False)
    fascicle_4.generate_random_NoR_position()
    fig, ax = plt.subplots(figsize=(8, 8))
    fascicle_4.plot(ax)
    fig.savefig('./unitary_tests/figures/517_large_fascicle_no_expansion.png')

    #Fascicle is larger than packet pop size and we fit to size
    fascicle_5 = nrv.fascicle(diameter=d_fasc*3)
    fascicle_5.define_length(L)
    fascicle_5.fill_with_population(axons_diameters, axons_type, y_axons=y_axons, z_axons=z_axons, delta = 10,fit_to_size=True)
    fascicle_5.generate_random_NoR_position()
    fig, ax = plt.subplots(figsize=(8, 8))
    fascicle_5.plot(ax)
    fig.savefig('./unitary_tests/figures/517_large_fascicle_with_expansion.png')

