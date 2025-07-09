"""
NRV-:class:`.NerveMshCreator` handling.
"""

from cmath import phase
import numpy as np
from math import log10, floor

from ....backend._NRV_Class import NRV_class, load_any
from ....backend._log_interface import rise_error, rise_warning

# from ....nmod.myelinated import myelinated
from ....utils._units import mm, sci_round
from ....utils.geom._misc import CShape, create_cshape
from ....backend._file_handler import rmv_ext
from ._MshCreator import MshCreator, pi


ENT_DOM_offset = {
    "Volume": 0,
    "Surface": 1,
    "Outerbox": 0,
    "Nerve": 2,
    "Fascicle": 10,
    "Electrode": 100,
    "Axon": 1000,
}


def get_mesh_domid(objtype: str, objid: int = 0, is_surf: bool = False) -> int:
    """
    function returning the corresponding physical domain in the mesh of an object in the context.

    Parameters
    ----------
    objtype : str
        type of object
    objid : int, optional
        for facicle, axon or electrode the corresponding id in the nerve, by default 0
    is_surf : bool, optional
        if true return the id of the surface dom, by default False

    Returns
    -------
    int
    """
    domid = 2 * objid
    if objtype.lower() in ["o", "outer", "outerbox"]:
        domid = ENT_DOM_offset["Outerbox"]
    elif objtype.lower() in ["n", "nerve"]:
        domid = ENT_DOM_offset["Nerve"]
    elif objtype.lower() in ["f", "fasc", "fascicle"]:
        domid += ENT_DOM_offset["Fascicle"]
    elif objtype.lower() in ["a", "ax", "axon"]:
        domid += ENT_DOM_offset["Axon"]
    elif objtype.lower() in ["e", "elec", "electrode"]:
        domid += ENT_DOM_offset["Electrode"]
    if is_surf:
        domid += 1
    return domid


ELEC_TYPES = ["CUFF MP", "CUFF", "LIFE"]


def is_NerveMshCreator(object):
    """
    check if an object is a NerveMshCreator, return True if yes, else False

    Parameters
    ----------
    result : object
        object to test

    Returns
    -------
    bool
        True it the type is a NerveMshCreator object
    """
    return isinstance(object, NerveMshCreator)


def get_node_physical_id(id_ax: int, i_node: int, volume: bool = False) -> int:
    id_ax_volume = id_ax - id_ax % 2
    i_node_str = str(2 * i_node)
    while len(i_node_str) < 3:
        i_node_str = "0" + i_node_str
    return int(str(id_ax_volume) + i_node_str)


