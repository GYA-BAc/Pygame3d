from utils import load_obj_file

# S = .5

# mesh = [
# 		[ [0, 0, 0],    [0, S, 0],    [S, S, 0] ],
# 		[ [0, 0, 0],    [S, S, 0],    [S, 0, 0] ],
# 		[ [S, 0, 0],    [S, S, 0],    [S, S, S] ],
# 		[ [S, 0, 0],    [S, S, S],    [S, 0, S] ],
# 		[ [S, 0, S],    [S, S, S],    [0, S, S] ],
# 		[ [S, 0, S],    [0, S, S],    [0, 0, S] ],
# 		[ [0, 0, S],    [0, S, S],    [0, S, 0] ],
# 		[ [0, 0, S],    [0, S, 0],    [0, 0, 0] ],
# 		[ [S, S, 0],    [0, S, 0],    [0, S, S] ],
# 		[ [S, S, 0],    [0, S, S],    [S, S, S] ],
# 		[ [S, 0, S],    [0, 0, S],    [0, 0, 0] ],
# 		[ [S, 0, S],    [0, 0, 0],    [S, 0, 0] ],
# ]

# mesh1a = [[[j[0], j[1]+S, j[2]] for j in i] for i in mesh]
# mesh2 = [[[j[0]+S, j[1], j[2]] for j in i] for i in mesh]
# mesh2a = [[[j[0]+S, j[1]+S, j[2]] for j in i] for i in mesh]
# mesh3 = [[[j[0]-S, j[1], j[2]] for j in i] for i in mesh]
# mesh3a = [[[j[0]-S, j[1]+S, j[2]] for j in i] for i in mesh]

# mesh4 = [[[j[0]+S+S, j[1], j[2]] for j in i] for i in mesh]
# mesh4a = [[[j[0]+S+S, j[1]+S, j[2]] for j in i] for i in mesh]

# mesh5 = [[[j[0]-S-S, j[1], j[2]] for j in i] for i in mesh]
# mesh5a = [[[j[0]-S-S, j[1]+S, j[2]] for j in i] for i in mesh]

# mesh6 = [[[j[0]+S+S+S, j[1]+S, j[2]] for j in i] for i in mesh]
# mesh6a = [[[j[0]+S+S+S, j[1], j[2]] for j in i] for i in mesh]


# meshes = [mesh, mesh1a, mesh2, mesh2a, mesh3a, mesh4, mesh4a, mesh5, mesh5a, mesh6, mesh6a]

meshes = [load_obj_file("./assets/teapot.obj")]