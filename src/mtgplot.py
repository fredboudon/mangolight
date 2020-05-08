from openalea.mtg import MTG
import imp
import openalea.mtg.plantframe as opf; imp.reload(opf) 
from openalea.mtg.plantframe.plantframe import PlantFrame
from openalea.mtg.plantframe.dresser import DressingData
from openalea.plantgl.all import *

def pos_prop(mtg):
    xx,yy,zz = mtg.property("XX"),mtg.property("YY"),mtg.property("ZZ")
    return dict ([(node,(x,-yy[node],-zz[node])) for node,x in list(xx.items())])

from math import radians, degrees

def orientation_prop(mtg):
    aa,bb,cc = mtg.property("AA"),mtg.property("BB"),mtg.property("CC")
    return dict ([(node,(radians(a),radians(bb[node]),radians(cc[node]))) for node,a in list(aa.items())])


matrixmethod = True


class HeigthColoring:
    def __init__(self, mtg):
        self.heights = dict([(v,mtg.Height(v)) for v in mtg.vertices(scale=mtg.max_scale()) if mtg.nb_children(v) == 0 ])
        self.maxh = float(max(self.heights.values()))
        self.minh = float(min(self.heights.values()))
        self.deltah = self.maxh - self.minh

    def __call__(self, turtle, vid):
        if vid in self.heights:
            f = (self.heights[vid] - self.minh)*2/self.deltah
            #if f > 1.5 :
            #    turtle.setColor(3)
            #elif f < 1:
            #    turtle.setColor(5)
            #else:
            #    turtle.setColor(4)
            minc, maxc, medianc = 5,3,4
            if f > 1:
                turtle.interpolateColors(medianc,maxc,f-1)
            else:
                turtle.interpolateColors(minc,medianc,f)
        else:
            turtle.setCustomAppearance(Material((100,100,100),transparency=0.5))


class LeafColoring: 
    def __init__(self, mtg):
        self.mtg = mtg
    def __call__(self, turtle, vid):
        turtle.setColor(2 if self.mtg.property('NbLeaf').get(vid,0) > 0 else 1)

class ClassColoring:
    def __init__(self, mtg):
        self.mtg = mtg
        self.unittype = self.mtg.property('UnitType')
        self.colors = { 'B' : 7, 'D' : 1, 'O' : 4, 'U' : 2}
    def __call__(self, turtle, vid):
        typechange =  (self.unittype[self.mtg.parent(vid)] != self.unittype[vid]) if self.mtg.parent(vid) else False
        gcon = turtle.getParameters().isGeneralizedCylinderOn()
        if typechange and gcon:
            turtle.stopGC()
        turtle.setColor(self.colors[self.unittype.get(vid,'B')])
        if typechange  and gcon:
            turtle.startGC()


def leafsmb():

    leafdiam = QuantisedFunction(NurbsCurve2D(Point3Array([Vector3(0,0.0,1),Vector3(0.239002,1.00091,1),Vector3(0.485529,0.991241,1),Vector3(0.718616,1.00718,1),Vector3(0.877539,0.231273,1),Vector3(1,0.0,1)])))
    leafpath = NurbsCurve2D(Point3Array([(-0.5, 0, 1),(-0.145022, -0.0735931, 1),(0.0844156, -0.212121, 1),(0.123377, -0.497835, 1)]))    
    leafsection = NurbsCurve2D(Point3Array([Vector3(-0.5,0.15,1),Vector3(-0.5,0.1,1),Vector3(-0.1,-0.1,1),Vector3(0,0.2,1),Vector3(0.1,-0.1,1),Vector3(0.5,0.1,1),Vector3(0.5,0.15,1)]))
    leafsection.stride = 1
    length = 1

    turtle = PglTurtle()
    turtle.push()
    turtle.down(60)
    turtle.startGC().sweep(leafpath,leafsection,length,length/3.,length*0.24,leafdiam).stopGC()
    turtle.pop()

    leafsmb = turtle.getScene()[0].geometry

    t = Tesselator()
    leafsmb.apply(t)
    leafsmb = t.result

    surfs = surfaces(leafsmb.indexList, leafsmb.pointList)
    toremove = [i for i,s in enumerate(surfs) if s < 1e-5]
    leafsmb.indexList = leafsmb.indexList.opposite_subset(toremove)
    assert leafsmb.isValid()

    print(abs(surface(leafsmb) - 0.18))
    assert abs(surface(leafsmb) - 0.18) < 0.1

    leafsmb.name = 'leaf'
    return leafsmb



