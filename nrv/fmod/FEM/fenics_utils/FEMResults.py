"""
NRV-:class:`.FEMResults` handling.
"""

import gmsh
import numpy as np
import scipy
from dolfinx.fem import Expression, Function, functionspace
from dolfinx.io.gmshio import model_to_mesh
from dolfinx.io.utils import XDMFFile, VTXWriter, VTKFile
from dolfinx.cpp.mesh import entities_to_geometry
from dolfinx.geometry import (
bb_tree,
compute_colliding_cells,
compute_collisions_points,
compute_closest_entity,
compute_distance_gjk,
create_midpoint_tree,
)
from mpi4py import MPI


from ....backend.file_handler import rmv_ext
from ....backend.log_interface import rise_error, rise_warning
from ....backend.parameters import parameters
from ....backend.MCore import MCH, synchronize_processes
from ....backend.NRV_Class import NRV_class
from ..mesh_creator.MshCreator import (
    is_MshCreator,
    clear_gmsh,
)




###############
## Functions ##
###############
def is_sim_res(result):
    """
    check if an object is a FEMResults, return True if yes, else False

    Parameters
    ----------
    result : object
        object to test

    Returns
    -------
    bool
        True it the type is a FEMResults object
    """
    return isinstance(result, FEMResults)


def save_sim_res_list(sim_res_list, fname, dt=1.):
    r"""
    save a list of SimResults in a .bp folder which can be open with PrarView

    Parameters
    ----------
    sim_res_list : list(FEMResults)
        list of :class:`.FEMResults` to be saved
    fname : str
        File name and path
    ftype : str 
        - if True .bp folder, else saved in a .xdmf file.
    dt : float
        time step between each results

    Warning
    -------
    For this function to work dolfinx and ParaView must be up to date: 
        -   dolfinx \\(\\geq\\) 0.8.0
        -   ParaView \\(\\geq\\) 5.12.0
    """
    N_list = len(sim_res_list)
    fname = rmv_ext(fname) + ".bp"
    vcp = sim_res_list[0].vout
    vtxf = VTXWriter(sim_res_list[0].domain.comm, fname, vcp)
    for i in range(N_list):
        vcp = sim_res_list[i].vout
        vtxf.write(i * dt)
    vtxf.close()



def read_gmsh(mesh, comm=MPI.COMM_WORLD, rank=0, gdim=3):
    """
    Given a mesh_file or a MeshCreator returns mesh cell_tags and facet_tags
    (see dolfinx.io.gmshio.model_to_mesh for more details)
    NB: copy of dolfinx.io.gmshio.read_from_msh verbose from gmsh

    Parameters
    ----------
    mesh_file : str,
        Path and name of mesh file
        NB: extention is not required but must be a .msh file
    comm            : tupple (str, int)
        The MPI communicator to use for mesh creation
    rank            : tupple (str, int)
        The rank the Gmsh model is initialized on
    gdim            : int
        dimension of the mesh, by default 3

    Returns
    -------
    output  :  tuple(3)
        (domain, cell_tag, facet_tag)
    """
    if isinstance(mesh, str):
        mesh_file = rmv_ext(mesh) + ".msh"
        clear_gmsh()
        gmsh.initialize()
        gmsh.option.setNumber("General.Verbosity", 2)
        gmsh.model.add("Mesh from file")
        gmsh.merge(mesh_file)
        output = model_to_mesh(gmsh.model, comm=comm, rank=rank, gdim=gdim)
        gmsh.finalize()
    elif is_MshCreator(mesh):
        output = model_to_mesh(mesh.model, comm=comm, rank=rank, gdim=gdim)
    else:
        rise_error("mesh should be either a filename or a MeshCreator")
    return output


def domain_from_meshfile(mesh_file):
    """
        return only the domain from mesh_file

    Parameters
    ----------
    mesh_file : str
        Path and name of mesh file
        NB: extention is not required but must be a .msh file

    Returns
    -------
        output  :
            domain of the mesh contain in the mesh_file
    """
    return read_gmsh(mesh_file)[0]


def V_from_meshfile(mesh_file, elem=("Lagrange", 1)):
    mesh = domain_from_meshfile(mesh_file)
    V = functionspace(mesh, elem)
    return V


def closest_point_in_mesh(mesh, point, tree, tdim, midpoint_tree):
    points = np.reshape(point, (1,3))
    entity = compute_closest_entity(tree, midpoint_tree, mesh, points)
    mesh_geom = mesh.geometry.x
    geom_dofs = entities_to_geometry(mesh._cpp_object, tdim, entity, False)
    mesh_nodes = mesh_geom[geom_dofs][0]
    displacement = compute_distance_gjk(points, mesh_nodes)
    return entity, points[0] - displacement

