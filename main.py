import pygame
from camera import Camera
from renderer import Renderer3D
from event_checker import EventChecker
from meshes import meshes
"""
TODO:
hide faces that are behind other faces
"""

WIDTH = 600
HEIGHT = 600

SPEED = .07

if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    cam = Camera(position=[0, 0, -2])
    renderer = Renderer3D(screen, cam)
    for mesh in meshes:
        renderer.add_mesh(mesh)

    eventChecker = EventChecker(
        {
            'forward'  : pygame.K_w,
            'left'     : pygame.K_a,
            'backward' : pygame.K_s,
            'right'    : pygame.K_d,
            'down'     : pygame.K_z,
            'up'       : pygame.K_x,
            'rot_right': pygame.K_m,
            'rot_left' : pygame.K_n,
            'rot_up'   : pygame.K_u,
            'rot_down' : pygame.K_j,
            'zoom_in'  : pygame.K_f,
            'zoom_out' : pygame.K_v, 
        }
    )
    run = True
    while (run):

        clock.tick(80)

        eventChecker.check_key_press()
        if eventChecker.get_state('quit'):
            run = False
            
        if eventChecker.get_state('forward'):
            cam.translate_cam((0, 0, SPEED))
        if eventChecker.get_state('backward'):
            cam.translate_cam((0, 0, -SPEED))
            
        if eventChecker.get_state('left'):
            cam.translate_cam((-SPEED, 0, 0))
        if eventChecker.get_state('right'):
            cam.translate_cam((SPEED, 0, 0))

        if eventChecker.get_state('down'):
            cam.translate_cam((0, -SPEED, 0))
        if eventChecker.get_state('up'):
            cam.translate_cam((0, SPEED, 0))

        if eventChecker.get_state('rot_left'):
            cam.rotate_cam(-3, 0)
            if (cam.x_rot <= 0):
                cam.x_rot = 360
        if eventChecker.get_state('rot_right'):
            cam.rotate_cam(3, 0)
            if (cam.x_rot >= 360):
                cam.x_rot = 0
        
        if eventChecker.get_state('rot_down'):
            if (cam.y_rot > -90):
                cam.rotate_cam(0, -3)
        if eventChecker.get_state('rot_up'):
            if (cam.y_rot < 90):
                cam.rotate_cam(0, 3)
        
        if eventChecker.get_state('zoom_in'):
            if (cam.fov < 2):
                cam.fov += .01
        if eventChecker.get_state('zoom_out'):
            if (cam.fov > 0):
                cam.fov -= .01

        screen.fill((0, 0, 0))
        renderer.render_all()
        pygame.display.update()
        
    