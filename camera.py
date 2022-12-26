import numpy as np
from numba import njit
import math

from meshes import Mesh

class Camera:
    """Represents a viewport into the world"""
    
    #__slots__ = [
    #    'WIDTH',
    #    'HEIGHT',
    #    'CLIPPING_PLANES',
    #    'PROJ',
    #    'PIX_SIZE',
    #    'MAX_Z',
    #    'position',
    #    'x_rot',
    #    'y_rot'
    #]

    OFFSET_Z = .1
    # honestly, FOV_RAD doesn't make any sense to me
    FOV_RAD = 360

    def __init__(
        self, 
        surf_dim: tuple[int, int], 
        pix_size = 1, 
        max_visible = 1000,
        init_pos: list[float] = (0, 0, 0), 
        x_rot: float = 0.0, y_rot: float = 0.0
    ):

        self.PIX_SIZE = int(pix_size)
        if (self.PIX_SIZE < 1):
            raise ValueError("pix_size cannot be smaller than native screen resolution (1)")

        self.WIDTH, self.HEIGHT = surf_dim
        self.MAX_Z = max_visible

        # a plane is just 3 points (ccw faces towards cam)
        # this is the frustum of the camera
        self.CLIPPING_PLANES = np.asarray((
            ((0, 0, self.OFFSET_Z*10+1), (1, 1, self.OFFSET_Z*10+1), (1, 0 , self.OFFSET_Z*10+1)), # front facing
            #((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 1.0, 1.0)), #cut screen in half
            # hardcoded camera limits for pix_size = 3
                # east 
            ((0, 0, 0), (self.WIDTH/200, self.HEIGHT/200, self.OFFSET_Z*10+pix_size*3), (self.WIDTH/200, -self.HEIGHT/200, self.OFFSET_Z*10+pix_size*3)),
                # west
            ((0, 0, 0), (-self.WIDTH/200, -self.HEIGHT/200, self.OFFSET_Z*10+pix_size*3), (-self.WIDTH/200, self.HEIGHT/200, self.OFFSET_Z*10+pix_size*3)),
                # north
            ((0, 0, 0), (-self.WIDTH/200, self.HEIGHT/200, self.OFFSET_Z*10+pix_size*3), (self.WIDTH/200, self.HEIGHT/200, self.OFFSET_Z*10+pix_size*3)),
                # south
            ((0, 0, 0), (self.WIDTH/200, -self.HEIGHT/200, self.OFFSET_Z*10+pix_size*3), (-self.WIDTH/200, -self.HEIGHT/200, self.OFFSET_Z*10+pix_size*3)),

        ), dtype=np.double)

        self.PROJ = np.asarray((
            ((self.HEIGHT/self.WIDTH) * self.FOV_RAD, 0, 0, 0),
            (0, self.FOV_RAD, 0, 0), 
            (0, 0, self.MAX_Z / (self.MAX_Z - self.OFFSET_Z), 1), 
            (0, 0, (-self.MAX_Z * self.OFFSET_Z) / (self.MAX_Z - self.OFFSET_Z), 0),
        ), dtype=np.double)

        self.position: list[float] = [init_pos[0], init_pos[1], init_pos[2]] #[x, y, z]
        # rotation is measured in degrees
        self.x_rot: float = x_rot
        self.y_rot: float = y_rot 

    def translate_cam(self, trans_vec: list[float]) -> None:
        "translate position, accounting for camera rotation"
        self.position[0] += trans_vec[0]*math.cos(math.radians(self.x_rot))
        self.position[2] -= trans_vec[0]*math.sin(math.radians(self.x_rot))

        # y position
        self.position[1] -= trans_vec[1]

        # z
        self.position[0] += trans_vec[2]*math.sin(math.radians(self.x_rot))
        self.position[2] += trans_vec[2]*math.cos(math.radians(self.x_rot))

    def rotate_cam(self, x_rot: float, y_rot: float) -> None:
        self.x_rot += x_rot
        self.y_rot += y_rot

    def get_visible_triangles(self, triangles, uv_coords, textures, culled_faces) -> tuple:
        """backface culling, clipping"""
        tris, uvs, texs, culled = self.__get_clipped(
            triangles, uv_coords, textures, culled_faces, self.CLIPPING_PLANES
        )
        self.__get_backfaces(tris, culled)

        return (tris, uvs, texs, culled)

    # public interface for internal func
    def transform_about_cam(self, mesh: Mesh) -> np.ndarray:
        "Transform mesh about the cam to give illusion of movement, returns new array of tris with transformed vertexes"
        return self.__transform(
            # convert to np arrays (for numba performance)
            np.asarray(self.position           , dtype=np.double), 
            np.asarray([self.x_rot, self.y_rot], dtype=np.double),
            np.asarray(mesh.position           , dtype=np.double),
            np.asarray(mesh.mesh               , dtype=np.double),
        )

    # njit increases performance ten-fold 
    #   but doesn't work well with the 'self' argument 
    #   usually passed to class methods.
    # Therefore, use staticmethods
    @staticmethod
    @njit
    def __transform(
        cam_pos:  np.ndarray, 
        cam_rot:  np.ndarray, 
        mesh_pos: np.ndarray,
        mesh:     np.ndarray,
    ) -> np.ndarray:
        "njit compiled internal function"
        final = np.empty_like(mesh)

        final_pos = cam_pos - mesh_pos

        for tri_index, tri in enumerate(mesh):
            for pt_index, point in enumerate(tri):
                # rotate about camera

                # xz axis rotation
                xz_hyp = ((point[0]-final_pos[0])**2 + (point[2]-final_pos[2])**2)**(1/2)
                # account for negative hypotenuse values
                if (final_pos[0]-point[0]) >= 0:
                    xz_hyp *= -1
                # final rotation (radians); cam rot + relative rot(directly in front of cam is 0 degrees rel rot)
                if (xz_hyp != 0):
                    xz_rot = math.radians(cam_rot[0]) + math.asin((point[2]-final_pos[2])/xz_hyp)
                else:
                    xz_rot = 0
                # final values
                nx = math.cos(xz_rot)*xz_hyp + final_pos[0]
                nz = math.sin(xz_rot)*xz_hyp + final_pos[2]

                # yz axis rotation
                yz_hyp = ((point[1]-final_pos[1])**2 + (nz-final_pos[2])**2)**(1/2)
                if (final_pos[1]-point[1]) >= 0:
                    yz_hyp *= -1

                if (yz_hyp != 0):
                    yz_rot = math.radians(cam_rot[1]) + math.asin((nz-final_pos[2])/yz_hyp)
                else:
                    yz_rot = 0

                ny = math.cos(yz_rot)*yz_hyp + final_pos[1]
                nz = math.sin(yz_rot)*yz_hyp + nz

                # translate point according to player position (gives illusion that player is moving)
                final[tri_index][pt_index] = [
                    nx - final_pos[0],
                    ny - final_pos[1],
                    nz - final_pos[2],
                ]
                
        return np.asarray(final, dtype=np.double)
                
    @staticmethod
    @njit
    def __get_clipped(tris, uvs, texs, culled_faces, planes) -> tuple:
        """
        Clip triangles against given plane. \n
        Args:
            tris         : triangles to be clipped
            uvs          : tris corresponding uv coords
            texs         : tris corresponding textures
            culled_faces : array of bool, denoting whether corresponding face is culled
                provide tris length array filled with false if none are culled
            plane        : array representing a plane, denoted by 3 points (order matters)
        Returns: 
            tuple:
                A tuple of results, element 1 being the new array of tris, 2 new uvs, etc.
                Note that original arrays are scrambled as a side-effect (incorrect) 
        """
        # triangle clipping sometimes results in a triangle becoming a quadrilateral
        #   ex:
        #        clipping across this line results in quadrilateral
        #  * - _ |        * - _ |      * - _     
        #   *    | *  -->  *    |  -->  * 1 /|   Since the renderer only handles triangles,
        #    *   |*         *   |        * /2|   this quad must be split into two tris
        #     *_-|           *_-|         *_-*
        # one triangle will replace the original, 
        # but the other must be appended to end of array
        # these overflow tris are accumulated and eventually appended

        # https://www.quora.com/Given-a-point-and-a-plane-how-would-you-determine-which-side-of-the-plane-the-point-lies
        # https://gabrielgambetta.com/computer-graphics-from-scratch/11-clipping.html
        for plane in planes:
            # where overflow data is stored to later be appended
            tri_over = []
            uvs_over = []
            tex_over = []
            cul_over = []

            normal = np.cross(plane[1]-plane[0], plane[2]-plane[0])
            d = np.sum(normal*plane[0])

            for tri_idx, tri in enumerate(tris):
                if culled_faces[tri_idx]: continue
                
                # filter points in tri (for ones that are outside of plane)
                cul_pnts = np.argwhere(np.dot(tris[tri_idx], normal) > d)
                # four cases for each tri:
                if (len(cul_pnts) == 0): # no points out of bound (do nothing)
                    continue

                elif (len(cul_pnts) == 1): # this case leads to quadrilateral (2 tris)
                    new_pnts = []
                    new_uvs = []

                    unculled = [pnt for pnt in (0, 1, 2) if pnt not in cul_pnts]
                    p1 = tri[cul_pnts[0]][0]
                    for pnt_idx in unculled:
                        p2 = tri[pnt_idx]

                        t = (np.dot(normal, plane[0]-p2) / np.dot(normal, p1-p2))
                        new_pnts.append(p2 + t*(p1-p2))
                        new_uvs.append(uvs[tri_idx][pnt_idx] - t*(uvs[tri_idx][pnt_idx]-uvs[tri_idx][cul_pnts[0]]))

                    # modify original tri
                    tris[tri_idx][cul_pnts[0]] = new_pnts[0]
                    uvs[tri_idx][cul_pnts[0]] = new_uvs[0]

                    # preserve winding order
                    order = (0, 1)
                    if (cul_pnts[0] == 1):
                        order = order[::-1]

                    new_tri = (
                        (new_pnts[order[0]][0],new_pnts[order[0]][1],new_pnts[order[0]][2]), 
                        (tri[unculled[-1]][0], tri[unculled[-1]][1],tri[unculled[-1]][2]),
                        (new_pnts[order[1]][0],new_pnts[order[1]][1],new_pnts[order[1]][2]), 
                    )
                    new_uv = (
                        (new_uvs[order[0]][0][0],new_uvs[order[0]][0][1]), 
                        (uvs[tri_idx][unculled[-1]][0], uvs[tri_idx][unculled[-1]][1]),
                        (new_uvs[order[1]][0][0],new_uvs[order[1]][0][1]), 
                    )
                    # append new tri
                    tri_over.append(new_tri)
                    uvs_over.append(new_uv)                    
                    tex_over.append(texs[tri_idx])
                    cul_over.append(False)


                elif (len(cul_pnts) == 2): # only original needs to be replaced
                    unculled = [pnt for pnt in (0, 1, 2) if pnt not in cul_pnts][0] 
                    p1 = tri[unculled]
                    for pnt_idx in cul_pnts:
                        p2 = tri[pnt_idx][0]

                        # code adapted from https://stackoverflow.com/questions/4938332/line-plane-intersection-based-on-points
                        t = (np.dot(normal, plane[0]-p1) / np.dot(normal, p2-p1))
                        new_pnt = p1 + t*(p2 - p1)
                        tris[tri_idx][pnt_idx] = new_pnt

                        new_uv = uvs[tri_idx][unculled] - t*(uvs[tri_idx][unculled]-uvs[tri_idx][pnt_idx])
                        uvs[tri_idx][pnt_idx] = new_uv

                else: # all points out of bound (cull)
                    culled_faces[tri_idx] = True

            if (tri_over): # append if there is overflow
                tris, uvs, texs, culled_faces = (
                    np.concatenate((tris        , np.asarray(tri_over, dtype=np.double))),
                    np.concatenate((uvs         , np.asarray(uvs_over, dtype=np.double))),
                    np.concatenate((texs        , np.asarray(tex_over, dtype=np.uint16))),
                    np.concatenate((culled_faces, np.asarray(cul_over, dtype=np.bool8 ))),
                )

        return (tris, uvs, texs, culled_faces)

    # njit increases performance ten-fold 
    #   but doesn't work well with the 'self' argument 
    # Therefore, use staticmethods
    @staticmethod
    @njit
    def __get_backfaces(faces: np.ndarray, culled_buffer: np.ndarray) -> None:
        """Determine if a face is a backface. Write results into provided buffer
        Note: winding order of faces must be CCW."""
        # credits to http://www.dgp.toronto.edu/~karan/courses/csc418/fall_2002/notes/cull.html

        for index, tri in enumerate(faces):
            normal = np.cross(tri[1]-tri[0], tri[2]-tri[0])
            
            if (not culled_buffer[index]):
                culled_buffer[index] = np.sum(normal*tri[0]) < 0

    # public method
    def project_triangles(self, tris) -> None:
        self.__project(tris, self.PROJ)

    @staticmethod
    @njit
    def __project(tris, proj_mat) -> None:
        
        for tri_idx, tri in enumerate(tris):
            for pnt_idx, point in enumerate(tri):

                # output = [
                #     mat1[0]*mat2[0][0] + mat1[1]*mat2[1][0] + mat1[2]*mat2[2][0] + mat2[3][0],
                #     mat1[0]*mat2[0][1] + mat1[1]*mat2[1][1] + mat1[2]*mat2[2][1] + mat2[3][1],
                #     mat1[0]*mat2[0][2] + mat1[1]*mat2[1][2] + mat1[2]*mat2[2][2] + mat2[3][2],
                # ] #this is equivalent np.dot

                # note that dot product must be with two similarly shaped arrays, hence the addition of 1
                output = np.dot(np.asarray([*point, 1]), proj_mat) 
                w = point[0]*proj_mat[0][3] + point[1]*proj_mat[1][3] + point[2]*proj_mat[2][3] + proj_mat[3][3]

                if w:
                    output[0] /= w; output[1] /= w; output[2] /= 2

                tris[tri_idx][pnt_idx][0] = output[0]
                tris[tri_idx][pnt_idx][1] = output[1]
                tris[tri_idx][pnt_idx][2] = output[2]