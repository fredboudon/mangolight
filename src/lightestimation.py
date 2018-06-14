""" Example script for reading / manipulating meteo data of mangosim
"""

import pandas
import openalea.plantgl.all as pgl
from alinea.astk.sun_and_sky import sun_sky_sources, sun_sources
from alinea.astk.meteorology.sky_irradiance import sky_irradiances
from lightsimulator import *

localisation={'latitude':-21.32, 'longitude':55.5, 'timezone': 'Indian/Reunion'}


from measuredlight import *

# read the meto
meteo = get_meteo()

# The sensor give a value every 10 minutes
measuredlight = get_sensor_data()

measuredates = measuredlight.index
mindate, maxdate = min(measuredates), max(measuredates)


# a digitized mango tree
mango = pgl.Scene('../data/consolidated_mango3d-b.bgeom')

#mango = pgl.Scene('ligthbugs.bgeom')
#pgl.Viewer.display(mango)

ghi = meteo.loc[measuredates,'global_radiation']

#sensors = get_sensors()
#gus = associate_sensors(sensors)

def get_dates():
    import glob
    alldates = set(map(lambda d : d.strftime('%Y-%m-%d'), measuredates))

    donedates = map(lambda x: x[8:-4], glob.glob('results_*.csv'))

    alldates = alldates.difference(donedates) 

    alldates= list(alldates)
    alldates.sort()
    return alldates

from random import sample
sdates = sample(get_dates(), 10)

ghigroup = ghi.groupby(pandas.Grouper(freq='D'))

def process(sdates):
    from alinea.caribu.CaribuScene import CaribuScene

    resdates = []
    results = [[] for i in gus]
    print 'Convert scene for caribu'
    scene = CaribuScene(mango, scene_unit='cm')
    print 'done'

    for d in sdates:
        daydate = pandas.Timestamp(d, tz=localisation['timezone'])
        sghi = ghigroup.get_group(daydate)
        dates = sghi.index
        sky_irr = sky_irradiances(ghi=sghi, dates=dates, **localisation)
        # normalised mean sky for the day
        _, sky = sun_sky_sources(ghi=sghi, dates=dates, **localisation)
        el,az,ei = sky
        sky = el, az, ei / ei.sum()

        _, aggsky1 = caribu(scene, None, sky)
        aggsky1 = aggsky1['Ei']

        for timeindex, row in sky_irr.iterrows():
            if row.dni > 0:
                dates = pandas.date_range(end=timeindex, freq="15min", periods = 4)
                suns = sun_sources(row.ghi-row.dhi, dates=dates, **localisation)
                _, aggsun = caribu(scene, suns, None)
                aggsun = aggsun['Ei']
            else:
                aggsun = {}

            resdates.append(timeindex)
            for i,gu in enumerate(gus):
                eitot = aggsun.get(gu,0) + aggsky1.get(gu,0)*row.dhi
                results[i].append(eitot)


    res = pandas.DataFrame(dict([('date',resdates)]+[('gu_'+str(gu), results[i]) for i,gu in enumerate(gus)]))
    return res


def processall(sdates):
    from alinea.caribu.CaribuScene import CaribuScene

    print 'Convert scene for caribu ...'
    t = time.time()
    scene = CaribuScene(mango, scene_unit='cm')
    print ' ... done in', time.time() - t

    gus = scene.scene.keys()

    for d in sdates:
        daydate = pandas.Timestamp(d, tz=localisation['timezone'])
        sghi = ghigroup.get_group(daydate)

        resdates = []
        results = [[] for i in gus]
        for timeindex, lghi in sghi.iteritems():
            print timeindex

            if lghi > 0:
                sun, sky = sun_sky_sources(ghi=lghi, dates=timeindex, **localisation)
                _, agg = caribu(scene, sun, sky)
                agg = agg['Ei']

                resdates.append(timeindex)
                for i,gu in enumerate(gus):
                    eitot = agg.get(gu,0)
                    results[i].append(eitot)

        resd = pandas.DataFrame(dict([('date',resdates)]+[('gu_'+str(gu), results[i]) for i,gu in enumerate(gus)]))
        print 'Write '+repr('results_'+d+'.csv')
        resd.to_csv('results_'+d+'.csv')


    return res


# pandas Dataframe.reindex pour rajouter des zero.

if __name__ == '__main__':
    res = processall(sdates)
    res.to_csv('results.csv')


