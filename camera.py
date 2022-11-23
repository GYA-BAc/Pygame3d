import numpy as np
from numba import njit
import math

from meshes import Mesh

class Camera:
    """Represents a viewport into the world"""
    
    __slots__ = ['position', 'x_rot', 'y_rot']

    def __init__(self, position: list[float] = (0, 0, 0), x_rot: float = 0.0, y_rot: float = 0.0):
        self.position: list[float] = [position[0], position[1], position[2]] #[x, y, z]
        # rotation is measured in degrees
        self.x_rot: float = x_rot
        self.y_rot: float = y_rot 

    # public interface for internal func
    def transform_about_cam(self, mesh: Mesh) -> list:
        "Transform mesh about the cam to give illusion of movement, returns new array"
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

