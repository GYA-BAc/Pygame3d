import math
# import numpy as np

import pygame

from camera import Camera
from utils import seg_intersect, point_in_triangle




class Renderer3D:
    """Class which renders 3d meshes to a 2d surface, from a given viewpoint"""

    __slots__ = [
        '__WIDTH', 
        '__HEIGHT', 
        '__ASPECT_RATIO', 
        '__PROJ', 
        '__SCREEN_SIDES',
        'cam', 
        'surface', 
        'meshes',
    ]

    __MAX_Z = 1000
    __OFFSET_Z = 0.1
    __FOV_RAD = 500


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
        self.__SCREEN_SIDES = (
            ((0, 0)                       , (self.__WIDTH, 0)            ), # top
            ((self.__WIDTH, 0)            , (self.__WIDTH, self.__HEIGHT)), # right 
            ((self.__WIDTH, self.__HEIGHT), (0, self.__HEIGHT)           ), # bottom
            ((0, self.__HEIGHT)           , (0, 0)                       ), # left
        )

        # define instance variables that will change
        self.cam = cam
        self.surface = surface
        self.meshes = []

    def add_mesh(self, mesh: list[list[list[float]]]) -> None:
        # function may not have purpose
        self.meshes.append(mesh)

    def render_all(self) -> None:
        "Render all meshes the renderer owns"

        # numrendered = 0 #
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
                
                # NOTE current backface culling algorithm only works for vertical or horizontal planes, not both
                # cull all non horizontal planes that are facing away from player
                if (final[2][0]<final[0][0]) and not (triangle[0][1]==triangle[1][1]==triangle[2][1]):
                   continue

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

                self.__draw_triangle(final)
                # numrendered += 1 #
        # print(numrendered) #

    def __draw_triangle(self, triangle: list[list[float]]) -> None: 
        "Note: triangles should have points in pygame notatio; (0,0) in top-left corner"
        # dont render if player is intersecting triangle (any vertex)
        for point in triangle:
            if (point[2] > 1): 
                return

        # shift all points so that (0,0) lies at the center of the screen, 
        #  also exclude 3rd dimension
        #  also turn into list of sides
        centered_tri = [(point[0]+self.__WIDTH//2, self.__HEIGHT//2-point[1]) for point in triangle]

        # if one point is off screen, cut triangle at edge of screen (to ensure offscreen pixels are not filled)
        final = self.__cull_edges(centered_tri)
        # print(final) #

        if (len(final) < 3):
            return
        pygame.draw.polygon(
            self.surface,
            (255, 255, 255),
            final,
            width=0
        )

    def __cull_edges(self, triangle: list[list[float]]) -> list[list[float]]:
        """If a triangle's sides go off screen, return new polygon's (potentially 3+ sides after transformation) 
        coordinates, which have vertices strictly within screen bounds, without affecting final image"""
       
        # algoritm is:
        # for side in triangle:
        #    if intersects a side:
        #    replace vertex with intersection
        # edge case:
        #    if a side lies completely outside of screen, check to see if corner vertex needed
            
        final = []
        # iterate through each of the triangle's lines
        for line in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])):
            
            cur = []
            if (0 < line[0][0]  < self.__WIDTH 
                and 0 < line[0][1] < self.__HEIGHT):
                cur.append(line[0])
            
            potential_corner = False
            for side in self.__SCREEN_SIDES:
                pnt = seg_intersect(side, line)
                if pnt:
                    cur.append(pnt)
                    potential_corner = True
            # ensure points are in correct order
            

            if (0 < line[1][0]  < self.__WIDTH 
                and 0 < line[1][1] < self.__HEIGHT):
                cur.append(line[1])

            # special case where point2 isn't in screen bounds, and line intersects screen side:
                # check if corner vertex needed
                #NOTE: this code cannot handle if more than 2 corners are found (order is incorrect)
            elif (potential_corner):
                corners = (
                    self.__SCREEN_SIDES[0][0], # top left
                    self.__SCREEN_SIDES[0][1], # top right
                    self.__SCREEN_SIDES[2][0], # bottom right
                    self.__SCREEN_SIDES[2][1], # bottom left
                )
                for corner in corners:
                    if (point_in_triangle(corner, triangle)):
                        cur.append(corner)
                

            final += cur
            
        # print([[f"{i:.2f}" for i in j] for j in final]) #
        
        return final

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

    