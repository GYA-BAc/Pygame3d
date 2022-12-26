import pygame
# scipy needed as a dependancy for numba
from scipy import __version__

from camera import Camera
from renderer import Renderer3D
from event_checker import EventChecker
from meshes import Mesh, load_obj_file, global_texture_atlas
"""
TODO:

efficiency
    <MEH> migrate to using np arrays instead of lists
        <   > reduce unnecessary transformations (from list to array, vice versa)
    <2  > more njit funcs?
    <   > entire rendering func njit?
       <   > Refactor, currently, some functions return a new array, while some modify the input

    <   > when clipping against planes, determine if entire meshes are in/out

texturing
    REFACTOR
    <   > global texture atlas could be a member of renderer
    <   > camera class should have some of renderer's responsibility? (projecting tri, culling, clipping)
    <   > transforming objects about a camera use dot product? (david)

mesh class?
    <MEH> implement
    <   > add support for transformations? (like rotations)

    With uv coords
        <MEH> BUG uv coords (not sure yet)
    
    <MEH> .obj file support?
        <   > Trianglify obj files (all faces must have 3 vertexes)
        <MEH> counterclockwise-ify all 
        <MEH> Texture Uvs
        <   > upgrade to python 3.11 (check if dependencies work)
           <   > use new pathlib module

        <   > refactor loading code (rn it reads through the file 3 times)

lighting
    ray tracing?
    fragment shading?
    <   > lighting data stored and calculated seperately per triangle?
       <   > seperate function from rendering function, data is passed into render func

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
        # these statements must come after screen initialization w/ display.set_mode()
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

    cam = Camera((WIDTH, HEIGHT), pix_size=3, init_pos=[0, 0, -4])
    renderer = Renderer3D(screen, cam)
    
    #for i in range(15):
    #    for j in range(15):
    #        renderer.add_mesh(
    #            Mesh(*load_obj_file(global_texture_atlas, "./assets/cube/cube_ccw.obj")[:-1], position=(i, 0 if j % 2 else 1, j)) # exclude last argument (textures)
    #        )

    for i in range(15):
        for j in range(15):
            renderer.add_mesh(
                Mesh(*load_obj_file(global_texture_atlas, "./assets/cube/cube_ccw.obj", scale=5)[:-1], position=(i*5, 0 if j % 2 else 5, j*5))
            )
    for i in range(7):
        renderer.add_mesh(Mesh(*load_obj_file(global_texture_atlas, "./assets/cube/cube_ccw.obj", scale=5)[:-1], position=(i*5,10,5)))

    #renderer.add_mesh(Mesh(*load_obj_file(global_texture_atlas, "./assets/cube/cube_ccw.obj", scale=15)[:-1], position=(-5, -15, 0)))

    renderer.add_mesh(
        Mesh(
            *load_obj_file(global_texture_atlas, "./assets/teapot/teapot.obj", scale=3),
            position = [5, 6, 7]
        )
    )

    # renderer.add_mesh(Mesh(*load_obj_file(global_texture_atlas, "./assets/tri/tri.obj")))

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
        #print(renderer.z_buffer[100, 100])
        #mesh.position[0] += .005
        
        # how much time has passed since last frame
        delta_time = clock.tick(FPS)/1000

        event_checker.check_key_press()
        if event_checker.get_state('quit'):
            run = False
        
        # mouse cam movement
        if (use_mouse):
            if (pygame.mouse.get_focused()):
                mouse_trav = pygame.mouse.get_rel()
                renderer.cam.rotate_cam(mouse_trav[0]//10, 0)
                renderer.cam.rotate_cam(0, -mouse_trav[1]//10)

        if event_checker.get_state('forward'):
            # multiply speed by time elapsed to account for 
            #   uneven framerate (same speed, regardless of FPS)
            renderer.cam.translate_cam((0, 0, SPEED*delta_time))
        if event_checker.get_state('backward'):
            renderer.cam.translate_cam((0, 0, -SPEED*delta_time))
            
        if event_checker.get_state('left'):
            renderer.cam.translate_cam((-SPEED*delta_time, 0, 0))
        if event_checker.get_state('right'):
            renderer.cam.translate_cam((SPEED*delta_time, 0, 0))

        if event_checker.get_state('down'):
            renderer.cam.translate_cam((0, -SPEED*delta_time, 0))
        if event_checker.get_state('up'):
            renderer.cam.translate_cam((0, SPEED*delta_time, 0))
        
        if event_checker.get_state('rot_left'):
            renderer.cam.rotate_cam(-ROT_SPEED*delta_time, 0)
        if event_checker.get_state('rot_right'):
            renderer.cam.rotate_cam(ROT_SPEED*delta_time, 0)
        
        if event_checker.get_state('rot_down'):
            renderer.cam.rotate_cam(0, -ROT_SPEED*delta_time)
        if event_checker.get_state('rot_up'):
            renderer.cam.rotate_cam(0, ROT_SPEED*delta_time)
        
        # cam limits
        if (renderer.cam.x_rot < 0):
            renderer.cam.x_rot = 360
        if (renderer.cam.x_rot > 360):
            renderer.cam.x_rot = 0
        if (renderer.cam.y_rot < -90):
            renderer.cam.y_rot = -90
        if (renderer.cam.y_rot > 90):
            renderer.cam.y_rot = 90

        renderer.render_all()

        if (debug):
            # display transparent rect as bg of stats        
            screen.blit(stat_area, (5,5))
            # display FPS
            screen.blit(FONT.render(f"FPS {clock.get_fps():.1f}", True, (255, 255, 255), None), (10, 10))
            # display pos and rot
            screen.blit(FONT.render(
                f"POS {renderer.cam.position[0]:.1f}, {renderer.cam.position[1]:.1f}, {renderer.cam.position[2]:.1f}", 
                True, (255, 255, 255), None), (10, 30)
            )
            screen.blit(FONT.render(
                f"X: {int(renderer.cam.x_rot)}, Y: {int(renderer.cam.y_rot)} DEG", 
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