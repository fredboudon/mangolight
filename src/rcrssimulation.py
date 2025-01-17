
import pandas
import openalea.plantgl.all as pgl
from openalea.plantgl.all import *
from alinea.astk.sun_and_sky import sun_sky_sources, sun_sources
from alinea.astk.meteorology.sky_irradiance import sky_irradiances
from lightsimulator import *
from measuredlight import *
from math import *
import os, sys, datetime
import numpy as np

DEBUG = False

localisation={'latitude':-21.32, 'longitude':55.5, 'timezone': 'Indian/Reunion'}

# read the meto
meteo = get_meteo()

# The sensor give a value every 10 minutes
measuredlight = get_sensor_data()

#measuredates = measuredlight.index
#mindate, maxdate = min(measuredates), max(measuredates)

# a digitized mango tree
mango = pgl.Scene('../data/consolidated_mango3d-wd.bgeom')
idshift = 1000

axis, north = (0,0,1), -(90-53)
mango = Scene([Shape(AxisRotated(axis,radians(-north),sh.geometry),sh.appearance,sh.id,sh.parentId) for sh in mango])

#global_horiz_irradiance = meteo.loc[measuredates,'global_radiation']
global_horiz_irradiance = meteo.loc[:,'global_radiation']
ghigroup = global_horiz_irradiance.groupby(pandas.Grouper(freq='D'))

# Reflectance_Up, Transmittance_Up, Reflectance_Down, Transmittance_Down
leaf_prop = { 'Rc' : (0.05, 0.007, 0.078, 0.007), 
              'Rs' : (0.413, 0.36, 0.455, 0.353),
              'PAR' : (0.067, 0.025, 0.108, 0.023) }

wood_prop = { 'Rc' : (0.0001, 0.0001), 'Rs' : (0.0001, 0.0001), 'PAR' : (0.0001, 0.0001)}

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

#targetdate = ['2017-08-26']
targetdates = ['2017-%s-%s' % (str(month).zfill(2), str(day).zfill(2)) for month in range(1,13) for day in [12,26]]  

def toCaribuScene(mangoscene = mango, leaf_prop=leaf_prop, wood_prop=wood_prop, idshift=idshift) :
    from alinea.caribu.CaribuScene import CaribuScene
    print ('Convert scene for caribu')
    t = time.time()
    geomdict = set([sh.id for sh in mangoscene])
    wavelenghts = list(leaf_prop.keys())
    opt = dict([(k,{}) for k in wavelenghts])
    for vid in geomdict:
        for rv in wavelenghts:
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
    #raw, agg = scene.run(direct=False, infinite = True, split_face = True, d_sphere = D_SPHERE)
    raw, agg = scene.run(direct=True, infinite = True, split_face = True)
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
    pandas.DataFrame(res).to_csv(os.path.join(outdir,'partial_result_%s_%s.csv' % (str(d), tag)))
    #fname = os.path.join(outdir,'partial_result_%s_%s.pkl' % (str(d), tag))
    #pickle.dump(res, open(fname,'wb'))

def test_partial_res(d, tag, outdir = None):
    fname = os.path.join(outdir,'partial_result_%s_%s.csv' % (str(d), tag))
    return os.path.exists(fname)

