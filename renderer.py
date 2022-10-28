import pygame
import numpy as np

from camera import Camera
from utils import draw_triangle

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
    # honesly, I have no clue how this variable actually affects the renderer
    # bigger number better?
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
        ).astype('d') # double type

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
        # texfill = pygame.Surface((5, 5))
        # texfill.fill((255, 255, 255))
        # texture = pygame.surfarray.array3d(texfill)

        texture = pygame.surfarray.array3d(pygame.image.load('./assets/Grass_tile.png'))

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

                # first apply camera transformations to triangle
                # then, apply backface culling, not discarding triangles that aren't facing camera
                #    (look at vertexes)
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

    
