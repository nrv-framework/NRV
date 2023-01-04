import json
import numpy as np
from ....backend.file_handler import json_load, json_dump, rmv_ext

class SimParameters:
    def __init__(self, D=3, mesh_file="", data=None):
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

        # gather mat_file name for domain and internal layer
        self.mat_file_map = {}

        if data is not None:
            self.load_SimParameters(data)


    def save_SimParameters(self, save=False, fname='SimParameters.json'):
        """
        Return SimParameters as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default 'SimParameters.json'

        Returns
        -------
        sp_dic : dict
            dictionary containing all information
        """
        sp_dic = {}
        sp_dic['D'] = self.D
        sp_dic['file'] = self.mesh_file
        sp_dic['Ndomains'] = self.Ndomains
        sp_dic['domainsID'] = self.domainsID
        sp_dic['domains'] = self.domains_list
        sp_dic['Nboundaries'] = self.Nboundaries
        sp_dic['boundariesID'] = self.boundariesID
        sp_dic['boundaries'] = self.boundaries_list
        sp_dic['inbound'] = self.inbound
        sp_dic['Ninboundaries'] = self.Ninboundaries
        sp_dic['inboundariesID'] = self.inboundariesID
        sp_dic['inboundaries'] = self.inboundaries_list
        sp_dic['mat_file_map'] = self.mat_file_map
        if save:
            json_dump(sp_dic, fname)
        return sp_dic


    def load_SimParameters(self, data):
        """
        Load all SimParameters properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing SimParameters information
        """
        if type(data) == str:
            sp_dic = json_load(data)
        else: 
            sp_dic = data
        self.D = sp_dic['D']
        self.mesh_file = sp_dic['file']
        self.Ndomains = sp_dic['Ndomains']
        self.domainsID = sp_dic['domainsID']
        self.domains_list = sp_dic['domains']
        self.Nboundaries = sp_dic['Nboundaries']
        self.boundariesID = sp_dic['boundariesID']
        self.boundaries_list = sp_dic['boundaries']
        self.inbound = sp_dic['inbound']
        self.Ninboundaries = sp_dic['Ninboundaries']
        self.inboundariesID = sp_dic['inboundariesID']
        self.inboundaries_list = sp_dic['inboundaries']
        self.mat_file_map = sp_dic['mat_file_map']



    def set_mesh_file(self, new_mesh_file):
        """
        set a new mesh file name
        Parameters
        ----------
        new_mesh_file   :str 
            name of the new filename, will be save without the filename extension
        """
        self.mesh_file = new_mesh_file.replace('.gmsh','').replace('.xdml','') 

    def __update_ID_list(self, lname, ID):
        """
        Internal use only:
        Parameter
        """
        if lname =='domains':
            IDlist = self.domainsID
        elif lname =='inbound':
            IDlist = self.inboundariesID
        elif lname =='bound':
            IDlist = self.boundariesID
        else:
            print('Error: _update_ID_list failed due to unknow list type')
        
        if IDlist == []:
            if ID is None:
                IDlist = [1]
            else:
                IDlist = [ID]
        else:
            np.sort(IDlist)
            if ID is None:
                IDlist += [IDlist[-1]+1]
            else:
                if ID in IDlist:
                    return ID
                else:
                    IDlist += [ID]
        
        if lname =='domains':
            self.domainsID = IDlist
        elif lname =='inbound':
            self.inboundariesID = IDlist     
        else:
            self.boundariesID = IDlist
        return IDlist[-1]

    def add_domain(self, mesh_domain, mat_file, ID=None):
        """
        add new domain or change if ID already exists
        Parameters
        ----------
        mesh_domain   :str 
            name of the new filename, will be save without the filename extension
        """
        IDdom= self.__update_ID_list('domains', mesh_domain)
        self.domains_list[IDdom] = {'mesh_domain': mesh_domain, 'mat_file':mat_file, 'mixed_domain':[mesh_domain]}

        self.mat_file_map[mesh_domain] = mat_file
        self.Ndomains = len(self.domainsID)
    
    def add_boundary(self, mesh_domain, btype, value=None, variable=None, mesh_domain_3D=0, ID=None):
        """
        add new boundary or change if ID already exists
        Parameters
        ----------
        new_mesh_file   :str 
            name of the new filename, will be save without the filename extension
        """
        IDbound= self.__update_ID_list('bound', mesh_domain)
        if value is not None:
            self.boundaries_list[IDbound] = {'mesh_domain': mesh_domain, 'condition':btype,\
                "value":value, "mesh_domain_3D":mesh_domain_3D}
        elif variable is not None:
            self.boundaries_list[IDbound] = {'mesh_domain': mesh_domain, 'condition':btype,\
                "variable":variable, "mesh_domain_3D":mesh_domain_3D}
        else: 
            print("Warning: boundary not set, variable or boundary have to be precised")
        self.Nboundaries = len(self.boundariesID)
        
    def add_inboundary(self, mesh_domain, mat_file, thickness, in_domains, ID=None):
        """
        add new internal boundary or change if ID already exists
        Parameters
        ----------
        new_mesh_file   :str 
            name of the new filename, will be save without the filename extension
        """
        self.inbound = True
        IDibound= self.__update_ID_list('inbound', mesh_domain)
        self.inboundaries_list[IDibound] = {'mesh_domain': mesh_domain, 'in_domains':in_domains,\
            'thickness' : thickness, 'mat_file':mat_file}
        # Cumpute corresponding domain for mixed space
        for i in in_domains:
            for j in self.domains_list:
                domain = self.domains_list[j]
                # Domain inside the boundary
                if domain['mesh_domain'] == i:
                    domain['mixed_domain'] += [i]
                    if domain['mesh_domain'] == domain['mixed_domain'][0]: ##refaire une fois avec la nouvelle valeur pour le cas des axon
                        domain['mixed_domain'][0] = mesh_domain
                # Domain outside the boundary
                else:
                    domain['mixed_domain'] += [mesh_domain] 
        self.mat_file_map[mesh_domain] = mat_file           
        self.Ninboundaries = len(self.inboundariesID)
    
    
    def get_mixedspace_domain(self, i_space=None, i_domain=None):
        """
        
        """
        if self.inbound:
            if i_space is None:
                if i_domain is None:
                    md = [self.domains_list[k]['mixed_domain'] for k in self.domains_list]
                else:
                    md = self.domains_list[i_domain]['mixed_domain']
            else:
                if i_domain is None:
                    md = [self.domains_list[k]['mixed_domain'][i_space] for k in self.domains_list]
                else:
                    md = self.domains_list[i_domain]['mixed_domain'][i_space]
            return md
    
    def get_mixedspace_mat_file(self, i_space=None, i_domain=None):
        """
        
        """
        if self.inbound:
            md = self.get_mixedspace_domain(i_space, i_domain)
            S = np.shape(md)
            if i_space is None:
                if i_domain is None:
                    mmf = [[self.mat_file_map[md[i][j]] for i in range(S[0])] for j in range(S[1])]
                else:
                    mmf = [self.mat_file_map[md[i]] for i in range(S[0])]
            else:
                if i_domain is None:
                    mmf = [self.mat_file_map[md[i]] for i in range(S[0])]
                else:
                    mmf = self.mat_file_map[md]
            return mmf

    def get_space_of_domain(self, i_domain=None):
        for i in range(len(self.domains_list[i_domain]['mixed_domain'])):
                if self.domains_list[i_domain]['mixed_domain'][i] == i_domain:
                    return(i)
        print("Error: domain "  + str(i_domain) + " is in no space")


