import pygame
#scipy is now a needed dependancy. (numba needs it)
from scipy import __version__

from camera import Camera
from renderer import Renderer3D
from event_checker import EventChecker
from meshes import meshes
"""
TODO:

efficiency
    <NEW> backface culling
texturing
    REFACTOR
triangle class?
    With uv coords
    <MEH> .obj file support?
        <   > Trianglify obj files (all faces must have 3 vertexes)
lighting
    ray tracing?
    fragment shading?

"""

WIDTH = 600
HEIGHT = 600

FPS = 80

# per second
SPEED = 2.5 
ROT_SPEED = 90 # (in degrees)

FONT = pygame.font.Font(pygame.font.get_default_font(), 15)

def main(use_mouse = False, debug = False):
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    if (use_mouse):
        pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()
    cam = Camera(position=(0, 0, -4))

    renderer = Renderer3D(screen, cam, pix_size=3)
    for mesh in meshes:
        renderer.add_mesh(mesh)

    event_checker = EventChecker(
        {
            'quit'     : {pygame.K_ESCAPE},
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

    # a transparent rectangle to put text on
    stat_area = pygame.Surface((150, 70)) 
    stat_area.set_alpha(128)               
    stat_area.fill((0, 0, 0))
    
    run = True
    while (run):
        
        delta_time = clock.tick(FPS)/1000

        event_checker.check_key_press()
        if event_checker.get_state('quit'):
            run = False
        
        if event_checker.get_state('forward'):
            cam.translate_cam((0, 0, SPEED*delta_time))
        if event_checker.get_state('backward'):
            cam.translate_cam((0, 0, -SPEED*delta_time))
            
        if event_checker.get_state('left'):
            cam.translate_cam((-SPEED*delta_time, 0, 0))
        if event_checker.get_state('right'):
            cam.translate_cam((SPEED*delta_time, 0, 0))

        if event_checker.get_state('down'):
            cam.translate_cam((0, -SPEED*delta_time, 0))
        if event_checker.get_state('up'):
            cam.translate_cam((0, SPEED*delta_time, 0))
        
        # mouse cam movement
        if (use_mouse and pygame.mouse.get_focused()):
            pygame.mouse.set_pos((WIDTH//2, HEIGHT//2))
            mouse_trav = pygame.mouse.get_pos()
            mouse_trav = (mouse_trav[0]-WIDTH//2, HEIGHT//2-mouse_trav[1])
            cam.rotate_cam(mouse_trav[0]//20, 0)
            cam.rotate_cam(0, mouse_trav[1]//20)

        if event_checker.get_state('rot_left'):
            cam.rotate_cam(-ROT_SPEED*delta_time, 0)
        if event_checker.get_state('rot_right'):
            cam.rotate_cam(ROT_SPEED*delta_time, 0)
        
        if event_checker.get_state('rot_down'):
            cam.rotate_cam(0, -ROT_SPEED*delta_time)
        if event_checker.get_state('rot_up'):
            cam.rotate_cam(0, ROT_SPEED*delta_time)
        
        if event_checker.get_state('zoom_in'):
            cam.fov += .01
        if event_checker.get_state('zoom_out'):
            cam.fov -= .01

        # cam limits
        if (cam.x_rot < 0):
            cam.x_rot = 360
        if (cam.x_rot > 360):
            cam.x_rot = 0
        if (cam.y_rot < -90):
            cam.y_rot = -90
        if (cam.y_rot > 90):
            cam.y_rot = 90
        if (cam.fov > 1.5):
            cam.fov = 1.5
        if (cam.fov < 0.5):
            cam.fov = 0.5

        renderer.render_all()

        if (debug):
            # display transparent rect as bg of stats        
            screen.blit(stat_area, (5,5))
            # display FPS
            screen.blit(FONT.render(f"{clock.get_fps():.1f} FPS", True, (255, 255, 255), None), (10, 10))
            # display pos and rot
            screen.blit(FONT.render(
                f"{cam.position[0]:.1f}, {cam.position[1]:.1f}, {cam.position[2]:.1f} POS", 
                True, (255, 255, 255), None), (10, 30)
            )
            screen.blit(FONT.render(
                f"X: {int(cam.x_rot)}, Y: {int(cam.y_rot)} DEG", 
                True, (255, 255, 255), None), (10, 50)
            )

        pygame.display.update()

    
if __name__ == "__main__":
    main(
        use_mouse=False,
        debug=True
    )

    # after main function stops running, 
    #   ensure pygame quits correctly
    pygame.quit()
