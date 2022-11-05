import pygame
import numpy as np
import math
import os

TEXTURE_NOT_FOUND = "./assets/Missing.png"

# this is a global variable, perhaps remove later
global_texture_atlas = {
	'' : pygame.surfarray.array3d(pygame.image.load(TEXTURE_NOT_FOUND))
}

class Mesh:

	__slots__ = ['mesh', 'uv_mesh', 'textures', 'position', 'x_rot', 'y_rot']

	def __init__(self, 
			mesh, 	 # mesh is the only required argument
					 #	 the rest are optional (have defaults)
			uv_mesh  = (), 
			textures  = (), 
			position = (0, 0, 0), 
		):

		self.position = [position[0], position[1], position[2]]

		self.mesh = np.asarray(mesh)

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
			self.textures = ['' for _ in self.mesh]


# NOTE: use triangulated obj files (3 vertex face elements)
def load_obj_file(atlas: dict[str: np.ndarray], filepath: str) -> Mesh:
    """
    Load an obj file, given the filepath of said object
    filepath:
        str
    returns:
        Mesh object

    Note that if object file is missing a texture, a default will be provided\n
    similarly, if object file is missing uv coords, a default will be provided
    """
    info = filepath.split('/')

    dirpath = '/'.join(info[:-1]) + '/'
    filename = info[-1]

    os.chdir(dirpath)

    with open(filename, 'r') as file:
        raw = file.readlines()

        # find materials
        mtllibs = []
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
                            atlas[curr_mtl] = pygame.surfarray.array3d(
                                pygame.image.load(f"./{mtl_path}")
                            )
                        curr_mtl = ""

        vertexes = []
        uv_coords = []

        faces = []
        uv_final = []
        textures = []

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
        
        # scale vertex data to be smaller
        scale = math.log(max([num for val in vertexes for num in val]), 10)
        vertexes = [(vtx[0]/10**scale, vtx[1]/10**scale, vtx[2]/10**scale) for vtx in vertexes]
        
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
                    uv_final.append((
                        uv_coords[int(uv_indexes[0][1])-1], 
                        uv_coords[int(uv_indexes[1][1])-1], 
                        uv_coords[int(uv_indexes[2][1])-1],
                    ))

                textures.append(curr_mtl)



        return Mesh(faces, uv_final, textures)



meshes = [load_obj_file(global_texture_atlas, "./assets/teapot/teapot.obj")]