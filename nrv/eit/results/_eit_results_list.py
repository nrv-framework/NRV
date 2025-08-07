import numpy as np
import os


from ._eit_class_results import eit_class_results, Literal
from ..utils._misc import set_idxs, get_query


class eit_results_list(eit_class_results):
    def __init__(self, dt:float|None=0.001, t_sim:float|None=None, results:list[eit_class_results]|eit_class_results|str=None, include_rec:bool=False):
        super().__init__()
        self.dt:float = dt
        self.t_sim:float|None = t_sim
        self.n_res = 0
        self.res_info = {}
        self.add_results(results,include_rec=include_rec)

    @property
    def r_axis(self)->int:
        return 0

    @property
    def _axes_labels(self):
        return ["res"] + super()._axes_labels
    
    @property
    def _column_labels(self):
        return ["i_res"] + super()._column_labels

    ## add and access results methods
    def add_results(self, results:list[eit_class_results]|eit_class_results|str, include_rec:bool=False):
        if isinstance(results, eit_class_results):
            #first results
            if self.t_sim is None:
                self.t_sim = results["t"][-1]
                self["t"] = np.arange(int(self.t_sim/self.dt), dtype=float)*self.dt
                self["f"] = results["f"]
                self["v_eit"] = np.expand_dims(results.v_eit(t=self["t"]), self.r_axis)
                if include_rec:
                    self["v_rec"] = np.expand_dims(results.v_rec(t=self["t"]), self.r_axis)
                    self["t_rec"] = self["t"]
            else:
                if self.t_sim < results["t"][-1]:
                    print(f"Warning: {results["label"]} t_sim longer than list t_sim. Some results migth no be taken in acount")
                if self.t_sim > results["t"][-1]:
                    ## Out of Bound handeling (keep last value)
                    i_t_last = np.argwhere(self["t"]>results["t"][-1])[0, 0]
                    v_eit_ = results.v_eit(t=self["t"][:i_t_last])
                    v_eit_oob = results.v_eit(t=self["t"][i_t_last:])*0+results.v_eit(i_t = [-1])
                    v_eit_ =np.concatenate([v_eit_, v_eit_oob])

                    v_eit_ = np.expand_dims(v_eit_,self.r_axis)
                else:
                    v_eit_ = np.expand_dims(results.v_eit(t=self["t"]),self.r_axis)
                self["v_eit"] = np.append(self["v_eit"], v_eit_, axis=self.r_axis)
                if include_rec:
                    v_rec_ = np.expand_dims(results.v_rec(t=self["t"]), self.r_axis)
                    self["v_rec"] = np.append(self["v_rec"], v_rec_, axis=self.r_axis)

            self.res_info[f"{self.n_res}"] = {
                "computation_time":results["computation_time"],
                "res_dir":results["res_dir"],
                "label":results["label"],
                "mesh_info":results["mesh_info"],
            }
            if "parameters" in results:
                # print(results["parameters"])
                self.res_info[f"{self.n_res}"].update(results["parameters"])
            else:
                print(DeprecationWarning("eit_class_results not up to date"))
            self.n_res += 1
        elif isinstance(results, str):
            self.add_results(eit_class_results(data=results), include_rec=include_rec)
        elif isinstance(results, list):
            rl = sort_list_res(results)
            for res in rl:
                self.add_results(res, include_rec=include_rec)
        elif results is None:
            pass
        else:
            print("warning: results type cannot be added")

    def res_where(self, to_check:str|list|dict):
        if isinstance(to_check, str):
            to_check = [to_check]
        ok_res = np.zeros(self.n_res, dtype=bool)
        if isinstance(to_check, dict):
            for i in range(self.n_res):
                ok_res[i] = (to_check.items() <= self.res_info[str(i)].items())
        for _t in to_check:
            for i in range(self.n_res):
                if not ok_res[i]:
                    ok_res[i] = (
                        _t in self.res_info[str(i)]["label"]
                        or _t in self.res_info[str(i)]["res_dir"]
                    )
        return ok_res

    def res_argwhere(self, to_check:str|list):
        list_res = np.arange(self.n_res)
        if isinstance(to_check, np.ndarray):
            ok_res = to_check
        else:
            ok_res = self.res_where(to_check)
        return list_res[ok_res]

    ## eit_class_results methods overwrite
    def v_0(self, i_e:np.ndarray|int|None=None, i_f:np.ndarray|int|None=None, i_p:np.ndarray|int|None=None, **kwgs):
        return super().v_0(i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)

    def get_idxs(self, i_res=0, i_t:np.ndarray|int|None=None, i_e:np.ndarray|int|None=None, i_f:np.ndarray|int|None=None, i_p:np.ndarray|int|None=None, n_t=None, **kwgs):
        idx_res = super().get_idxs(i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, n_t=n_t)
        i_res = set_idxs(i_res, self.n_res)
        idx_res_list = ()
        idx_res_list += (i_res,)
        for i in idx_res:
            idx_res_list += (i,)
        return idx_res_list


    ## Post processing
    def get_res(self, which:str="v_eit", i_res:np.ndarray|int|None=None, t:np.ndarray|float|None=None, i_t:np.ndarray|int|None=None, i_e:np.ndarray|int|None=None, i_f:np.ndarray|int|None=None, i_p:np.ndarray|int|None=None, v_abs:bool=False,**kwgs)->np.ndarray:
        if "_cap" in which:
            which = which.replace("_cap","")
            __meth_str = f"self.get_cap_res(which='{which}', i_res=i_res, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)"
        else:
            __meth_str = f"self.{which}(i_res=i_res, t=t,i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)"
        _v = eval(__meth_str)
        if v_abs:
            _v = np.abs(_v)
        return _v
    
    def error(self, which="v_eit", abs_err=True, i_res=None, i_res_ref=0, t=None, i_t:np.ndarray|int|None=None, i_e:np.ndarray|int|None=None, i_f:np.ndarray|int|None=None, i_p:np.ndarray|int|None=None, **kwgs):
        if i_res is None:
            i_res = np.arange(self.n_res)
            i_res = i_res[i_res!=i_res_ref]
        _v = self.get_res(which=which, i_res=i_res, t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
        _v_ref = self.get_res(which=which, i_res=i_res_ref, t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
        if abs_err:
            return _v - _v_ref
        else:
            return (_v - _v_ref)/_v_ref


    ## inconsistent output methods
    def _get_acap_i_res(self, i_l:int|np.ndarray, with_f:bool=True):
        if self.is_multi_freqs and with_f:
            return (i_l // (self.n_e*self.n_f)) % self.n_res
        return (i_l // self.n_e) % self.n_res

    def _get_line_ppt(self, i_l:int|np.ndarray, with_f:bool=True):
        return np.vstack((
            self._get_acap_i_res(i_l,  with_f=with_f),
            super()._get_line_ppt(i_l, with_f=with_f)
        ))

    def get_acap_ppt(self, thr:float=0.05, verbose:bool=False, store:Literal["default","overwrite","external"]="default", **kwgs):
        return super().get_acap_v_ppt(thr=thr, verbose=verbose, store=store, i_res=None, **kwgs)


    def get_acap_t_ppt(self, thr:float= 0.05, verbose:bool=False, store:Literal["default","overwrite","external"]="default", **kwgs):
        """
        Overwrite to impose `i_res=None`

        Parameters
        ----------
        thr : float, optional
            _description_, by default 0.05
        verbose : bool, optional
            _description_, by default False
        i_res : _type_, optional
            _description_, by default None

        Returns
        -------
        _type_
            _description_
        """
        kwgs["i_res"] = None
        return super().get_acap_t_ppt(thr=thr, verbose=verbose, store=store, **kwgs)

    def get_acap_v_ppt(self, thr=0.05, verbose=False, store:Literal["default","overwrite","external"]="default", **kwgs):
        kwgs["i_res"] = None
        return super().get_acap_v_ppt(thr=thr, verbose=verbose, store=store, **kwgs)


    def get_cap_i_t(self, thr:float=0.05, i_res:np.ndarray|int|None=None, **kwgs)->list:
        """
        Return the temporal steps of caps of each results

        Warning
        -------
        As CAP duration can change from one results to another, the time steps arrays can have different length. Thus, outputs are saved in list instead of numpy arrays. 

        Parameters
        ----------
        thr : float, optional
            proportion of the max change to use as threshold to detect the cap, by default 0.05
        i_res : np.ndarray | int | None, optional
            _description_, by default None

        Returns
        -------
        list
        """
        if not np.iterable(i_res):
            return super().get_cap_i_t(thr, i_res=i_res, **kwgs)
        i_res = set_idxs(i_res, self.n_res)
        _all_cap_i_t = [super().get_cap_i_t(thr, i_res=k, **kwgs) for k in i_res]
        return _all_cap_i_t
    
    def get_cap_i_t_lim(self, thr:float=0.05, i_cap=None, ext_factor=None, expr:str|None=None, i_res:np.ndarray|int|None=None, i_e:np.ndarray|int|None=None, i_f:np.ndarray|int|None=None, i_p:np.ndarray|int|None=None):
        if self._cap_ppt is None:
            self.get_acap_t_ppt(thr=thr, i_res=None)
        _quer=get_query(
        i_cap=i_cap,
        i_res=i_res,
        i_e=i_e,
        i_f=i_f,
        i_p=i_p,
        sup1=expr,
        )
        if _quer is not None:
            _sel_cap_ppt = self._cap_ppt.query(_quer)
        else:
            _sel_cap_ppt = self._cap_ppt
        _cap_i_t_lim = [_sel_cap_ppt["i_t_min"].min(),_sel_cap_ppt["i_t_max"].max()]

        # Extend the temporal range
        if ext_factor is not None:
            lim_range = (_cap_i_t_lim[1]-_cap_i_t_lim[0])
            lim_shift = int(((ext_factor-1)*lim_range)/2)
            _cap_i_t_lim[0] = max(0,_cap_i_t_lim[0]-lim_shift)
            _cap_i_t_lim[1] = min(self.n_t,_cap_i_t_lim[1]+lim_shift)
        return tuple(_cap_i_t_lim)


    def get_cap_res(self, thr:float=0.05, ext_factor=None, expr:str|None=None, which="v_eit", with_t:bool=False, i_res:np.ndarray|int|None=None, i_e:np.ndarray|int|None=None, i_f:np.ndarray|int|None=None, i_p:np.ndarray|int|None=None, v_abs:bool=False,**kwgs)->np.ndarray:
        i_res = set_idxs(i_res, self.n_res)
        i_t_lim = self.get_cap_i_t_lim(thr=thr, ext_factor=ext_factor, i_res=i_res, expr=expr)
        i_t = np.arange(*i_t_lim)
        _cap_res = self.get_res(which=which, i_res=i_res, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, v_abs=v_abs, **kwgs)
        if with_t:
            _cap_res = _cap_res, self["t"][i_t]
        return _cap_res

    def cap_duration(self, alpha=0.01, dv_pc=True, i_res=None, t=None, i_t:np.ndarray|int|None=None, i_e:np.ndarray|int|None=None, i_f:np.ndarray|int|None=None, i_p:np.ndarray|int|None=None, **kwgs):
        if i_res is None:
            i_res = np.arange(self.n_res)
        __dv = abs(self.get_res(i_res=i_res, t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, which="dv_eit",pc=dv_pc))
        __dv /= np.max(__dv, axis=0)
        return np.sum(__dv > alpha, axis=0)*self.dt

    ## numpy-like methodes
    def mean(self, which="v_eit", i_res=None, t=None, i_t:np.ndarray|int|None=None, i_e:np.ndarray|int|None=None, i_f:np.ndarray|int|None=None, i_p:np.ndarray|int|None=None, **kwgs):
        _v = self.get_res(which=which, i_res=i_res, t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
        return np.mean(_v, axis=0)

    def std(self, which="v_eit", i_res=None, t=None, i_t:np.ndarray|int|None=None, i_e:np.ndarray|int|None=None, i_f:np.ndarray|int|None=None, i_p:np.ndarray|int|None=None, **kwgs):
        _v = self.get_res(which=which, i_res=i_res, t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
        return np.std(_v, axis=0)


def res_list_from_labels(res_dnames:str|list, labels:str|list)->eit_results_list:
    fname_list = []
    if not isinstance(res_dnames, list):
        res_dnames = [res_dnames]
    if not isinstance(labels, list):
        labels = [labels]
    for dname in res_dnames:
        if not os.path.isdir(dname):
            print(f"results directory not found: {dname}")
        for label in labels:
                fem_res_file = f"{dname}/{label}_fem.json"
                if os.path.isfile(fem_res_file):
                    fname_list += [fem_res_file]
                else:
                    print(f"results file not found: {fem_res_file}")
    return eit_results_list(results=fname_list)

def sort_list_res(list_res:list):
    lr = []
    t_sim = 0
    for res_i in list_res: 
        if isinstance(res_i, eit_class_results):
            res = res_i
        else:
            res = eit_class_results(data=res_i)
        if res["t"][-1] > t_sim:
            t_sim = res["t"][-1]
            lr = [res] + lr
        else:
            lr += [res]
    return lr
