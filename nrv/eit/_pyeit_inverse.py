import numpy as np
import matplotlib.pyplot as plt
from typing import Literal
from pyeit.eit import jac, bp
import pyeit.eit.protocol as protocol
import pyeit.mesh as mesh

from . import eit_inverse
from .results import eit_forward_results

pyeit_methods = {
    "jac":{"solver":jac.JAC, "default":{"p":0.50, "lamb":1e-3, "method":"kotre"}},
    "bp":{"solver":bp.BP, "default":{}}
}


class pyeit_inverse(eit_inverse):
    def __init__(self, data:None|eit_forward_results=None, method:Literal["jac", "bp"]="jac", **kwgs):

        # Attribute instantiated when data is set
        # NOTE Must be initialised before super().__init__
        self.n_elec:int|None = None
        self.inj_offset:int|None = None
        self.mesh_obj: mesh.PyEITMesh|None = None
        self.protocol_obj: protocol.PyEITProtocol|None = None
        self.v0:None|np.ndarray = None
        self.inv_obj = None


        super().__init__(data, **kwgs)
        self.method = method


    @eit_inverse.data.setter
    def data(self, data:None|eit_forward_results):
        if data is None:
            self._data=data
        elif isinstance(data, eit_forward_results) and data.is_multi_patern:
            self._data=data
            self.n_elec = data.n_e
            self.inj_offset = (self.data["p"][0][1] - self.data["p"][0][0])%self.n_elec
            self.protocol_obj = protocol.create(n_el=self.n_elec, dist_exc=self.inj_offset, step_meas=1, parser_meas="fmmu")
            self.update_mesh()

        else:
            raise TypeError("data must be None or eit_forward_results")



    def fromat_data(self, i_t:int=0, i_f:int=0, i_res:int=0,verbose:bool=False)->np.ndarray:
        if self.has_data:
            
            if self.inj_offset == 1:
                i_e_skiped = 2
            else:
                i_e_skiped = 3
            n_rec_per_inj = self.n_elec - (i_e_skiped + 1)
            v_forward = np.zeros(self.n_elec * n_rec_per_inj)

            i_rec = np.arange(n_rec_per_inj)
            mask = (i_e_skiped-1)*(1+i_rec>=(self.inj_offset-1))

            for i_p, (i_ep, i_en) in enumerate(self.data["p"]):
                i_e2 = (1 + i_ep + i_rec + mask) % self.n_elec
                i_e1 = (i_e2+1)% self.n_elec
                if verbose:
                    for _i in range(n_rec_per_inj):
                        print((i_ep, i_en), (i_e1[_i], i_e2[_i]))

                v_forward[i_p*n_rec_per_inj : (i_p+1)*n_rec_per_inj] = (
                    self.data.v_eit(i_t=i_t, i_f=i_f, i_p=i_p, i_e=i_e1, signed=True) -
                    self.data.v_eit(i_t=i_t, i_f=i_f, i_p=i_p, i_e=i_e2, signed=True)
                )
            return v_forward

    def update_mesh(self, newmesh:mesh.PyEITMesh=None, h0=0.05):
        if newmesh is not None:
            self.mesh_obj = newmesh
        else:
            self.mesh_obj = mesh.create(n_el=self.n_elec, h0=h0)
        self.inv_obj = None

    def set_inversor(self, method:None|Literal["jac", "bp"]=None, inv_params:None|dict=None):
        if method is not None:
            self.method = method
        if inv_params is None:
            inv_params = pyeit_methods[self.method]["default"]

        self.inv_obj = pyeit_methods[self.method]["solver"](self.mesh_obj, self.protocol_obj)
        self.inv_obj.setup(**inv_params)



    # ---------------------- #
    # Reconstruction methods #
    # ---------------------- #
    def _run_inverse(self, i_to_solve=None, i_t:int=0, i_f:int=0, i_res:int=0):
        i_t, i_f, i_res = self._get_i_to_solve(i_to_solve=i_to_solve, i_t=i_t, i_f=i_f, i_res=i_res)
        if self.v0 is None:
            self.v0 = self.fromat_data(i_t=0, i_f=i_f, i_res=i_res)
        if self.inv_obj is None:
            self.set_inversor()

        v1 = self.fromat_data(i_t=i_t, i_f=i_f, i_res=i_res)
        return self.inv_obj.solve(v1, self.v0, normalize=True), (i_t, i_f, i_res)
    

    # ------------------- #
    # Plot images methods #
    # ------------------- #
    def plot(self, ax:plt.Axes, i_t:int=0, i_f:int=0, i_res:int=0, filter=None, **kwgs):
        # extract node, element, alpha
        _ds = self.get_results(i_t, i_f, i_res)

        if callable(filter):
            _ds = filter(_ds)
        rotation_90_matrix = np.array([[0, -1],
                                       [1,  0]])
        pts = self.mesh_obj.node[:,[0,1]] @ rotation_90_matrix
        tri = self.mesh_obj.element

        ax.tripcolor(pts[:, 0], pts[:, 1], tri, _ds)
        ax.axis("equal")
        ax.set_axis_off()

    def cbar(self, ax:plt.Axes, i_to_solve=None, i_t:int=0, i_f:int=0, i_res:int=0, **kwgs):
        # extract node, element, alpha
        _ds = self.get_results(i_t, i_f, i_res)
        _cbar = plt.colorbar()

