
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
		#for plane in planes:
		#	if (meshplanes.get(plane) is None):
		#		meshplanes[plane] = [point for point in planes.get(plane)]
		#		continue
		#	meshplanes[plane] += [point for point in planes.get(plane) if point not in meshplanes[plane]]

		
	return newmesh





S = 1

ogmesh = [
		[ [0, 0, 0],    [0, S, 0],    [S, S, 0] ],
		[ [0, 0, 0],    [S, S, 0],    [S, 0, 0] ],
		[ [S, 0, 0],    [S, S, 0],    [S, S, S] ],
		[ [S, 0, 0],    [S, S, S],    [S, 0, S] ],
		[ [S, 0, S],    [S, S, S],    [0, S, S] ],
		[ [S, 0, S],    [0, S, S],    [0, 0, S] ],
		[ [0, 0, S],    [0, S, S],    [0, S, 0] ],
		[ [0, 0, S],    [0, S, 0],    [0, 0, 0] ],
		[ [0, S, 0],    [0, S, S],    [S, S, S] ],
		[ [0, S, 0],    [S, S, S],    [S, S, 0] ],
		[ [S, 0, S],    [0, 0, S],    [0, 0, 0] ],
		[ [S, 0, S],    [0, 0, 0],    [S, 0, 0] ],
]


mesh = [
		[ [0, 0, 0],    [0, S, 0],    [S, S, 0] ],
		[ [0, 0, 0],    [S, S, 0],    [S, 0, 0] ],
		[ [S, 0, 0],    [S, S, 0],    [S, S, S] ],
		[ [S, 0, 0],    [S, S, S],    [S, 0, S] ],
		[ [S, 0, S],    [S, S, S],    [0, S, S] ],
		[ [S, 0, S],    [0, S, S],    [0, 0, S] ],
		[ [0, 0, S],    [0, S, S],    [0, S, 0] ],
		[ [0, 0, S],    [0, S, 0],    [0, 0, 0] ],
		[ [S, S, 0],    [0, S, 0],    [0, S, S] ],
		[ [S, S, 0],    [0, S, S],    [S, S, S] ],
		[ [S, 0, S],    [0, 0, S],    [0, 0, 0] ],
		[ [S, 0, S],    [0, 0, 0],    [S, 0, 0] ],
]



mesh1a = [[[j[0], j[1]+S, j[2]] for j in i] for i in mesh]
mesh2 = [[[j[0]+S, j[1], j[2]] for j in i] for i in mesh]
mesh2a = [[[j[0]+S, j[1]+S, j[2]] for j in i] for i in mesh]
mesh3 = [[[j[0]-S, j[1], j[2]] for j in i] for i in mesh]
mesh3a = [[[j[0]-S, j[1]+S, j[2]] for j in i] for i in mesh]

mesh4 = [[[j[0]+S+S, j[1], j[2]] for j in i] for i in mesh]
mesh4a = [[[j[0]+S+S, j[1]+S, j[2]] for j in i] for i in mesh]

mesh5 = [[[j[0]-S-S, j[1], j[2]] for j in i] for i in mesh]
mesh5a = [[[j[0]-S-S, j[1]+S, j[2]] for j in i] for i in mesh]

mesh6 = [[[j[0]+S+S+S, j[1]+S, j[2]] for j in i] for i in mesh]
mesh6a = [[[j[0]+S+S+S, j[1], j[2]] for j in i] for i in mesh]


meshes = [mesh]#, mesh1a, mesh2, mesh2a, mesh3, mesh3a, mesh4, mesh4a, mesh5, mesh5a, mesh6, mesh6a]