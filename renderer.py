import pygame
import numpy as np
from numba import njit

from camera import Camera
from meshes import Mesh, global_texture_atlas


class Renderer3D:
    """Class which renders 3d meshes to a 2d surface, from a given viewpoint"""

    __slots__ = [
        '__WIDTH', 
        '__HEIGHT', 
        '__ASPECT_RATIO', 
        '__PROJ', 
        '__CLIPPING_PLANES',
        'cam', 
        'pix_size',
        'surface', 
        'z_buffer',
        'meshes',
    ]

    __MAX_Z = 1000
    __OFFSET_Z = .1
    __FOV_RAD = 360

    def __init__(self, surface: pygame.surface.Surface, cam: Camera, pix_size: int = 1):

        # define constants
        self.__WIDTH, self.__HEIGHT = surface.get_size()
        self.__ASPECT_RATIO = self.__HEIGHT/self.__WIDTH
        self.__PROJ = np.asarray((
            (self.__ASPECT_RATIO * self.__FOV_RAD, 0, 0, 0),
            (0, self.__FOV_RAD, 0, 0), 
            (0, 0, self.__MAX_Z / (self.__MAX_Z - self.__OFFSET_Z), 1), 
            (0, 0, (-self.__MAX_Z * self.__OFFSET_Z) / (self.__MAX_Z - self.__OFFSET_Z), 0),
        ), dtype=np.double)
        # a plane is just 3 points
        self.__CLIPPING_PLANES = np.asarray((
            ((0, 0, self.__OFFSET_Z), (1, 1, self.__OFFSET_Z), (1, 0 ,self.__OFFSET_Z))
        ), dtype=np.double)

        self.cam: Camera = cam
        self.pix_size: int = int(pix_size)
        if (pix_size < 1):
            raise ValueError("pix_size cannot be smaller than native screen resolution (1)")
        
        # define instance variables that will change

        self.surface: pygame.surface.Surface = surface
        self.z_buffer: np.ndarray = np.full(
            (self.__WIDTH//self.pix_size, self.__HEIGHT//self.pix_size),
            self.__MAX_Z
        ).astype('d') # array of doubles

        self.meshes: list[Mesh] = []

    def add_mesh(self, mesh: Mesh) -> None:
        # function may not have purpose
        self.meshes.append(mesh)

    def render_all(self) -> None:
        """
        Render all meshes the renderer owns, clearing screen in the process.\n
        Note that this will directly update the surface owned by renderer
        """

        # convert screen to numpy array for easier pixel manipulation
        #    also clears screen
        #    also scale down to account for pix_size
        surface = np.full(
            (self.__WIDTH//self.pix_size, self.__HEIGHT//self.pix_size, 3), 
            fill_value=(120, 170, 210), # Background RGB
            dtype=np.uint8
        )
        
        # clear z buffer
        self.z_buffer = np.full(
            (self.__WIDTH//self.pix_size, self.__HEIGHT//self.pix_size),
            self.__MAX_Z,
            dtype=np.double
        )

        # flatten all meshes into array of tris
        triangles = [tri for mesh in self.meshes for tri in self.cam.transform_about_cam(mesh)]

        # triangle clipping sometimes results in a triangle becoming a quadrilateral
        #   ex:
        #       | clipping across this line results in quadrilateral
        #  * - _|             * - _     
        #   *   | *   ---->    *    |   Since the renderer only handles triangles,
        #    *  |*              *   |   this quad must be split into two tris
        #     * |                *__*

        #   final:
        #       * - _  
        #        * 1 /|
        #         * /2|
        #          *__*

        # This means that worst case scenario, all triangles become quads.
        # BUG NOTE FOR EACH PLANE THAT NEEDS TO BE CLIPPED AGAINST, SIZE GROWS EXPONENTIALLY
        #      perhaps solve with clipping loop

        buf_size = len(triangles) # offset by -1 when indexing (but not slicing)
        
        tri_buffer = np.empty((buf_size*2, 3, 3), dtype=np.double)
        tri_buffer[:buf_size] = triangles

        # same process with corresponding uv coords and texture keys
        uv_buffer = np.empty((buf_size*2, 3, 2), dtype=np.double)
        uv_buffer[:buf_size] = [coord for mesh in self.meshes for coord in mesh.uv_mesh]

        tex_buffer = np.empty((buf_size*2), dtype=np.object0)
        tex_buffer[:buf_size] = [key for mesh in self.meshes for key in mesh.textures]

        # array of bools, indicating whether the corresponding face should be culled
        culled_faces = np.full((buf_size*2), False, np.bool8)

        self.__clip_triangles(tri_buffer, uv_buffer, buf_size, culled_faces, self.__CLIPPING_PLANES)

        self.__get_backfaces(tri_buffer[:buf_size], culled_faces)
        self.__project_triangles(tri_buffer[:buf_size], self.__PROJ)

        #numrendered = 0 #
        for index, tri in enumerate(tri_buffer[:buf_size]):
            if culled_faces[index]: continue

            # if all points behind player
            if (tri[0][2] < 0 or tri[1][2] < 0 or tri[2][2] < 0):
                continue
            # if all points out of bounds
            #if (
            #    tri[0]
            #):
            #    continue

            self.__draw_triangle(
                surface,
                self.z_buffer,
                tri,
                global_texture_atlas.get(
                    tex_buffer[index], 
                    global_texture_atlas[''] # default texture if texture key not found
                ),
                uv_buffer[index]
            )
            
            #pygame.draw.polygon(self.surface, (0, 0, 0), [(int(point[0]+self.__WIDTH//2), int(self.__HEIGHT//2-point[1])) for point in tri], width=1)
        #pygame.draw.circle(self.surface, (255, 0 ,0), [triangles[1][0][0]+self.__WIDTH//2, self.__HEIGHT//2-triangles[1][0][1]], 10)
            # numrendered += 1 #

        surf = pygame.surfarray.make_surface(surface)
        # scale back to surface size
        surf = pygame.transform.scale(surf, (self.__WIDTH, self.__HEIGHT))
        self.surface.blit(surf, (0, 0)) 
        # print(numrendered) #

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
            v1 = (tri[1][0]-tri[0][0], tri[1][1]-tri[0][1], tri[1][2]-tri[0][2])
            v2 = (tri[2][0]-tri[0][0], tri[2][1]-tri[0][1], tri[2][2]-tri[0][2])
            normal = np.cross(v1, v2)
            
            culled_buffer[index] = (
                ( normal[0]*(tri[0][0]) 
                + normal[1]*(tri[0][1]) 
                + normal[2]*(tri[0][2])) < 0
            )

    @staticmethod
    @njit
    def __clip_triangles(tris, uvs, buf_size, culled_faces, planes) -> int:
        return 0
        
                
    @staticmethod
    @njit
    def __project_triangles(tris, proj_mat) -> None:
        
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
                    output[0] /= w; output[1] /= w

                tris[tri_idx][pnt_idx][0] = output[0]
                tris[tri_idx][pnt_idx][1] = output[1]
                tris[tri_idx][pnt_idx][2] = output[2]

    @staticmethod
    @njit()
    # A LOT of inspirations from https://github.com/FinFetChannel/SimplePython3DEngine 
    def __draw_triangle(surfarray, z_buffer, triangle, texture, texture_uv):
        "njit compiled internal function"
        # start with perspective correct triangle
        tex_size = np.asarray([len(texture)-1, len(texture[0])-1])
        surf_width, surf_height = len(surfarray), len(surfarray[0])
    
        # normalize pygame coordinates (pygame has (0,0) in top left corner)
        centered_tri = np.asarray([(int(point[0]+surf_width//2), int(surf_height//2-point[1]), point[2]) for point in triangle])
    
        # sort points of triangle by y value (top to botton)
        #   note this returns sorted INDEXES to be used later
        sorted_y = centered_tri[:,1].argsort()
    
        x_start, y_start, z_start = centered_tri[sorted_y[0]]
        x_middle, y_middle, z_middle = centered_tri[sorted_y[1]]
        x_stop, y_stop, z_stop = centered_tri[sorted_y[2]] 
    
        x_slope_1 = (x_stop - x_start)/(y_stop - y_start + 1e-32)
        x_slope_2 = (x_middle - x_start)/(y_middle - y_start + 1e-32)
        x_slope_3 = (x_stop - x_middle)/(y_stop - y_middle + 1e-32)  
        
    
        # invert z for interpolation
        z_start, z_middle, z_stop = 1/(z_start +1e-32), 1/(z_middle + 1e-32), 1/(z_stop +1e-32)
    
        z_slope_1 = (z_stop - z_start)/(y_stop - y_start + 1e-32) 
        z_slope_2 = (z_middle - z_start)/(y_middle - y_start + 1e-32) 
        z_slope_3 = (z_stop - z_middle)/(y_stop - y_middle + 1e-32)  
    
        # uv coordinates multiplied by inverted z to account for perspective
        uv_start = texture_uv[sorted_y[0]]*z_start 
        uv_middle = texture_uv[sorted_y[1]]*z_middle
        uv_stop = texture_uv[sorted_y[2]]*z_stop
    
        uv_slope_1 = (uv_stop - uv_start)/(y_stop - y_start + 1e-32)  
        uv_slope_2 = (uv_middle - uv_start)/(y_middle - y_start + 1e-32)  
        uv_slope_3 = (uv_stop - uv_middle)/(y_stop - y_middle + 1e-32) 

        # min and max used to cut off rows not in screen
        for y in range(max(0, int(y_start)), min(surf_height, int(y_stop))):
            # to get start and end of each row, traverse the lines 
            # of the triangle that make up the row (on either side)
            # simply use slope to find x limits given y
    
            delta_y = y - y_start
            x1 = x_start + int(delta_y*x_slope_1)
            z1 = z_start + delta_y*z_slope_1
            uv1 = uv_start + delta_y*uv_slope_1
    
            # y middle is the where the lines that the row is between changes
            #   ex: above y_middle, the row is between line 1 and line 2, but below it,
            #       the line is between line 3 and line 2
            #                O
            #       line 1  * *
            #              *   *  line 2
            #             O—————*—————————————
            #               **   *    below this line (y-middle), the rows (x vals) of pixels in the triangle
            #          line 3  ** *    are between line 3 and line 2, as opposed to line 1 and 2
            #                     *O 
            if y < y_middle:
                x2 = x_start + int(delta_y*x_slope_2)
                z2 = z_start + delta_y*z_slope_2
                uv2 = uv_start + delta_y*uv_slope_2
    
            else:
                delta_y = y - y_middle
                x2 = x_middle + int(delta_y*x_slope_3)
                z2 = z_middle + delta_y*z_slope_3
                uv2 = uv_middle + delta_y*uv_slope_3
                
            # x1 should be smaller
            if x1 > x2:
                x1, x2 = x2, x1
                z1, z2 = z2, z1
                uv1, uv2 = uv2, uv1
    
            uv_slope = (uv2 - uv1)/(x2 - x1 + 1e-32) # 1e-32 to avoid zero division ¯\_(ツ)_/¯
            z_slope = (z2 - z1)/(x2 - x1 + 1e-32)
    
            # min and max used to cut off pixels not in screen
            for x in range(max(0, int(x1)), min(surf_width, int(x2))):
                z = 1/(z1 + (x - x1)*z_slope + 1e-32) # retrive z
    
                # if pixel trying to be rendered falls behind 
                #   player in 3d space, don't render
                if (z < 1): 
                    continue
                
                # if pixel's z distance from cam is closer than previous 
                #   value in z_buf, update z_buf and draw pixel.
                # Otherwise, the pixel is behind another pixel (don't render)
                if (z > z_buffer[x, y]):
                    continue
                z_buffer[x, y] = z
    
                # multiply by z to go back to uv space
                uv = (uv1 + (x - x1)*uv_slope)*z
                # for now, shading is determined by distance from cam (farther=darker)
                shade = max(0, 1 - z/(20))
                # don't render texture if uv out of bounds
                if min(uv) >= 0 and max(uv) <= 1: 
                    surfarray[x, y] = texture[int(uv[0]*tex_size[0])][int(uv[1]*tex_size[1])]*shade
    
        
    