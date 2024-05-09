################################
## rasterize membrane voltage ##
################################
if not self.record_g_mem:
    rise_error("gmem not recorded nothing will be done")
else:
    if "fgx" in kwargs:
        fgmem = rmv_ext(kwargs["fgx"]) + f"{self.ID}_{k}.csv"
    else:
        fgmem = self.save_path + f"fgx_{self.ID}_{k}.csv"


    if "ft" in kwargs:
        ft = kwargs["ft"]
    else:
        ft= self.save_path + "ft.csv"

    if "t_start_rec" in kwargs:
        t_start_rec = kwargs["t_start_rec"]
    else:
        t_start_rec=0

    if "t_stop_rec" in kwargs:
        t_stop_rec = kwargs["t_stop_rec"]
    else:
        t_stop_rec=self.t_sim

    if "sample_dt" in kwargs:
        sample_dt = kwargs["sample_dt"]
    else:
        sample_dt=self.dt

    if "rec_bounds" in kwargs:
        rec_bounds = kwargs["rec_bounds"]
    else:
        rec_bounds=(0,self.L)

    if np.iterable(rec_bounds):
        I_x = np.argwhere((axon_sim["x_rec"]>rec_bounds[0])&(axon_sim["x_rec"]<rec_bounds[1]))[:,0]
    else:
        rec_bounds = [rec_bounds]
        I_x = np.array([np.argmin(abs(axon_sim["x_rec"]-rec_bounds[0]))])


    N_x = len(I_x)
    i_t_min = np.argwhere(axon_sim["t"]>t_start_rec)[0][0]
    i_t_max = np.argwhere(axon_sim["t"]<t_stop_rec)[-1][0]


    t_APs = [k for k in range(i_t_min,i_t_max)]
    t_APs = t_APs[::int(sample_dt/self.dt)]
    N_t = len(t_APs)


    # Under sampling to reduce memory consumption
    axon_sim["x_rec"] = axon_sim["x_rec"][I_x] - rec_bounds[0]
    axon_sim["t"] = axon_sim["t"][t_APs]
    axon_sim["g_mem"] = axon_sim["g_mem"][np.ix_(I_x, t_APs)]

    to_save =  np.zeros((N_t+1, N_x))
    to_save[0,:] = axon_sim["x_rec"]
    to_save[1:,:] = axon_sim["g_mem"].T
    if self.save_results:
        np.savetxt(fgmem, to_save, delimiter=",")
        if k == 0:
            np.savetxt(ft, axon_sim["t"],delimiter=",")


    ###############################
    ## remove non nevessary data ##
    ###############################
    list_keys = []
    removable_keys = []
    if not self.return_parameters_only:
        list_keys += ["g_mem", "x_rec", "rec", "Nseg_per_sec", "axon_path_type", "t_sim"]
        if k==0:
            list_keys += ["t"]


    for key in axon_sim:
        if not key in list_keys:
            removable_keys += [key]
    for key in removable_keys:
        nrv.remove_key(axon_sim, key, verbose=False)

