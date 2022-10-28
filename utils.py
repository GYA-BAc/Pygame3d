import math
import numpy as np
from numba import njit

# algorithm for line intersection https://www.geeksforgeeks.org/program-for-point-of-intersection-of-two-lines/
def seg_intersect(seg1, seg2: list[float]) -> tuple[float]:
    "Determine where 2 segments intersect, if they don't, return empty tuple"

    a1 = seg1[1][1]-seg1[0][1]
    b1 = seg1[0][0]-seg1[1][0]
    c1 = a1*seg1[0][0] + b1*seg1[0][1]

    a2 = seg2[1][1]-seg2[0][1]
    b2 = seg2[0][0]-seg2[1][0]
    c2 = a2*seg2[0][0] + b2*seg2[0][1]

    determinant = a1*b2 - a2*b1
 
    # if lines parallel, return (prevent div by zero)
    if (determinant == 0):
        return ()
    
    # NOTE: these coordinates are the intersection point of the LINES formed by the points (infinite length)
    x = (b2*c1 - b1*c2)/determinant
    y = (a1*c2 - a2*c1)/determinant

    # check if the point lies within the intervals of the segments 
    # (actual intersection between segments, not lines (infinite))
    #    NOTE: instead of using >= and <=, check for equality and strict inequality seperately:
    #    as comparing float equality is inaccurate. 
    #       (conversion from base 2 (binary) to base 10 (decimal) is bad, 
    #       as floats do not have infinite precision, and must be rounded at some point, 
    #       leading to rounding errors. )
    #       EX: 0.1 + 0.2 does not result in 0.3 (Try it)
    # 
    #       This can be solved by using the math.isclose() function

    if (
        not (min(seg1[0][0], seg1[1][0]) < x or math.isclose(min(seg1[0][0], seg1[1][0]), x)) or
        not (x < max(seg1[0][0], seg1[1][0]) or math.isclose(max(seg1[0][0], seg1[1][0]), x)) or
        not (min(seg2[0][0], seg2[1][0]) < x or math.isclose(min(seg2[0][0], seg2[1][0]), x)) or
        not (x < max(seg2[0][0], seg2[1][0]) or math.isclose(max(seg2[0][0], seg2[1][0]), x)) or

        not (min(seg1[0][1], seg1[1][1]) < y or math.isclose(min(seg1[0][1], seg1[1][1]), y)) or
        not (y < max(seg1[0][1], seg1[1][1]) or math.isclose(max(seg1[0][1], seg1[1][1]), y)) or
        not (min(seg2[0][1], seg2[1][1]) < y or math.isclose(min(seg2[0][1], seg2[1][1]), y)) or
        not (y < max(seg2[0][1], seg2[1][1]) or math.isclose(max(seg2[0][1], seg2[1][1]), y))
    ):  
        return ()

    return (x, y)

# code taken directly from https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
# used like a module
def point_in_triangle(point: list[float], triangle: list[list[float]]) -> bool:
    """Returns True if the point is inside the triangle
    and returns False if it falls outside.
    - The argument *point* is a tuple with two elements
    containing the X,Y coordinates respectively.
    - The argument *triangle* is a tuple with three elements each
    element consisting of a tuple of X,Y coordinates.

    It works like this:
    Walk clockwise or counterclockwise around the triangle
    and project the point onto the segment we are crossing
    by using the dot product.
    Finally, check that the vector created is on the same side
    for each of the triangle's segments.
    """
    # Unpack arguments
    x, y = point
    ax, ay = triangle[0]
    bx, by = triangle[1]
    cx, cy = triangle[2]
    # Segment A to B
    side_1 = (x - bx) * (ay - by) - (ax - bx) * (y - by)
    # Segment B to C
    side_2 = (x - cx) * (by - cy) - (bx - cx) * (y - cy)
    # Segment C to A
    side_3 = (x - ax) * (cy - ay) - (cx - ax) * (y - ay)
    # All the signs must be positive or all negative
    return (side_1 < 0.0) == (side_2 < 0.0) == (side_3 < 0.0)

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

