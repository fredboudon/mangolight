import numpy as np
from alinea.caribu.CaribuScene import CaribuScene
from openalea.plantgl.all import *
import time, datetime
from display_theozeta import *
from random import uniform
from math import sqrt


tR, tFR, tPAR = 0.007, 0.35, 0.025 
rR, rFR, rPAR = 0.06, 0.435, 0.08

#tR, tFR, tPAR = 0.01, 0.4, 0.01
#rR, rFR, rPAR = 0.01, 0.4, 0.01

layershift = 1000000


def compute_scene(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5,
                      discretization = 8,
                      pertriangles = False):
    assert 0 <= gapfraction <= 1

    R = (tR, tR)  # (0.10, 0.07, 0.10, 0.07)  # Combes et al
    FR = (tFR, tFR)  # (0.41, 0.43, 0.41, 0.43)
    PAR = (tPAR, tPAR)  # (0.41, 0.43, 0.41, 0.43)

    opt = {'FR': {}, 'R': {}, 'PAR': {}}

    # strategie des m spheres concentriques
    scene = Scene()
    t = Tesselator()
    sf = sqrt(1-gapfraction)
    invgf = (1 - sf)/2

    for lid in range(1,nblayers+1):
        sp = Sphere(nblayers+1 - lid, discretization, discretization)
        if pertriangles or gapfraction > 0 :
            sp.apply(t)
            triangleset = t.result
            points = triangleset.pointList
            pts = []
            indices = []
            for i, idx in enumerate(triangleset.indexList):
                p0 = Vector3(points[idx[0]])
                p1 = Vector3(points[idx[1]])
                p2 = Vector3(points[idx[2]])
                v1 = p1-p0
                v2 = p2-p0
                u = uniform(0, invgf)
                p0b = p0 + v1*u + v2*uniform(0,invgf-u)
                p1b = p0b + (v1 * sf)
                p2b = p0b + (v2 * sf)
                tpts = [p0b, p1b, p2b]
                if pertriangles:
                    sh = Shape(TriangleSet(tpts, [list(range(3))]), id = lid*layershift+i )
                    scene.add(sh)
                    opt['FR'][lid*layershift+i] = FR
                    opt['R'][lid*layershift+i] = R
                    opt['PAR'][lid*layershift+i] = PAR
                else:
                    pts += tpts
                    indices.append([3*i,3*i+1,3*i+2])
            if not pertriangles:
                sp = TriangleSet(pts, indices)
        if not pertriangles:
            scene.add(Shape(sp, id = lid))
            opt['FR'][lid] = FR
            opt['R'][lid] = R
            opt['PAR'][lid] = PAR

    return scene, opt

def compute_zeta_caribu(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5, 
                      discretization = 8,
                      resultingscene = ''):
    assert (tR+rR) <= 1
    assert (tFR+rFR) <= 1
    assert (tPAR+rPAR) <= 1

    ranks = range(1,nblayers+1)
    scene, opt = compute_scene(gapfraction, tR, tFR, tPAR, rR, rFR, rPAR, nblayers, discretization)

    # Soleil vertical
    soleil = [(1.0, (0., -0.0, -1))]

    # Viewer.display(s_prov)
    cc_scene = CaribuScene(scene=scene, opt=opt, light=soleil)

    current_time_of_the_system = time.time()
    raw, aggregated = cc_scene.run(direct=False, 
                                        infinite=False,
                                        split_face=False)  # ,sensors=dico_capt)#,screen_resolution=12000)
    execution_time = int(time.time() - current_time_of_the_system)
    #print('Execution time', execution_time)
    # print aggregated_direct
    #print('R ', aggregated['R'])
    #print('FR ', aggregated['FR'])
    #print('PAR ', aggregated['PAR'])

    par = np.array([aggregated['PAR']['Ei'][lid] for lid in ranks])
    r = np.array([aggregated['R']['Ei'][lid] for lid in ranks])
    fr = np.array([aggregated['FR']['Ei'][lid] for lid in ranks])
    if resultingscene:
        sc, v = cc_scene.plot(raw[resultingscene]['Ei'], display=False)
        nsc = Scene()
        for sh in sc:
            geom = sh.geometry
            for idtr,idx in enumerate(geom.indexList):
                c = geom.colorList[idtr]
                nsc.add(Shape(TriangleSet([geom.pointList[i] for i in idx],[list(range(3))]), Material(Color3(c.red,c.green,c.blue)),sh.id))
        return par, r, fr, nsc
    return par, r, fr, None


