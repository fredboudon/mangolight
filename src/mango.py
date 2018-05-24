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
    from vplants.fractalysis.light.directLight import scene_irradiance
    with_fractalysis = True
except ImportError, ie:
    with_fractalysis = False

try:
    from alinea.pyratp.interface.ratp_scene import RatpScene
    with_ratp = True
except ImportError, ie:
    with_ratp = False


import time

def reader(data_file='../data/rayostpierre2002.csv'):
    """ reader for mango meteo files """
    


    data = pandas.read_csv(data_file, parse_dates=['Date'],
                               delimiter = ';',
                               usecols=['Date','Rayonnement','Temperature_Air','HR'], dayfirst=True)
    data = data.rename(columns={'Date':'date',
                                 'Rayonnement':'global_radiation',
                                 'Temperature_Air':'temperature_air',
                                 'HR':'relative_humidity'})
    # convert J.cm2.h-1 to W.m-2
    data['global_radiation'] *= (10000. / 3600)
    index = pandas.DatetimeIndex(data['date']).tz_localize('Indian/Reunion')
    data = data.set_index(index)
    return data
  
# a strange mango tree

#mango = pgl.Scene('mango0.bgeom')
mango = pgl.Scene('../data/consolidated_mango3d.bgeom')
pgl.Viewer.display(mango)
localisation={'latitude':-21.32, 'longitude':55.5, 'timezone': 'Indian/Reunion'}

meteo = reader()

dates = pandas.date_range(start='2002-09-02', end = '2002-09-03', freq='H',tz='Indian/Reunion')
ghi = meteo.loc[dates,'global_radiation']

sun, sky = sun_sky_sources(ghi=ghi, dates=dates, normalisation = 1, **localisation)

view = False

# Caribu
if with_caribu:
    print 'start caribu...'
    t = time.time()
    print 'Create light source'
    light = light_sources(*sun) + light_sources(*sky)
    print 'Convert scene for caribu'
    cs = CaribuScene(mango, light=light, scene_unit='cm')
    print 'Run caribu'
    raw, agg = cs.run(direct=True, simplify=True)
    res = pandas.DataFrame(agg)
    print 'made in', time.time() - t
    if view : 
        cs.plot(agg['Ei'])

with_fractalysis = False
# #muslim
if with_fractalysis:
    print 'start fractalysis ...'
    t = time.time()
    # permute az, el, irr to el, az, irr
    sun_m = sun[1], sun[0], sun[2]
    sky_m = sky[1], sky[0], sky[2]
    directions = zip(*sun_m) + zip(*sky_m)
    dfm =scene_irradiance(mango, directions, horizontal=True, scene_unit='cm', screenwidth = 1000)
    print 'made in', time.time() - t

    def mplot( scene, scproperty, display = True):
        from openalea.plantgl.scenegraph.colormap import PglMaterialMap
        nscene = Scene()
        cm = PglMaterialMap(min(scproperty.values()), max(scproperty.values()))
        for sh in scene:
            nscene.add(Shape(sh.geometry, cm(scproperty[sh.id]), sh.id))
        if display:
            Viewer.display(nscene)
        return nscene
    d = dict(zip(list(defm.index), defm['irradiance']))
    mplot(mango, d)


#ratp
if with_ratp:
    print 'start ratp...'
    t = time.time()
    ratp = RatpScene(mango, rleaf=0, rsoil=0, scene_unit='cm', resolution=(0.15, 0.15, 0.15), mu=0.7)
    dfv = ratp.do_irradiation(sky_sources=sky, sun_sources=sun, mu=0.6)
    resr = ratp.scene_lightmap(dfv, 'shape_id')
    dfr = resr.loc[:,('shape_id', 'Area', 'PAR')].set_index('shape_id')
    print 'made in', time.time() - t

# compare
res = res.rename(columns={'area': 'area_c'})
if with_ratp:
    df = res.join(resm).join(dfr)
    df.plot('irradiance', ['Ei', 'PAR'],xlim=(0,35000), ylim=(0,35000), style='p')
    df.plot('area', ['area_c', 'Area'],xlim=(0,0.2), ylim=(0,0.2), style='p')






