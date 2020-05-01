
import pandas
import openalea.plantgl.all as pgl
from alinea.astk.sun_and_sky import sun_sky_sources, sun_sources
from alinea.astk.meteorology.sky_irradiance import sky_irradiances
from lightsimulator import *
from measuredlight import *
import os

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
woodidshift = 100000

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

def toCaribuScene(mangoscene = mango, leaf_prop=leaf_prop, wood_prop=wood_prop, woodidshift=woodidshift) :
    from alinea.caribu.CaribuScene import CaribuScene
    print ('Convert scene for caribu')
    t = time.time()
    geomdict = set([sh.id for sh in mangoscene])
    opt = { 'Rc' : {}, 'Rs' : {}}
    for vid in geomdict:
        for rv in ['Rc','Rs']:
            opt[rv][vid] = (leaf_prop if vid < woodidshift else wood_prop)[rv]
    cs = CaribuScene(mangoscene, opt=opt, scene_unit='cm',  debug = DEBUG)
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
    raw, agg = cs.run(direct=False)
    print('made in', time.time() - t)
    if view : 
        cs.plot(raw['Ei'])
    return raw, agg


def process_caribu(scene, sdates, gus = None, outdir = None):

    if not type(sdates) == list:
        sdates = [sdates]

    resdates = dict()
    allgus = list(mango.todict().keys())
    #if gus is None:

    def filter_res(values, gus = gus):
        if gus is None : 
            return list(values.values())
        else:
            return { i : values.get(i,0) for i in gus }

    for d in sdates:

        res = dict([('GUs',['incident']+(gus if gus else allgus))])

        daydate = pandas.Timestamp(d, tz=localisation['timezone'])
        day_global_horiz_radiation = ghigroup.get_group(daydate)
        hours = day_global_horiz_radiation.index

        sky_irr = sky_irradiances(ghi=day_global_horiz_radiation, dates=hours, **localisation)
        # normalised mean sky for the day
        _, sky = sun_sky_sources(ghi=day_global_horiz_radiation, dates=hours, **localisation)
        el,az,ei = sky
        sky = el, az, ei / ei.sum()

        _, aggsky1 = caribu(scene, None, sky)
        aggskyRc = filter_res(aggsky1['Rc']['Ei'])
        aggskyRs = filter_res(aggsky1['Rs']['Ei'])

        for timeindex, row in sky_irr.iterrows():
            if row.dni > 0:
                global_horizontal_irradiance  = row.ghi
                diffuse_horizontal_irradiance = row.dhi
                direct_horizontal_irradiance  = global_horizontal_irradiance - diffuse_horizontal_irradiance

                # We need to convert PAR global, direct, diffuse horizontal irradiance into Rc and Rs irradiance

                hours = pandas.date_range(end=timeindex, freq="15min", periods = 4) # We compute 4 positions of suns during the sun.
                suns = sun_sources(direct_horizontal_irradiance, dates=hours, **localisation)
                #print(direct_horizontal_irradiance)
                #print(hours, suns)
                _, aggsun = caribu(scene, suns, None)
                aggsunRc = filter_res(aggsun['Rc']['Ei'])
                aggsunRs = filter_res(aggsun['Rs']['Ei'])
                res[str(timeindex.hour)+'H-DirectRc'] = [direct_horizontal_irradiance]+aggsunRc
                res[str(timeindex.hour)+'H-DirectRs'] = [direct_horizontal_irradiance]+aggsunRs
                res[str(timeindex.hour)+'H-DiffusRc'] = [diffuse_horizontal_irradiance]+[v*diffuse_horizontal_irradiance for v in aggskyRc]
                res[str(timeindex.hour)+'H-DiffusRs'] = [diffuse_horizontal_irradiance]+[v*diffuse_horizontal_irradiance for v in aggskyRs]
                res[str(timeindex.hour)+'H-TransmisRc'] = [global_horizontal_irradiance]+[sun + sky*diffuse_horizontal_irradiance for sun,sky in zip(aggsunRc,aggskyRc)]
                res[str(timeindex.hour)+'H-TransmisRs'] = [global_horizontal_irradiance]+[sun + sky*diffuse_horizontal_irradiance for sun,sky in zip(aggsunRs,aggsunRs)]

                #eitot = aggsun.get(gu,0) + aggsky1.get(gu,0)*row.dhi

        res = pandas.DataFrame(res)
        resdates[d] = res
        if not outdir is None:
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            res.to_csv(os.path.join(outdir,'result_%s.csv' % str(d)))

    return resdates

if __name__ == '__main__':
    mango = [sh for sh in mango if sh.id < woodidshift]
    mango = pgl.Scene(mango)
    cs = toCaribuScene(mango)
    res = process_caribu(cs, targetdate,outdir = 'results-rcrs')
