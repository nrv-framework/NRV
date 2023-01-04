import numpy as np

from mpi4py import MPI 
import scipy
from dolfinx import *
from dolfinx.fem import (FunctionSpace, Function, Expression)
from dolfinx.io.gmshio import read_from_msh, model_to_mesh
from dolfinx.io.utils import XDMFFile
from dolfinx.geometry import (BoundingBoxTree, compute_collisions, compute_colliding_cells)
import gmsh


from ....backend.file_handler import json_load, json_dump, rmv_ext

###############
## Functions ##
###############
def is_sim_res(result):
    """
    check if an object is a SimResult, return True if yes, else False

    Parameters
    ----------
    stim : object
        object to test

    Returns
    -------
    bool
        True it the type is a SimResult object
    """
    return isinstance(result, SimResult)

def mesh_from_meshfile(mesh_file):
    """
    overload of dolfinx.io.gmshio.read_from_msh with no verbose from gmsh
    """
    mesh_file = rmv_ext(mesh_file) + ".msh"
    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.model.add("Mesh from file")
    gmsh.merge(mesh_file)
    output = model_to_mesh(gmsh.model, comm=MPI.COMM_WORLD, rank=0, gdim=3)
    gmsh.finalize()
    return output[0]


def V_from_meshfile(mesh_file, elem=('Lagrange', 1)):
    mesh = mesh_from_meshfile(mesh_file)
    V = FunctionSpace(mesh, elem)
    return V
    

class SimResult:
    def __init__(self, mesh_file="", domain=None, elem=('Lagrange', 1), V=None, vout=None,comm=MPI.COMM_WORLD):
        self.mesh_file = mesh_file

        self.domain = domain
        self.V = V
        self.elem = elem
        self.vout = vout
        self.comm = comm

    def set_sim_result(self, mesh_file="", domain=None, V=None, elem=None,vout=None, comm=None):
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
    
    def save_sim_result(self, file, ftype=None):
        if ftype == 'xdmf':
            fname = rmv_ext(file) + '.xdmf'
            with XDMFFile(self.comm, fname, "w") as file:
                file.write_mesh(mesh_from_meshfile(self.mesh_file))
                file.write_function(self.vout)
        else:
            fname = rmv_ext(file) + '.sres'
            mdict = {"mesh_file":self.mesh_file, "element": self.elem,"vout":self.vout.vector[:]}
            scipy.io.savemat(fname, mdict)
            return mdict

    def load_sim_result(self, file):
        fname = rmv_ext(file) + '.sres'
        mdict = scipy.io.loadmat(fname)
        self.mesh_file = mdict['mesh_file'][0]
        self.elem = (mdict['element'][0].strip(), int(mdict['element'][1]))
        if self.domain is None:
            self.domain = mesh_from_meshfile(self.mesh_file)
            self.V = FunctionSpace(self.domain, self.elem)
        self.vout = Function(self.V)
        self.vout.vector[:] = mdict['vout']

    
    #############
    ## methods ##
    #############

    def vector(self):
        return self.vout.x.array

    def aline_V(self, res2):
        """
        
        """
        if is_sim_res(res2):
            if self.mesh_file == res2.mesh_file:
                expr = Expression(self.vout, res2.V.element.interpolation_points())
                self.vout = Function(res2.V)
                self.vout.interpolate(expr)
                self.V = res2.V
            else:
                print("Error: to aline mesh function reslults must have the same meshfile")
        else:
            print("Error: mesh function alinment must be done with SimResult")

         
    def eval(self, X):
        """
        Eval the result field at X position

        """
        N = len(X)
        tree = BoundingBoxTree(self.domain, self.domain.geometry.dim)
        cells_candidates = compute_collisions(tree, X)
        cells_colliding = compute_colliding_cells(self.domain, cells_candidates, X)        
        cells = [cells_colliding.links(i)[0] for i in range(N)]

        return self.vout.eval(X, cells)

        

    #####################
    ## special methods ##
    #####################

    """
    def __abs__(self):
        res = SimResult(mesh_file=self.mesh_file, V=self.V)
        res.vout = df.project(abs(self.vout), self.V, solver_type=self.solver,\
            preconditioner_type=self.preconditioner, form_compiler_parameters=self.compiler_parameters)
        return res
    """
    def __neg__(self):
        expr = Expression(-self.vout, self.V.element.interpolation_points())
        res = SimResult(mesh_file=self.mesh_file, V=self.V)
        res.vout = Function(self.V)
        self.vout.interpolate(expr)

        return res

    def __add__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(self.vout + b.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(self.vout + b, self.V.element.interpolation_points())

        C = SimResult(mesh_file=self.mesh_file, V=self.V)
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __sub__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(self.vout - b.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(self.vout - b, self.V.element.interpolation_points())

        C = SimResult(mesh_file=self.mesh_file, V=self.V)
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __mul__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(self.vout * b.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(self.vout * b, self.V.element.interpolation_points())

        C = SimResult(mesh_file=self.mesh_file, V=self.V)
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __radd__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(b.vout + self.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(b + self.vout, self.V.element.interpolation_points())

        C = SimResult(mesh_file=self.mesh_file, V=self.V)
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __rsub__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(b.vout - self.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(b - self.vout, self.V.element.interpolation_points())

        C = SimResult(mesh_file=self.mesh_file, V=self.V)
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __rmul__(self, b):
        if is_sim_res(b):
            self.aline_V(b)
            expr = Expression(b.vout * self.vout, self.V.element.interpolation_points())
        else:
            expr = Expression(b * self.vout, self.V.element.interpolation_points())

        C = SimResult(mesh_file=self.mesh_file, V=self.V)
        C.vout = Function(self.V)
        C.vout.interpolate(expr)
        return C

    def __eq__(self, b):
        if is_sim_res(b):
            if b.mesh_file == self.mesh_file:
                if np.allclose(self.vector(), b.vector()):
                    return True
        return False

    def __ne__(self, b): # self != b
        return not self == b
