
import pandas
import openalea.plantgl.all as pgl
from alinea.astk.sun_and_sky import sun_sky_sources, sun_sources
from alinea.astk.meteorology.sky_irradiance import sky_irradiances
from lightsimulator import *
from measuredlight import *
import os, sys
import datetime

DEBUG = False

localisation={'latitude':-21.32, 'longitude':55.5, 'timezone': 'Indian/Reunion'}

# read the meto
meteo = get_meteo()

# The sensor give a value every 10 minutes
measuredlight = get_sensor_data()

measuredates = measuredlight.index
mindate, maxdate = min(measuredates), max(measuredates)

# a digitized mango tree
idshift = 1000

global_horiz_irradiance = meteo.loc[measuredates,'global_radiation']
ghigroup = global_horiz_irradiance.groupby(pandas.Grouper(freq='D'))

# Reflectance_Up, Transmittance_Up, Reflectance_Down, Transmittance_Down
leaf_prop = { 'Rc' : (0.05015, 0.0116, 0.0782, 0.01215), 'Rs' : (0.388, 0.3577, 0.43255, 0.35595)}
wood_prop = { 'Rc' : (0.0001, 0.0001), 'Rs' : (0.0001, 0.0001)}


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

def toCaribuScene(mangoscene, leaf_prop=leaf_prop, wood_prop=wood_prop, idshift=idshift) :
    from alinea.caribu.CaribuScene import CaribuScene
    print ('Convert scene for caribu')
    t = time.time()
    geomdict = set([sh.id for sh in mangoscene])
    opt = { 'Rc' : {}, 'Rs' : {}}
    for vid in geomdict:
        for rv in ['Rc','Rs']:
            opt[rv][vid] = (wood_prop if (vid % idshift) == 0 else leaf_prop)[rv]
    cs = CaribuScene(mangoscene, opt=opt, scene_unit='cm', pattern=(-230,-245,320,290), debug = DEBUG)
    print('done in', time.time() - t)
    return cs


def caribu(scene, sun = None, sky = None, view = False, debug = False):
    from alinea.caribu.light import light_sources
    print('start caribu...')
    t = time.time()
    print('Create light source', end=' ')
    light = []
    if not sun is None:
        light += light_sources(*sun) 
    if not sky is None:
        light += light_sources(*sky)
    print('... ',len(light),' sources.')
    scene.setLight(light)
    print('Run caribu')
    raw, agg = scene.run(direct=False, infinite = True, d_sphere = 60)
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

def partial_sky_res(scname, skyid, skydir, d, gus, outdir):
    if test_partial_res(d, 'sky_'+str(skyid),  outdir):
        return
    s = pgl.Scene(scname)
    cs = toCaribuScene(s)
    ei = skydir[2][0]
    print('Sky ',skyid,':',*skydir)
    _, aggsky1 = caribu(cs, None, skydir)
    aggskyRc = filter_keys(aggsky1['Rc']['Ei'], gus)
    aggskyRs = filter_res(aggsky1['Rs']['Ei'], gus)
    lres = dict()
    lres['Entity'] = ['incident']+list(aggskyRc.keys())
    lres['DiffusRc-'+str(skyid)] = [ei]+list(aggskyRc.values())
    lres['DiffusRs-'+str(skyid)] = [ei]+aggskyRs 
    save_partial_res(lres, d, 'sky_'+str(skyid), outdir)

