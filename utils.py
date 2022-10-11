import math

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
def point_in_triangle(point, triangle) -> bool:
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
