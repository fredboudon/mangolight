import numpy as np
from alinea.caribu.CaribuScene import CaribuScene
from openalea.plantgl.all import *
import time, datetime
from display_theozeta import *
from random import uniform
from math import sqrt
from openalea.plantgl.light.sunDome import skyTurtleWDir
from discretization import compute_scene

tR, tFR, tPAR = 0.007, 0.35, 0.025 
rR, rFR, rPAR = 0.06, 0.435, 0.08

#tR, tFR, tPAR = 0.01, 0.4, 0.01
#rR, rFR, rPAR = 0.01, 0.4, 0.01



def compute_zeta_caribu(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5, 
                      discretization = 8, 
                      horizontality = 0):
    assert (tR+rR) <= 1
    assert (tFR+rFR) <= 1
    assert (tPAR+rPAR) <= 1

    ranks = range(1,nblayers+1)
    scene, opt = compute_scene(gapfraction, tR, tFR, tPAR, rR, rFR, rPAR, nblayers, discretization, horizontality)

    # Soleil vertical
    soleil = [(1.0, (0., -0.0, -1))]

    # Viewer.display(s_prov)
    cc_scene = CaribuScene(scene=scene, opt=opt, light=soleil)

    current_time_of_the_system = time.time()
    raw, aggregated = cc_scene.run(direct=False, 
                                        infinite=False,
                                        split_face=False)  # ,sensors=dico_capt)#,screen_resolution=12000)
    execution_time = int(time.time() - current_time_of_the_system)


    par = np.array([aggregated['PAR']['Ei'][lid] for lid in ranks])
    r = np.array([aggregated['R']['Ei'][lid] for lid in ranks])
    fr = np.array([aggregated['FR']['Ei'][lid] for lid in ranks])
    return par, r, fr, scene


def compute_zeta_caribu_per_triangles(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5, 
                      discretization = 8,
                      horizontality = 0,
                      sunratio = 1,
                      widthratio = 1):
    assert (tR+rR) <= 1
    assert (tFR+rFR) <= 1
    assert (tPAR+rPAR) <= 1

    scene, opt = compute_scene(gapfraction, tR, tFR, tPAR, rR, rFR, rPAR, nblayers, discretization, pertriangles = True, horizontality = horizontality, widthratio=widthratio)

    # Soleil vertical
    assert 0 <= sunratio <= 1
    lights = []
    if sunratio > 0 :
        lights += [(sunratio, (0., -0.0, -1))]
    elif sunratio < 1:
        lights += [(w*(1-sunratio),tuple(d)) for d,w in skyTurtleWDir()]

    # Viewer.display(s_prov)
    cc_scene = CaribuScene(scene=scene, opt=opt, light=lights)

    current_time_of_the_system = time.time()
    raw, aggregated = cc_scene.run(direct=False, 
                                        infinite=False,
                                        split_face=False)  # ,sensors=dico_capt)#,screen_resolution=12000)
    execution_time = int(time.time() - current_time_of_the_system)


    par = aggregated['PAR']['Ei']
    r = aggregated['R']['Ei']
    fr = aggregated['FR']['Ei']
    return scene,(par, r, fr)



def plot_zeta_caribu(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5, 
                      discretization = 8, 
                      horizontality = 0):

    sc, (par, r, fr) =  compute_zeta_caribu(gapfraction, 
                      tR, tFR, tPAR, rR, rFR, rPAR, nblayers, discretization, horizontality)
    plot_zeta_analysis(par, r, fr)
    return sc, (par, r, fr)


def plot_zeta_caribu_simp(gapfraction = 0, 
                      pR = (tR+rR)/2, pFR = (tFR+rFR)/2, pPAR = (tPAR+rPAR)/2,
                      nblayers = 5, 
                      discretization = 8, horizontality = 0):
    return plot_zeta_caribu(gapfraction = gapfraction, 
                      tR = pR, tFR = pFR, tPAR = pPAR,
                      rR = pR, rFR = pFR, rPAR = pPAR, 
                      nblayers = nblayers, 
                      discretization = discretization, horizontality = horizontality)

def plot_zeta_caribu_per_triangles(gapfraction = 0, 
                                   pR = (tR+rR)/2, pFR = (tFR+rFR)/2, pPAR = (tPAR+rPAR)/2,
                                   nblayers = 5, 
                                   discretization = 8, horizontality = 0,
                                   sunratio = 1,
                                   widthratio = 1):
    sc, (par, r, fr) =  compute_zeta_caribu_per_triangles(gapfraction, 
                      tR = pR, tFR = pFR, tPAR = pPAR,
                      rR = pR, rFR = pFR, rPAR = pPAR, 
                      nblayers = nblayers, 
                      discretization = discretization, 
                      horizontality = horizontality, 
                      sunratio = sunratio,
                      widthratio = widthratio)
    fig = plot_zeta_analysis_per_triangles(par, r, fr, sc)
    return sc, (par, r, fr), fig


if __name__ == '__main__':
    import sys
    args = [tR, tFR, tPAR]
    if len(sys.argv) > 1:
        for i, v in enumerate(sys.argv[1:]):
            args[i] = float(v)
    plot_zeta_caribu_simp(*args)