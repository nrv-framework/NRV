import os
import math
import numpy as np

from dolfinx.io import gmshio
import gmsh

from ....backend.file_handler import rmv_ext
from ....backend.MCore import *
from ....backend.log_interface import rise_error, rise_warning, pass_info
pi = np.pi

def is_MshCreator(object):
    """
    check if an object is a MshCreator, return True if yes, else False

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

class MshCreator:
    def __init__(self, D, ver_level=2):
        self.D = D 
        self.entities = {}
        self.volumes = []
        self.volumes_com = []
        self.volumes_bd = []

        self.faces = []
        self.faces_com = []
        self.faces_bd = []

        self.N_domains = 0
        self.domains = []
        self.file = ""

        self.Nfeild = 0
        self.res = 1

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
        
        #gmsh.option.setNumber('General.NumThreads', 3)
        #gmsh.option.set_number('Geometry.OCCParallel', 4)
        
        #gmsh.option.set_number('Mesh.Algorithm3D', 10)
    
    def __del__(self):
        gmsh.finalize()
    
    #####################
    ## special methods ##
    #####################

    def get_obj(self):
        """
        update and return list of mesh entities  
        RETURNS
        -------
        self.entities       :dict
        """
        return self.entities
    
    def get_volumes(self, com=False, bd=False):
        """
        update and return list of mesh volumes (optional: with their center of mass)
        
        RETURNS
        -------
        self.faces      :list[tuple]
        """
        self.model.occ.synchronize()
        self.volumes = self.model.getEntities(dim=3)
        self.volumes_com = []
        self.volumes_bd = []
        for i in range(len(self.volumes)):
            volume = self.volumes[i]
            self.volumes_com += [np.round(self.model.occ.getCenterOfMass(volume[0], volume[1]),4)]
            self.volumes_bd += [np.round(self.model.occ.getBoundingBox(volume[0], volume[1]),4)]
        
        if com:
            if bd:
                return self.volumes, self.volumes_com, self.volumes_bd
            else:
                return self.volumes, self.volumes_com
        else:
            if bd:
                return self.volumes, self.volumes_bd
            
        return self.volumes

    def get_mesh_info(self, verbose=False):
        entities = self.model.getEntities()
        nodeTags= self.model.mesh.getNodes()[0]
        elemTags = self.model.mesh.getElements()[1]

        self.N_entities = len(entities)
        self.N_nodes = len(nodeTags)
        self.N_elements = sum(len(i) for i in elemTags)
        if verbose:
            pass_info('Mesh properties:')
            pass_info('Number of entities : ' + str(self.N_entities))
            pass_info('Number of nodes : ' + str(self.N_nodes))
            pass_info('Number of elements : ' + str(self.N_elements))
 
            
    
    def get_faces(self, com=False, bd=False):
        """
        update and return list of mesh face (optional: with their center of mass)
        
        RETURNS
        -------
         self.faces     :list[tuple]
        """
        self.model.occ.synchronize()
        self.faces = self.model.getEntities(dim=2)
        self.faces_com = []
        self.faces_bd = []
        for i in range(len(self.faces)):
            face = self.faces[i]
            self.faces_com += [np.round(self.model.occ.getCenterOfMass(face[0], face[1]),4)]
            self.faces_bd += [np.round(self.model.occ.getBoundingBox(face[0], face[1]),4)]

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
        RETURNS
        -------
        res     :float
            global resolution saved in the object
        """
        return self.res

    def set_res(self, new_res):
        """
        set the global resolution saved (usefull when no field are set)
        INPUT
        -----
        new_res     :float
            global resolution to set the object

        """
        self.res = new_res

    def set_verbosity(self, i=2):
        """
        from gmsh : Level of information printed on the terminal and the message console\
            
        INPUT
        -----
        i     : int (1, 2, 3, 4, 5 or 99)
            0: silent except for fatal errors
            1: +errors
            2: +warnings
            3: +direct
            4: +information
            5: +status
            99: +debug
        """
        self.verbosity_level = i 
        gmsh.option.setNumber("General.Verbosity", self.verbosity_level)
        

    def add_box(self,x=0, y=0, z=0, ax=5, ay=1, az=1):
        """
        
        INPUTS
        ------
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
  
        RETURNS
        -------
        """
        if self.D ==3:
            parameters = {"x":x, "y":y, "z":z, "ax":ax, "ay":ay, "az":az}
            box =self.model.occ.addBox(x, y, z,ax, ay, az)
            self.model.occ.synchronize()
            bounds =self.model.getEntities(dim=2)[-6:]
            self.entities[box] = {"type":"box","parameters":parameters, "bounds":bounds, 'dim':3}
            return box
        else:
            rise_warning('Not added : add_cylinder requiere 3D mesh')
            return None
        

    def add_cylinder(self, x=0, y=0, z=0, L=5, R=1):
        """
        add a x-oriented cylinder to mesh entities 

        INPUTS
        ------
        x       : float
            x position of the first face center
        y       : float
            y position of the first face center
        z       : float
            z position of the first face center
        L       : float
            Cylinder length along x
        R       : float
            Cylinder radius       

        RETURNS
        -------

        """
        if self.D ==3:
            parameters = {"x":x, "y":y, "z":z, "L":L, "R":R}
            cyl = self.model.occ.addCylinder(x, y,z,L,0,0, R)
            self.model.occ.synchronize()
            bounds =self.model.getEntities(dim=2)[-3:]
            self.entities[cyl] = {"type":"cylinder","parameters":parameters, "bounds":bounds, 'dim':3}
            return cyl
        else:
            rise_warning('Not added : add_cylinder requiere 3D mesh')
            return None


    def rotate(self, volume, angle,x=0, y=0, z=0, ax=0, ay=0, az=0, rad=True):
        """
        rotate volume

        INPUTS
        ------

        RETURNS
        -------

        """
        if not rad:
            angle = math.radians(angle)
        self.model.occ.rotate([(3,volume)], x,y, z, ax, ay, az, angle)


    def fragment(self, IDs=None, dim=3, verbose=True):
        """
        Fragmentation of the mesh important to link entities to each other

        INPUTS
        ------

        RETURNS
        -------

        """
        if IDs is None:
            if dim == 2:
                list_obj = self.get_faces(com=False)
            elif dim == 3:
                list_obj = self.get_volumes(com=False)
            else:
                list_obj = [(dim, k) for k in self.entities]
        elif not np.iterable(IDs) or len(IDs)<2:
            rise_warning('Need at least 2 entities to fragment')
            return -1
        else:
            list_obj = [(dim, k) for k in IDs]
        
        N_obj = len(list_obj)
        frag = self.model.occ.fragment([list_obj[0]], [k for k in list_obj[1:]])
        
        new_entities={}
        if verbose:
            pass_info("Warning: New volume generated by fragmentation, bounds are no longer up to date")
        for i in frag[0][:]:
            mask = [i in k for k in frag[1]]
            p_id =  (np.array(list_obj)[mask][:,1]).tolist()
            p_types = [self.entities[k]['type'] for k in p_id]
            dim = min([self.entities[k]['dim'] for k in p_id])
            com = np.round(self.model.occ.getCenterOfMass(i[0],i[1]),3)
            parameters = {'p_id':p_id, "p_types":p_types, "com":com}
            new_entities[i[1]] = {"type":"fragment","parameters":parameters, 'dim':dim}
        self.entities.update(new_entities)

    def add_domains(self,obj_IDs,phys_ID,dim=None, name=None):
        """
        add domains (ID + name) to a goupe of entities
        Caution: as to be used after all entities are placed 

        INPUTS
        ------
        fname    : str
            path and name of saving file. If ends with '.msh' only save in '.msh' file 
        """
        if not np.iterable(obj_IDs):
            obj_IDs = [obj_IDs]
        if dim is None:
            dim = max([self.entities[k]['dim'] for k in obj_IDs])
        self.model.addPhysicalGroup(dim, obj_IDs, phys_ID)
        
        if name is None:
            name = "domain " + str(self.N_domains)

        self.domains += (dim, phys_ID, name)
        
    def refine_entities(self, ent_ID, res_in, dim, res_out=None, IncludeBoundary=True):
        """
        refine mesh resolution in a list of faces or volumes IDs 

        INPUTS
        ------
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
        if not np.iterable(ent_ID) :
            ent_ID = [ent_ID]

        if dim==2:
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
    
    def refine_min(self, feild_IDs):
        """
        refine mesh resolution taking the minimum value for a list of refinment fields

        INPUTS
        ------
        feild_IDs    : list[int]
            list of field from wich the minimum should be taken
        """
        self.Nfeild += 1

        self.model.mesh.field.add("Min", self.Nfeild)
        self.model.mesh.field.setNumbers(self.Nfeild, "FieldsList", feild_IDs)

        return self.Nfeild
    
    def generate(self):
        """
        
        """
        if self.Nfeild>0:
            self.model.mesh.field.setAsBackgroundMesh(self.Nfeild)
        else:
            gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.1*self.res)
            gmsh.option.setNumber("Mesh.CharacteristicLengthMax", self.res)

        self.model.occ.synchronize()

        #print("nt:", gmsh.option.getNumber("General.NumThreads"))
        self.model.mesh.generate(self.D)
        self.is_generated = True

    def save(self, fname):
        """
        Save mesh in fname in '.msh'

        INPUTS
        ------
        fname    : str
            path and name of saving file. If ends with '.msh' only save in '.msh' file 
        """
        if self.is_generated:
            fname = rmv_ext(fname)
            gmsh.write(fname+".msh")
            self.file = fname

    def visualize(self, fname=None):
        if fname is None:
            self.generate()
            gmsh.fltk.run()
        elif fname is not None:
            self.save(fname=fname)
            os.system('gmsh '+ self.file +'.msh')
            
        