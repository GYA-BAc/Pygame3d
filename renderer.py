import pygame
import numpy as np
from numba import njit

from camera import Camera

# njit increases performance ten-fold 
@njit()
def draw_triangle(surfarray, z_buffer, triangle, texture, texture_uv):

    # start with perspective correct triangle
    tex_size = np.asarray([len(texture)-1, len(texture[0])-1])
    surf_width, surf_height = len(surfarray), len(surfarray[0])

    # normalize pygame coordinates (pygame has (0,0) in top left corner)
    centered_tri = np.asarray([(int(point[0]+surf_width//2), int(surf_height//2-point[1]), point[2]) for point in triangle])

    # sort triangles by y (from top of screen to bottom)
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


class Renderer3D:
    """Class which renders 3d meshes to a 2d surface, from a given viewpoint"""

    __slots__ = [
        '__WIDTH', 
        '__HEIGHT', 
        '__ASPECT_RATIO', 
        '__PROJ', 
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
        self.__PROJ = (
            (self.__ASPECT_RATIO * self.__FOV_RAD, 0, 0, 0),
            (0, self.__FOV_RAD, 0, 0), 
            (0, 0, self.__MAX_Z / (self.__MAX_Z - self.__OFFSET_Z), 1), 
            (0, 0, (-self.__MAX_Z * self.__OFFSET_Z) / (self.__MAX_Z - self.__OFFSET_Z), 0),
        )

        self.cam = cam
        self.pix_size = pix_size
        if (pix_size < 1):
            raise ValueError("pix_size cannot be smaller than native screen resolution (1)")
        
        # define instance variables that will change

        self.surface = surface
        self.z_buffer = np.full(
            (self.__WIDTH//self.pix_size, self.__HEIGHT//self.pix_size),
            self.__MAX_Z
        ).astype('d') # array of doubles

        self.meshes = []

    def add_mesh(self, mesh: list[list[list[float]]]) -> None:
        # function may not have purpose
        self.meshes.append(mesh)

    def render_all(self) -> None:
        """
        Render all meshes the renderer owns, clearing screen in the process.\n
        Note that this will directly update the surface owned by renderer
        """

        #numrendered = 0 #

        # convert screen to numpy array for easier pixel manipulation
        #    also clears screen
        #    also scale down to account for pix_size
        surface = np.full(
            (self.__WIDTH//self.pix_size, self.__HEIGHT//self.pix_size, 3), 
            fill_value=(120, 170, 210), #RGB
        ).astype('uint8')

        # clear z buffer
        self.z_buffer = np.full(
            (self.__WIDTH//self.pix_size, self.__HEIGHT//self.pix_size),
            self.__MAX_Z
        ).astype('d')

        # pure white texture
        texfill = pygame.Surface((5, 5))
        texfill.fill((255, 255, 255))
        texture = pygame.surfarray.array3d(texfill)

        # texture = pygame.surfarray.array3d(pygame.image.load('./assets/Grass_tile.png'))

        # texture uv coordinates
        texture_uv = np.asarray([[0, 0.85], [1, 0.85], [0.5, 0]])

        # intermediate rendering stage
        #   tris transformed inverse to cam position/orientation
        #   give illusion of movement
        #   also, all meshes are flattened down to list of triangles
        intermed = [
            (
            self.cam.transform_about_cam(triangle[0]),
            self.cam.transform_about_cam(triangle[1]),
            self.cam.transform_about_cam(triangle[2]),
            )
            for mes in self.meshes for triangle in mes
        ]

        """sorting triangles by distance from cam unecessary, with z buffer
           painter's algorithm not needed"""
        
        for tri in intermed:

            # backface culling culls unseen tris
            v1 = (tri[1][0]-tri[0][0], tri[1][1]-tri[0][1], tri[1][2]-tri[0][2])
            v2 = (tri[2][0]-tri[0][0], tri[2][1]-tri[0][1], tri[2][2]-tri[0][2])
            nx = (v1[1]*v2[2]) - (v1[2]*v2[1])
            ny = (v1[2]*v2[0]) - (v1[0]*v2[2])
            nz = (v1[0]*v2[1]) - (v1[1]*v2[0])
            fin = nz/((nx**2+ny**2+nz**2)**(1/2) + 1e-32)
            if fin < 0:
                continue
            # this algorithm mostly works, 
            # but culls a few visible triangles on the edge


            final_tri = (
                self.__matrix_multiply(tri[0]),
                self.__matrix_multiply(tri[1]),
                self.__matrix_multiply(tri[2]),
            )
                
            # dont render if any vertex is behind player
            for point in final_tri:
                if (point[2] < 0): 
                    break
            else: # if not break
                draw_triangle(surface, self.z_buffer, final_tri, texture, texture_uv)
                #draw_triangle(surface, final, texture, texture_uv)
            # numrendered += 1 #

        surf = pygame.surfarray.make_surface(surface) 
        # scale back to surface size
        surf = pygame.transform.scale(surf, (self.__WIDTH, self.__HEIGHT))
        self.surface.blit(surf, (0, 0)) 
        # print(numrendered) #

    def __matrix_multiply(self, matrix: list[float]) -> list[float]:
        """Used to project 3d points to 2d screen, input matrix is 3d point.
        Note that result will still be a 3 element list, 3rd element is still useful"""
        output = [
            matrix[0]*self.__PROJ[0][0]*self.cam.fov + matrix[1]*self.__PROJ[1][0] + matrix[2]*self.__PROJ[2][0] + self.__PROJ[3][0],
            matrix[0]*self.__PROJ[0][1] + matrix[1]*self.__PROJ[1][1]*self.cam.fov + matrix[2]*self.__PROJ[2][1] + self.__PROJ[3][1],
            matrix[0]*self.__PROJ[0][2] + matrix[1]*self.__PROJ[1][2] + matrix[2]*self.__PROJ[2][2] + self.__PROJ[3][2],
        ]
    
        w = matrix[0] * self.__PROJ[0][3] + matrix[1] * self.__PROJ[1][3] + matrix[2] * self.__PROJ[2][3] + self.__PROJ[3][3]
    
        if w:
            output = [output[0]/w, output[1]/w, output[2]]
    
        return output

    
