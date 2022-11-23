import numpy as np

#NOTE this doesn't work
def merge_meshes(meshlist: list[list[list[list]]]):
	"Only works with cube meshes"
	newmesh = []

	meshplanes = {}
	for mesh in meshlist:
		planes = {}
		badplanes = {}
		for triangle in mesh:
			plane = (
					triangle[0][0] if (triangle[0][0] == triangle[1][0] == triangle[2][0]) else None,
					triangle[0][1] if (triangle[0][1] == triangle[1][1] == triangle[2][1]) else None,
					triangle[0][2] if (triangle[0][2] == triangle[1][2] == triangle[2][2]) else None,
			)
			if (planes.get(plane) is None):
				planes[plane] = []
			pl = planes.get(plane)
			counter = 0

			if (meshplanes.get(plane) is None):
				pass
			else:
				for point in triangle:
					if point not in meshplanes.get(plane):
						pl.append(point)
						continue
					counter += 1
		
			if (counter < 3):
				newmesh.append(triangle)
			else:
				
				if (badplanes.get(plane) is None):
					badplanes[plane] = []
				p = badplanes.get(plane)
				for badpoint in triangle:
					if badpoint not in p:
						p.append(badpoint)
				
		badtris = []
		for tri in newmesh:
			plane = (
					tri[0][0] if (tri[0][0] == tri[1][0] == tri[2][0]) else None,
					tri[0][1] if (tri[0][1] == tri[1][1] == tri[2][1]) else None,
					tri[0][2] if (tri[0][2] == tri[1][2] == tri[2][2]) else None,
			)
			p = badplanes.get(plane)
			if (p is None):
				continue
			if (
				tri[0] in p and
				tri[1] in p and
				tri[2] in p
			):
				badtris.append(tri)
		for tri in badtris:
			newmesh.remove(tri) 
		meshplanes.update(planes)
		# for plane in planes:
		#	if (meshplanes.get(plane) is None):
		#		meshplanes[plane] = [point for point in planes.get(plane)]
		#		continue
		#	meshplanes[plane] += [point for point in planes.get(plane) if point not in meshplanes[plane]]
		
	return newmesh

# @njit
def draw_triangle_affline(
    surface: np.ndarray, triangle: list, texture: np.ndarray, texture_uv: np.ndarray
) -> None: 
    "Affline uv mapping doesn't account for distance distortion"

    texture_size = np.asarray([len(texture)-1, len(texture[0])-1])
    surf_width, surf_height = len(surface), len(surface[0])

    centered_tri = np.asarray([(int(point[0]+surf_width//2), int(surf_height//2-point[1])) for point in triangle])

    # get list of indexes of triangle points, sorted by y value (ascending)
    tri_order = centered_tri[:,1].argsort()

    x_start, y_start = centered_tri[tri_order[0]]
    x_middle, y_middle = centered_tri[tri_order[1]]
    x_stop, y_stop = centered_tri[tri_order[2]]
    
    # get slopes of each line in tri
    # add tiny number to denominator to prevent divide by zero
    x_slope_1 = (x_stop - x_start)  /(y_stop - y_start + 1e-16)
    x_slope_2 = (x_middle - x_start)/(y_middle - y_start + 1e-16)
    x_slope_3 = (x_stop - x_middle) /(y_stop - y_middle + 1e-16)

    uv_start  = texture_uv[tri_order[0]]
    uv_middle = texture_uv[tri_order[1]]
    uv_stop   = texture_uv[tri_order[2]]

    uv_slope_1 = (uv_stop - uv_start)  /(y_stop - y_start + 1e-16)
    uv_slope_2 = (uv_middle - uv_start)/(y_middle - y_start + 1e-16)
    uv_slope_3 = (uv_stop - uv_middle) /(y_stop - y_middle + 1e-16)
    

    # iterate through every row of pixels in the triangle
    #    ensure that only rows in screen are looped over (min and max is 0 and screen height)
    for y in range(max(0, y_start), min(y_stop, surf_height)):
        
        # get point on left-edge of triangle (and texture)
        x1 = x_start + int((y-y_start)*x_slope_1)
        uv1 = uv_start + (y-y_start)*uv_slope_1

        # y middle is the where the lines that the row is between changes
        #   ex: above y_middle, the row is between line 1 and line 2, but below it,
        #       the line is between line 3 and line 2
        #                O
        #       line 1  * *
        #              *   *  line 2
        #             O—————*—————————————
        #               **   *    below this line (y-middle), the rows (x vals) of pixels in the triangle
        #          line 3  ** *    are between line 3 and line 2, as opposed to line 1 and 2
        #                     *O  

        if (y < y_middle):
            x2 = x_start + int((y-y_start)*x_slope_2)
            uv2 = uv_start + (y-y_start)*uv_slope_2
        else:
            x2 = x_middle + int((y-y_middle)*x_slope_3)
            uv2 = uv_middle + (y-y_middle)*uv_slope_3
                
        # flip points if they are backwards (x1 should be the smaller one)
        if (x1 > x2):
            x1, x2 = x2, x1
            uv1, uv2 = uv2, uv1
            
        uv_slope = (uv2 - uv1)/(x2 - x1 + 1e-16)
        for x in range(max(0, x1), min(x2, surf_width)):
            uv = uv1 + (x - x1)*uv_slope

            surface[x, y] = texture[int(uv[0]*texture_size[0])][int(uv[1]*texture_size[1])]


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