def plot(mtg, focus = None, colorizer = ClassColoring, leaves = False, gc = True, todate = None, display = True, leafid = True, idshift = 1000):
    posproperty = pos_prop(mtg)
    orientations = orientation_prop(mtg)

    div10 = lambda x : abs(x/10.) if x else x
    minus = lambda x : -x if x else x

    topdia = lambda x: mtg.property('Diameter').get(x)
    diameters = {}
    for vid in mtg.vertices(scale=3):
        td = topdia(vid)
        if td is None :
            if not mtg.parent(vid) is None:
                diameters[vid] = diameters[mtg.parent(vid)]
        else:
            diameters[vid] = td

    zz = lambda x: minus(mtg.property('ZZ').get(x))
    yy = lambda x: minus(mtg.property('YY').get(x))
    TopDiameter = lambda v: diameters.get(v)

    pf = PlantFrame(mtg, 
                    # BottomDiameter=botdia, 
                    TopDiameter=TopDiameter, 
                    YY = yy, 
                    ZZ = zz, 
                    origin=posproperty[mtg.roots(3)[0]]
                    )

    #diameters = pf.compute_diameters()
    #pf.points = dict([(node,Vector3(pos)-pf.origin) for node,pos in pf.points.items()])
    pf.points = dict([(node,Vector3(pos)) for node,pos in list(pf.points.items())])


    colorizer = colorizer(mtg)

    meanleaflength = 20
    leaf_length_distrib = { '<'  : ( 17.06 , 2.7) ,
                            '+' : ( 14.87 , 2.7) }
    
    todraw = None
    if not focus is None:
        if type(focus) == str:
            vids = [vid for vid,rem in list(mtg.property('Id').items()) if rem == focus]
            if len(vids) >= 1:
                todraw = set()
                for v in vids:
                    print('Display', v)
                    todraw |= set(mtg.Descendants(v))
                    todraw |= set(mtg.Ancestors(v))
                focus = set(vids)
            else:
                print('Cannot find', focus)
                focus = None
        else:
            todraw = set(mtg.Descendants(focus))
            todraw |= set(mtg.Ancestors(focus))
            focus = set([focus])

    if todate:
        import pandas as pd
        todate = pd.Timestamp(todate)


    def plantframe_visitor(g, v, turtle):
        if todraw and not v in todraw: return
        if todate and g.property('DigitDate')[v] > todate: return

        from random import gauss
        radius = diameters.get(v)
        #resolution = 4+int(4*(radius -1.6)/280.)
        pt = pf.points.get(v)

        unittype = g.property('UnitType').get(vid,'B')

        turtle.sectionResolution = 4 
        if pt:
            turtle.setId(v*idshift)
            if 'M' in unittype:
                pass
            elif 'C' in unittype:
                turtle.lineTo(pt)
            else:
                if focus and v in focus:
                    turtle.setColor(3)
                else:
                    colorizer(turtle, v)
                if g.edge_type(v) == '<':
                    nbleaf = mtg.property('NbLeaf').get(v,0)
                    if not leaves or nbleaf == 0:
                        turtle.lineTo(pt, radius)
                    else:
                        turtle.push()
                        turtle.lineTo(pt, radius)
                        turtle.pop()
                        turtle.pinpoint(pt)
                        parent = mtg.parent(v)
                        parentpos = pf.points[parent]
                        length = norm(pt-parentpos)
                        seglength = length/nbleaf
                        #parentradius = diameters.get(parent)
                        #segdiaminc = (radius-parentradius)/nbleaf
                        for i in range(nbleaf):
                            turtle.f(seglength) #,parentradius+segdiaminc*(i+1))
                            turtle.rollR(144)
                            if leafid:
                                turtle.setId(v*idshift+i+1)
                            turtle.surface('leaf', gauss(*leaf_length_distrib[mtg.edge_type(mtg.parent(v))]))
                            turtle.setId(v*idshift)
                            #leaf(turtle, gauss(*leaf_length_distrib[mtg.edge_type(mtg.parent(v))]) )

                else:

                    if gc : turtle.stopGC()
                    if g.edge_type(v) == '+':
                        parent = mtg.parent(v)
                        grandparent = mtg.parent(parent)
                        parentpos = pf.points[parent]
                        grandparentpos = pf.points[grandparent]
                        bpt, l, u = closestPointToSegment(pt, grandparentpos, parentpos)
                        turtle.move(bpt)
                        turtle.setWidth(radius)
                        if gc : turtle.startGC()
                        turtle.lineTo(pt)
                    else:
                        turtle.move(pt)
                        turtle.setWidth(radius)
                        if gc : turtle.startGC()



    turtle = PglTurtle()
    turtle.setSurface('leaf', leafsmb())
    turtle.setColorAt(7,(30,22,7))
    turtle.setColorAt(1,(65,45,15))
    #turtle.sectionResolution = 6
    sc = pf.plot(origins=[(0,0,0)],visitor=plantframe_visitor,gc=gc, turtle = turtle, display = display)
    return sc


def retrievedates(mtg):
    import numpy as np
    import pandas as pd
    dates = np.unique(list(mtg.property('DigitDate').values()))
    dates.sort()
    dates = np.unique([pd.Timestamp(d.year,d.month,d.day,23,59) for d in dates])
    return dates

from openalea.plantgl.all import *

def discretization_test(sc, minsurface = 1e-4):
    t = Tesselator()
    minmin = None
    for sh in sc:
        sh.apply(t)
        triangleset = t.result
        sfs = surfaces(triangleset.indexList, triangleset.pointList)
        nmin = sfs.getMin()
        if nmin < minsurface:
            print('!!!',sh.id)
        print(sh.id, nmin)
        if minmin is None or nmin < minmin:
            minmin = nmin


def triangles(sh):
    t = Tesselator()
    sh.apply(t)
    return Shape(t.result,sh.appearance,sh.id)


if __name__ == '__main__':
    g = MTG('../data/consolidated_mango3d.mtg')
    sc = plot(g, leaves = True, gc = False, display = True, colorizer = LeafColoring, idshift=1000)