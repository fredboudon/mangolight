""" 
    Debugging lighting
"""

from openalea.plantgl.all import *

def test_bug(raw, scene):
    from openalea.plantgl.all import Tesselator
    scdict = scene.todict()
    result = []
    for sid, values in list(raw.items()):
        maxvalue = max(values)
        if maxvalue > 1 :
            triangleids = []
            for i,v in enumerate(values):
                if v > 1 :
                    triangleids.append((i,v))
            t = Tesselator()
            tid = 0
            nextiditer = 0
            nextid = triangleids[nextiditer][0]
            for sh in scdict[sid]:
                done = False
                sh.apply(t)
                triangleset = t.result
                nbtriangles = len(triangleset.indexList)
                while tid <= nextid < tid + nbtriangles:
                    index = triangleset.indexList[nextid-tid]
                    result.append((sid, nextid, triangleids[nextiditer][1], [triangleset.pointList[idx] for idx in index]))
                    nextiditer += 1                    
                    if nextiditer >= len(triangleids):
                        done = True
                        break
                    else:
                        nextid = triangleids[nextiditer][0]
                if done: 
                    break
                else:
                    tid += nbtriangles

    return result



def plot_detection(detect):
    from openalea.plantgl.scenegraph.colormap import PglMaterialMap
    cmap = PglMaterialMap(1,max([value for sid, tid, value, points in detect]))
    result = Scene()
    for sid, tid, value, points in detect:
        result.add(Shape(TriangleSet(points,[list(range(3))]), cmap(value),sid))
    Viewer.display(result)
    return result

def mindegelength(p1,p2,p3):
    return min(norm(p1-p2),norm(p2-p3), norm(p1-p3))

def maxdegelength(p1,p2,p3):
    return max(norm(p1-p2),norm(p2-p3), norm(p1-p3))

def mindegelengths(detect):
    return [mindegelength(*points) for sid, tid, value, points in detect]

def surfaces(detect):
    return [surface(*points) for sid, tid, value, points in detect]


def plot_edgelenth_ei(detect, threshold = None):
    from matplotlib.pyplot import plot, show
    el = mindegelengths(detect)
    ei = [v for s,t,v,p in detect]
    if not threshold:
        plot(el,ei,'o')
    else:
        below = [(elv,eiv) for elv,eiv in zip(el,ei) if elv < threshold]
        above = [(elv,eiv) for elv,eiv in zip(el,ei) if elv >= threshold]
        print(len(below), len(above))
        plot([elv for elv,eiv in below] ,[eiv for elv,eiv in below],'ro')
        plot([elv for elv,eiv in above] ,[eiv for elv,eiv in above],'go')
    show()

def surfaces(detect):
    return [surface(*points) for sid, tid, value, points in detect]

def plot_surfaces_ei(detect):
    from matplotlib.pyplot import plot, show
    el = surfaces(detect)
    ei = [v for s,t,v,p in detect]
    plot(el,ei,'o')
    show()

def heigths(detect):
    return [2*surface(*points)/maxdegelength(*points) for sid, tid, value, points in detect]

def plot_height_ei(detect, threshold = None):
    from matplotlib.pyplot import plot, show
    el = heigths(detect)
    ei = [v for s,t,v,p in detect]
    if not threshold:
        plot(el,ei,'o')
    else:
        below = [(elv,eiv) for elv,eiv in zip(el,ei) if elv < threshold]
        above = [(elv,eiv) for elv,eiv in zip(el,ei) if elv >= threshold]
        print(len(below), len(above))
        plot([elv for elv,eiv in below] ,[eiv for elv,eiv in below],'ro')
        plot([elv for elv,eiv in above] ,[eiv for elv,eiv in above],'go')
    show()