class FEMResults(NRV_class):
    """
    Result of a FEMSimulation.
    Store the resulting function space giving the possibility to apply basic mathematical
    operations on multiple results
    """

    def __init__(
        self,
        mesh_file="",
        domain=None,
        elem=("Lagrange", 1),
        V=None,
        vout=None,
        comm=MPI.COMM_WORLD,
    ):
        """
        initialisation of the FEMParameters:

        Parameters
        ----------
        mesh_file       :str
            mesh directory and file name: by default ""
        domain       : None or mesh
            mesh domain on which the result is defined, by default None
        elem            :tupple (str, int)
            if None, ("Lagrange", 1), else (element type, element order), by default None
        V       : None or dolfinx.fem.functionspace
            functionspace on which the result is defined, by default None
        vout       : None or dolfinx.fem.Function
            Function resulting from the FEMSimulation, by default None
        comm            :int
            The MPI communicator to use for mesh creation, by default MPI.COMM_WORLD
        """
        super().__init__()
        self.type = "simresult"
        self.mesh_file = mesh_file
        self.domain = domain
        self.V = V
        self.elem = elem
        self.vout = vout
        self.comm = comm

    def set_sim_result(
        self, mesh_file="", domain=None, V=None, elem=None, vout=None, comm=None
    ):
        if mesh_file != "":
            self.mesh_file = mesh_file
        if domain is not None:
            self.domain = domain
        if elem is not None:
            self.elem = elem
        if V is not None:
            self.V = V
        if vout is not None:
            self.vout = vout
        self.comm = comm

    def save(self, file, ftype="vtx", overwrite=True, t=0.0):
        fname = rmv_ext(file)
        if ftype.lower() == "vtx": #and dfx_utd:
            fname += ".bp"
            with VTXWriter(self.domain.comm, fname, self.vout, "bp4") as f:
                f.write(t)
        elif ftype == "xdmf":
            fname += ".xdmf"
            with XDMFFile(self.comm, fname, "w") as file:
                if not overwrite:
                    file.parameters.update(
                        {"functions_share_mesh": True, "rewrite_function_mesh": False}
                    )
                else:
                    file.write_mesh(self.domain)
                file.write_function(self.vout)
        else:
            fname += ".sres"
            mdict = {
                "mesh_file": self.mesh_file,
                "element": self.elem,
                "vout": self.vout.vector[:],
            }
            scipy.io.savemat(fname, mdict)
            return mdict

    def load(self, file):
        fname = rmv_ext(file) + ".sres"
        mdict = scipy.io.loadmat(fname)
        self.mesh_file = mdict["mesh_file"][0]
        self.elem = (mdict["element"][0].strip(), int(mdict["element"][1]))
        if self.domain is None:
            self.domain = domain_from_meshfile(self.mesh_file)
            self.V = functionspace(self.domain, self.elem)
        self.vout = Function(self.V)
        self.vout.vector[:] = mdict["vout"]

    def save_sim_result(self, file, ftype="vtx", overwrite=True):
        rise_warning("save_sim_result is a deprecated method use save")
        self.save(file=file, ftype=ftype, overwrite=overwrite)

    def load_sim_result(self, data="sim_result.json"):
        rise_warning("load_sim_result is a deprecated method use load")
        # self.load(data=data)
        # FIXME: data does not exist yet in load method
        self.load(file=data)

    #############
    ## methods ##
    #############

    def vector(self):
        return self.vout.x.array

    def aline_V(self, res2):
        """
        Change the function space of the result to aline with the result of another FEMResults

        Parameters
        ----------
        res2 : FEMResults
            result to aline with
        """
        if is_sim_res(res2):
            if self.mesh_file == res2.mesh_file:
                expr = Expression(self.vout, res2.V.element.interpolation_points())
                self.vout = Function(res2.V)
                self.vout.interpolate(expr)
                self.V = res2.V
            else:
                rise_error(
                    "To aline mesh function reslults must have the same meshfile"
                )
        else:
            rise_error("Mesh function alinment must be done with FEMResults")

    def eval(self, X, is_multi_proc=False):
        """
        Eval the result field at X position
        """
        X = np.array(X)
        N = len(X)
        cells = []
        points_on_proc = []
        tdim = self.domain.geometry.dim
        n_entities_local = self.domain.topology.index_map(tdim).size_local\
            + self.domain.topology.index_map(tdim).num_ghosts
        entities = np.arange(n_entities_local, dtype=np.int32)
        midpoint_tree = create_midpoint_tree(self.domain, tdim, entities)
        tree = bb_tree(self.domain, tdim)
        # Find cells whose bounding-box collide with the the points
        cells_candidates = compute_collisions_points(tree, X)

        # Choose one of the cells that contains the point
        cells_colliding = compute_colliding_cells(self.domain, cells_candidates, X)
        for i in range(N):
            cell = cells_colliding.links(i)
            if is_multi_proc:
                if len(cell) > 0:
                    points_on_proc.append(X[i])
                    cells.append(cells_colliding.links(i)[0])
            else:
                #point not in the mesh
                if len(cell) == 0:
                    cell, x_closest = closest_point_in_mesh(self.domain, X[i], tree, tdim, midpoint_tree)
                    rise_warning(
                        X[i], " not found in mesh, value of ", x_closest, " reused"
                    )
                    #compute_colliding_cells(self.domain, cells_candidates, X)
                    cells += [cell[0]]
                else:
                    cells += [cell[0]]
        if is_multi_proc:
            points_on_proc = np.array(points_on_proc, dtype=np.float64)
            s_values = self.vout.eval(points_on_proc, cells)
            if len(points_on_proc) > 0:
                m_values = np.concatenate((points_on_proc.T, s_values.T)).T
            else:
                m_values = np.array([])
            m_values = self.comm.gather(m_values.tolist(), root=0)
            if MCH.do_master_only_work():
                val = []
                for i in range(len(m_values)):
                    for j in range(len(m_values[i])):
                        val += [m_values[i][j]]
                val = np.array(val)
                values = np.empty((N), dtype="float64")
                for i, p in enumerate(X):
                    i_p = np.where((np.isclose(val[:, :3], p)).all(axis=1))[0]
                    if len(i_p > 0):
                        values[i] = val[i_p[0], 3]
                    else:
                        values[i] = values[i - 1]
            else:
                values = np.empty((N), dtype="float64")
            synchronize_processes()
            self.comm.Bcast(values, root=0)
        else:
            values = self.vout.eval(X, cells)
            if N > 1:
                values = values[:, 0]
        return values

    #####################
    ## special methods ##
    #####################
    def __abs__(self):
        res = FEMResults(
            mesh_file=self.mesh_file,
            V=self.V,
            domain=self.domain,
            elem=self.elem,
            comm=self.comm,
        )
        if self.vout is not None:
            expr = Expression(abs(self.vout), self.V.element.interpolation_points())
            res.vout = Function(self.V)
            self.vout.interpolate(expr)
        return res

    def __neg__(self):
        res = FEMResults(
            mesh_file=self.mesh_file,
            V=self.V,
            domain=self.domain,
            elem=self.elem,
            comm=self.comm,
        )
        if self.vout is not None:
            expr = Expression(-1 * self.vout, self.V.element.interpolation_points())
            res.vout = Function(self.V)
            self.vout.interpolate(expr)
        return res

    def __add__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(self.vout + b.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(self.vout + b, self.V.element.interpolation_points())

        C = FEMResults(
            mesh_file=self.mesh_file,
            V=self.V,
            domain=self.domain,
            elem=self.elem,
            comm=self.comm,
        )
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __sub__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(self.vout - b.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(self.vout - b, self.V.element.interpolation_points())

        C = FEMResults(
            mesh_file=self.mesh_file,
            V=self.V,
            domain=self.domain,
            elem=self.elem,
            comm=self.comm,
        )
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __mul__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(self.vout * b.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(self.vout * b, self.V.element.interpolation_points())

        C = FEMResults(
            mesh_file=self.mesh_file,
            V=self.V,
            domain=self.domain,
            elem=self.elem,
            comm=self.comm,
        )
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __radd__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(b.vout + self.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(b + self.vout, self.V.element.interpolation_points())

        C = FEMResults(
            mesh_file=self.mesh_file,
            V=self.V,
            domain=self.domain,
            elem=self.elem,
            comm=self.comm,
        )
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __rsub__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(b.vout - self.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(b - self.vout, self.V.element.interpolation_points())

        C = FEMResults(
            mesh_file=self.mesh_file,
            V=self.V,
            domain=self.domain,
            elem=self.elem,
            comm=self.comm,
        )
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __rmul__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(b.vout * self.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(b * self.vout, self.V.element.interpolation_points())

        C = FEMResults(
            mesh_file=self.mesh_file,
            V=self.V,
            domain=self.domain,
            elem=self.elem,
            comm=self.comm,
        )
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __eq__(self, b):
        if is_sim_res(b):
            if b.mesh_file == self.mesh_file:
                if np.allclose(self.vector(), b.vector()):
                    return True
        return False

    def __ne__(self, b):  # self != b
        return not self == b
