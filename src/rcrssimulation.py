
import pandas
import openalea.plantgl.all as pgl
from openalea.plantgl.all import *
from alinea.astk.sun_and_sky import sun_sky_sources, sun_sources
from alinea.astk.meteorology.sky_irradiance import sky_irradiances
from lightsimulator import *
from measuredlight import *
from math import *
import os, sys

DEBUG = False

localisation={'latitude':-21.32, 'longitude':55.5, 'timezone': 'Indian/Reunion'}

# read the meto
meteo = get_meteo()

# The sensor give a value every 10 minutes
measuredlight = get_sensor_data()

measuredates = measuredlight.index
mindate, maxdate = min(measuredates), max(measuredates)

# a digitized mango tree
mango = pgl.Scene('../data/consolidated_mango3d-wd.bgeom')
idshift = 1000

axis, north = (0,0,1), -(90-53)
mango = Scene([Shape(AxisRotated(axis,radians(-north),sh.geometry),sh.appearance,sh.id,sh.parentId) for sh in mango])

global_horiz_irradiance = meteo.loc[measuredates,'global_radiation']
ghigroup = global_horiz_irradiance.groupby(pandas.Grouper(freq='D'))

# Reflectance_Up, Transmittance_Up, Reflectance_Down, Transmittance_Down
leaf_prop = { 'Rc' : (0.05015, 0.0116, 0.0782, 0.01215), 
              'Rs' : (0.388, 0.3577, 0.43255, 0.35595),
              'PAR' : (0.069039866, 0.117477242, 0.036254034, 0.03668661) }
wood_prop = { 'Rc' : (0.0001, 0.0001), 'Rs' : (0.0001, 0.0001)}

xcenter, ycenter = -21,   -40
xsize,   ysize   = 250+7, 300
xmin, xmax = -xcenter-xsize, -xcenter+xsize
ymin, ymax = -ycenter-ysize,-ycenter+ysize

D_SPHERE = 60

def get_dates():
    import glob
    alldates = set(map(lambda d : d.strftime('%Y-%m-%d'), measuredates))

    p = 'results-caribu'
    donedates = map(lambda x: x[len(p)+9:-4], glob.glob(p+'/results_*.csv'))

    #alldates = alldates.difference(donedates) 
    alldates = alldates.intersection(donedates) 

    alldates= list(alldates)
    alldates.sort()
    return alldates

targetdate = '2017-08-26'

def toCaribuScene(mangoscene = mango, leaf_prop=leaf_prop, wood_prop=wood_prop, idshift=idshift) :
    from alinea.caribu.CaribuScene import CaribuScene
    print ('Convert scene for caribu')
    t = time.time()
    geomdict = set([sh.id for sh in mangoscene])
    opt = { 'Rc' : {}, 'Rs' : {}}
    for vid in geomdict:
        for rv in ['Rc','Rs']:
            opt[rv][vid] = (wood_prop if (vid % idshift) == 0 else leaf_prop)[rv]
    cs = CaribuScene(mangoscene, opt=opt, scene_unit='cm', pattern=(xmin,ymin,xmax,ymax), debug = DEBUG)
    print('done in', time.time() - t)
    return cs


def caribu(scene, sun = None, sky = None, view = False, debug = False):
    from alinea.caribu.light import light_sources
    print('start caribu...')
    t = time.time()
    print('Create light source', end=' ')
    light = []
    if not sun is None:
        light += light_sources(*sun, orientation = north) 
    if not sky is None:
        light += light_sources(*sky, orientation = north)
    print('... ',len(light),' sources.')
    scene.setLight(light)
    print('Run caribu')
    raw, agg = scene.run(direct=False, infinite = True, d_sphere = D_SPHERE)
    #raw, agg = scene.run(direct=True) #, infinite = False, d_sphere = 60)
    print('made in', time.time() - t)
    if view : 
        scene.plot(raw['Ei'])
    return raw, agg


def normalize_energy(lights):
    el,az,ei = lights
    sumei = ei.sum()
    lights = el, az, ei / sumei
    return lights, sumei

import multiprocessing
import glob
import pickle
from random import randint
from os.path import join

def save_partial_res(res, d, tag, outdir = None):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    fname = os.path.join(outdir,'result_%s_%s.pkl' % (str(d), tag))
    stream = open(fname,'wb')
    pickle.dump(res, stream)

def test_partial_res(d, tag, outdir = None):
    fname = os.path.join(outdir,'result_%s_%s.pkl' % (str(d), tag))
    return os.path.exists(fname)

