import pygame
import numpy as np
import os
from typing import Optional

from textures import Atlas

# this is a global variable, perhaps remove later
global_texture_atlas = Atlas()

class Mesh:

	__slots__ = ['mesh', 'uv_mesh', 'textures', 'position']

	def __init__(self, 
			mesh, 	 # mesh is the only required argument
					 #	 the rest are optional (have defaults)
			uv_mesh  = (), 
			textures = (), 
			position = (0, 0, 0), 
		):


		self.mesh: np.ndarray = np.asarray(mesh)

		if (uv_mesh):
			self.uv_mesh = np.asarray(uv_mesh)
		else: 
			#default val
			self.uv_mesh = np.asarray([
				((0, 0),
				 (0, 1),
				 (1, 1),)
				for _ in self.mesh # for every tri in mesh
			]) #list comprehension to make np array

		if (textures):
			self.textures = textures
		else:
			self.textures = [0 for _ in self.mesh]

		self.position: list[float] = [position[0], position[1], position[2]]


# NOTE: use triangulated obj files (3 vertex face elements)
def load_obj_file(
    atlas:    Atlas, 
    filepath: str, 
    scale:    Optional[float] = 0
)   ->        tuple:
    """
    Load an obj file, given the filepath of said object
    
    atlas:      Alias object
        all loaded textures are stored here
        texturedata in meshes refer to indexes in atlas
    filepath:   str
    scale:      float, None
        The max size of any one face. Largest face becomes scale value. \n
        Defaults to 0, which will enable auto-scaling \n
        Setting scale to None preserves original values. 

    returns:    tuple
        element 1: list of faces
        element 2: list of uv coordinates corresponding to faces
        element 3: list of face texture indexes (corresponding to Atlas object), 

    Note that if object file is missing a texture, a default will be provided\n
    Similarly, if object file is missing uv coords, a default will be provided
    """
    # sanitize args
    if (scale is not None) and (scale < 0):
        raise ValueError("scale argument must be greater than zero")

    info = filepath.split('/')

    dirpath = '/'.join(info[:-1]) + '/'
    filename = info[-1]

    prev_dir = os.getcwd()
    os.chdir(dirpath)

    with open(filename, 'r') as file:
        raw = file.readlines()

        # read file
        mtllibs = []

        vertexes = []
        uv_coords = []

        faces = []
        uv_faces = []
        textures = []
        
        for line in raw:
            if (line[:6] == 'mtllib'):
                mtllibs.append(f"./{line.split()[1]}")

        # load all materials
        for lib in mtllibs:

            with open(lib) as libfile: 
                rawlib = libfile.readlines()

                curr_mtl = ""
                for line in rawlib:
                    
                    # NOTE add other loading features here
                    #   for now, only basic texture maps implemented
                    if   (line.strip()[:6] == 'newmtl'):
                        curr_mtl = line.split()[1]
                    elif (line.strip()[:6] == 'map_Kd'):
                        mtl_path = line.split()[1]
                        if (curr_mtl not in atlas):
                            atlas.add_tex(
                                curr_mtl,
                                pygame.surfarray.array3d(pygame.image.load(f"./{mtl_path}"))
                            )
                        curr_mtl = ""

        curr_mtl  = ""
        for line in raw:
            if (line.strip()[:6] == 'usemtl'):
                curr_mtl = line.split()[1]

            if (line.strip()[:2] == 'v '):
                vertexes.append(
                    (float(line.split()[1]), float(line.split()[2]), float(line.split()[3]))
                )
            if (line.strip()[:2] == 'vt'):
                uv_coords.append(
                    (float(line.split()[1]), float(line.split()[2]) 
                        if len(line.split()) >=3 else 0.0)
                )
        
        # scale vertex data
        if (scale is not None):
            if (scale == 0):
                scale_coef = 1/max([num for val in vertexes for num in val])
            else:
                scale_coef = scale/max([num for val in vertexes for num in val])
            vertexes = [(vtx[0]*scale_coef, vtx[1]*scale_coef, vtx[2]*scale_coef) for vtx in vertexes]
        
        for line in raw:
            if (line.strip()[:2] == 'f '):
                indexes = [i.split('/') for i in line.split()[1:]]

                faces.append((
                    vertexes[int(indexes[0][0])-1], 
                    vertexes[int(indexes[1][0])-1], 
                    vertexes[int(indexes[2][0])-1],
                ))

                
                if (
                    ((len(indexes[0]) > 1) and (indexes[0][1] != ''))
                and ((len(indexes[1]) > 1) and (indexes[1][1] != ''))
                and ((len(indexes[2]) > 1) and (indexes[2][1] != ''))
                ):
                    uv_indexes = [i[1] for i in indexes]
                    uv_faces.append((
                        uv_coords[int(uv_indexes[0])-1], 
                        uv_coords[int(uv_indexes[1])-1], 
                        uv_coords[int(uv_indexes[2])-1],
                    ))

                textures.append(atlas[curr_mtl] if curr_mtl in atlas else 0)

    os.chdir(prev_dir)

    return (faces, uv_faces, textures)

