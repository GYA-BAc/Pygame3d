import pygame
# scipy needed as a dependancy for numba
from scipy import __version__

from camera import Camera
from renderer import Renderer3D
from event_checker import EventChecker
from meshes import Mesh, load_obj_file, global_texture_atlas
"""
TODO:
BUG:
    <   > getting too close to meshes distorts textures
BUG:
    <   > projection function is wrong (incorrect points when 1+ points out of cam)
        this is due to a lack of a clipping plane, points cannot be projected that are behind camera
        <   > implementing this would require the renderer to handle quadrilaterals
            <   > quads = 2 tris

efficiency
    <MEH> migrate to using np arrays instead of lists
        <   > reduce unnecessary transformations (from list to array, vice versa)
    <2  > more njit funcs?
    <   > entire rendering func njit?
    <NEW> NOTE current bottleneck is in matrix multiply function
       <   > Refactor, currently, some functions return a new array, while some modify the input
texturing
    REFACTOR
    <   > global texture atlas could be a list (so texture keys can just be ints)
mesh class?
    <MEH> implement
    <   > add support for transformations? (like rotations)

    With uv coords
        <MEH> BUG uv coords (not sure yet)
    
    <MEH> .obj file support?
        <   > Trianglify obj files (all faces must have 3 vertexes)
        <MEH> counterclockwise-ify all 
        <MEH> Texture Uvs
        <   > REFACTOR, use new pathlib module?
           <   > refactor loading code (rn it reads through the file 3 times)

lighting
    ray tracing?
    fragment shading?

"""

WIDTH = 600
HEIGHT = 600

FPS = 80

# camera settings
SPEED = 4 #per second
ROT_SPEED = 90 # (in degrees)

FONT = pygame.font.Font(pygame.font.get_default_font(), 15)

def main(use_mouse = False, debug = False):
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    if (use_mouse):
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

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
        }
    )
    clock = pygame.time.Clock()
    cam = Camera(position=(0, 0, -4))

    renderer = Renderer3D(screen, cam, pix_size=3)
    
    # for i in range(15):
    #     for j in range(15):
    #         renderer.add_mesh(
    #             Mesh(*load_obj_file(global_texture_atlas, "./assets/cube/cube_ccw.obj")[:-1], position=(i, 0 if j % 2 else 1, j)) # exclude last argument (textures)
    #         )

    renderer.add_mesh(Mesh(*load_obj_file(global_texture_atlas, "./assets/cube/cube_ccw.obj", scale=15)[:-1], position=(-5, -15, 0)))

    # renderer.add_mesh(
    #     Mesh(
    #         *load_obj_file(global_texture_atlas, "./assets/teapot/teapot.obj", scale=3),
    #         position = [2, 3, 1.5]
    #     )
    # )

    # renderer.add_mesh(
    #     Mesh(*load_obj_file(global_texture_atlas, "./assets/tri/tri.obj"))
    # )

    # renderer.add_mesh(
    #     Mesh(*load_obj_file(global_texture_atlas, "./assets/plane/plane.obj", scale=10))
    # )

    # a transparent rectangle to put text on
    stat_area = pygame.Surface((150, 70)) 
    stat_area.set_alpha(128)               
    stat_area.fill((0, 0, 0))

    # on startup, display loading screen (before numba compiles functions)
    screen.blit(
        FONT.render(
            "Loading... (this may take several seconds)", 
            True, (255, 255, 255), None
        ),
        (10, 10)
    )
    pygame.display.update()


    run = True
    while (run):
        #mesh.position[0] += .005
        
        # how much time has passed since last frame
        delta_time = clock.tick(FPS)/1000

        event_checker.check_key_press()
        if event_checker.get_state('quit'):
            run = False
        
        if event_checker.get_state('forward'):
            # multiply speed by time elapsed to account for 
            #   uneven framerate (same speed, regardless of FPS)
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
        if (use_mouse):
            if (pygame.mouse.get_focused()):
                mouse_trav = pygame.mouse.get_rel()
                cam.rotate_cam(mouse_trav[0]//10, 0)
                cam.rotate_cam(0, -mouse_trav[1]//10)
            
        if event_checker.get_state('rot_left'):
            cam.rotate_cam(-ROT_SPEED*delta_time, 0)
        if event_checker.get_state('rot_right'):
            cam.rotate_cam(ROT_SPEED*delta_time, 0)
        
        if event_checker.get_state('rot_down'):
            cam.rotate_cam(0, -ROT_SPEED*delta_time)
        if event_checker.get_state('rot_up'):
            cam.rotate_cam(0, ROT_SPEED*delta_time)
        
        # cam limits
        if (cam.x_rot < 0):
            cam.x_rot = 360
        if (cam.x_rot > 360):
            cam.x_rot = 0
        if (cam.y_rot < -90):
            cam.y_rot = -90
        if (cam.y_rot > 90):
            cam.y_rot = 90

        renderer.render_all()

        if (debug):
            # display transparent rect as bg of stats        
            screen.blit(stat_area, (5,5))
            # display FPS
            screen.blit(FONT.render(f"FPS {clock.get_fps():.1f}", True, (255, 255, 255), None), (10, 10))
            # display pos and rot
            screen.blit(FONT.render(
                f"POS {cam.position[0]:.1f}, {cam.position[1]:.1f}, {cam.position[2]:.1f}", 
                True, (255, 255, 255), None), (10, 30)
            )
            screen.blit(FONT.render(
                f"X: {int(cam.x_rot)}, Y: {int(cam.y_rot)} DEG", 
                True, (255, 255, 255), None), (10, 50)
            )

        pygame.display.update()

    
if __name__ == "__main__":
    try:
        main(
            use_mouse = False,
            debug     = True
        )
    except Exception as e:
        print(e)
    finally:
        # after main function stops running, (whether by normal exit or error)
        #   ensure pygame quits correctly
        pygame.quit()