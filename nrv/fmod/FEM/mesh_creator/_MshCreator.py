"""
NRV-:class:`.MshCreator` handling.
"""

import math
import os

import gmsh
import numpy as np

from ....utils.geom._cshape import CShape
from ....backend._file_handler import rmv_ext
from ....backend._log_interface import pass_info, rise_error, rise_warning
from ....backend._NRV_Class import NRV_class
from ....backend._parameters import parameters

dir_path = parameters.nrv_path + "/_misc"


###############
## Constants ##
###############

pi = np.pi


def is_MshCreator(object):
    """
    Check if an object is a MshCreator, return True if yes, else False

    Parameters
    ----------
    result : object
        object to test

    Returns
    -------
    bool
        True it the type is a MshCreator object
    """
    return isinstance(object, MshCreator)


def clear_gmsh():
    if gmsh.isInitialized():
        gmsh.finalize()


class MshCreator(NRV_class):
    """
    Class handling the creation of a gmsh mesh (https://gmsh.info/doc/texinfo/gmsh.html)
    Contains methodes dealing with the mesh geometries, physical domains and feilds
    """

    def __init__(self, D=3, ver_level=None):
        """
        initialisation of the MshCreator

        Parameters
        ----------
        D           : int(1,2,3)
            mesh dimension
        ver_level   : int(0,1,2,3,4,5,99)
            verbosity level of gmsh (see MshCreator.set_verbosity), by default 2
        """
        super().__init__()
        self.type = "GMSH"
        self.D = D
        self.entities = {}
        self.volumes = []
        self.volumes_com = []
        self.volumes_bd = []

        self.faces = []
        self.faces_com = []
        self.faces_bd = []

        self.id_domains = np.array([], dtype=int)
        self.dim_domains = np.array([], dtype=int)
        self.name_domain = []

        self.file = ""

        self.Nfeild = 0
        self.res = 1

        clear_gmsh()
        gmsh.initialize()

        self.verbosity_level = ver_level
        self.set_verbosity(ver_level)
        self.model = gmsh.model
        self.model.add("DFG 3D")

        # Mesh properties
        self.is_generated = False
        self.N_entities = 0
        self.N_nodes = 0
        self.N_elements = 0

        self.n_proc = None
        self.n_core = None

    @property
    def n_core(self):
        return self.n_proc

    @n_core.setter
    def n_core(self, i: int | None = None):
        if i is None:
            self.n_proc = parameters.GMSH_Ncores
        else:
            self.n_proc = i
        gmsh.option.setNumber("General.NumThreads", self.n_proc)
        if self.n_proc > 1:
            gmsh.option.set_number("Mesh.Algorithm3D", 10)
        else:
            gmsh.option.set_number("Mesh.Algorithm3D", 1)

    @n_core.deleter
    def n_core(self):
        n_core = None

    def set_ncore(self, i: int | None = None) -> None:
        """_summary_

        Parameters
        ----------
        i : int | None, optional
            _description_, by default None
        """

    #####################
    ## special methods ##
    #####################
    def get_obj(self):
        """
        update and return list of mesh entities

        Returns
        -------
        self.entities       :dict
        """
        return self.entities

    def get_volumes(self, com=False, bd=False):
        """
        update and return list of mesh volumes (optional: with their center of mass)

        Returns
        -------
        self.faces      :list[tuple]
        """
        self.model.occ.synchronize()
        self.volumes = self.model.getEntities(dim=3)
        self.volumes_com = []
        self.volumes_bd = []
        for i in range(len(self.volumes)):
            volume = self.volumes[i]
            self.volumes_com += [
                np.round(self.model.occ.getCenterOfMass(volume[0], volume[1]), 4)
            ]
            self.volumes_bd += [
                np.round(self.model.occ.getBoundingBox(volume[0], volume[1]), 4)
            ]

        if com:
            if bd:
                return self.volumes, self.volumes_com, self.volumes_bd
            else:
                return self.volumes, self.volumes_com
        else:
            if bd:
                return self.volumes, self.volumes_bd

        return self.volumes

    def get_info(self, verbose=False):
        entities = self.model.getEntities()
        nodeTags = self.model.mesh.getNodes()[0]
        elemTags = self.model.mesh.getElements()[1]

        self.N_entities = len(entities)
        self.N_nodes = len(nodeTags)
        self.N_elements = sum(len(i) for i in elemTags)
        if verbose:
            pass_info("Mesh properties:")
            pass_info("Number of processes : " + str(self.n_proc))
            pass_info("Number of entities : " + str(self.N_entities))
            pass_info("Number of nodes : " + str(self.N_nodes))
            pass_info("Number of elements : " + str(self.N_elements))
        return self.n_proc, self.N_entities, self.N_nodes, self.N_elements

    def get_mesh_info(self, verbose=False):
        rise_warning("DEPRECATED method use get_info instead")
        self.get_info(verbose=verbose)

    def get_faces(self, com=False, bd=False):
        """
        update and return list of mesh face (optional: with their center of mass)

        Returns
        -------
         self.faces     :list[tuple]
        """
        self.model.occ.synchronize()
        self.faces = self.model.getEntities(dim=2)
        self.faces_com = []
        self.faces_bd = []
        for i in range(len(self.faces)):
            face = self.faces[i]
            self.faces_com += [
                np.round(self.model.occ.getCenterOfMass(face[0], face[1]), 4)
            ]
            self.faces_bd += [
                np.round(self.model.occ.getBoundingBox(face[0], face[1]), 4)
            ]

        if com:
            if bd:
                return self.faces, self.faces_com, self.faces_bd
            else:
                return self.faces, self.faces_com
        else:
            if bd:
                return self.faces, self.faces_com
        return self.faces

    def get_res(self):
        """
        return the global resolution saved (usefull when no field are set)

        Returns
        -------
        res     :float
            global resolution saved in the object
        """
        return self.res

    def set_res(self, new_res):
        """
        set the global resolution saved (usefull when no field are set)

        Parameters
        ----------
        new_res     :float
            global resolution to set the object
        """
        self.res = new_res

    def set_verbosity(self, i=None):
        """
        from gmsh: Level of information printed on the terminal and the message console.

        Parameters
        ----------
        i     : int (1, 2, 3, 4, 5 or 99)
            - 0, silent except for fatal errors
            - 1, +errors
            - 2, +warnings
            - 3, +direct
            - 4, +information
            - 5, +status
            - 99, +debug
        """
        if i is None:
            i = parameters.VERBOSITY_LEVEL
        self.verbosity_level = i
        gmsh.option.setNumber("General.Verbosity", self.verbosity_level)

    def set_chara_blen(self, i=0):
        """
        from gmsh: Extend characteristic lengths from the boundaries inside the surface/volume

        Parameters
        ----------
        i   : int, float, bool
            Parameter value, by default 0
        """
        i = float(i)
        gmsh.option.set_number("Mesh.CharacteristicLengthExtendFromBoundary", i)

    ##############################################################################################
    #######################################   geometry methods  ##################################
    ##############################################################################################

    def add_point(self, x=0, y=0, z=0):
        """
        add a point to the mesh

        Parameters
        ----------
        x        : float
            x position of the first face center
        y        : float
            y position of the first face center
        z        : float
            z position of the first face center

        Returns
        -------
        point    : int
            id of the added object
        """
        point = self.model.occ.addPoint(x, y, z)
        self.model.occ.synchronize()
        return point

    def add_line(self, X0, X1):
        """
        add a line to the mesh

        Parameters
        ----------
        X0       : int or tupple(3)
            x position of the first face center
        X1       : int or tupple(3)
            y position of the first face center

        Returns
        -------
        line    : int
            id of the added object
        """
        if isinstance(X0, int):
            ix0 = X0
        elif np.iterable(X0):
            if len(X0) != self.D:
                rise_error("not enough dimension given in add_line")
            else:
                ix0 = self.add_point(X0[0], X0[1], X0[2])

        if isinstance(X1, int):
            ix0 = X0
        elif np.iterable(X1):
            if len(X1) != self.D:
                rise_error("not enough dimension given in add_line")
            else:
                ix1 = self.add_point(X1[0], X1[1], X1[2])
        line = self.model.occ.addLine(ix0, ix1)
        self.model.occ.synchronize()
        return line

    def add_box(self, x=0, y=0, z=0, ax=5, ay=1, az=1):
        """
        add a box to the mesh

        Parameters
        ----------
        x       : float
            x position of the first face center
        y       : float
            y position of the first face center
        z       : float
            z position of the first face center
        ax      : float
            Box length along x
        ay      : float
            Box length along y
        az      : float
            Box length along z

        Returns
        -------
        box    : int
            id of the added object
        """
        if self.D == 3:
            parameters = {"x": x, "y": y, "z": z, "ax": ax, "ay": ay, "az": az}
            box = self.model.occ.addBox(x, y, z, ax, ay, az)
            self.model.occ.synchronize()
            bounds = self.model.getEntities(dim=2)[-6:]
            self.entities[box] = {
                "type": "box",
                "parameters": parameters,
                "bounds": bounds,
                "dim": 3,
            }
            return box
        else:
            rise_warning("Not added : add_cylinder requiere 3D mesh")
            return None

    def add_from_cshape(
        self,
        shape: CShape,
        n_pts_trace: int = 100,
        x: float = 0,
        dx: float = 10,
        res: None | float = None,
    ):
        """
        genertate a volume by extruding a :class:`....utils.geom._cshape.CShape` along

        Warining
        --------
        Not fully implemented

        Parameters
        ----------
        shape       : CShape
            shape to set as initial
        n_pts_trace       : float
            z position of the x-min face center
        x       : float
            x position of the x-min face center
        dx       : float
            Cylinder length along x

        Returns
        -------
        cyl    : int
            id of the added object
        """
        if res is not None:
            # NOTE TC - alpha is arbitrarily set to 5 see if it needs to be access
            alpha = 5
            n_pts_trace = alpha * round(shape.perimeter / res)
        pt_tags = []
        y_trace, z_trace = shape.get_trace(n_theta=n_pts_trace)

        # Create OCC points
        for y, z in zip(y_trace, z_trace):
            pt_tags.append(gmsh.model.occ.addPoint(x, y, z))

        # Connect with a periodic B-spline curve (closed loop)
        curve = gmsh.model.occ.addBSpline(pt_tags + [pt_tags[0]])

        # Make curve loop and surface
        loop = gmsh.model.occ.addCurveLoop([curve])
        surf = gmsh.model.occ.addPlaneSurface([loop])
        gmsh.model.occ.synchronize()

        if self.D == 3:
            cyl = gmsh.model.occ.extrude([(2, surf)], dx, 0, 0)
            gmsh.model.occ.synchronize()
        return cyl

    def add_cylinder(self, x=0, y=0, z=0, L=5, R=1):
        """
        add a x-oriented cylinder to mesh entities

        Parameters
        ----------
        x       : float
            x position of the x-min face center
        y       : float
            y position of the x-min face center
        z       : float
            z position of the x-min face center
        L       : float
            Cylinder length along x
        R       : float
            Cylinder radius

        Returns
        -------
        cyl    : int
            id of the added object
        """
        if self.D == 3:
            parameters = {"x": x, "y": y, "z": z, "L": L, "R": R}
            cyl = self.model.occ.addCylinder(x, y, z, L, 0, 0, R)
            self.model.occ.synchronize()
            bounds = self.model.getEntities(dim=2)[-3:]
            self.entities[cyl] = {
                "type": "cylinder",
                "parameters": parameters,
                "bounds": bounds,
                "dim": 3,
            }
            return cyl
        else:
            rise_warning("Not added : add_cylinder requiere 3D mesh")
            return None

    def add_cone(self, x=0, y=0, z=0, L=5, R1=1, R2=0):
        """
        add a x-oriented cone to mesh entities

        Parameters
        ----------
        x       : float
            x position of the x-min face center.
        y       : float
            y position of the x-min face center.
        z       : float
            z position of the x-min face center.
        L       : float
            Cone length along x.
        R1       : float
            Cone x-min face radius.
        R2       : float
            Cone x-max face radius.

        Returns
        -------
        cone    : int
            id of the added object
        """
        if self.D == 3:
            parameters = {"x": x, "y": y, "z": z, "L": L, "R1": R1, "R2": R2}
            cone = self.model.occ.addCone(x, y, z, L, 0, 0, R1, R2)
            self.model.occ.synchronize()
            bounds = self.model.getEntities(dim=2)[-3:]
            self.entities[cone] = {
                "type": "cone",
                "parameters": parameters,
                "bounds": bounds,
                "dim": 3,
            }
            return cone
        else:
            rise_warning("Not added : add_cylinder requiere 3D mesh")
            return None

    def rotate(self, volume, angle, x=0, y=0, z=0, ax=0, ay=0, az=0, rad=True):
        """
        rotate volume

        Parameters
        ----------
        volume      : int
            gmsh id of the volume
        angle:      : float
            angle of the rotation
        x           : float
            x-position of the center of the rotation, by default 0
        y           : float
            y-position of the center of the rotation, by default 0
        z           : float
            z-position of the center of the rotation, by default 0
        ax          : float
            x-coefficient of the rotation axis direction vector, by default 0
        ay          : float
            y-coefficient of the rotation axis direction vector, by default 0
        az          : float
            z-coefficient of the rotation axis direction vector, by default 0
        rad         : bool
            if true angle considered in rad, else in degree, by default 0
        """
        if not rad:
            angle = math.radians(angle)
        self.model.occ.rotate([(3, volume)], x, y, z, ax, ay, az, angle)

    def fragment(self, IDs=None, dim=3, verbose=True):
        """
        Fragmentation of the mesh important to link entities to each other

        Parameters
        ----------
        IDs     : list or None
            list of IDs of the element to fragments, if None all dim dimension elements are
            fragmented, by default None
        dim     : int
            dimension of the elements considerated, by default 3
        verbose : bool
            print or not the verbose on the temrminal, by default False
        """
        if IDs is None:
            if dim == 2:
                list_obj = self.get_faces(com=False)
            elif dim == 3:
                list_obj = self.get_volumes(com=False)
            else:
                list_obj = [(dim, k) for k in self.entities]
        elif not np.iterable(IDs) or len(IDs) < 2:
            rise_warning("Need at least 2 entities to fragment")
            return -1
        else:
            list_obj = [(dim, k) for k in IDs]

        frag = self.model.occ.fragment([list_obj[0]], [k for k in list_obj[1:]])
        new_entities = {}
        if verbose:
            pass_info(
                "Warning: New volume generated by fragmentation, bounds are no longer up to date"
            )
        # for i in frag[0][:]:
        #     mask = [i in k for k in frag[1]]
        #     p_id = (np.array(list_obj)[mask][:, 1]).tolist()
        #     p_types = [self.entities[k]["type"] for k in p_id]
        #     dim = min([self.entities[k]["dim"] for k in p_id])
        #     com = np.round(self.model.occ.getCenterOfMass(i[0], i[1]), 3)
        #     parameters = {"p_id": p_id, "p_types": p_types, "com": com}
        #     new_entities[i[1]] = {
        #         "type": "fragment",
        #         "parameters": parameters,
        #         "dim": dim,
        #     }
        # self.entities.update(new_entities)

    ##############################################################################################
    #######################################   domains methods  ###################################
    ##############################################################################################

    def add_domains(self, obj_IDs, phys_ID, dim=None, name=None):
        """
        add domains (ID + name) to a goupe of entities
        Caution: as to be used after all entities are placed

        Parameters
        ----------
        fname    : str
            path and name of saving file. If ends with ".msh" only save in ".msh" file
        """
        if not np.iterable(obj_IDs):
            obj_IDs = [obj_IDs]
        if dim is None:
            dim = max([self.entities[k]["dim"] for k in obj_IDs])
        self.model.addPhysicalGroup(dim, obj_IDs, phys_ID)
        if name is None:
            name = "domain " + str(self.n_domains)
        self.id_domains = np.append(self.id_domains, phys_ID)
        self.dim_domains = np.append(self.dim_domains, dim)
        self.name_domain += [name]

    @property
    def n_domains(self):
        return len(self.id_domains)

    @property
    def domains_1D(self):
        I = np.where(self.dim_domains == 1)
        return self.id_domains[I]

    @property
    def domains_2D(self):
        I = np.where(self.dim_domains == 2)
        return self.id_domains[I]

    @property
    def domains_3D(self):
        I = np.where(self.dim_domains == 3)
        return self.id_domains[I]

    ##############################################################################################
    #######################################   feilds methods  ####################################
    ##############################################################################################
    def refine_entities(self, ent_ID, res_in, dim, res_out=None, IncludeBoundary=True):
        """
        refine mesh resolution in a list of faces or volumes IDs

        Parameters
        ----------
        ent_ID    : list[int] or int
            ID or list of ID of the entities where the resolution should be changed
        res_in    : float
            resolution inside the entities
        dim    : int (2 or 3)
            dimention of the considerated entities
        res_out    : float
            resolution outside the entities if None take self.res, default None
        IncludeBoundary    : bool
            include the boundaries for the refinment, default True
        """
        self.Nfeild += 1
        if not np.iterable(ent_ID):
            ent_ID = [ent_ID]

        if dim == 2:
            typelist = "SurfacesList"
        else:
            typelist = "VolumesList"

        if res_out is None:
            res_out = self.res

        self.model.mesh.field.add("Constant", self.Nfeild)
        self.model.mesh.field.setNumbers(self.Nfeild, typelist, ent_ID)
        self.model.mesh.field.setNumber(self.Nfeild, "IncludeBoundary", IncludeBoundary)
        self.model.mesh.field.setNumber(self.Nfeild, "VIn", res_in)
        self.model.mesh.field.setNumber(self.Nfeild, "VOut", res_out)

        return self.Nfeild

    def refine_threshold(
        self, ent_ID, dim, dist_min, dist_max, res_min, res_max=None, N_samples=100
    ):
        """
        refine mesh resolution in a list of faces or volumes IDs

        Parameters
        ----------
        ent_ID    : list[int] or int
            ID or list of ID of the entities where the resolution should be changed
        res_in    : float
            resolution inside the entities
        dim    : int (2 or 3)
            dimention of the considerated entities
        res_out    : float
            resolution outside the entities if None take self.res, default None
        IncludeBoundary    : bool
            include the boundaries for the refinment, default True
        """
        self.Nfeild += 1
        if not np.iterable(ent_ID):
            ent_ID = [ent_ID]

        if dim == 2:
            typelist = "SurfacesList"
        elif dim == 1:
            typelist = "CurvesList"
        else:
            typelist = "PointsList"

        if res_max is None:
            res_max = self.res

        self.Nfeild += 1
        i_Dist_field = self.Nfeild
        self.model.mesh.field.add("Distance", i_Dist_field)
        self.model.mesh.field.setNumbers(i_Dist_field, typelist, ent_ID)
        self.model.mesh.field.setNumber(i_Dist_field, "Sampling", N_samples)

        self.Nfeild += 1
        self.model.mesh.field.add("Threshold", self.Nfeild)
        self.model.mesh.field.setNumber(self.Nfeild, "InField", i_Dist_field)
        self.model.mesh.field.setNumber(self.Nfeild, "SizeMin", res_min)
        self.model.mesh.field.setNumber(self.Nfeild, "SizeMax", res_max)
        self.model.mesh.field.setNumber(self.Nfeild, "DistMin", dist_min)
        self.model.mesh.field.setNumber(self.Nfeild, "DistMax", dist_max)
        self.model.mesh.field.setNumber(self.Nfeild, "Sigmoid", 1)

        return self.Nfeild

    def refine_min(self, feild_IDs):
        """
        refine mesh resolution taking the minimum value for a list of refinment fields

        Parameters
        ----------
        feild_IDs    : list[int]
            list of field from wich the minimum should be taken
        """
        self.Nfeild += 1

        self.model.mesh.field.add("Min", self.Nfeild)
        self.model.mesh.field.setNumbers(self.Nfeild, "FieldsList", feild_IDs)

        return self.Nfeild

    def refinement_callback(self, meshSizeCallback):
        """
        Add a call back function which is apply to the mesh size defined by fields and return
        the final mesh size

        Parameters
        ----------
        meshSizeCallback    : nrv.utils.MeshCallBack
        """
        self.model.mesh.setSizeCallback(meshSizeCallback)

    ##############################################################################################
    ################################   generate and saving methods  ##############################
    ##############################################################################################
    def generate(self):
        """
        genetate the mesh
        """
        if not self.is_generated:
            if self.Nfeild > 0:
                self.model.mesh.field.setAsBackgroundMesh(self.Nfeild)
            else:
                gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.1 * self.res)
                gmsh.option.setNumber("Mesh.CharacteristicLengthMax", self.res)

            self.model.occ.synchronize()
            self.model.mesh.generate(self.D)
            self.is_generated = True

    def save_geom(self, fname):
        """
        save only the mesh geometry in a `.brep` file

        Note
        ----
        `.brep` files can be open similarly to `.msh` in `gmsh` application.

        Parameters
        ----------
        fname : _type_
            _description_
        """
        fname = rmv_ext(fname)
        gmsh.write(fname + ".brep")
        self.file = fname

    def save(self, fname, generate=True):
        """
        Save mesh in fname in ".msh"

        Parameters
        ----------
        fname    : str
            path and name of saving file. If ends with ".msh" only save in ".msh" file
        """
        if generate == True:
            self.generate()
        fname = rmv_ext(fname)
        gmsh.write(fname + ".msh")
        self.file = fname

    def load(self, fname):
        """
        load mesh from ".msh" file
        """
        if ".msh" not in fname:
            fname += ".msh"
        if not os.path.isfile(fname):
            rise_warning(fname + " not found: Mesh could not be loaded")
        else:
            gmsh.merge(fname)
            self.file = fname

    def visualize(self, fname=None):
        if fname is None:
            self.generate()
            gmsh.fltk.run()
        elif fname is not None:
            self.save(fname=fname)
            os.system("gmsh " + self.file + ".msh")
