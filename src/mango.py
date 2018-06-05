""" Example script for reading / manipulating meteo data of mangosim
"""

import pandas
import openalea.plantgl.all as pgl
from alinea.astk.sun_and_sky import sun_sky_sources
try:
    from alinea.caribu.CaribuScene import CaribuScene
    from alinea.caribu.light import light_sources
    with_caribu = True
except ImportError, ie:
    with_caribu = False

try:
    from openalea.plantgl.light import scene_irradiance
    # from vplants.fractalysis.light.directLight import scene_irradiance
    with_fractalysis = True
except ImportError, ie:
    with_fractalysis = False

try:
    from alinea.pyratp.interface.ratp_scene import RatpScene
    with_ratp = True
except ImportError, ie:
    with_ratp = False


import time


localisation={'latitude':-21.32, 'longitude':55.5, 'timezone': 'Indian/Reunion'}


from measuredlight import get_data, get_meteo, get_sensors

# read the meto
meteo = get_meteo()

# The sensor give a value every 10 minutes
measuredlight = get_data()

measuredates = measuredlight.index
mindate, maxdate = min(measuredates), max(measuredates)


# a digitized mango tree
mango = pgl.Scene('../data/consolidated_mango3d.bgeom')
#mango = pgl.Scene('ligthbugs.bgeom')
#pgl.Viewer.display(mango)

ghi = meteo.loc[measuredates,'global_radiation']

sensors = get_sensors()

from random import sample
sdates = sample(measuredates, 1)

dates = []
for d in sdates:
    dates = pandas.date_range(start=d.strftime('%Y-%m-%d 00:00:00'), end = d.strftime('%Y-%m-%d 23:00:00'), freq='H',tz=localisation['timezone'])

sun, sky = sun_sky_sources(ghi=ghi, dates=dates, normalisation = 1, **localisation)

view = True
with_caribu = True

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

# Caribu

def caribu(scene, sun, sky, view = view):
    print 'start caribu...'
    t = time.time()
    print 'Create light source'
    light = light_sources(*sun) + light_sources(*sky)
    print 'Convert scene for caribu'
    cs = CaribuScene(scene, light=light, scene_unit='cm')
    print 'Run caribu'
    raw, agg = cs.run(direct=True, simplify=True)
    res = pandas.DataFrame(agg)
    print 'made in', time.time() - t
    if view : 
        cs.plot(raw['Ei'])
    return raw, agg, res, cs

if with_caribu:
    raw, agg, res, cs = caribu(mango,sun,sky)


with_fractalysis = False

def fractalysis(scene, sun, sky, view = view):
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

# #muslim
if with_fractalysis:
    defm = fractalysis(mango,sun,sky)


def ratp(scene, sun, sky):
    print 'start ratp...'
    t = time.time()
    ratp = RatpScene(mango, rleaf=0, rsoil=0, scene_unit='cm', resolution=(0.15, 0.15, 0.15), mu=0.7)
    dfv = ratp.do_irradiation(sky_sources=sky, sun_sources=sun, mu=0.6)
    resr = ratp.scene_lightmap(dfv, 'shape_id')
    dfr = resr.loc[:,('shape_id', 'Area', 'PAR')].set_index('shape_id')
    print 'made in', time.time() - t
    return dfr

#ratp
if with_ratp:
    dfr = ratp(mango, sun, sky)

# compare
if with_caribu and with_ratp:
    res = res.rename(columns={'area': 'area_c'})
    df = res.join(resm).join(dfr)
    df.plot('irradiance', ['Ei', 'PAR'],xlim=(0,35000), ylim=(0,35000), style='p')
    df.plot('area', ['area_c', 'Area'],xlim=(0,0.2), ylim=(0,0.2), style='p')