def partial_sun_res(scname, timeindex, direct_horizontal_irradiance, d, gus, outdir):
    s = pgl.Scene(scname)
    cs = toCaribuScene(s)
    print('Sun :',str(timeindex.hour)+'H')

    # We need to convert PAR global, direct, diffuse horizontal irradiance into Rc and Rs irradiance

    hours = pandas.date_range(end=timeindex, freq="1H", periods = 1) # We compute 1 positions of sun during the sun.
    suns = sun_sources(direct_horizontal_irradiance, dates=hours, **localisation)
    #print(direct_horizontal_irradiance)
    suns, _ = normalize_energy(suns)

    _, aggsun = caribu(cs, suns, None)
    aggsunRc = filter_keys(aggsun['Rc']['Ei'], gus)
    aggsunRs = filter_res(aggsun['Rs']['Ei'], gus)
    lres = dict()
    lres['Entity'] = ['incident']+list(aggsunRc.keys())
    lres[str(timeindex.hour)+'H-DirectRc'] = [1]+list(aggsunRc.values())
    lres[str(timeindex.hour)+'H-DirectRs'] = [1]+aggsunRs
    return lres,s

def test_partial_sun_res(scname, timeindex, direct_horizontal_irradiance, d, gus, outdir):
    t = time.time()
    lres, s = partial_sun_res(scname, timeindex, direct_horizontal_irradiance, d, gus, outdir)
    restime = time.time() - t
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    #print('save bgeom')
    #s.save(os.path.join(outdir,"scene_%i.bgeom" % len(s)))
    csvname = os.path.join(outdir,'result_%sH_%i.csv' % (str(timeindex.hour),len(s)))
    print('save csv')
    print(csvname)
    pandas.DataFrame(lres).to_csv(csvname)
    print('done')
    perffilename = os.path.join(outdir,'performance_%sH_%i.csv' % (str(timeindex.hour),len(s)))
    with open(perffilename,'w') as perffile:
        perffile.write(str(datetime.datetime.now())+' --> '+str(restime))

from math import *

def test_process_caribu(sdates, gus = None, outdir = None, nbprocesses = 1) :#multiprocessing.cpu_count()):

    if not type(sdates) == list:
        sdates = [sdates]

    resdates = dict()

    pool = multiprocessing.Pool(processes=nbprocesses)

    datadir = 'benchmark-all'
    if os.path.exists(datadir):
        import glob
        scenes = glob.glob(os.path.join(datadir,'scene_*.bgeom'))
        scenes.sort()
        print (scenes)
    else:
        from random import sample
        scene = pgl.Scene('../data/consolidated_mango3d-wd.bgeom')
        scene = pgl.Scene([sh for sh in mango if sh.id % idshift > 0])
        nbelem = len(scene)
        nblogelem = ceil(log(nbelem,10))
        allsh = [sh for sh in scene]
        nbelems = [int(min(nbelem,pow(10,i))) for i in range(1, nblogelem+1)]
        print(nbelems)
        scenes = [pgl.Scene(sample(allsh,i)) for i in nbelems]

    for sc in scenes:
      if type(sc) != str:
          scname = os.path.join(datadir,"scene_%i.bgeom" % len(s))
          sc.save(scname)
      else:
          scname = sc
      for d in sdates:
        daydate = pandas.Timestamp(d, tz=localisation['timezone'])
        day_global_horiz_radiation = ghigroup.get_group(daydate)
        hours = day_global_horiz_radiation.index

        sky_irr = sky_irradiances(ghi=day_global_horiz_radiation, dates=hours, **localisation)
  
        for timeindex, row in sky_irr.iterrows():
            if row.dni > 0 and timeindex.hour == 10:
                global_horizontal_irradiance  = row.ghi
                diffuse_horizontal_irradiance = row.dhi
                direct_horizontal_irradiance  = global_horizontal_irradiance - diffuse_horizontal_irradiance

                if nbprocesses > 1:
                    pool.apply_async(test_partial_sun_res, args=(scname, timeindex, direct_horizontal_irradiance, d, gus, outdir))
                else:
                    test_partial_sun_res(scname, timeindex, direct_horizontal_irradiance, d, gus, outdir)

    pool.close()
    pool.join()


    return resdates

if __name__ == '__main__':
    
    res = test_process_caribu(targetdate, outdir = 'benchmark-'+sys.platform)