def filter_keys(values, gus):
    if gus is None : 
        return list(values.keys())
    else:
        return [ i for i in values.keys() if i // idshift in gus ]

def filter_res(values, gus):
    if gus is None : 
        return list(values.values())
    else:
        return [ values.get(i,0) for i in values.keys() if i // idshift in gus ]

def generate_dataframe_data(aggregatedResults, date, name, ei, gus, outdir):
    aggRc = filter_keys(aggregatedResults['Rc']['Ei'], gus)
    lres = dict()
    lres['Entity'] = ['incident']+list(aggRc)
    for wavelength in ['Rc','Rs','PAR']:
        for result in ['Ei','Ei_sup','Ei_inf','Eabs']:
            res = filter_res(aggregatedResults[wavelength][result], gus)
            if sum(np.array(res) < -1e-5) > 0:
                errormsg = str(datetime.datetime.now())+' : Error with '+name+' on '+wavelength+'-'+result+' : Negative values found.'
                print(errormsg)
                open(os.path.join(outdir,'error.log'),'a').write(errormsg+'\n')
            lres[name+'-'+wavelength+'-'+result] = [ei]+res
    return lres

def partial_sky_res(scname, skyid, skydir, d, gus, outdir):
    tag = str(skyid).zfill(2)
    ftag = 'diffus_'+tag
    if test_partial_res(d, ftag,  outdir):
        return
    s = pgl.Scene(scname)
    cs = toCaribuScene(s)
    ei = skydir[2][0]
    print('Sky '+tag,':',*skydir)
    _, aggsky1 = caribu(cs, None, skydir)
    lres = generate_dataframe_data(aggsky1, d, 'Diffus-'+tag, ei, gus, outdir)
    save_partial_res(lres, d, ftag, outdir)

def partial_sun_res(scname, timeindex, direct_horizontal_irradiance, d, gus, outdir):
    tag = str(timeindex.hour).zfill(2)+'H'
    ftag = 'direct_'+tag
    if test_partial_res(d, ftag, outdir):
        return
    s = pgl.Scene(scname)
    cs = toCaribuScene(s)
    print('Sun :',tag)

    # We need to convert PAR global, direct, diffuse horizontal irradiance into Rc and Rs irradiance

    hours = pandas.date_range(end=timeindex, freq="1H", periods = 1) # We compute 1 positions of sun during the sun.
    suns = sun_sources(direct_horizontal_irradiance, dates=hours, **localisation)
    #print(direct_horizontal_irradiance)
    suns, _ = normalize_energy(suns)

    _, aggsun = caribu(cs, suns, None)
    lres = generate_dataframe_data(aggsun, d, 'Direct-'+tag, 1, gus, outdir)
    save_partial_res(lres, d, ftag, outdir)


def process_caribu(scene, sdates, gus = None, outdir = None, nbprocesses = multiprocessing.cpu_count()):
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if not type(sdates) == list:
        sdates = [sdates]

    resdates = dict()
    allgus = list(mango.todict().keys())
    #if gus is None:

    scname = 'tmpscene_%i.bgeom' % randint(0,1000)
    scene.save(scname)

    pool = multiprocessing.Pool(processes=nbprocesses)

    for did, ldate in enumerate(sdates):

        daydate = pandas.Timestamp(ldate, tz=localisation['timezone'])
        day_global_horiz_radiation = ghigroup.get_group(daydate)
        hours = day_global_horiz_radiation.index

        sky_irr = sky_irradiances(ghi=day_global_horiz_radiation, dates=hours, **localisation)
        # normalised mean sky for the day
        _, sky = sun_sky_sources(ghi=day_global_horiz_radiation, dates=hours, **localisation)

        sky, _ = normalize_energy(sky)

        if did == 0:
            for dirid, (az,el,ei) in enumerate(zip(*sky)):
                if nbprocesses > 1:
                    pool.apply_async(partial_sky_res, args=(scname, dirid, [[az],[el],[ei]], ldate, gus, outdir))
            else:
                partial_sky_res(scname, dirid, [[az],[el],[ei]], ldate, gus, outdir)

        for timeindex, row in sky_irr.iterrows():
           if row.dni > 0:
               global_horizontal_irradiance  = row.ghi
               diffuse_horizontal_irradiance = row.dhi
               direct_horizontal_irradiance  = global_horizontal_irradiance - diffuse_horizontal_irradiance

               if nbprocesses > 1:
                   pool.apply_async(partial_sun_res, args=(scname, timeindex, direct_horizontal_irradiance, ldate, gus, outdir))
               else:
                   partial_sun_res(scname, timeindex, direct_horizontal_irradiance, ldate, gus, outdir)


    pool.close()
    pool.join()

    os.remove(scname)

    return resdates


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        nbproc = int(sys.argv[1])
    else:
        nbproc = multiprocessing.cpu_count()
    if len(sys.argv) > 2:
        D_SPHERE = int(sys.argv[2])
    mango = pgl.Scene([sh for sh in mango if sh.id % idshift > 0])
    from random import sample
    #mango = sample(mango,1000)
    #mango = pgl.Scene(mango)
    #pgl.Viewer.display(mango)
    #res = process_caribu(mango, targetdates, outdir = 'results-rcrs-reunionpo-'+str(D_SPHERE)+'-'+sys.platform, nbprocesses = nbproc)
    res = process_caribu(mango, targetdates, outdir = 'results-rcrs-reunionpo-direct-'+sys.platform, nbprocesses = nbproc)
    #process_quasimc(mango)
