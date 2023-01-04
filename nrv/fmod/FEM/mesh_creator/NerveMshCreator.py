from cmath import phase

from .MshCreator import *


class NerveMshCreator(MshCreator):
    def __init__(self, Length=10000, Outer_D=5,  Nerve_D=4000, y_c=0, z_c=0, data=None):
        super().__init__(D=3)
        self.res = 1000

        self.L = Length
        self.y_c = y_c
        self.z_c = z_c
        self.surf_c = [self.L/2]

        self.Outer_D = Outer_D
        self.Outer_Dum = Outer_D * 1000
        self.Outer_entities = {"face":[], "volume":[]}

        self.Nerve_D = Nerve_D
        self.Nerve_entities = {"face":[], "volume":[]}

        self.N_fascicle = 0
        self.fascicles = {}
        self.N_axon = 0
        self.axons = {}

        self.N_electrode = 0
        self.electrodes = {}

        self.default_res = {"Outerbox" : 1000, "Nerve":1000, "Fascicle":100, "Axon":10, "Electrode":50}
        
        self.geo_flag = False
        self.domain_flag = False
        self.refined_flag = False
        #gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.1)
        #gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 1)

    def compute_mesh(self):
        self.compute_geo()
        self.compute_domains()
        self.compute_res()

    ####################################################################################################
    #####################################   geometry definition  ##########################################
    ####################################################################################################

    def reshape_outerBox(self, Outer_D=None, res="default"):
        """
        Reshape the size of the FEM simulation outer box

        Parameters
        ----------
        outer_D : float
            FEM simulation outer box diameter, in mm, WARNING, this is the only parameter in mm !
        """
        if Outer_D is not None:
            self.Outer_D = Outer_D
        
        if not res=="default":
            self.default_res["Outerbox"]=res



    def reshape_nerve(self, Nerve_D=None, Length=None, y_c=None, z_c=None, Perineurium_thickness=5, res="default"):
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
        Perineurium_thickness   :float
            Thickness of the Perineurium sheet surounding the fascicles in um, 5 by default
        """
        
        if Length is not None:
            self.Length = Length
        if Nerve_D is not None:
            self.Nerve_D = Nerve_D
        if y_c is not None:
            self.y_c = y_c
        if z_c is not None:
            self.z_c = z_c

        if not res=="default":
            self.default_res["Nerve"]=res

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
                ID = 100
                while ID in self.fascicles:
                    ID += 1
            self.N_fascicle +=1

        if res == "default":
            res = self.default_res["Fascicle"]

        self.fascicles[ID] = {"y_c":y_c, "z_c":z_c,"D":D, "res":res, "face":None, "volume":None}
        

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
        if ID not in self.fascicles:
            if ID is None:
                ID = 0
                while ID in self.fascicles:
                    ID += 1
            self.N_fascicle +=1

        if res == "default":
            res = self.default_res["Axon"]

        self.axons[ID] = {"y_c":y_c, "z_c":z_c, "D":D, "res":res, "face":None, "volume":None}

    def add_electrode(self, elec_type, ID=None, res="default", **kwargs):
        """
        
        """
        if ID not in self.electrodes:
            if ID is None:
                ID = 0
                while ID in self.electrodes:
                    if self.electrodes[ID]["type"]=="CUFF MEA":
                        ID += self.electrodes[ID]["kwargs"]["N"]
                    ID += 1
            self.N_electrode +=1

        if res == "default":
            res = self.default_res["Electrode"]

        self.electrodes[ID] = {"type":elec_type, "res":res, "kwargs":kwargs}   

    
    def compute_geo(self):
        """
        Compute the mesh geometry

        """
        self.add_cylinder(0, self.y_c, self.z_c, self.L, self.Outer_Dum/2)
        
        self.add_cylinder(0, self.y_c, self.z_c, self.L, self.Nerve_D/2)
        for i in self.fascicles:
            fascicle = self.fascicles[i]
            self.add_cylinder(0, fascicle["y_c"], fascicle["z_c"], self.L, fascicle["D"]/2)

        for i in self.axons:
            axon = self.axons[i]
            self.add_cylinder(0, axon["y_c"], axon["z_c"], self.L, axon["D"]/2)
        
        for i in self.electrodes:
            electrode = self.electrodes[i]
            if electrode["type"]=="CUFF MEA":
                self.add_Cuff_MEA(ID=i, **electrode["kwargs"])
            elif electrode["type"]=="LIFE":
                self.add_LIFE(ID=i, **electrode["kwargs"])
        
        self.fragment()
        self.geo_flag = True


    ####################################################################################################
    #####################################   domains definition  ##########################################
    ####################################################################################################

    def compute_domains(self):
        if not self.geo_flag:
            print("compute geometry before domain")
            return None
        else:
            self.link_entity_domains(2)
            self.link_entity_domains(3)
            self.compute_entity_domain()
            self.domain_flag =True


    def _is_outerbox(self, dx, dy, dz):
        """
        Internal use only: check if volume is the box
        INPUTS
        ------
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        
        """
        return np.allclose([dx, dy, dz], [self.L, self.Outer_Dum,self.Outer_Dum])

    def _is_nerve(self, dx, dy, dz):
        """
        Internal use only: check if volume is nerve or face is external face of nerve
        INPUTS
        ------
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        
        """
        return np.allclose([dy, dz], [self.Nerve_D, self.Nerve_D]) \
            and not np.isclose(dx, 0)

    def _is_fascicle(self, ID, dx, dy, dz, com, dim_key):
        """
        Internal use only: check if volume is fascicle ID or face is external face of fascicle ID
        INPUTS
        ------
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        com         : tupple(float)
            entity Center of Mass
        """
        fascicle = self.fascicles[ID]
        # Already computed
        status_test = fascicle[dim_key] is None
        # test good diameter
        size_test =  np.allclose([dx, dy, dz], [self.L, fascicle["D"],fascicle["D"]])
        # test center of mass in fascicle
        com_test = np.allclose(com,(self.L/2,fascicle["y_c"], fascicle["z_c"]), rtol=1, atol= fascicle["D"]/2)
        # print(ID, dx, dy, dz, com)
        # print(size_test,com_test)
        return status_test and size_test and com_test

    def _is_axon(self, ID, dx, dy, dz, com, dim_key):
        """
        Internal use only: check if volume is axon ID or face is external face of fascicle ID
        INPUTS
        ------
        dx          : float
            length along x of the entity boundbox
        dy          : float
            length along y of the entity boundbox
        dz          : float
            length along z of the entity boundbox
        com         : tupple(float)
            entity Center of Mass
        """

        axon = self.axons[ID]
        # Already computed
        status_test = axon[dim_key] is None
        # test good diameter
        size_test =  np.allclose([dx, dy, dz], [self.L, axon["D"],axon["D"]])
        # test center of mass in axon
        com_test = np.allclose(com,(self.L/2,axon["y_c"], axon["z_c"]), rtol=1, atol= axon["D"]/2)
        #print(size_test,com_test)
        return status_test and size_test and com_test
    
    def _is_CUFF_MEA_electrode(self, ID, dx, teta, com):
        """
        Internal use only: check if volume is electrode ID or face is external face of fascicle ID
        INPUTS
        ------
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
        if self.electrodes[ID]['type'] != 'CUFF MEA':
            return False

        # test good diameter
        size_test =  np.allclose([dx], [elec_kwargs["size"][0]])
        #print(ID, dx, dy, dz, com)

        com_test = np.isclose(com[0], elec_kwargs["x_c"])
        # test center of mass in axon

        N = elec_kwargs["N"]
        tetas = [teta for i in range(N)]
        angle_test = np.isclose(tetas, self.electrodes[ID]["angles"]).any()

        return size_test and com_test and angle_test


    def _is_LIFE_electrode(self, ID, dx, dy, dz, com):
        """
        Internal use only: check if volume is electrode ID or face is external face of fascicle ID
        INPUTS
        ------
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
        if self.electrodes[ID]['type'] != 'LIFE':
            return False

        size_test =  np.allclose([dx], [elec_kwargs["length"]])

        # test good diameter
        size_test =  np.allclose([dx, dy, dz], [elec_kwargs["length"], elec_kwargs["D"],elec_kwargs["D"]])
        # test center of mass in axon
        com_test = np.allclose(com,(elec_kwargs["x_c"],elec_kwargs["y_c"], elec_kwargs["z_c"]), rtol=1, atol= elec_kwargs["D"]/2)
        return size_test and com_test

    def link_entity_domains(self, dim):

        if dim == 2:
            entities, ent_com, ent_bd = self.get_faces(com=True, bd=True)
            key = "face"
            offset = 1
        else:
            entities, ent_com, ent_bd = self.get_volumes(com=True, bd=True)
            key = "volume"
            offset = 0
        
        for i in range(len(entities)):
            bd_x = abs(ent_bd[i][3]-ent_bd[i][0])
            bd_y = abs(ent_bd[i][4]-ent_bd[i][1])
            bd_z = abs(ent_bd[i][5]-ent_bd[i][2])
            if self._is_outerbox(bd_x, bd_y, bd_z):
                self.Outer_entities[key] += [entities[i][1]]

            elif self._is_nerve(bd_x, bd_y, bd_z):
                self.Nerve_entities[key] += [entities[i][1]]

            for j in self.fascicles:
                if self._is_fascicle(j,bd_x, bd_y, bd_z, ent_com[i],key):
                    self.fascicles[j][key] = entities[i][1]
            
            for j in self.axons:
                if self._is_axon(j,bd_x, bd_y, bd_z, ent_com[i],key):
                    self.axons[j][key] = entities[i][1]

            for j in self.electrodes:
                r_c = ((ent_com[i][1]-self.y_c)**2 + (ent_com[i][2]-self.z_c)**2)**0.5
                teta = phase(complex(ent_com[i][2] - self.z_c, ent_com[i][1] - self.y_c)) % (2*pi)
                if self._is_CUFF_MEA_electrode(j,bd_x, teta, ent_com[i]):
                    N = self.electrodes[j]['kwargs']['N']
                    ID_EA = round(teta * N /(2*pi))
                    if dim == 3:
                        if self.electrodes[j][key][ID_EA] is None:
                        #print(teta/(2*pi),ID_EA, ent_com[i], j)
                            self.electrodes[j][key][ID_EA] = entities[i][1]
                        else:
                            print("Warning : two volumes can be same electrode only the first one is kept")
                    else:
                        if self.electrodes[j][key][ID_EA] is None:
                        #print(teta/(2*pi),ID_EA, ent_com[i], j)
                            self.electrodes[j][key][ID_EA] = (entities[i][1], r_c)
                        elif isinstance(self.electrodes[j][key][ID_EA], tuple):
                            if r_c > self.electrodes[j][key][ID_EA][1]:
                                self.electrodes[j][key][ID_EA] = (entities[i][1], r_c)
                elif self._is_LIFE_electrode(j,bd_x, bd_y, bd_z, ent_com[i]):
                    self.electrodes[j][key] = entities[i][1]


    def compute_entity_domain(self):
        """

        """
        # Outer box domain
        self.add_domains(obj_IDs= self.Outer_entities['face'],phys_ID=1,dim=2)
        self.add_domains(obj_IDs= self.Outer_entities['volume'],phys_ID=0,dim=3)
        
        # nerve domain
        self.add_domains(obj_IDs=self.Nerve_entities['face'],phys_ID=3,dim=2)
        self.add_domains(obj_IDs=self.Nerve_entities['volume'],phys_ID=2,dim=3)

        for j in self.fascicles:
            self.add_domains(obj_IDs=self.fascicles[j]['face'],phys_ID=10+(2*j+1)%90,dim=2)
            self.add_domains(obj_IDs=self.fascicles[j]['volume'],phys_ID=10+(2*j)%90,dim=3)
        
        for j in self.axons:
            self.add_domains(obj_IDs=self.axons[j]['face'],phys_ID=1000+(2*j+1)%9000,dim=2)
            self.add_domains(obj_IDs=self.axons[j]['volume'],phys_ID=1000+(2*j)%9000,dim=3)

        for j in self.electrodes:
            if self.electrodes[j]['type']=="CUFF MEA":
                for ID_EA in range(self.electrodes[j]['kwargs']['N']):
                    self.add_domains(obj_IDs=self.electrodes[j]['face'][ID_EA][0],phys_ID=100+(2*(j+ID_EA)+1)%900,dim=2)                
                    self.add_domains(obj_IDs=self.electrodes[j]['volume'][ID_EA],phys_ID=100+(2*(j+ID_EA))%900,dim=3)
            else:
                self.add_domains(obj_IDs=self.electrodes[j]['face'],phys_ID=100+(2*j+1)%900,dim=2)                
                self.add_domains(obj_IDs=self.electrodes[j]['volume'],phys_ID=100+(2*j)%900,dim=3)



    ####################################################################################################
    ###################################   field (res) definition  ######################################
    ####################################################################################################

    def compute_res(self):
        if not self.domain_flag and self.geo_flag:
            print("compute geometry before domain")
            return None
        else:
            fields = []

            fields += [self.refine_entities(ent_ID=self.Outer_entities['volume'], res_in=self.default_res['Outerbox'], \
                dim=3, res_out=None, IncludeBoundary=True)]
            
            fields += [self.refine_entities(ent_ID=self.Nerve_entities['volume'], res_in=self.default_res['Nerve'], \
                dim=3, res_out=None, IncludeBoundary=True)]
            print(self.fascicles)
            for j in self.fascicles:
                fascicle = self.fascicles[j]
                fields += [self.refine_entities(ent_ID=fascicle['volume'], res_in=fascicle['res'], \
                    dim=3, res_out=None, IncludeBoundary=True)]
            
            for j in self.axons:
                axon = self.axons[j]
                fields += [self.refine_entities(ent_ID=axon['volume'], res_in=axon['res'], \
                    dim=3, res_out=None, IncludeBoundary=True)]
            
            for j in self.electrodes:
                electrode = self.electrodes[j]
                if electrode['type']=="CUFF MEA":
                    for ID_EA in range(electrode['kwargs']['N']):
                        fields += [self.refine_entities(ent_ID=electrode['volume'][ID_EA], res_in=electrode['res'], \
                            dim=3, res_out=None, IncludeBoundary=True)]
                elif electrode['type']=="LIFE":
                    fields += [self.refine_entities(ent_ID=electrode['volume'], res_in=electrode['res'], \
                            dim=3, res_out=None, IncludeBoundary=True)]

                        
            self.refine_min(fields)
            self.refined_flag = True

                
            

    ####################################################################################################
    #####################################   electrodes definition  ##########################################
    ####################################################################################################


    def add_Cuff_MEA(self, ID=None, N=4, x_c=0, y_c=0, z_c=0, size=None, thickness=100, inactive=True,\
        inactive_th=None, inactive_L=None):
        """
        
        """
        print(N)
        if size is None:
            s = pi*self.Nerve_D*4/(5*N)
            size = (s , s)
        elif not isinstance(size, tuple):
            size = (size, size)

        if ID is not None:
            self.electrodes[ID]["kwargs"]["size"] = size
            self.electrodes[ID]["kwargs"]["thickness"] = thickness
            self.electrodes[ID]["volume"] = [None for i in range(N)]
            self.electrodes[ID]["face"] = [None for i in range(N)]

        angles = []
        bar_fus = []

        x_active = x_c-size[0]/2
        y_active = y_c-size[1]/2
        z_active = 0

        if inactive:
            if inactive_th is None:
                inactive_th = thickness * 3
            if inactive_L is None:
                inactive_L = size[0] * 2
            
            x_inactive = x_c-inactive_L/2
            y_inactive = y_c
            z_inactive = z_c

            cyl1 = self.add_cylinder(x_inactive, y_inactive,z_inactive,inactive_L, self.Nerve_D/2 + inactive_th)
            cyl2 = self.add_cylinder(x_inactive, y_inactive,z_inactive,inactive_L, self.Nerve_D/2)
            self.model.occ.cut([(3, cyl1)], [(3, cyl2)])


        for i in range(N):
            bar = self.add_box(x_active, y_active, z_active, size[0], size[1], thickness+self.Nerve_D/2)
            angles += [(2 * pi * i) / (N)]
            self.rotate(bar, angles[-1],x_c,y_c, z_c, ax=1)
            bar_fus += [(3,bar)]

        if ID is not None:
            self.electrodes[ID]["angles"] = angles
        
        cyl = self.add_cylinder(0, self.y_c, self.z_c, self.L, self.Nerve_D/2)
        self.model.occ.cut(bar_fus, [(3, cyl)])


    def add_LIFE(self, ID=None, x_c=0, y_c=0, z_c=0, length=1000, D=25):
        """
        
        """

        if ID is not None:
            self.electrodes[ID]["volume"] = []
            self.electrodes[ID]["face"] = []

        angles = []
        bar_fus = []

        x_active = x_c-length/2
        y_active = y_c
        z_active = z_c

        LIFE = self.add_cylinder(x_active, y_active,z_active,length,D/2)


