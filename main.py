import pygame

from camera import Camera
from renderer import Renderer3D
from event_checker import EventChecker
from meshes import meshes
"""
TODO:
edge culling (DONE NOTE: bug where point order is incorrect for if more than 3 corners)
hide faces that are behind other faces
texturing
triangle class?

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
    event_checker = EventChecker(
        {
            'forward'  : {pygame.K_w, pygame.K_UP   },
            'left'     : {pygame.K_a, pygame.K_LEFT },
            'backward' : {pygame.K_s, pygame.K_DOWN },
            'right'    : {pygame.K_d, pygame.K_RIGHT},
            'down'     : {pygame.K_z},
            'up'       : {pygame.K_x},
            'rot_right': {pygame.K_m},
            'rot_left' : {pygame.K_n},
            'rot_up'   : {pygame.K_u},
            'rot_down' : {pygame.K_j},
            'zoom_in'  : {pygame.K_f},
            'zoom_out' : {pygame.K_v},
        }
    )
    
    run = True
    while (run):

        clock.tick(80)

        event_checker.check_key_press()
        if event_checker.get_state('quit'):
            run = False
            
        if event_checker.get_state('forward'):
            cam.translate_cam((0, 0, SPEED))
        if event_checker.get_state('backward'):
            cam.translate_cam((0, 0, -SPEED))
            
        if event_checker.get_state('left'):
            cam.translate_cam((-SPEED, 0, 0))
        if event_checker.get_state('right'):
            cam.translate_cam((SPEED, 0, 0))

        if event_checker.get_state('down'):
            cam.translate_cam((0, -SPEED, 0))
        if event_checker.get_state('up'):
            cam.translate_cam((0, SPEED, 0))

        if event_checker.get_state('rot_left'):
            cam.rotate_cam(-3, 0)
            if (cam.x_rot <= 0):
                cam.x_rot = 360
        if event_checker.get_state('rot_right'):
            cam.rotate_cam(3, 0)
            if (cam.x_rot >= 360):
                cam.x_rot = 0
        
        if event_checker.get_state('rot_down'):
            if (cam.y_rot > -90):
                cam.rotate_cam(0, -3)
        if event_checker.get_state('rot_up'):
            if (cam.y_rot < 90):
                cam.rotate_cam(0, 3)
        
        if event_checker.get_state('zoom_in'):
            if (cam.fov < 1.5):
                cam.fov += .01
        if event_checker.get_state('zoom_out'):
            if (cam.fov > .5):
                cam.fov -= .01
                

        screen.fill((0, 0, 0))
        renderer.render_all()
        pygame.display.update()
        
    