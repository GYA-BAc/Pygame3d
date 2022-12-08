"""Various utility functions"""

def ccwify_obj_file(filepath: str) -> None:
    """Note: this will create a new file with '_ccw' concatenated to the original filename
    More accurately, this function flips all face winding orders, so cw -> ccw and vice-versa
    """

    if (filepath[-4:] != ".obj"):
        raise FileNotFoundError(f"No obj file found at {filepath}")

    with open(filepath, 'r') as file:
        raw = file.readlines()

        with open(filepath[:-4]+"_ccw.obj", 'w') as newf:

            #vertexes = [[float(vertex) for vertex in line.split()[1:]] for line in raw if line[:2] == 'f ']
            
            for line in raw:
                if (line[:2] == 'f '):
                    faces = line.split()[1:]
                    
                    newf.write("f " + ' '.join(faces[::-1])+'\n')
                    continue
                newf.write(line)
#ccwify_obj_file("./assets/cube/cube.obj")
