# A 3d renderer made in python, using pygame

a project started in August 2022, by Alan Ji

Works with counter-clockwise wound meshes

Dependancies:
  - pygame
  - numpy
  - numba
    - scipy (dependancy of numba)
<pre>
Project Structure:
                   [main.py]
               ________|________
          [Renderer]     [EventChecker]
               | 
           [Camera]
</pre>
main.py contains:
 - An *EventChecker* instance (to get keypresses)
 - A *Renderer3d* instance to render meshes to screen
    - Which must have an instance of a *Camera*



Sources:

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

