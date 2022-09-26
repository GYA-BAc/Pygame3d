import math

class Camera:
    """Represents a viewport into the world"""
    
    __slots__ = ['position', 'x_rot', 'y_rot', 'fov']

    def __init__(self, position: list = [0, 0, 0], x_rot: int = 0, y_rot: int = 0):
        self.position = position #a list of [x, y, z]
        #rotation is measured in degrees
        self.x_rot = x_rot
        self.y_rot = y_rot 

        self.fov = 1.0 #value will be multiplied with actual fov_radius to get final

    def transform_about_cam(self, point: list) -> list:

        #rotate about camera

        #xz axis rotation
        xz_hyp = ((point[0]-self.position[0])**2 + (point[2]-self.position[2])**2)**(1/2)
        #account for negative hypotenuse values
        if (self.position[0]-point[0]) >= 0:
            xz_hyp *= -1
        #final rotation (radians); cam rot + relative rot(directly in front of cam is 0 degrees rel rot)
        xz_rot = math.radians(self.x_rot) + math.asin((point[2]-self.position[2])/xz_hyp)
        #final values
        nx = math.cos(xz_rot)*xz_hyp + self.position[0]
        nz = math.sin(xz_rot)*xz_hyp + self.position[2]
        
        #yz axis rotation
        yz_hyp = ((point[1]-self.position[1])**2 + (nz-self.position[2])**2)**(1/2)
        if (self.position[1]-point[1]) >= 0:
            yz_hyp *= -1

        yz_rot = math.radians(self.y_rot) + math.asin((nz-self.position[2])/yz_hyp)

        ny = math.cos(yz_rot)*yz_hyp + self.position[1]
        nz = math.sin(yz_rot)*yz_hyp + nz
        
        # translate point according to player position (gives illusion that player is moving)
        return [
            nx - self.position[0],
            ny - self.position[1],
            nz - self.position[2],
        ]


    def translate_cam(self, trans_vec: list) -> None:
        "translate position, accounting for camera rotation"
        self.position[0] += trans_vec[0]*math.cos(math.radians(self.x_rot))
        self.position[2] -= trans_vec[0]*math.sin(math.radians(self.x_rot))

        #y position
        self.position[1] -= trans_vec[1]

        #z
        self.position[0] += trans_vec[2]*math.sin(math.radians(self.x_rot))
        self.position[2] += trans_vec[2]*math.cos(math.radians(self.x_rot))

    def rotate_cam(self, x_rot: int, y_rot: int) -> None:
        self.x_rot += x_rot
        self.y_rot += y_rot

