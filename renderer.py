import pygame
import numpy as np
from numba import njit

from camera import Camera


# njit increases performance ten-fold 
@njit
def draw_triangle(
    surface: np.ndarray, triangle: list, texture: np.ndarray, texture_uv: np.ndarray
) -> None: 
    "Note: triangles should have points in pygame notation; (0,0) in top-left corner"

    texture_size = np.asarray([len(texture)-1, len(texture[0])-1])
    surf_width, surf_height  = len(surface[0]), len(surface)

    centered_tri = np.asarray([(int(point[0]+surf_width//2), int(surf_height//2-point[1])) for point in triangle])

    # get list of indexes of triangle points, sorted by y value (ascending)
    tri_order = centered_tri[:,1].argsort()

    x_start, y_start = centered_tri[tri_order[0]]
    x_middle, y_middle = centered_tri[tri_order[1]]
    x_stop, y_stop = centered_tri[tri_order[2]]
    
    # get slopes of each line in tri
    # add tiny number to denominator to prevent divide by zero
    x_slope_1 = (x_stop - x_start)  /(y_stop - y_start + 1e-16)
    x_slope_2 = (x_middle - x_start)/(y_middle - y_start + 1e-16)
    x_slope_3 = (x_stop - x_middle) /(y_stop - y_middle + 1e-16)

    uv_start  = texture_uv[tri_order[0]]
    uv_middle = texture_uv[tri_order[1]]
    uv_stop   = texture_uv[tri_order[2]]

    uv_slope_1 = (uv_stop - uv_start)  /(y_stop - y_start + 1e-16)
    uv_slope_2 = (uv_middle - uv_start)/(y_middle - y_start + 1e-16)
    uv_slope_3 = (uv_stop - uv_middle) /(y_stop - y_middle + 1e-16)
    

    # iterate through every row of pixels in the triangle
    #    ensure that only columns in screen are looped over (min and max is 0 and screen height)
    for y in range(max(0, y_start), min(y_stop, surf_height)):
        
        # get point on left-edge of triangle (and texture)
        x1 = x_start + int((y-y_start)*x_slope_1)
        uv1 = uv_start + (y-y_start)*uv_slope_1

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

        if (y < y_middle):
            x2 = x_start + int((y-y_start)*x_slope_2)
            uv2 = uv_start + (y-y_start)*uv_slope_2
        else:
            x2 = x_middle + int((y-y_middle)*x_slope_3)
            uv2 = uv_middle + (y-y_middle)*uv_slope_3
                
        # flip points if they are backwards (x1 should be the smaller one)
        if (x1 > x2):
            x1, x2 = x2, x1
            uv1, uv2 = uv2, uv1
            
        uv_slope = (uv2 - uv1)/(x2 - x1 + 1e-16)
            
        for x in range(max(0, x1), min(x2, surf_width)):
            uv = uv1 + (x - x1)*uv_slope

            surface[x, y] = texture[int(uv[0]*texture_size[0])][int(uv[1]*texture_size[1])]

class Renderer3D:
    """Class which renders 3d meshes to a 2d surface, from a given viewpoint"""

    __slots__ = [
        '__WIDTH', 
        '__HEIGHT', 
        '__ASPECT_RATIO', 
        '__PROJ', 
        'cam', 
        'surface', 
        'meshes',
    ]

    __MAX_Z = 1000
    __OFFSET_Z = 0.1
    __FOV_RAD = 360


    def __init__(self, surface: pygame.surface.Surface, cam: Camera):

        # define constants
        self.__WIDTH, self.__HEIGHT = surface.get_size()
        self.__ASPECT_RATIO = self.__HEIGHT/self.__WIDTH
        self.__PROJ = (
            (self.__ASPECT_RATIO * self.__FOV_RAD, 0, 0, 0),
            (0, self.__FOV_RAD, 0, 0), 
            (0, 0, self.__MAX_Z / (self.__MAX_Z - self.__OFFSET_Z), 1), 
            (0, 0, (-self.__MAX_Z * self.__OFFSET_Z) / (self.__MAX_Z - self.__OFFSET_Z), 0),
        )

        # define instance variables that will change
        self.cam = cam
        self.surface = surface
        self.meshes = []

    def add_mesh(self, mesh: list[list[list[float]]]) -> None:
        # function may not have purpose
        self.meshes.append(mesh)

    def render_all(self) -> None:
        "Render all meshes the renderer owns, clearing screen in the process"

        # numrendered = 0 #

        # convert screen to numpy array for easier pixel manipulation
        #    also clears screen
        #surface = np.zeros((self.__WIDTH, self.__HEIGHT, 3)).astype('uint8')
        surface = np.full((self.__WIDTH, self.__HEIGHT, 3), fill_value=(120, 170, 210)).astype('uint8')


        # for now, texture beign rendered is just white
        texfill = pygame.Surface((5, 5))
        texfill.fill((255, 255, 255))
        texture = pygame.surfarray.array3d(texfill)

        texture = pygame.surfarray.array3d(pygame.image.load('Grass_tile.png'))

        # texture uv coordinates
        texture_uv = np.asarray([[0, 0], [0, 1], [1, 1]])

        # apply painter's algorithm
        ordered = [(
            self.cam.transform_about_cam(triangle[0]),
            self.cam.transform_about_cam(triangle[1]),
            self.cam.transform_about_cam(triangle[2]),
        )
            for mes in self.meshes for triangle in mes]

        ordered = sorted(ordered, 
            key=lambda tri: (
                    ((tri[0][0]+tri[1][0]+tri[2][0])/3)**2+
                    ((tri[0][1]+tri[1][1]+tri[2][1])/3)**2+
                    ((tri[0][2]+tri[1][2]+tri[2][2])/3)**2)**(1/2), 
            reverse=True)
        
        for tri in ordered:
            #for triangle in mesh:

                # first apply camera transformations to triangle
                # then, apply backface culling, not discarding triangles that aren't facing camera
                #    (look at vertexes)
              
                final = (
                    self.__matrix_multiply(tri[0]),
                    self.__matrix_multiply(tri[1]),
                    self.__matrix_multiply(tri[2]),
                )
                
                # NOTE current backface culling algorithm only works for vertical or horizontal planes, not both
                # cull all non horizontal planes that are facing away from player
                # if (final[2][0]<final[0][0]):# and not (triangle[0][1]==triangle[1][1]==triangle[2][1]):
                #    continue

                """
                #cull all horizontal planes facing away from player (TODO; NOTE: below code doesn't work)
                # if (triangle[0][1]==triangle[1][1]==triangle[2][1]):
                #     if (final[2][1]<final[0][1]) and (final[1][1]>final[2][1]):
                #         continue
                    
                #    a = (final[2][0]<final[1][0])
                #    if ((final[1][0]>final[2][0])) and (0<=360-self.cam.x_rot<90):
                #       continue
                #    #if (a if self.cam.position[1]-triangle[0][1]>0 else (not a)) and (90<=360-self.cam.x_rot<=180):
                #    #   continue
                #    if (final[2][0]<final[0][0]) and  (90<=360-self.cam.x_rot<=180): continue
                #    if (final[1][1]<final[2][1]) and (180<=360-self.cam.x_rot<=270):
                #       continue
                #    #if ((not a) if self.cam.position[1]-triangle[0][1]>0 else (a)) and (270<=360-self.cam.x_rot<=360):
                #    #   continue
                """
                # dont render if player is intersecting triangle (any vertex)
                tri_behind = False
                for point in final:
                    if (point[2] > 1): 
                        tri_behind = True
                        break
                
                if (not tri_behind):
                    draw_triangle(surface, final, texture, texture_uv)
                # numrendered += 1 #

        surf = pygame.surfarray.make_surface(surface) 
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
            output = [i/w for i in output]
    
        return output

    