def compute_zeta_caribu_per_triangles(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5, 
                      discretization = 8,
                      resultingscene = ''):
    assert (tR+rR) <= 1
    assert (tFR+rFR) <= 1
    assert (tPAR+rPAR) <= 1

    scene, opt = compute_scene(gapfraction, tR, tFR, tPAR, rR, rFR, rPAR, nblayers, discretization, pertriangles = True)

    # Soleil vertical
    soleil = [(1.0, (0., -0.0, -1))]

    # Viewer.display(s_prov)
    cc_scene = CaribuScene(scene=scene, opt=opt, light=soleil)

    current_time_of_the_system = time.time()
    raw, aggregated = cc_scene.run(direct=False, 
                                        infinite=False,
                                        split_face=False)  # ,sensors=dico_capt)#,screen_resolution=12000)
    execution_time = int(time.time() - current_time_of_the_system)


    par = aggregated['PAR']['Ei']
    r = aggregated['R']['Ei']
    fr = aggregated['FR']['Ei']
    if resultingscene:
        sc, v = cc_scene.plot(raw[resultingscene]['Ei'], display=False)
        nsc = Scene()
        for sh in sc:
            geom = sh.geometry
            for idtr,idx in enumerate(geom.indexList):
                c = geom.colorList[idtr]
                nsc.add(Shape(TriangleSet([geom.pointList[i] for i in idx],[list(range(3))]), Material(Color3(c.red,c.green,c.blue)),sh.id))
        return par, r, fr, nsc, scene
    return par, r, fr, None



def plot_zeta_caribu(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5, 
                      discretization = 8, resultingscene = ''):

    par, r, fr,  sc =  compute_zeta_caribu(gapfraction, 
                      tR, tFR, tPAR, rR, rFR, rPAR, nblayers, discretization, resultingscene)
    plot_zeta_analysis(par, r, fr)
    return sc, [par, r, fr]


def plot_zeta_caribu_simp(gapfraction = 0, 
                      pR = (tR+rR)/2, pFR = (tFR+rFR)/2, pPAR = (tPAR+rPAR)/2,
                      nblayers = 5, 
                      discretization = 8, resultingscene = ''):
    return plot_zeta_caribu(gapfraction = gapfraction, 
                      tR = pR, tFR = pFR, tPAR = pPAR,
                      rR = pR, rFR = pFR, rPAR = pPAR, 
                      nblayers = nblayers, 
                      discretization = discretization, resultingscene = resultingscene)

def plot_zeta_caribu_per_triangles(gapfraction = 0, 
                                   pR = (tR+rR)/2, pFR = (tFR+rFR)/2, pPAR = (tPAR+rPAR)/2,
                                   nblayers = 5, 
                                   discretization = 8, resultingscene = ''):
    par, r, fr, sc, osc =  compute_zeta_caribu_per_triangles(gapfraction, 
                      tR = pR, tFR = pFR, tPAR = pPAR,
                      rR = pR, rFR = pFR, rPAR = pPAR, 
                      nblayers = nblayers, 
                      discretization = discretization, resultingscene = resultingscene)
    plot_zeta_analysis_per_triangles(par, r, fr, osc)
    return sc, [par, r, fr]


if __name__ == '__main__':
    import sys
    args = [tR, tFR, tPAR]
    if len(sys.argv) > 1:
        for i, v in enumerate(sys.argv[1:]):
            args[i] = float(v)
    plot_zeta_caribu_simp(*args)