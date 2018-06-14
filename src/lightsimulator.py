""" Example script for reading / manipulating meteo data of mangosim
"""

import pandas
import time

def mplot( scene, scproperty, minval = None, display = True):
    from openalea.plantgl.scenegraph import Scene, Shape
    from openalea.plantgl.gui import Viewer
    from openalea.plantgl.scenegraph.colormap import PglMaterialMap
    nscene = Scene()
    cm = PglMaterialMap(min(scproperty.values()), max(scproperty.values()))
    for sh in scene:
        if minval is None or scproperty[sh.id] > minval :
            nscene.add(Shape(sh.geometry, cm(scproperty[sh.id]), sh.id))
    if display:
        Viewer.display(nscene)
    return nscene

def caribu(scene, sun = None, sky = None, view = False):
    from alinea.caribu.CaribuScene import CaribuScene
    from alinea.caribu.light import light_sources
    print 'start caribu...'
    t = time.time()
    print 'Create light source',
    light = []
    if not sun is None:
        light += light_sources(*sun) 
    if not sky is None:
        light += light_sources(*sky)
    print '... ',len(light),' sources.'
    if isinstance(scene, CaribuScene):
        cs = scene
        cs.setLight(light)
    else:
        print 'Convert scene for caribu'
        cs = CaribuScene(scene, light=light, scene_unit='cm')
    print 'Run caribu'
    raw, agg = cs.run(direct=True, simplify=True, debug=False)
    print 'made in', time.time() - t
    if view : 
        cs.plot(raw['Ei'])
    return raw, agg


def fractalysis(scene, sun, sky, view = False):
    from openalea.plantgl.light import scene_irradiance
    print 'start fractalysis ...'
    t = time.time()
    # permute az, el, irr to el, az, irr
    sun_m = sun[1], sun[0], sun[2]
    sky_m = sky[1], sky[0], sky[2]
    directions = zip(*sun_m) + zip(*sky_m)
    defm =scene_irradiance(scene, directions, horizontal=True, scene_unit='cm', screenwidth = 800)
    print 'made in', time.time() - t

    if view:
        d = dict(zip(list(defm.index), defm['irradiance']))
        mplot(scene, d)

    return defm


def ratp(scene, sun, sky):
    from alinea.pyratp.interface.ratp_scene import RatpScene
    print 'start ratp...'
    t = time.time()
    ratp = RatpScene(mango, rleaf=0, rsoil=0, scene_unit='cm', resolution=(0.15, 0.15, 0.15), mu=0.7)
    dfv = ratp.do_irradiation(sky_sources=sky, sun_sources=sun, mu=0.6)
    resr = ratp.scene_lightmap(dfv, 'shape_id')
    dfr = resr.loc[:,('shape_id', 'Area', 'PAR')].set_index('shape_id')
    print 'made in', time.time() - t
    return dfr

def compare(rescaribu, resratp):
    rescaribu = rescaribu.rename(columns={'area': 'area_c'})
    df = rescaribu.join(resratp)
    df.plot('irradiance', ['Ei', 'PAR'],xlim=(0,35000), ylim=(0,35000), style='p')
    df.plot('area', ['area_c', 'Area'],xlim=(0,0.2), ylim=(0,0.2), style='p')