# njit increases performance ten-fold 
@njit()
def draw_triangle(surfarray, z_buffer, triangle, texture, texture_uv):

    # start with perspective correct triangle
    tex_size = np.asarray([len(texture)-1, len(texture[0])-1])
    surf_width, surf_height = len(surfarray), len(surfarray[0])

    # normalize pygame coordinates (pygame has (0,0) in top left corner)
    centered_tri = np.asarray([(int(point[0]+surf_width//2), int(surf_height//2-point[1]), point[2]) for point in triangle])

    # sort triangles by y (from top of screen to bottom)
    sorted_y = centered_tri[:,1].argsort()

    x_start, y_start, z_start = centered_tri[sorted_y[0]]
    x_middle, y_middle, z_middle = centered_tri[sorted_y[1]]
    x_stop, y_stop, z_stop = centered_tri[sorted_y[2]] 

    x_slope_1 = (x_stop - x_start)/(y_stop - y_start + 1e-32)
    x_slope_2 = (x_middle - x_start)/(y_middle - y_start + 1e-32)
    x_slope_3 = (x_stop - x_middle)/(y_stop - y_middle + 1e-32)  
    

    # invert z for interpolation
    z_start, z_middle, z_stop = 1/(z_start +1e-32), 1/(z_middle + 1e-32), 1/(z_stop +1e-32)

    z_slope_1 = (z_stop - z_start)/(y_stop - y_start + 1e-32) 
    z_slope_2 = (z_middle - z_start)/(y_middle - y_start + 1e-32) 
    z_slope_3 = (z_stop - z_middle)/(y_stop - y_middle + 1e-32)  

    # uv coordinates multiplied by inverted z to account for perspective
    uv_start = texture_uv[sorted_y[0]]*z_start 
    uv_middle = texture_uv[sorted_y[1]]*z_middle
    uv_stop = texture_uv[sorted_y[2]]*z_stop

    uv_slope_1 = (uv_stop - uv_start)/(y_stop - y_start + 1e-32)  
    uv_slope_2 = (uv_middle - uv_start)/(y_middle - y_start + 1e-32)  
    uv_slope_3 = (uv_stop - uv_middle)/(y_stop - y_middle + 1e-32) 

    # min and max used to cut off rows not in screen
    for y in range(max(0, int(y_start)), min(surf_height, int(y_stop))):
        # to get start and end of each row, traverse the lines 
        # of the triangle that make up the row (on either side)
        # simply use slope to find x limits given y

        delta_y = y - y_start
        x1 = x_start + int(delta_y*x_slope_1)
        z1 = z_start + delta_y*z_slope_1
        uv1 = uv_start + delta_y*uv_slope_1

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
        if y < y_middle:
            x2 = x_start + int(delta_y*x_slope_2)
            z2 = z_start + delta_y*z_slope_2
            uv2 = uv_start + delta_y*uv_slope_2

        else:
            delta_y = y - y_middle
            x2 = x_middle + int(delta_y*x_slope_3)
            z2 = z_middle + delta_y*z_slope_3
            uv2 = uv_middle + delta_y*uv_slope_3
            
        # x1 should be smaller
        if x1 > x2:
            x1, x2 = x2, x1
            z1, z2 = z2, z1
            uv1, uv2 = uv2, uv1

        uv_slope = (uv2 - uv1)/(x2 - x1 + 1e-32) # 1e-32 to avoid zero division ¯\_(ツ)_/¯
        z_slope = (z2 - z1)/(x2 - x1 + 1e-32)

        # min and max used to cut off pixels not in screen
        for x in range(max(0, int(x1)), min(surf_width, int(x2))):
            z = 1/(z1 + (x - x1)*z_slope + 1e-32) # retrive z

            # if pixel trying to be rendered falls behind 
            #   player in 3d space, don't render
            if (z < 1): 
                continue

            # if pixel's z distance from cam is closer than previous 
            #   value in z_buf, update z_buf and draw pixel.
            # Otherwise, the pixel is behind another pixel (don't render)
            if (z > z_buffer[x, y]):
                continue
            z_buffer[x, y] = z

            # multiply by z to go back to uv space
            uv = (uv1 + (x - x1)*uv_slope)*z
            # for now, shading is determined by distance from cam (farther=darker)
            shade = max(0, 1 - z/(20))
            # don't render texture if uv out of bounds
            if min(uv) >= 0 and max(uv) <= 1: 
                surfarray[x, y] = texture[int(uv[0]*tex_size[0])][int(uv[1]*tex_size[1])]*shade

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