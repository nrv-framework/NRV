import nrv


if __name__ == "__main__":
    unmy1 = nrv.unmyelinated(y=0,z=3,d=1,L=10,model="Sundt",T=25,dt=0.01, Nrec=10)
    unmy_dict1 = unmy1.save()
    results = unmy1.simulate(t_sim=1)
    del unmy1

    unmy2 = nrv.generate_axon_from_results(results)
    unmy_dict2 = unmy2.save()
    del unmy2

    for key in unmy_dict1:
        if not key in unmy_dict2:
            print(False)
        else:
            print(unmy_dict1[key]==unmy_dict2[key])


    my1 = nrv.myelinated(y=0,z=0,d=10,L=1000,model="Gaines_motor",T=25,dt=0.01, Nseg_per_sec=2)
    my_dict1 = my1.save()
    results = my1.simulate(t_sim=1)
    del my1

    my2 = nrv.generate_axon_from_results(results)
    my_dict2 = my2.save()
    del my2

    for key in my_dict1:
        if not key in my_dict2:
            print(False)
        else:
            print(my_dict1[key]==my_dict2[key])