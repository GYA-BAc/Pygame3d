a project started in August 2022, by Alan Ji

A 3d renderer made in python, using pygame

Note that meshes are wound clockwise

Dependancies:
  - pygame
  - numpy
  - numba

Sources:

    - original inspiration 
      https://www.youtube.com/watch?v=ih20l3pJoeU 
        - NOTE: only the first video of the series was followed
          along with the code from 
        https://github.com/OneLoneCoder/Javidx9/blob/master/ConsoleGameEngine/BiggerProjects/Engine3D/OneLoneCoder_olcEngine3D_Part1.cpp (adapted from c++ to python)

    - segment intersection algorithm adapted from
      https://www.geeksforgeeks.org/program-for-point-of-intersection-of-two-lines/
        - used for fitting triangle vertexes to screen (cut off at screen border)
        - <add location citation for where referenced>

    - point in triangle algoritm
      https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
        - python code copied directly for use in project, used like an external library
        - <add location citation for where referenced>

    - triangle drawing algorithm and texture mapping:
      https://github.com/FinFetChannel/SimplePython3DEngine 
        - modified to suit needs

