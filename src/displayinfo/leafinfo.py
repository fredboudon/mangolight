import openalea.plantgl.all as pgl
from openalea.plantgl.all import *
from openalea.mtg import MTG
import mangoG3 as mg3
import pandas as pd
from math import *

idshift = 1000
mtg = mg3.get_G3_mtg()
root = mtg.roots(scale=mtg.max_scale())[0]
mango = pgl.Scene('../data/consolidated_mango3d-wd.bgeom')
mango = pgl.Scene([sh for sh in mango if sh.id % idshift > 0])

gurootdepth = mg3.gus_depth_from_root(mtg)

pos = {}
XX = {}
YY = {}
ZZ = {}
El = {}
Az = {}
leafdepth = {}
rootdepth = {}

d = pgl.Discretizer()

for sh in mango:
    id = sh.id    
    idgu = id // idshift
    sh.apply(d)
    tr = d.result
    p = tr.pointList.getCenter()
    pos[id] = p
    XX[id] = p.x
    YY[id] = p.y
    ZZ[id] = p.z

    tr.normalPerVertex
    tr.computeNormalList()
    nml = pgl.Vector3.Spherical(sum(tr.normalList,pgl.Vector3(0,0,0)) / len(tr.normalList))
    El[id] = degrees(nml.phi)
    Az[id] = degrees(nml.theta)

    leafdepth[id] = mg3.get_gu_terminal_min_depth(mtg,idgu)
    rootdepth[id] = gurootdepth[idgu]

points = pgl.Point3Array(list(pos.values()))
#pointgrid = pgl.Point3Grid(points,10)

mangodict = mango.todict()



def spherical_order():
    geomorder = {}
    center = points.getCenter()
    extent = points.getExtent()
    center.z -= extent.z /2
    extent = pgl.norm(extent)
    ids = list(pos.keys())

    def toThetaPhi(v):
        vs = Vector3.Spherical(v) 
        return Vector2(vs.theta, vs.phi)

    anglegrid = pgl.Point2Grid([toThetaPhi(v-center) for v in pos.values()],20)

    for id, opt in pos.items():
        dir = opt-center
        dist = dir.normalize()
        n = dist/extent
        b = center + dir*extent

        artan()
        pids = anglegrid.query_ball_point(toThetaPhi(dir),pi/8)

        geomorder[id] = 0
        #sc = Scene([Shape(Translated(center,Sphere(5)),Material((255,255,255))), 
        #            Shape(Translated(b,Sphere(5)),Material((100,100,100))),
        #            Shape(mangodict[id][0].geometry,Material((255,255,255))),
        #            Shape(PointSet(points.subset(pids)),Material((255,255,255)))])
        for lid in pids:
            cp, d, u = pgl.closestPointToSegment(points[lid], center, b)
            #print(d,u)
            if d < 20 :
                if u > n:
                    geomorder[id] += 1
                    #c = (255,0,0)
                    
                #else:
                #    c = (0,255,0)
            #else:
            #    c = (0,0,255)
            #sc.add(Shape(mangodict[ids[lid]][0].geometry,Material(c)))

        #Viewer.display(sc)
        #if not Viewer.dialog.question('ok','ok') :
        #    break
    return geomorder

print("compute sphericalorder")
sphericalorder = spherical_order()
result = pd.DataFrame(dict(XX=XX,YY=YY,ZZ=ZZ,
                           Elevation=El,Azimuth=Az,
                           TopoLeafDepth=leafdepth,
                           TopoRootDepth=rootdepth, 
                           SphericalDepth=sphericalorder))
result.to_csv("leafinfo.csv")

def horizontal_order():
    point2grid = pgl.Point2Grid([Vector2(p.x,p.y) for p in pos.values()],20)
    indices = list(pos.keys())
    geomorder = {}
    zmax = points[points.getZMaxIndex()].z
    for id, opt in pos.items():
        dir = (0,0,1)
        n = opt.z/zmax
        opti = pgl.Vector3(opt.x,opt.y,0)
        optj = pgl.Vector3(opt.x,opt.y,zmax)
        geomorder[id] = 0
        pids = point2grid.query_ball_point((opt.x,opt.y), 20)
        for lid in pids:
            cp, d, u = pgl.closestPointToSegment(points[lid], opti, optj)
            if d < 20 and u > n:
                geomorder[id] += 1
    return geomorder

print("compute horizontalorder")
horizontalorder = horizontal_order()


result = pd.DataFrame(dict(XX=XX,YY=YY,ZZ=ZZ,
                           Elevation=El,Azimuth=Az,
                           TopoLeafDepth=leafdepth,
                           TopoRootDepth=rootdepth, 
                           SphericalDepth=sphericalorder, 
                           HorizontalDepth=horizontalorder))
result.to_csv("leafinfo.csv")