# A 3d renderer made in python, using pygame

a project started in August 2022, by Alan Ji
  Huge thanks to David for his support and help throughout

Works with counter-clockwise, triangulated meshes

## Dependancies:
  - pygame
  - numpy
  - numba
    - scipy (dependancy of numba)

    
## Project Structure:
<pre>
                   [main.py]
    ___________________|
[EventChecker]    [Renderer]
                   |     |
               [Camera][Meshes]

main.py contains:
 - An *EventChecker* instance (to get keypresses)
 - A *Renderer3d* instance to render meshes to screen
    - Which must have an instance of a *Camera*
    - Also has instances of *Meshes* to render
</pre>

## Sources:

    - original inspiration 
      https://www.youtube.com/watch?v=ih20l3pJoeU 
        - NOTE: only the first video of the series was followed
          along with the code from 
      https://github.com/OneLoneCoder/Javidx9/blob/master/ConsoleGameEngine/BiggerProjects/Engine3D/OneLoneCoder_olcEngine3D_Part1.cpp (adapted from c++ to python)

    - triangle drawing algorithm and texture mapping:
      https://github.com/FinFetChannel/SimplePython3DEngine 
        - mostly copied

    - backface culling using surface normal calculations:
      https://math.stackexchange.com/questions/305642/how-to-find-surface-normal-of-a-triangle 
      http://www.dgp.toronto.edu/~karan/courses/csc418/fall_2002/notes/cull.html 

    - triangle clipping: 
      https://www.quora.com/Given-a-point-and-a-plane-how-would-you-determine-which-side-of-the-plane-the-point-lies
      https://gabrielgambetta.com/computer-graphics-from-scratch/11-clipping.html

    - obj files taken from https://people.sc.fsu.edu/~jburkardt/data/obj/obj.html 
      - other useful info about .obj files
          - https://people.computing.clemson.edu/~dhouse/courses/405/docs/brief-obj-file-format.html 
          - https://www.loc.gov/preservation/digital/formats/fdd/fdd000508.shtml 
          - https://en.wikipedia.org/wiki/Wavefront_.obj_file#Vertex_texture_coordinate_indices
          - https://www.cs.cmu.edu/~mbz/personal/graphics/obj.html 

    - misc 
      - https://www.scratchapixel.com

