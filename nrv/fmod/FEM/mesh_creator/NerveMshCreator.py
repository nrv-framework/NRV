from cmath import phase
import numpy as np

from ....backend.NRV_Class import NRV_class
from ....backend.log_interface import rise_error, rise_warning
from ....utils.units import mm
from ....backend.file_handler import rmv_ext
from .MshCreator import MshCreator, pi

ENT_DOM_offset = {
    "Volume": 0,
    "Surface": 1,
    "Outerbox": 0,
    "Nerve": 2,
    "Fascicle": 10,
    "Electrode": 100,
    "Axon": 1000,
}

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


class NerveMshCreator(MshCreator):
    """
    Class allowing to generate Nerve shape 3D gmsh mesh with labeled physical domain
    Contains methodes dealing with the mesh geometries, physical domains and feilds
    Inherit from MshCreator class. see MshCreator for further detail
    """

    def __init__(
        self, Length=10000, Outer_D=5, Nerve_D=4000, y_c=0, z_c=0, ver_level=2,
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
        return param

    def save(
        self,
        fname="nervemshcreator.json",
        save=True,
        mshfname=None,
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
        if self.is_generated and save:
            if mshfname is None:
                mshfname = rmv_ext(fname) + ".msh"
            super().save(fname=mshfname, generate=False)
        fname = rmv_ext(fname) + ".json"
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
            for i in self.fascicles:
                fascicle = self.fascicles[i]
                self.add_cylinder(
                    0, fascicle["y_c"], fascicle["z_c"], self.L, fascicle["D"] / 2
                )

            for i in self.axons:
                axon = self.axons[i]
                self.add_cylinder(0, axon["y_c"], axon["z_c"], self.L, axon["D"] / 2)
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

    def reshape_fascicle(self, D, y_c=0, z_c=0, ID=None, res="default"):
        """
        Reshape a fascicle of the FEM simulation

        Parameters
        ----------
        Fascicle_D  : float
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

        if res == "default":
            res = self.default_res["Fascicle"]
        if D / 5 < res:
            res = D / 5

        self.fascicles[ID] = {
            "y_c": y_c,
            "z_c": z_c,
            "D": D,
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
        elif ID in self.fascicles:
            del self.fascicles[ID]
            self.N_fascicle -= 1

    def reshape_axon(self, D, y_c=0, z_c=0, ID=None, res="default"):
        """
        Reshape a axon of the FEM simulation

        Parameters
        ----------
        Fascicle_D  : float
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
        if D / 3 < res:
            res = D / 3

        self.axons[ID] = {
            "y_c": y_c,
            "z_c": z_c,
            "D": D,
            "res": res,
            "face": None,
            "volume": None,
        }

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
            if "D" in kwargs:
                D = kwargs["D"]
            else:
                D = 25
            if D / 3 < res:
                res = D / 3

        self.electrodes[ID] = {"type": elec_type, "res": res, "kwargs": kwargs}

    ####################################################################################################
    #####################################   domains definition  ########################################
    ####################################################################################################

    def compute_domains(self):
        if not self.is_geo:
            rise_error("compute geometry before domain")
        elif not self.is_dom:
            self.__link_entity_domains(2)
            self.__link_entity_domains(3)
            self.compute_entity_domain()
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

    def __is_fascicle(self, ID, dx, dy, dz, com, dim_key):
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
        fascicle = self.fascicles[ID]
        # Already computed
        status_test = fascicle[dim_key] is None
        # test good diameter
        size_test = np.allclose([dx, dy, dz], [self.L, fascicle["D"], fascicle["D"]])
        # test center of mass in fascicle
        com_test = np.allclose(
            com,
            (self.L / 2, fascicle["y_c"], fascicle["z_c"]),
            rtol=1,
            atol=fascicle["D"] / 2,
        )
        return status_test and size_test and com_test

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
        status_test = axon[dim_key] is None
        # test good diameter
        size_test = np.allclose([dx, dy, dz], [self.L, axon["D"], axon["D"]])
        # test center of mass in axon
        com_test = np.allclose(
            com, (self.L / 2, axon["y_c"], axon["z_c"]), rtol=1, atol=axon["D"] / 2
        )
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
            [dx, dy, dz], [elec_kwargs["length"], elec_kwargs["D"], elec_kwargs["D"]]
        )
        # test center of mass in LIFE
        com_test = np.allclose(
            com,
            (elec_kwargs["x_c"], elec_kwargs["y_c"], elec_kwargs["z_c"]),
            atol=elec_kwargs["D"] / 2,
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
                if self.__is_fascicle(j, bd_x, bd_y, bd_z, ent_com[i], key):
                    self.fascicles[j][key] = entities[i][1]

            for j in self.axons:
                if self.__is_axon(j, bd_x, bd_y, bd_z, ent_com[i], key):
                    self.axons[j][key] = entities[i][1]

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

        for j in self.axons:
            id_ph = ENT_DOM_offset["Axon"] + (2 * j)
            self.add_domains(obj_IDs=self.axons[j]["volume"], phys_ID=id_ph, dim=3)
            id_ph += ENT_DOM_offset["Surface"]
            self.add_domains(obj_IDs=self.axons[j]["face"], phys_ID=id_ph, dim=2)

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
            for j in self.fascicles:
                fascicle = self.fascicles[j]
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
            for j in self.axons:
                axon = self.axons[j]
                fields += [
                    self.refine_entities(
                        ent_ID=axon["volume"],
                        res_in=axon["res"],
                        dim=3,
                        res_out=None,
                        IncludeBoundary=True,
                    )
                ]
            # Electrodes fields
            for j in self.electrodes:
                electrode = self.electrodes[j]

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

    ####################################################################################################
    ###################################   electrodes definition  #######################################
    ####################################################################################################

    def add_LIFE(
        self, ID=None, x_c=0, y_c=0, z_c=0, length=1000, D=25, is_volume=False
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
        D           :float
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
        self.add_cylinder(x_active, y_active, z_active, length, D / 2)

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
                5 * contact_thickness, 0.4 * (self.Outer_D - self.Nerve_D) / 2
            )
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
            if contact_length / 3 < self.electrodes[ID]["res"]:
                self.electrodes[ID]["res"] = contact_length / 2

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