def filter_keys(values, gus):
    if gus is None : 
        return values
    else:
        return { i : values.get(i,0) for i in values.keys() if i // idshift in gus }

def filter_res(values, gus):
    if gus is None : 
        return list(values.values())
    else:
        return [ values.get(i,0) for i in values.keys() if i // idshift in gus ]

def generate_dataframe_data(aggregatedResults, name, ei, gus):
    aggRc = filter_keys(aggregatedResults['Rc']['Ei'], gus)
    lres = dict()
    lres['Entity'] = ['incident']+list(aggRc.keys())
    for wavelength in ['Rc','Rs','PAR']:
        for result in ['Ei','Ei_sup','Ei_inf','Eabs']:
            res = filter_res(aggregatedResults[wavelength][result], gus)
            lres[name+'-'+wavelength+'-'+result] = [ei]+list(res.values())
    return lres

def partial_sky_res(scname, skyid, skydir, d, gus, outdir):
    if test_partial_res(d, 'sky_'+str(skyid),  outdir):
        return
    s = pgl.Scene(scname)
    cs = toCaribuScene(s)
    ei = skydir[2][0]
    print('Sky ',skyid,':',*skydir)
    _, aggsky1 = caribu(cs, None, skydir)
    lres = generate_dataframe_data(aggsky1, 'Diffus-'+str(skyid).zfill(2), ei, gus)
    save_partial_res(lres, d, 'sky_'+str(skyid), outdir)

def partial_sun_res(scname, timeindex, direct_horizontal_irradiance, d, gus, outdir):
    if test_partial_res(d, 'sun_'+str(timeindex.hour)+'H',outdir):
        return
    s = pgl.Scene(scname)
    cs = toCaribuScene(s)
    print('Sun :',str(timeindex.hour)+'H')

    # We need to convert PAR global, direct, diffuse horizontal irradiance into Rc and Rs irradiance

    hours = pandas.date_range(end=timeindex, freq="1H", periods = 1) # We compute 1 positions of sun during the sun.
    suns = sun_sources(direct_horizontal_irradiance, dates=hours, **localisation)
    #print(direct_horizontal_irradiance)
    suns, _ = normalize_energy(suns)

    _, aggsun = caribu(cs, suns, None)
    lres = generate_dataframe_data(aggsun, 'Direct-'+str(skyid).zfill(2)+'H', 1, gus)
    save_partial_res(lres, d, 'sun_'+str(timeindex.hour)+'H', outdir)
    return lres,s


def process_caribu(scene, sdates, gus = None, outdir = None, nbprocesses = multiprocessing.cpu_count()):

    if not type(sdates) == list:
        sdates = [sdates]

    resdates = dict()
    allgus = list(mango.todict().keys())
    #if gus is None:

    scname = 'tmpscene_%i.bgeom' % randint(0,1000)
    scene.save(scname)

    pool = multiprocessing.Pool(processes=nbprocesses)

    for d in sdates:

        daydate = pandas.Timestamp(d, tz=localisation['timezone'])
        day_global_horiz_radiation = ghigroup.get_group(daydate)
        hours = day_global_horiz_radiation.index

        sky_irr = sky_irradiances(ghi=day_global_horiz_radiation, dates=hours, **localisation)
        # normalised mean sky for the day
        _, sky = sun_sky_sources(ghi=day_global_horiz_radiation, dates=hours, **localisation)

        sky, _ = normalize_energy(sky)

        for dirid, (az,el,ei) in enumerate(zip(*sky)):
            if nbprocesses > 1:
                pool.apply_async(partial_sky_res, args=(scname, dirid, [[az],[el],[ei]], d, gus, outdir))
            else:
                partial_sky_res(scname, dirid, [[az],[el],[ei]], d, gus, outdir)

        for timeindex, row in sky_irr.iterrows():
            if row.dni > 0:
                global_horizontal_irradiance  = row.ghi
                diffuse_horizontal_irradiance = row.dhi
                direct_horizontal_irradiance  = global_horizontal_irradiance - diffuse_horizontal_irradiance

                if nbprocesses > 1:
                    pool.apply_async(partial_sun_res, args=(scname, timeindex, direct_horizontal_irradiance, d, gus, outdir))
                else:
                    partial_sun_res(scname, timeindex, direct_horizontal_irradiance, d, gus, outdir)

        pool.close()
        pool.join()

        res = dict() 
        for fname in glob.glob(os.path.join(outdir,'result_%s_*.pkl' % str(d))):
            lres = pickle.load(open(fname,'rb'))
            os.remove(fname)
            res.update(lres)
        res = pandas.DataFrame(res)
        if not outdir is None:
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            res.to_csv(os.path.join(outdir,'result_%s.csv' % str(d)))
        resdates[d] = res

    os.remove(scname)

    return resdates


if __name__ == '__main__':
    mango = pgl.Scene([sh for sh in mango if sh.id % idshift > 0])
    from random import sample
    #mango = sample(mango,1000)
    #mango = pgl.Scene(mango)
    #pgl.Viewer.display(mango)
    res = process_caribu(mango, targetdate, outdir = 'results-rcrs-'+str(D_SPHERE)+'-'+sys.platform)
    #process_quasimc(mango)
