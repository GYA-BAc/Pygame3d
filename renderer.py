from camera import Camera
import pygame
import math
#import numpy as np


class Renderer3D:
    """Class which renders 3d meshes to a 2d surface, from a given viewpoint"""

    __slots__ = ['__WIDTH', '__HEIGHT', '__ASPECT_RATIO', '__PROJ', 'cam', 'surface', 'meshes',]

    __MAX_Z = 1000
    __OFFSET_Z = 0.1
    __FOV_RAD = 500

    __UNIT = .5
    
    def __init__(self, surface: pygame.surface.Surface, cam: Camera):
        #define constants
        self.__WIDTH, self.__HEIGHT = surface.get_size()
        self.__ASPECT_RATIO = self.__HEIGHT/self.__WIDTH

        self.__PROJ = (
            (self.__ASPECT_RATIO * self.__FOV_RAD, 0, 0, 0),
            (0, self.__FOV_RAD, 0, 0), 
            (0, 0, self.__MAX_Z / (self.__MAX_Z - self.__OFFSET_Z), 1), 
            (0, 0, (-self.__MAX_Z * self.__OFFSET_Z) / (self.__MAX_Z - self.__OFFSET_Z), 0),
        )

        self.cam = cam
        self.surface = surface
        self.meshes = []
    
    def render_all_experimental(self) -> None:
        "Experimental, render with backface cullling algorithm"
        for mesh in self.meshes:
            for triangle in mesh:

                # first apply camera transformations to triangle
                # then, apply backface culling, not discarding triangles that aren't facing camera
                #    (triangles who's angles [formed by the normal vector and the camera vector] > 90)
                # then, project 3d into 2d, and draw resulting 2d triangles 
                tri = (
                    self.cam.transform_about_cam(triangle[0]),
                    self.cam.transform_about_cam(triangle[1]),
                    self.cam.transform_about_cam(triangle[2]),
                )

                vec1 = (tri[1][0]-tri[0][0], tri[1][1]-tri[0][1], tri[1][2]-tri[0][2])
                vec2 = (tri[2][0]-tri[1][0], tri[2][1]-tri[1][1], tri[2][2]-tri[1][2])
                normal = (
                    vec1[1]*vec2[2] - vec1[2]*vec2[1],
                    vec1[2]*vec2[0] - vec2[0]*vec2[2],
                    vec1[0]*vec2[1] - vec1[1]*vec2[0],
                )
                center = (
                    (tri[0][0] + tri[1][0] + tri[2][0])/3,
                    (tri[0][1] + tri[1][1] + tri[2][1])/3,
                    (tri[0][2] + tri[1][2] + tri[2][2])/3,
                )
                point = (
                    center[0] + normal[0],
                    center[1] + normal[1],
                    center[2] + normal[2],
                )
                side1 = ((center[0])**2 + (center[1])**2 + (center[2])**2)**(1/2)
                side2 = ((normal[0])**2 + (normal[1])**2 + (normal[2])**2)**(1/2)
                side3 = ((point[0])**2 + (point[1])**2 + (point[2])**2)**(1/2)
                
                try:
                    angle = math.acos((-side3**2+side1**2+side2**2)/(2.0*side1*side2))
                    #angle = math.acos((-side3**2+side1**2+side2**2)/(2*side1*side2))

                    if (angle >= math.radians(90)):
                        continue
                except ValueError:
                    pass
                except ZeroDivisionError:
                    pass
                final = (
                    self.__matrix_multiply(tri[0]),
                    self.__matrix_multiply(tri[1]),
                    self.__matrix_multiply(tri[2]),
                )

                self.__draw_triangle(final)


    def render_all(self) -> None:
        "Render all meshes the renderer owns"

        numrendered = 0
        for mesh in self.meshes:
            for triangle in mesh:

                # first apply camera transformations to triangle
                # then, apply backface culling, not discarding triangles that aren't facing camera
                #    (look at vertexes)
              
                final = (
                    self.__matrix_multiply(self.cam.transform_about_cam(triangle[0])),
                    self.__matrix_multiply(self.cam.transform_about_cam(triangle[1])),
                    self.__matrix_multiply(self.cam.transform_about_cam(triangle[2])),
                )

                #NOTE current backface culling algorithm only works for vertical or horizontal planes, not both
                #cull all non horizontal planes that are facing away from player
                if (final[2][0]<final[0][0]) and not (triangle[0][1]==triangle[1][1]==triangle[2][1]):
                   continue
                #cull all horizontal planes facing away from player (TODO)
                if (triangle[0][1]==triangle[1][1]==triangle[2][1]):
                    if (final[2][1]<final[0][1]) and (final[1][1]>final[2][1]):
                        continue
                    
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

                self.__draw_triangle(final)
                numrendered += 1 #
        #print(numrendered)
    

    def add_mesh(self, mesh: list[list[list]]) -> None:
        #transform mesh into appropriate scale factor
        #self.meshes.append([[[coord*self.__UNIT for coord in point] for point in triangle] for triangle in mesh])
        self.meshes.append(mesh)

    def __draw_triangle(self, triangle: list) -> None: 
        #dont render if player intersecting triangle
        for point in triangle:
            if (point[2] > 1): 
                return
        pygame.draw.polygon(
            self.surface,
            (255, 255, 255),
            #points are translated so that (0, 0) is in the center of screen
            [(point[0]+self.__WIDTH//2, self.__HEIGHT//2-point[1]) for point in triangle],
            width=1
        )

    def __matrix_multiply(self, matrix: list) -> list:
        output = [
            matrix[0]*self.__PROJ[0][0]*self.cam.fov + matrix[1]*self.__PROJ[1][0] + matrix[2]*self.__PROJ[2][0] + self.__PROJ[3][0],
            matrix[0]*self.__PROJ[0][1] + matrix[1]*self.__PROJ[1][1]*self.cam.fov + matrix[2]*self.__PROJ[2][1] + self.__PROJ[3][1],
            matrix[0]*self.__PROJ[0][2] + matrix[1]*self.__PROJ[1][2] + matrix[2]*self.__PROJ[2][2] + self.__PROJ[3][2],
        ]
    
        w = matrix[0] * self.__PROJ[0][3] + matrix[1] * self.__PROJ[1][3] + matrix[2] * self.__PROJ[2][3] + self.__PROJ[3][3]
    
        if w:
            output = [i/w for i in output]
    
        return output

    