import numpy as np

from ....backend.file_handler import json_dump, json_load, rmv_ext
from ....backend.log_interface import rise_error, rise_warning
from ....backend.NRV_Class import NRV_class


def is_sim_param(X):
    """
    check if an object is a SimParameters, return True if yes, else False

    Parameters
    ----------
    X : object
        object to test

    Returns
    -------
    bool
        True it the type is a SimParameters object
    """
    return isinstance(X, SimParameters)


class SimParameters(NRV_class):
    """
    Class gathering parameters of a FEM FEniCS simulation. It allows to add,
    modify and store domains, boundaries condition and internal boundaries (thin layers)
    Can be saved and used to generate FEMsimulation.
    """

    def __init__(self, D=3, mesh_file="", data=None):
        """
        initialisation of the SimParameters:

        Parameters
        ----------
        D               :int
            dim of the mesh, by default 3
            NB: only 3 is implemented
        mesh_file       :str
            mesh directory and file name: by default ""
        data            :str, dict or SimParameters
            if not None, load SimParameters attribute from data, by default None
            (see SimParameters.load)
        """
        super().__init__()
        self.type = "simparameters"
        self.D = D
        self.mesh_file = rmv_ext(mesh_file)

        # domains
        self.Ndomains = 0
        self.domainsID = []
        self.domains_list = {}

        # boundaries
        self.Nboundaries = 0
        self.boundariesID = []
        self.boundaries_list = {}

        # internal boundaries (thin layer)
        self.inbound = False
        self.Ninboundaries = 0
        self.inboundariesID = []
        self.inboundaries_list = {}

        # gather mat_pty name for domain and internal layer
        self.mat_pty_map = {}

        if data is not None:
            self.load(data)

    def save(self, save=False, fname="SimParameters.json"):
        """
        Return SimParameters as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default "SimParameters.json"

        Returns
        -------
        sp_dic : dict
            dictionary containing all information
        """
        sp_dic = {}
        sp_dic["D"] = self.D
        sp_dic["file"] = self.mesh_file
        sp_dic["Ndomains"] = self.Ndomains
        sp_dic["domainsID"] = self.domainsID
        sp_dic["domains"] = self.domains_list
        sp_dic["Nboundaries"] = self.Nboundaries
        sp_dic["boundariesID"] = self.boundariesID
        sp_dic["boundaries"] = self.boundaries_list
        sp_dic["inbound"] = self.inbound
        sp_dic["Ninboundaries"] = self.Ninboundaries
        sp_dic["inboundariesID"] = self.inboundariesID
        sp_dic["inboundaries"] = self.inboundaries_list
        sp_dic["mat_pty_map"] = self.mat_pty_map
        if save:
            json_dump(sp_dic, fname)
        return sp_dic

    def load(self, data):
        """
        Load all SimParameters properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing SimParameters information
        """
        if type(data) == str:
            sp_dic = json_load(data)
        elif is_sim_param(data):
            sp_dic = self.save()
        else:
            sp_dic = data
        self.D = sp_dic["D"]
        self.mesh_file = sp_dic["file"]
        self.Ndomains = sp_dic["Ndomains"]
        self.domainsID = sp_dic["domainsID"]
        self.domains_list = sp_dic["domains"]
        self.Nboundaries = sp_dic["Nboundaries"]
        self.boundariesID = sp_dic["boundariesID"]
        self.boundaries_list = sp_dic["boundaries"]
        self.inbound = sp_dic["inbound"]
        self.Ninboundaries = sp_dic["Ninboundaries"]
        self.inboundariesID = sp_dic["inboundariesID"]
        self.inboundaries_list = sp_dic["inboundaries"]
        self.mat_pty_map = sp_dic["mat_pty_map"]

    def save_SimParameters(self, save=False, fname="SimParameters.json"):
        rise_warning("save_SimParameters is a deprecated method use save")
        return self.save(save=save, fname=fname)

    def load_SimParameters(self, data="SimParameters.json"):
        rise_warning("load_SimParameters is a deprecated method use load")
        self.load(data=data)

    def set_mesh_file(self, new_mesh_file):
        """
        set a new mesh file name

        Parameters
        ----------
        new_mesh_file   :str
            name of the new filename, will be save without the filename extension
        """
        self.mesh_file = new_mesh_file.replace(".gmsh", "").replace(".xdml", "")

    def __update_ID_list(self, lname, ID):
        """
        Internal use only:
        Parameter
        """
        if lname == "domains":
            IDlist = self.domainsID
        elif lname == "inbound":
            IDlist = self.inboundariesID
        elif lname == "bound":
            IDlist = self.boundariesID
        else:
            rise_error("_update_ID_list failed due to unknow list type")

        if IDlist == []:
            if ID is None:
                IDlist = [1]
            else:
                IDlist = [ID]
        else:
            np.sort(IDlist)
            if ID is None:
                IDlist += [IDlist[-1] + 1]
            else:
                if ID in IDlist:
                    return ID
                else:
                    IDlist += [ID]

        if lname == "domains":
            self.domainsID = IDlist
        elif lname == "inbound":
            self.inboundariesID = IDlist
        else:
            self.boundariesID = IDlist
        return IDlist[-1]

    def add_domain(
        self, mesh_domain, mat_pty=None, mat_file=None, mat_perm=None, ID=None
    ):
        """
        add new domain or update if mesh_domain already exists

        Parameters
        ----------
        mesh_domain     : int
            Mesh ID of the domain (should be 3D)
        mat_pty         : str, float or list[3]
            Material property, either mat_file or mat_perm
        mat_file        : str
            Material filename (see fmod.material.py) if None use mat_perm,
                by default None
        mat_perm        : float or list[3]
            Material permitivity, if float isotropic mat, if list[3] anisotropic mat
                if None set to 1 (and mat_file is None), by default None
        """
        if mat_pty is not None:
            mat_pty = mat_pty
        elif mat_file is not None:
            mat_pty = mat_file
        elif mat_perm is not None:
            mat_pty = mat_perm
        else:
            mat_pty = 1
            rise_warning(
                "neither mat_file or mat_perm set, set to default permitivity 1 S/m"
            )

        if mesh_domain not in self.domains_list:
            IDdom = self.__update_ID_list("domains", mesh_domain)
            self.domains_list[IDdom] = {
                "mesh_domain": mesh_domain,
                "mat_pty": mat_pty,
                "mixed_domain": [mesh_domain],
            }
        else:
            self.domains_list[mesh_domain]["mat_pty"] = mat_pty
        self.mat_pty_map[mesh_domain] = mat_pty
        self.Ndomains = len(self.domainsID)

    def add_boundary(
        self, mesh_domain, btype, value=None, variable=None, mesh_domain_3D=0, ID=None
    ):
        """
        add new boundary or update if mesh_domain already exists

        Parameters
        ----------
        mesh_domain     : int
            Mesh ID of the boundary (should be 2D)
        btype           : str {"Dirichlet", "Neuman"}
            Type of boundary condition either "Dirichlet" to set the
        value           : float
            set the condition to the value
        variable        : str
            name of a python variable from which the boundary value should be taken.
            NB: variable should be place as kwarg in prepare_sim see examples
        mesh_domain_3D  : int
            ID of the mesh of corresponding volume, by default 0
            NB: Most of the time 0 except for LIFE electrode, must be set to the corresponding fascicle)
        ID              : int
            ID of the boundary condition
        """
        IDbound = self.__update_ID_list("bound", mesh_domain)
        if value is not None:
            self.boundaries_list[IDbound] = {
                "mesh_domain": mesh_domain,
                "condition": btype,
                "value": value,
                "mesh_domain_3D": mesh_domain_3D,
            }
        elif variable is not None:
            self.boundaries_list[IDbound] = {
                "mesh_domain": mesh_domain,
                "condition": btype,
                "variable": variable,
                "mesh_domain_3D": mesh_domain_3D,
            }
        else:
            rise_warning("boundary not set, variable or boundary have to be precised")
        self.Nboundaries = len(self.boundariesID)

    def add_inboundary(
        self,
        mesh_domain,
        in_domains,
        thickness,
        mat_pty=None,
        mat_file=None,
        mat_perm=None,
        ID=None,
    ):
        """
        add new internal boundary or update if mesh_domain already exists

        Parameters
        ----------
        mesh_domain     : int
            Mesh ID of the boundary (should be 2D)
        in_domains       : list
            List of mesh IDs of the domain (if 3D group) or internal boundary (if 2D group)
            inside the boundary
        thickness       : float
            thicness of the internal boundary
        mat_pty         : str, float or list[3]
            Material property, either mat_file or mat_perm
        mat_file        : str
            Material filename (see fmod.material.py) if None use mat_perm,
                by default None
        mat_perm        : float or list[3]
            Material permitivity, if float isotropic mat, if list[3] anisotropic mat
                if None set to 1 (and mat_file is None), by default None
        """
        if mat_pty is not None:
            mat_pty = mat_pty
        elif mat_file is not None:
            mat_pty = mat_file
        elif mat_perm is not None:
            mat_pty = mat_perm
        else:
            mat_pty = 1
            rise_warning(
                "neither mat_file or mat_perm set, set to default permitivity 1 S/m"
            )

        self.inbound = True
        if mesh_domain not in self.inboundaries_list:
            IDibound = self.__update_ID_list("inbound", mesh_domain)
            self.inboundaries_list[IDibound] = {
                "mesh_domain": mesh_domain,
                "in_domains": in_domains,
                "thickness": thickness,
                "mat_pty": mat_pty,
            }
            # Compute corresponding domain for mixed space
            for j in self.domains_list:
                domain = self.domains_list[j]
                # Domain inside the boundary
                if domain["mesh_domain"] in in_domains:
                    domain["mixed_domain"] += [domain["mesh_domain"]]
                    if domain["mesh_domain"] == domain["mixed_domain"][0]:
                        domain["mixed_domain"][0] = mesh_domain
                # Domain inside the boundary but surounded by another internal boundary
                elif domain["mesh_domain"] + 1 in in_domains:
                    domain["mixed_domain"] += [domain["mesh_domain"] + 1]
                    if domain["mesh_domain"] == domain["mixed_domain"][0]:
                        domain["mixed_domain"][0] = mesh_domain
                # Domain outside the boundary
                else:
                    domain["mixed_domain"] += [mesh_domain]
        else:
            self.inboundaries_list[mesh_domain]["thickness"] = thickness
            self.inboundaries_list[mesh_domain]["mat_pty"] = mat_pty
        self.mat_pty_map[mesh_domain] = mat_pty
        self.Ninboundaries = len(self.inboundariesID)

    def get_mixedspace_domain(self, i_space=None, i_domain=None):
        """
        TO DO
        """
        if not self.inbound:
            if i_domain is None:
                return self.domains_list
            else:
                return i_domain
        else:
            if i_space is None:
                if i_domain is None:
                    md = [
                        self.domains_list[k]["mixed_domain"] for k in self.domains_list
                    ]
                else:
                    md = self.domains_list[i_domain]["mixed_domain"]
            else:
                if i_domain is None:
                    md = [
                        self.domains_list[k]["mixed_domain"][i_space]
                        for k in self.domains_list
                    ]
                else:
                    md = self.domains_list[i_domain]["mixed_domain"][i_space]
            return md

    def get_mixedspace_mat_pty(self, i_space=None, i_domain=None):
        """
        TO DO
        """
        if self.inbound:
            md = self.get_mixedspace_domain(i_space, i_domain)
            S = np.shape(md)
            if i_space is None:
                if i_domain is None:
                    mmf = [
                        [self.mat_pty_map[md[i][j]] for i in range(S[0])]
                        for j in range(S[1])
                    ]
                else:
                    mmf = [self.mat_pty_map[md[i]] for i in range(S[0])]
            else:
                if i_domain is None:
                    mmf = [self.mat_pty_map[md[i]] for i in range(S[0])]
                else:
                    mmf = self.mat_pty_map[md]
            return mmf

    def get_space_of_domain(self, i_domain):
        """
        TO DO
        """
        if i_domain == 0:
            return 0
        for i in range(len(self.domains_list[i_domain]["mixed_domain"])):
            if self.domains_list[i_domain]["mixed_domain"][i] == i_domain:
                return i
        rise_error("Domain " + str(i_domain) + " is in no space")

    def get_spaces_of_ibound(self, i_ibound):
        """
        retrun the surounding spaces of an internal boundary.
        !! Caution work for NerveMshCreator only : see if it can be generalized
        """
        in_space = self.get_space_of_domain(i_ibound - 1)
        out_space = 0
        if i_ibound > 100:  # Should be a perineurium
            out_space = 0
        else:  # Should be an axon membrane
            for i in self.inboundaries_list:
                if i_ibound in self.inboundaries_list[i]["in_domains"]:
                    out_space = self.get_space_of_domain(i - 1)
        return in_space, out_space

    def print_mixedspace_domain(self):
        doms = self.get_mixedspace_domain()
        print("spaces:   ", [k for k in range(len(doms[0]))])
        for i, dom in enumerate(doms):
            print("domain " + str(i) + ": ", dom)

    def print_mixedspace_mat_pty(self):
        mats = self.get_mixedspace_mat_pty()
        print("domains:   ", [k for k in range(len(mats[0]))])
        for i, mat in enumerate(mats):
            print("space " + str(i) + ": ", mat)