class NerveMshCreator(MshCreator):
    """
    Class allowing to generate Nerve shape 3D gmsh mesh with labeled physical domain
    Contains methodes dealing with the mesh geometries, physical domains and feilds
    Inherit from MshCreator class. see MshCreator for further detail
    """

    def __init__(
        self,
        Length=10000,
        Outer_D=5,
        Nerve_D=4000,
        y_c=0,
        z_c=0,
        ver_level=2,
    ):
        """
        initialisation of the NerveMshCreator

        Parameters
        ----------
        Length          : float
            Nerve length in um, by default 10000
        Outer_D         : float
            Outer box diameter in mm, by default 5
        Nerve_D         : float
            Nerve diameter in um, by default 4000
        y_c             : float
            y-axis position of the Nerve center, by default 0
        z_c             : float
            z-axis position of the Nerve center, by default 0
        ver_level       : int(0,1,2,3,4,5,99)
            verbosity level of gmsh (see MshCreator.set_verbosity), by default 2
        """
        super().__init__(D=3, ver_level=ver_level)
        self.L = Length
        self.y_c = y_c
        self.z_c = z_c
        self.surf_c = [self.L / 2]

        self.gnd_facet = {"outfacet": True, "lfacet": False, "rfacet": False}
        if Outer_D is None:
            self.is_outer = False
            self.gnd_facet["outfacet"] = False
            self.gnd_facet["rfacet"] = True
            self.Outer_D = 0
            self.Outer_entities = {"face": [], "volume": []}
        else:
            self.is_outer = True
            self.Outer_D = Outer_D * mm
            self.Outer_entities = {"face": [], "volume": []}

        self.Nerve_D = Nerve_D
        self.Nerve_entities = {"face": [], "volume": []}

        self.N_fascicle = 0
        self.fascicles = {}
        self.N_axon = 0
        self.axons = {}

        self.geometries: dict[str, CShape] = {}

        self._continuous_myelin = True

        self.N_electrode = 0
        self.electrodes = {}

        self.default_res = {
            "Outerbox": self.Outer_D / 5,
            "Outerbox_tresholded": False,
            "Nerve": self.Nerve_D / 5,
            "Fascicle": 500,
            "Axon": 10,
            "Electrode": 1000,
        }
        self.Ox = None  # add an Ox line (need for thresholded resolution)

        self.res = self.default_res["Outerbox"]
        self.alpha_Outerboxres = 0.05

        self.is_geo = False
        self.is_dom = False
        self.is_refined = False

    def get_parameters(self):
        param = {}
        param["res"] = self.res
        param["L"] = self.L
        param["y_c"] = self.y_c
        param["z_c"] = self.z_c
        param["surf_c"] = self.surf_c
        param["Outer_D"] = self.Outer_D
        param["Outer_entities"] = self.Outer_entities
        param["Nerve_D"] = self.Nerve_D
        param["Nerve_entities"] = self.Nerve_entities
        param["N_fascicle"] = self.N_fascicle
        param["fascicles"] = self.fascicles
        param["N_axon"] = self.N_axon
        param["axons"] = self.axons
        param["N_electrode"] = self.N_electrode
        param["electrodes"] = self.electrodes
        param["geometries"] = self.geometries
        return param

    def save(
        self,
        fname="nervemshcreator.json",
        save=True,
        blacklist=[],
        **kwargs,
    ):
        """
        Return extracellular context as dictionary and eventually save it as json file
        NB: caution, first argument is fname to match with MshCreator.save arguments

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default "extracel_context.json"

        Returns
        -------
        context_dic : dict
            dictionary containing all information
        """
        blacklist += [
            "model",
        ]
        mshfname = ".msh" in fname
        if self.is_generated and (save or mshfname):
            if mshfname is None:
                mshfname = rmv_ext(fname) + ".msh"
            super().save(fname=fname, generate=False)
        fname = rmv_ext(fname) + ".json"
        save = save and not mshfname
        return NRV_class.save(
            self, save=save, fname=fname, blacklist=blacklist, **kwargs
        )

    def load(self, data, mshfname=None, blacklist={}, **kwargs):
        """
        Generic loading method for NRV class instance

        Parameters
        ----------
        data : dict
            Dictionary containing the NRV object
        blacklist : dict, optional
            Dictionary containing the keys to be excluded from the load
        **kwargs : dict, optional
            Additional arguments to be passed to the load method of the NRV object
        """
        NRV_class.load(self, data, **kwargs)
        self.electrodes = {int(k): v for k, v in self.electrodes.items()}
        self.fascicles = {int(k): v for k, v in self.fascicles.items()}
        self.axons = {int(k): v for k, v in self.axons.items()}
        if self.is_generated and self.file != "":
            super().load(self.file)

    def compute_mesh(self):
        """
        Compute mesh geometry, domains and resolution and then generate the mesh
        """
        self.compute_geo()
        self.compute_domains()
        self.compute_res()
        self.generate()

    def set_gnd_facet(self, outfacet=None, lfacet=None, rfacet=None):
        """
        Set which of the outer facet should be the ground (element 1)

        Parameters
        ----------
        outfacet        : bool or None
            if true outer ring facet is included to the element 1, if None not modified
            by default None
        lfacet          : bool or None
            if true left facet is included to the element 1, if None not modified
            by default None
        rfacet          : bool or None
            if true right facet is included to the element 1, if None not modified
            by default None
        """
        if outfacet is not None:
            self.gnd_facet["outfacet"] = outfacet
        if lfacet is not None:
            self.gnd_facet["lfacet"] = lfacet
        if rfacet is not None:
            self.gnd_facet["rfacet"] = rfacet

    ###############################################################################################
    #####################################   geometry definition  ##################################
    ###############################################################################################

    def compute_geo(self):
        """
        Compute the mesh geometry

        """
        if not self.is_geo:
            if self.is_outer:
                self.add_cylinder(0, self.y_c, self.z_c, self.L, self.Outer_D / 2)
                if self.default_res["Outerbox_tresholded"]:
                    self.Ox = self.add_line((0, 0, 0), (self.L, 0, 0))
            self.add_cylinder(0, self.y_c, self.z_c, self.L, self.Nerve_D / 2)

            for _id, fascicle in self.fascicles.items():
                _s_id = self.add_from_cshape(
                    self.geometries[f"fa{_id}"], x=0, dx=self.L, res=fascicle["res"]
                )
                self.__collect_geom_ppt(fascicle, _s_id)
            for i in self.axons:
                self.add_axon(i)

            for i in self.electrodes:
                electrode = self.electrodes[i]
                if "CUFF MP" in electrode["type"]:
                    self.add_CUFF_MP(ID=i, **electrode["kwargs"])
                elif "CUFF MEA" in electrode["type"]:
                    self.add_CUFF_MEA(ID=i, **electrode["kwargs"])
                elif "CUFF" in electrode["type"]:
                    self.add_CUFF(ID=i, **electrode["kwargs"])
                elif "LIFE" in electrode["type"]:
                    self.add_LIFE(ID=i, **electrode["kwargs"])
            self.fragment(verbose=False)
            self.is_geo = True

    def reshape_outerBox(self, Outer_D=None, res="default", tresholded_res=None):
        """
        Reshape the size of the FEM simulation outer box

        Parameters
        ----------
        outer_D : float
            FEM simulation outer box diameter, in mm, WARNING, this is the only parameter in mm !
        """
        if Outer_D is not None:
            """
            ## See how if it should be added
            if self.default_res["Outerbox"] == self.Outer_D/5:
                self.default_res["Outerbox"] = Outer_D/5
            """
            self.Outer_D = Outer_D * mm

        if tresholded_res is not None:
            self.default_res["Outerbox_tresholded"] = tresholded_res

        if not res == "default":
            self.default_res["Outerbox"] = res

        if self.default_res["Outerbox"] > self.Outer_D / 3:
            self.default_res["Outerbox"] = self.Outer_D / 3

    def reshape_nerve(
        self, Nerve_D=None, Length=None, y_c=None, z_c=None, res="default"
    ):
        """
        Reshape the nerve of the FEM simulation

        Parameters
        ----------
        Nerve_D                 : float
            Nerve diameter, in um
        Length                  : float
            Nerve length, in um
        y_c                     : float
            Nerve center y-coordinate in um, 0 by default
        z_c                     : float
            Nerve z-coordinate center in um, 0 by default
        """

        if Length is not None:
            self.L = Length
        if Nerve_D is not None:
            if self.default_res["Nerve"] == self.Nerve_D / 5:
                self.default_res["Nerve"] = Nerve_D / 5
            self.Nerve_D = Nerve_D
        if y_c is not None:
            self.y_c = y_c
        if z_c is not None:
            self.z_c = z_c

        if not res == "default":
            self.default_res["Nerve"] = res

        if self.default_res["Nerve"] > self.Nerve_D / 5:
            self.default_res["Nerve"] = self.Nerve_D / 5

    def reshape_fascicle(
        self, d=0, y_c=0, z_c=0, ID=None, res="default", geometry: CShape | None = None
    ):
        """
        Reshape a fascicle of the FEM simulation

        Parameters
        ----------
        d  : float
            Fascicle diameter, in um
        y_c         : float
            Fascicle center y-coodinate in um, 0 by default
        z_c         : float
            Fascicle center y-coodinate in um, 0 by default
        ID          : int
            If the simulation contains more than one fascicles, ID number of the fascicle to reshape as in COMSOL
        """
        if ID not in self.fascicles:
            if ID is None:
                ID = 0
                while ID in self.fascicles:
                    ID += 1
            self.N_fascicle += 1

        # Mostly for retrocompatibility
        if geometry is None and d != 0:
            geometry = create_cshape(center=(y_c, z_c), diameter=d)
        if np.iterable(geometry.radius):
            min_length = min(geometry.radius)
        else:
            min_length = geometry.radius

        if res == "default":
            res = self.default_res["Fascicle"]
        if res > min_length / 2:
            res = min_length / 2

        self.geometries[f"fa{ID}"] = geometry

        self.fascicles[ID] = {
            "gid": f"fa{ID}",
            "res": res,
            "face": None,
            "volume": None,
        }

    def remove_fascicles(self, ID=None):
        """
        remove a fascicle of the FEM simulation

        Parameters
        ----------
        ID          : int, None
            ID number of the fascicle to remove, if None, remove all fascicles, by default None
        """
        if ID is None:
            self.fascicles = {}
            self.N_fascicle = 0
            self.geometries = {
                k: v for k, v in self.geometries.items() if "fa" not in k
            }
        elif ID in self.fascicles:
            del self.geometries[self.fascicles[ID]["gid"]]
            del self.fascicles[ID]
            self.N_fascicle -= 1

    def reshape_axon(
        self,
        d,
        y=0,
        z=0,
        ID=None,
        myelinated=False,
        res="default",
        res_node="default",
        **kwargs,
    ):
        """
        Reshape a axon of the FEM simulation

        Parameters
        ----------
        d  : float
            Fascicle diameter, in um
        y_c         : float
            Fascicle center y-coodinate in um, 0 by default
        z_c         : float
            Fascicle center y-coodinate in um, 0 by default
        ID          : int
            If the simulation contains more than one fascicles, ID number of the fascicle to reshape as in COMSOL
        """
        if ID not in self.axons:
            if ID is None:
                ID = 0
                while ID in self.axons:
                    ID += 1
            self.N_axon += 1

        if res == "default":
            res = self.default_res["Axon"]
        if d / 3 < res:
            res = d / 3
        if res_node == "default":
            res_node = res / 3

        self.axons[ID] = kwargs
        self.axons[ID].update(
            {
                "y": y,
                "z": z,
                "d": d,
                "myelinated": myelinated,
                "res": res,
                "res_node": res_node,
                "face": [],
                "volume": [],
            }
        )

    def add_electrode(self, elec_type, ID=None, res="default", **kwargs):
        """ """
        if elec_type not in ELEC_TYPES + ["CUFF MEA"]:
            rise_warning(
                elec_type
                + " not implemented, electrode will not be added\nList of Electrode types: "
                + str(ELEC_TYPES)
            )
        if ID not in self.electrodes:
            if ID is None:
                ID = 0
                while ID in self.electrodes:
                    if (
                        "CUFF MEA" in self.electrodes[ID]["type"]
                        or "CUFF MP" in self.electrodes[ID]["type"]
                    ):
                        ID += self.electrodes[ID]["kwargs"]["N"]
                    else:
                        ID += 1
            self.N_electrode += 1

        if res == "default":
            res = self.default_res["Electrode"]

        if "LIFE" in elec_type:
            if "d" in kwargs:
                d = kwargs["d"]
            else:
                d = 25
            if d / 3 < res:
                res = d / 3

        self.electrodes[ID] = {"type": elec_type, "res": res, "kwargs": kwargs}

    def __collect_geom_ppt(self, d_store: dict, shape_ids: tuple[tuple[int]]):
        for c in shape_ids:
            bbox = np.round(self.model.occ.getBoundingBox(*c), 4)
            if np.isclose(abs(bbox[0] - bbox[3]), self.L):
                if c[0] == 2:
                    key = "face_bbox"
                else:
                    key = "volume_bbox"
                d_store[key] = bbox

    ####################################################################################################
    #####################################   domains definition  ########################################
    ####################################################################################################

    def compute_domains(self):
        if not self.is_geo:
            rise_error("compute geometry before domain")
        elif not self.is_dom:
            self.__link_entity_domains(dim=2)
            self.__link_entity_domains(dim=3)
            try:
                self.compute_entity_domain()
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except TypeError:
                self.save_geom("./__mesh_geom_dbg")
                rise_error(
                    TypeError,
                    "One or several domain not found, ",
                    "please check your geometry saved in `./__mesh_geom_dbg.brep`",
                )
            except Exception as e:
                rise_error("Error in during the mehsing:\n", e)

            self.is_dom = True

    def __is_outerbox(self, dx, dy, dz, com, dim_key):
        """
        Internal use only: check if volume is the box or face is external face of box

        Parameters
        ----------
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox

        """
        outer_ring_test = (
            np.allclose([dx, dy, dz], [self.L, self.Outer_D, self.Outer_D])
            and self.is_outer
        )
        if dim_key == "volume":
            return outer_ring_test
        outer_ring_test = outer_ring_test and self.gnd_facet["outfacet"]
        left_facet_test = np.allclose(com[0], [0]) and self.gnd_facet["lfacet"]
        rigth_facet_test = np.allclose(com[0], [self.L]) and self.gnd_facet["rfacet"]
        return outer_ring_test or left_facet_test or rigth_facet_test

    def __is_nerve(self, dx, dy, dz):
        """
        Internal use only: check if volume is nerve or face is external face of nerve

        Parameters
        ----------
        dx          : float
            length along x of the tested entity
        dy          : float
            length along y of the tested entity
        dz          : float
            length along z of the tested entity
        """
        return np.allclose([dy, dz], [self.Nerve_D, self.Nerve_D]) and not np.isclose(
            dx, 0
        )

    def __is_fascicle(self, ID, bbox, com, dim_key):
        """
        Internal use only: check if volume is fascicle ID or face is external face of fascicle ID

        Parameters
        ----------
        ID          :int
            ID of fascicle to test
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        com         : tupple(float)
            entity Center of Mass
        dim_key     :"face" or "volume"
            element type
        """
        # Already computed
        # fasc = self.fascicles[ID][dim_key]
        status_test = self.fascicles[ID][dim_key] is None
        # test good diameter
        size_test = np.allclose(bbox, self.fascicles[ID][dim_key + "_bbox"], atol=1)
        # test center of mass in fascicle
        geom = self.geometries[f"fa{ID}"]
        com_test = geom.is_inside(com[1:])
        return status_test and size_test and com_test

    def __is_axon_node(self, ID, dx, dy, dz, com, dim_key):
        """
        Internal use only: check if volume is axon ID or face is external face of axon ID

        Parameters
        ----------
        ID          :int
            ID of axon to test
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        com         : tupple(float)
            entity Center of Mass
        dim_key     :"face" or "volume"
            element type
        """
        axon = self.axons[ID]
        # Already computed
        if not axon["myelinated"]:
            return False

        # test good diameter
        size_test = np.allclose(
            [dx, dy, dz], [axon["node_l"], axon["node_d"], axon["node_d"]], atol=0.001
        )

        # test first and last node
        if "first_node_l" in axon and not size_test:
            size_test = np.allclose(
                [dx, dy, dz], [axon["first_node_l"], axon["node_d"], axon["node_d"]]
            )
        if "last_node_l" in axon and not size_test:
            size_test = np.allclose(
                [dx, dy, dz], [axon["last_node_l"], axon["node_d"], axon["node_d"]]
            )

        # test center of mass in axon
        com_test = np.allclose(com[1:], (axon["y"], axon["z"]))
        return size_test and com_test

    def __is_axon(self, ID, dx, dy, dz, com, dim_key):
        """
        Internal use only: check if volume is axon ID or face is external face of axon ID

        Parameters
        ----------
        ID          :int
            ID of axon to test
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        com         : tupple(float)
            entity Center of Mass
        dim_key     :"face" or "volume"
            element type
        """
        axon = self.axons[ID]
        # Already computed
        status_test = True  # axon[dim_key] is None
        # test good diameter
        size_test = np.allclose([dy, dz], [axon["d"], axon["d"]])
        size_test &= not np.isclose(dx, 0)
        # test center of mass in axon
        com_test = np.allclose(com[1:], (axon["y"], axon["z"]), atol=axon["d"] / 2)
        return status_test and size_test and com_test

    def __is_CUFF_MP_electrode(self, ID, rc, dx, teta, com, dim_key):
        """
        Internal use only: check if volume is electrode ID or face is external face of fascicle ID

        Parameters
        ----------
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        com         : tupple(float)
            entity Center of Mass
        """
        elec_kwargs = self.electrodes[ID]["kwargs"]
        if self.electrodes[ID]["type"] != "CUFF MP":
            return False

        # test good length
        size_test = np.allclose([dx], [elec_kwargs["contact_length"]])
        # test good x-location
        com_test = np.isclose(com[0], elec_kwargs["x_c"])
        # test good polar coordinate
        if elec_kwargs["is_volume"] or dim_key == "volume":
            N = elec_kwargs["N"]
            tetas = [teta for i in range(N)]
            angle_test = np.isclose(tetas, self.electrodes[ID]["angles"]).any()
            radius_test = rc > self.Nerve_D / 2
            polar_test = angle_test and radius_test
        else:
            polar_test = rc <= self.Nerve_D / 2

        return size_test and com_test and polar_test

    def __is_CUFF_electrode(self, ID, dx, dy, dz, com, dim_key):
        """
        Internal use only: check if volume is electrode ID or face is external face of fascicle ID

        Parameters
        ----------
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        com         : tupple(float)
            entity Center of Mass
        """
        elec_kwargs = self.electrodes[ID]["kwargs"]
        if self.electrodes[ID]["type"] != "CUFF":
            return False

        # test good diameter
        Syz = self.Nerve_D
        if elec_kwargs["is_volume"] or dim_key == "volume":
            Syz += 2 * elec_kwargs["contact_thickness"]
        size_test = np.allclose([dx, dy, dz], [elec_kwargs["contact_length"], Syz, Syz])
        # test center of mass in CUFF
        com_test = np.allclose(com, (elec_kwargs["x_c"], self.y_c, self.z_c))
        return size_test and com_test

    def __is_LIFE_electrode(self, ID, dx, dy, dz, com):
        """
        Internal use only: check if volume is electrode ID or face is external face of fascicle ID

        Parameters
        ----------
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        com         : tupple(float)
            entity Center of Mass
        """

        elec_kwargs = self.electrodes[ID]["kwargs"]
        if self.electrodes[ID]["type"] != "LIFE":
            return False
        # test good diameter
        size_test = np.allclose(
            [dx, dy, dz], [elec_kwargs["length"], elec_kwargs["d"], elec_kwargs["d"]]
        )
        # test center of mass in LIFE
        com_test = np.allclose(
            com,
            (elec_kwargs["x_c"], elec_kwargs["y_c"], elec_kwargs["z_c"]),
            atol=elec_kwargs["d"] / 2,
        )
        return size_test and com_test

    def __link_entity_domains(self, dim):
        """
        Internal use only: link all entities from

        Parameters
        ----------
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        com         : tupple(float)
            entity Center of Mass
        """
        if dim == 2:
            entities, ent_com, ent_bd = self.get_faces(com=True, bd=True)
            key = "face"
            offset = 1
        else:
            entities, ent_com, ent_bd = self.get_volumes(com=True, bd=True)
            key = "volume"
            offset = 0

        for i in range(len(entities)):
            bd_x = abs(ent_bd[i][3] - ent_bd[i][0])
            bd_y = abs(ent_bd[i][4] - ent_bd[i][1])
            bd_z = abs(ent_bd[i][5] - ent_bd[i][2])
            if self.__is_outerbox(bd_x, bd_y, bd_z, ent_com[i], key):
                self.Outer_entities[key] += [entities[i][1]]

            elif self.__is_nerve(bd_x, bd_y, bd_z):
                self.Nerve_entities[key] += [entities[i][1]]

            for j in self.fascicles:
                if self.__is_fascicle(j, ent_bd[i], ent_com[i], key):
                    # if self.__is_fascicle(j, ent_bd, ent_com[i], key):
                    self.fascicles[j][key] = entities[i][1]

            for j in self.axons:
                if self.__is_axon_node(j, bd_x, bd_y, bd_z, ent_com[i], key):
                    node_id = int(ent_com[i][0] // self.axons[j]["deltax"])
                    self.axons[j]["nodes_" + key][node_id] = [entities[i][1]]
                elif self.__is_axon(j, bd_x, bd_y, bd_z, ent_com[i], key):
                    self.axons[j][key] += [entities[i][1]]

            for j in self.electrodes:
                r_c = (
                    (ent_com[i][1] - self.y_c) ** 2 + (ent_com[i][2] - self.z_c) ** 2
                ) ** 0.5
                teta = phase(
                    complex(ent_com[i][2] - self.z_c, ent_com[i][1] - self.y_c)
                ) % (2 * pi)
                if self.__is_CUFF_MP_electrode(j, r_c, bd_x, teta, ent_com[i], key):
                    N = self.electrodes[j]["kwargs"]["N"]
                    ID_EA = round(teta * N / (2 * pi)) % N
                    if dim == 3:
                        if self.electrodes[j][key][ID_EA] is None:
                            self.electrodes[j][key][ID_EA] = entities[i][1]
                        else:
                            rise_warning(
                                "two volumes can be same electrode only the first one is kept"
                            )
                    else:
                        if self.electrodes[j][key][ID_EA] is None:
                            self.electrodes[j][key][ID_EA] = entities[i][1]
                        else:
                            self.electrodes[j][key][ID_EA] = [
                                entities[i][1],
                                self.electrodes[j][key][ID_EA],
                            ]

                elif self.__is_CUFF_electrode(j, bd_x, bd_y, bd_z, ent_com[i], key):
                    self.electrodes[j][key] = entities[i][1]
                    if not self.electrodes[j]["kwargs"]["is_volume"] and key == "face":
                        self.Nerve_entities[key].remove(entities[i][1])

                elif self.__is_LIFE_electrode(j, bd_x, bd_y, bd_z, ent_com[i]):
                    self.electrodes[j][key] = entities[i][1]

    def compute_entity_domain(self):
        """
        link all geometrical entities to corresponding physical domains
        """
        # Outer box domain
        if self.is_outer:
            self.add_domains(obj_IDs=self.Outer_entities["volume"], phys_ID=0, dim=3)
            self.add_domains(obj_IDs=self.Outer_entities["face"], phys_ID=1, dim=2)
        else:
            self.add_domains(obj_IDs=self.Outer_entities["face"], phys_ID=1, dim=2)

        # nerve domain
        self.add_domains(obj_IDs=self.Nerve_entities["volume"], phys_ID=2, dim=3)
        self.add_domains(obj_IDs=self.Nerve_entities["face"], phys_ID=3, dim=2)
        for j in self.fascicles:
            id_ph = ENT_DOM_offset["Fascicle"] + (2 * j)
            if id_ph < ENT_DOM_offset["Electrode"]:
                self.add_domains(
                    obj_IDs=self.fascicles[j]["volume"], phys_ID=id_ph, dim=3
                )
                id_ph += ENT_DOM_offset["Surface"]
                self.add_domains(
                    obj_IDs=self.fascicles[j]["face"], phys_ID=id_ph, dim=2
                )
            else:
                rise_warning("Too much Fascicles: " + str(j) + " not added")

        for j, ax in self.axons.items():
            id_ph = ENT_DOM_offset["Axon"] + (2 * j)
            self.add_domains(obj_IDs=ax["volume"], phys_ID=id_ph, dim=3)
            id_ph += ENT_DOM_offset["Surface"]
            self.add_domains(obj_IDs=ax["face"], phys_ID=id_ph, dim=2)
            # adding one physical domain by node
            if ax["myelinated"]:
                id_ax = id_ph
                for i_node in range(ax["n_nodes"]):
                    id_ph = get_node_physical_id(id_ax, i_node)
                    self.add_domains(
                        obj_IDs=ax["nodes_volume"][i_node], phys_ID=id_ph, dim=3
                    )
                    id_ph += ENT_DOM_offset["Surface"]
                    self.add_domains(
                        obj_IDs=ax["nodes_face"][i_node], phys_ID=id_ph, dim=2
                    )

        for j in self.electrodes:
            id_ph = ENT_DOM_offset["Electrode"] + (2 * j)
            if id_ph < ENT_DOM_offset["Axon"]:
                if "CUFF MP" in self.electrodes[j]["type"]:
                    for ID_EA in range(self.electrodes[j]["kwargs"]["N"]):
                        if self.electrodes[j]["kwargs"]["is_volume"]:
                            self.add_domains(
                                obj_IDs=self.electrodes[j]["volume"][ID_EA],
                                phys_ID=id_ph,
                                dim=3,
                            )
                        id_ph += ENT_DOM_offset["Surface"]
                        self.add_domains(
                            obj_IDs=self.electrodes[j]["face"][ID_EA],
                            phys_ID=id_ph,
                            dim=2,
                        )
                        id_ph += 1
                else:
                    if self.electrodes[j]["kwargs"]["is_volume"]:
                        self.add_domains(
                            obj_IDs=self.electrodes[j]["volume"], phys_ID=id_ph, dim=3
                        )
                    id_ph += ENT_DOM_offset["Surface"]
                    self.add_domains(
                        obj_IDs=self.electrodes[j]["face"], phys_ID=id_ph, dim=2
                    )
            else:
                rise_warning("Too much Electrodes: " + str(j) + " not added")

    ####################################################################################################
    ###################################   field (res) definition  ######################################
    ####################################################################################################

    def compute_res(self):
        if not self.is_dom and self.is_geo:
            rise_error("compute geometry and domain before resolution")
        elif not self.is_refined:
            self.res = max(self.default_res.values())
            fields = []

            # Outerbox field
            if self.is_outer:
                fields += self.__refine_Outer_box(alpha=self.alpha_Outerboxres)
            # Nerve field
            fields += [
                self.refine_entities(
                    ent_ID=self.Nerve_entities["volume"],
                    res_in=self.default_res["Nerve"],
                    dim=3,
                    res_out=None,
                    IncludeBoundary=True,
                )
            ]
            # Facsicle fields
            for fascicle in self.fascicles.values():
                fields += [
                    self.refine_entities(
                        ent_ID=fascicle["volume"],
                        res_in=fascicle["res"],
                        dim=3,
                        res_out=None,
                        IncludeBoundary=True,
                    )
                ]
            # Axon fields
            for axon in self.axons.values():
                fields += self.__refine_axon(axon)

            # Electrodes fields
            for electrode in self.electrodes.values():
                if electrode["type"] in ["CUFF MEA", "CUFF MP"]:
                    for ID_EA in range(electrode["kwargs"]["N"]):
                        fields += [
                            self.refine_entities(
                                ent_ID=electrode["volume"][ID_EA],
                                res_in=electrode["res"],
                                dim=3,
                                res_out=None,
                                IncludeBoundary=True,
                            )
                        ]
                else:
                    fields += [
                        self.refine_entities(
                            ent_ID=electrode["volume"],
                            res_in=electrode["res"],
                            dim=3,
                            res_out=None,
                            IncludeBoundary=True,
                        )
                    ]
            self.refine_min(fields)
            self.is_refined = True

    def __refine_axon(self, axon):
        """ """
        # First set the field for unmyelinated axon or myelin
        fields = [
            self.refine_entities(
                ent_ID=axon["volume"],
                res_in=axon["res"],
                dim=3,
                res_out=None,
                IncludeBoundary=True,
            )
        ]
        # Then set the field for myelinated axon nodes
        if axon["myelinated"]:
            for i in range(len(axon["nodes_volume"])):
                fields += [
                    self.refine_entities(
                        ent_ID=axon["nodes_volume"][i],
                        res_in=axon["res_node"],
                        dim=3,
                        res_out=None,
                        IncludeBoundary=True,
                    )
                ]
        return fields

    def __refine_Outer_box(self, alpha=0.1):
        """ """
        if not self.default_res["Outerbox_tresholded"]:
            field = [
                self.refine_entities(
                    ent_ID=self.Outer_entities["volume"],
                    res_in=self.default_res["Outerbox"],
                    dim=3,
                    res_out=None,
                    IncludeBoundary=True,
                )
            ]
        else:
            dmin = self.Nerve_D
            dmax = dmin + alpha * self.Outer_D
            field = [
                self.refine_threshold(
                    ent_ID=self.Ox,
                    dim=1,
                    res_min=self.default_res["Nerve"],
                    res_max=self.default_res["Outerbox"],
                    dist_min=self.Nerve_D,
                    dist_max=dmax,
                )
            ]
        return field

    ################################################################
    ############## complex volumes adding methods ##################
    ################################################################
    def __add_mye_section(self, i_sec: int, sec: str, x, ax_pties: dict, l_sec: float):
        """_summary_

        Parameters
        ----------
        i_sec : int
            section index
        sec : str
            section label
        x : _type_
            x position
        ax_pties : dict
            axon properties
        l_sec : float
            length of the section
        r_sec : float
            radius of the section
        """
        if sec == "MYSA":
            neighbour_sec = {"node", "FLUT"}
            if i_sec == 0:
                next_sec = ax_pties["path_type"][1]
                neighbour_sec -= {next_sec}
                prev_sec = neighbour_sec.pop()
            else:
                prev_sec = ax_pties["path_type"][i_sec - 1]
                neighbour_sec -= {prev_sec}
                next_sec = neighbour_sec.pop()
            r_1 = ax_pties[prev_sec]["r"]
            r_2 = ax_pties[next_sec]["r"]

            self.add_cone(x, ax_pties["y"], ax_pties["z"], l_sec, r_1, r_2)
        else:
            self.add_cylinder(
                x, ax_pties["y"], ax_pties["z"], l_sec, ax_pties[sec]["r"]
            )

    def add_axon(self, ID):
        """
        Add an axon to the mesh.

        Note
        ----
         - if the axon is unmyelinated this method add only a cylinder to the mesh

        Parameters
        ----------
        """
        axon = self.axons[ID]
        if not axon["myelinated"]:
            self.add_cylinder(0, axon["y"], axon["z"], self.L, axon["d"] / 2)
        else:
            axon.update(
                {
                    "L": self.L,
                    "rec": "all",
                    "N_seg_per_sec": True,
                    "__NRVObject__": True,
                    "nrv_type": "myelinated",
                }
            )
            # !! Ideally it would be easier to use: ax = myelinated(**axon)
            # But myelinated cannot be imported without causing an import loop
            ax = load_any(data=axon)
            ax_pties = {
                "d": axon["d"],
                "y": axon["y"],
                "z": axon["z"],
                "path_type": ax.axon_path_type,
                "n_nodes": ax.n_nodes,
                "deltax": ax.deltax,
                "l_first_sec": ax.first_section_size,
                "l_last_sec": ax.last_section_size,
                "node": {"r": ax.nodeD / 2, "l": ax.nodelength},
                "MYSA": {"r": axon["d"] / 2, "l": ax.paralength1},
                "FLUT": {"r": axon["d"] / 2, "l": ax.paralength2},
                "STIN": {"r": axon["d"] / 2, "l": ax.interlength},
            }
            x = ax.first_section_size
            del ax

            axon["res_node"] = min(axon["res_node"], ax_pties["node"]["l"])
            res_min = axon["res_node"]

            ## adding 1st section
            # merge the two first sections when the first is too small
            if x < res_min:

                if ax_pties["path_type"].pop(0) == "node":
                    ax_pties["n_nodes"] -= 1
                ax_pties["path_type"].pop(0)
                sec = ax_pties["path_type"][0]
                x += ax_pties[sec]["l"]
            else:
                sec = ax_pties["path_type"][0]
            l_sec = x
            r_sec = ax_pties[sec]["r"]
            if sec == "node":
                self.axons[ID]["first_node_l"] = l_sec
            self.add_cylinder(0, ax_pties["y"], ax_pties["z"], l_sec, r_sec)
            self.__add_mye_section(
                i_sec=0, sec=sec, x=0, ax_pties=ax_pties, l_sec=l_sec
            )

            ## adding mid sections
            for i_sec, sec in enumerate(ax_pties["path_type"][1:]):
                l_sec = ax_pties[sec]["l"]
                # merge the two last sections when it the last is too small
                if abs(self.L - (l_sec + x)) < res_min:
                    l_sec = self.L - x
                    if ax_pties["path_type"].pop(-1) == "node":
                        ax_pties["n_nodes"] -= 1
                    if ax_pties["path_type"][-1] == "node":
                        self.axons[ID]["last_node_l"] = l_sec
                elif l_sec > self.L - x:
                    l_sec = self.L - x
                self.__add_mye_section(
                    i_sec=i_sec + 1, sec=sec, x=x, ax_pties=ax_pties, l_sec=l_sec
                )
                x += l_sec

            self.axons[ID]["node_d"] = 2 * ax_pties["node"]["r"]
            self.axons[ID]["node_l"] = ax_pties["node"]["l"]
            self.axons[ID]["deltax"] = ax_pties["deltax"]
            self.axons[ID]["n_nodes"] = ax_pties["n_nodes"]
            self.axons[ID]["nodes_volume"] = [None for _ in range(ax_pties["n_nodes"])]
            self.axons[ID]["nodes_face"] = [None for _ in range(ax_pties["n_nodes"])]

    def add_LIFE(
        self, ID=None, x_c=0, y_c=0, z_c=0, length=1000, d=25, is_volume=False
    ):
        """
        Add LIFE electrode to the mesh

        Parameters
        ----------
        ID          :int
            electrod ID, ,by defalt None
        x_c         :float
            x-position of the LIFE center in um, by default 0
        y_c         :float
            y-position of the LIFE center in um, by default 0
        z_c         :float
            z-position of the LIFE center in um, by default 0
        length      :float
            length of the LIFE electrod in um, by default 1000
        d           :float
            diameter of the LIFE electrod in um, by default 25
        is_volume   : bool
            if True in cylinder of the LIFE is kept on the mesh

        """

        if ID is not None:
            self.electrodes[ID]["volume"] = []
            self.electrodes[ID]["face"] = []
            self.electrodes[ID]["kwargs"]["is_volume"] = is_volume
        x_active = x_c - length / 2
        y_active = y_c
        z_active = z_c
        self.add_cylinder(x_active, y_active, z_active, length, d / 2)

    def add_CUFF(
        self,
        ID=None,
        x_c=0,
        contact_length=100,
        is_volume=True,
        contact_thickness=None,
        insulator=True,
        insulator_thickness=None,
        insulator_length=None,
        insulator_offset=0,
    ):
        """
        Add CUFF electrode to the mesh

        Parameters
        ----------
        ID                      :int
            if not none and ID exist, change electrod ID,by defalt None
        x_c                     :float
            x-position of the CUFF center in um, by default 0
            length of the CUFF electrod in um, by default 100
        contact_length       :float
            length along x of the contact site in um, by default 100
        is_volume   : bool
            if True the contact is kept on the mesh as a volume, by default True
        contact_thickness       :float
            thickness of the contact site in um, by default 5
        insulator                :bool
            remove insulator ring from the mesh (no conductivity), by default True
        insulator_thickness     :float
            thickness of the insulator ring in um, by default 20
        insulator_length        :float
            length along x of the insulator ring in um, by default 1000
        """

        if contact_thickness is None:
            contact_thickness = 0.1 * (self.Outer_D - self.Nerve_D) / 2
            if contact_thickness < 0:
                contact_thickness = self.Nerve_D * 0.1
        if insulator_thickness is None:
            insulator_thickness = min(
                5 * contact_thickness, 0.4 * abs(self.Outer_D - self.Nerve_D) / 2
            )
            if insulator_thickness < 0:
                insulator_thickness = 5 * contact_thickness
        if insulator_length is None:
            insulator_length = 2 * contact_length
        # self.reshape_outerBox(tresholded_res=True)
        if ID is not None:
            self.electrodes[ID]["kwargs"]["contact_length"] = contact_length
            self.electrodes[ID]["kwargs"]["contact_thickness"] = contact_thickness
            self.electrodes[ID]["kwargs"]["is_volume"] = is_volume
            self.electrodes[ID]["kwargs"]["insulator_offset"] = insulator_offset
            self.electrodes[ID]["volume"] = []
            self.electrodes[ID]["face"] = []
            if (
                self.electrodes[ID]["res"]
                > min(contact_length, insulator_thickness) / 2
            ):
                self.electrodes[ID]["res"] = (
                    min(contact_length, insulator_thickness) / 2
                )

        x_active = x_c - contact_length / 2
        y_active = self.y_c
        z_active = self.z_c
        cyl_act = self.add_cylinder(
            x_active,
            y_active,
            z_active,
            contact_length,
            self.Nerve_D / 2 + contact_thickness,
        )
        cyl_ner2 = self.add_cylinder(
            x_active, y_active, z_active, contact_length, self.Nerve_D / 2
        )
        self.model.occ.cut([(3, cyl_act)], [(3, cyl_ner2)])

        if insulator:
            x_insulator = x_c + insulator_offset - insulator_length / 2
            y_insulator = self.y_c
            z_insulator = self.z_c

            cyl_ina = self.add_cylinder(
                x_insulator,
                y_insulator,
                z_insulator,
                insulator_length,
                self.Nerve_D / 2 + insulator_thickness,
            )
            cyl_ner = self.add_cylinder(
                x_insulator,
                y_insulator,
                z_insulator,
                insulator_length,
                self.Nerve_D / 2,
            )
            self.model.occ.cut([(3, cyl_ina)], [(3, cyl_ner), (3, cyl_act)])

    def add_CUFF_MP(
        self,
        ID=None,
        N=4,
        x_c=0,
        contact_width=None,
        contact_length=100,
        is_volume=True,
        contact_thickness=None,
        insulator=True,
        insulator_thickness=None,
        insulator_length=None,
        insulator_offset=0,
    ):
        """
        Add MultiPolar CUFF electrodes to the mesh

        Parameters
        ----------
        ID                      :int
            if not none and ID exist, change electrod ID,by defalt None
        N                       :int
            Number of active site, by default 4
        x_c                     :float
            x-position of the CUFF center in um, by default 0
            length of the CUFF electrod in um, by default 100
        contact_width           :float or None
            width of the active sites around the nerve, if None set to cover 4/5 of the perimeter
            with active sites
        contact_length          :float
            length along x of the contact site in um, by default 100
        is_volume   : bool
            if True the contact is kept on the mesh as a volume, by default True
        contact_thickness       :float
            thickness of the contact site in um, by default 5
        insulator                :bool
            remove insulator ring from the mesh (no conductivity), by default True
        insulator_thickness     :float
            thickness of the insulator ring in um, by default 20
        insulator_length        :float
            length along x of the insulator ring in um, by default 1000
        """
        if contact_width is None:
            contact_width = pi * self.Nerve_D * 4 / (5 * N)

        if contact_thickness is None:
            contact_thickness = 0.1 * (self.Outer_D - self.Nerve_D) / 2
            if contact_thickness < 0:
                contact_thickness = self.Nerve_D * 0.1
        if insulator_thickness is None:
            insulator_thickness = min(
                5 * contact_thickness, 0.4 * (self.Outer_D - self.Nerve_D) / 2
            )
        if insulator_length is None:
            insulator_length = 2 * contact_length

        if ID is not None:
            self.electrodes[ID]["kwargs"]["contact_width"] = contact_width
            self.electrodes[ID]["kwargs"]["contact_length"] = contact_length
            self.electrodes[ID]["kwargs"]["contact_thickness"] = contact_thickness
            self.electrodes[ID]["kwargs"]["insulator_thickness"] = insulator_thickness
            self.electrodes[ID]["kwargs"]["insulator_length"] = insulator_length
            self.electrodes[ID]["kwargs"]["insulator_offset"] = insulator_offset
            self.electrodes[ID]["kwargs"]["is_volume"] = is_volume
            self.electrodes[ID]["volume"] = [None for i in range(N)]
            self.electrodes[ID]["face"] = [None for i in range(N)]
            if contact_length / 3 < self.electrodes[ID]["res"]:
                self.electrodes[ID]["res"] = contact_length / 2

        angles = []
        bar_fus = []

        x_active = x_c - contact_length / 2
        y_active = self.y_c - contact_width / 2
        y_c = self.y_c
        z_c = self.z_c

        if insulator:
            if insulator_thickness is None:
                insulator_thickness = contact_thickness * 3
            if insulator_length is None:
                insulator_length = contact_length * 2

            x_insulator = x_c + insulator_offset - insulator_length / 2

            cyl1 = self.add_cylinder(
                x_insulator,
                y_c,
                z_c,
                insulator_length,
                self.Nerve_D / 2 + insulator_thickness,
            )
            cyl2 = self.add_cylinder(
                x_insulator, y_c, z_c, insulator_length, self.Nerve_D / 2
            )
            self.model.occ.cut([(3, cyl1)], [(3, cyl2)])

        for i in range(N):
            bar = self.add_box(
                x_active,
                y_active,
                z_c,
                contact_length,
                contact_width,
                contact_thickness + self.Nerve_D / 2,
            )
            angles += [(2 * pi * i) / (N)]
            self.rotate(bar, angles[-1], x_c, y_c, z_c, ax=1)
            bar_fus += [(3, bar)]

        if ID is not None:
            self.electrodes[ID]["angles"] = angles

        cyl = self.add_cylinder(0, self.y_c, self.z_c, self.L, self.Nerve_D / 2)
        self.model.occ.cut(bar_fus, [(3, cyl)])

    def add_CUFF_MEA(
        self,
        ID=None,
        N=4,
        x_c=0,
        y_c=0,
        z_c=0,
        size=None,
        thickness=100,
        inactive=True,
        inactive_th=None,
        inactive_L=None,
    ):
        """ """
        rise_warning("add_CUFF_MEA not updated use add_CUFF_MP instead")

        if size is None:
            s = pi * self.Nerve_D * 4 / (5 * N)
            size = (s, s)
        elif not np.iterable(size):
            size = (size, size)
        elif len(size) != 2:
            size = (size[0], size[0])

        self.add_CUFF_MP(
            ID=ID,
            N=N,
            x_c=x_c,
            contact_width=size[1],
            contact_length=size[0],
            is_volume=True,
            contact_thickness=thickness,
            insulator=inactive,
            insulator_thickness=inactive_th,
            insulator_length=inactive_L,
        )
        if ID is not None:
            self.electrodes[ID]["type"] = "CUFF MP"
