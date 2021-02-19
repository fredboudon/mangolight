import numpy as np
from alinea.caribu.CaribuScene import CaribuScene
from openalea.plantgl.all import *
import time, datetime
from display_theozeta import *
from random import uniform


tR, tFR, tPAR = 0.007, 0.35, 0.025 
rR, rFR, rPAR = 0.06, 0.435, 0.08

#tR, tFR, tPAR = 0.01, 0.4, 0.01
#rR, rFR, rPAR = 0.01, 0.4, 0.01

def compute_scene(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5):
    R = (tR, tR)  # (0.10, 0.07, 0.10, 0.07)  # Combes et al
    FR = (tFR, tFR)  # (0.41, 0.43, 0.41, 0.43)
    PAR = (tPAR, tPAR)  # (0.41, 0.43, 0.41, 0.43)

    opt = {'FR': {}, 'R': {}, 'PAR': {}}

    # strategie des m spheres concentriques
    scene = Scene()
    t = Tesselator()
    invgf = 1 - gapfraction

    for lid in range(1,nblayers+1):
        tri_label = 1000
        num_tri = 1
        sp = Sphere(nblayers - lid)
        if gapfraction > 0:
            sp.apply(t)
            triangleset = t.result
            points = triangleset.pointList
            pts = []
            indices = []
            for i, idx in enumerate(triangleset.indexList):
                p0 = points[idx[0]]
                p1 = points[idx[1]]
                p2 = points[idx[2]]
                v1 = p1-p0
                v2 = p2-p0
                p0b = p0 + v1*uniform(0, invgf) + v2*uniform(0, invgf)
                p1b = p0b + v1 * gapfraction
                p2b = p0b + v2 * gapfraction
                pts += [p0b, p1b, p2b]
                indices.append([3*i,3*i+1,3*i+2])
                sp = TriangleSet(pts, indices)
                id_tri =  tri_label*lid + num_tri
                scene.add(Shape(sp, id = id_tri))
                num_tri += 1
                opt['FR'][tri_label] = FR
                opt['R'][tri_label] = R
                opt['PAR'][tri_label] = PAR

    return scene, opt

def compute_zeta_caribu(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5, resultingscene = ''):
    assert (tR+rR) <= 1
    assert (tFR+rFR) <= 1
    assert (tPAR+rPAR) <= 1

    ranks = range(1,nblayers+1)
    scene, opt = compute_scene(gapfraction, tR, tFR, tPAR, rR, rFR, rPAR, nblayers)

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
    res = (par, r, fr, None, None, None)
    if resultingscene:
        sc, v = cc_scene.plot(raw[resultingscene]['Ei'], display=False)
        return par, r, fr, None, None, None, sc
    return par, r, fr, None, None, None, None



def plot_zeta_caribu(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5, resultingscene = ''):

    par, r, fr, par_sky, r_sky, fr_sky, sc =  compute_zeta_caribu(gapfraction, 
                      tR, tFR, tPAR, rR, rFR, rPAR, nblayers, resultingscene)
    plot_zeta_analysis(par, r, fr, par_sky, r_sky, fr_sky)
    return sc


def plot_zeta_caribu_simp(gapfraction = 0, 
                      pR = (tR+rR)/2, pFR = (tFR+rFR)/2, pPAR = (tPAR+rPAR)/2,
                      nblayers = 5, resultingscene = ''):
    return plot_zeta_caribu(gapfraction = gapfraction, 
                      tR = pR, tFR = pFR, tPAR = pPAR,
                      rR = pR, rFR = pFR, rPAR = pPAR, 
                      nblayers = nblayers, resultingscene = resultingscene)


if __name__ == '__main__':
    import sys
    args = [tR, tFR, tPAR]
    if len(sys.argv) > 1:
        for i, v in enumerate(sys.argv[1:]):
            args[i] = float(v)
    plot_zeta_caribu_simp(*args)