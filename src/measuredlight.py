def isnullmeasures(m):
    if sum([float(x) for x in m]) < 1: return True
    return False

def days():
    import os
    import datetime
    import glob
    files = glob.glob('../data/*.dat')
    dayset = []
    for f in files:
        print('process',f)
        stream = open(f,'r')
        for l in stream.readlines():
            info = l.split(',')
            dateinfo = info[1:4]
            if dateinfo[2] == '2400':
              dateinfo[2] = '2359'
            date = datetime.datetime.strptime(','.join(dateinfo),'%Y,%j,%H%M')
            if isnullmeasures(info[5:]):
                print("remove", date)
                continue
            dayset.append(date)
    dayset.sort()
    return dayset

def histodays(dayset):
    import datetime
    from collections import Counter
    import  matplotlib.pyplot as plt
    days = list(map(datetime.datetime.date, dayset))
    c = Counter(days)
    c = list(c.items())
    c.sort(key = lambda x : x[0])
    print(list(range(len(c))), [v[1] for v in c])
    plt.bar(list(range(len(c))),[v[1] for v in c], 1)
    plt.xticks(list(range(len(c))),[v[0] for v in c],rotation=90)
    plt.show()


def read_sensor_data(timezone = 'Indian/Reunion'):
    from pandas import DataFrame, DatetimeIndex
    import os
    import datetime
    import glob
    files = glob.glob('../data/*.dat')
    data = []
    for f in files:
        #print 'process',f
        stream = open(f,'r')
        for l in stream.readlines():
            info = l.split(',')
            if len(info) != 37:
                #print info
                continue
            dateinfo = info[1:4]
            Onedaytoadd = False
            if dateinfo[2] == '2400':
              dateinfo[2] = '0000'
              Onedaytoadd = True
            date = datetime.datetime.strptime(','.join(dateinfo),'%Y,%j,%H%M')
            if Onedaytoadd:
                date += datetime.timedelta(days=1)
            #if isnullmeasures(info[5:]):
            #    print "remove", date
            #    continue
            data.append([date]+list(map(float,info[5:])))
    data.sort(key = lambda v : v[0])

    sensororder = get_sensors_order()

    data = DataFrame(data,columns=['date']+['sensor_'+str(i) for i in sensororder])
    index = DatetimeIndex(data['date'])
    if timezone:
        index = index.tz_localize(timezone)
    data = data.set_index(index)
    return data

def convert_sensor_data(df):
    from pandas import DataFrame, to_datetime, DatetimeIndex
    from datetime import timedelta
    idx = df.index-timedelta(minutes=1)
    timeid = DatetimeIndex(to_datetime(DataFrame({'year' : idx.year, 'month' : idx.month, 'day' : idx.day, 'hour' : idx.hour+1})))
    timeid = timeid.tz_localize(idx.tzinfo)
    ### measure in mVolt. 60 mV -> 1200 mumol/m2/s 
    ### 4.6 mumol/m2/s -> Watt/m2 
    mumol_m2_s_to_wat_m2 = (1200 / 60) / 4.6
    ndf = df.groupby(timeid).mean() * mumol_m2_s_to_wat_m2
    return ndf

def filter_sensor_data(data, toremove = [8,9,28,29]):
    for v in toremove:
        del data['sensor_'+str(int(v))]
    return data

SENSORDATA = None

def get_sensor_data():
    global SENSORDATA
    if SENSORDATA is None:
        SENSORDATA = filter_sensor_data(convert_sensor_data(read_sensor_data()))
    return SENSORDATA


def read_meteo(data_file='../data/MeteoBassinPlat2017.csv', localisation = 'Indian/Reunion'):
    """ reader for mango meteo files """
    import pandas
    data = pandas.read_csv(data_file, parse_dates=['DATES'],
                               delimiter = ';',
                               usecols=['DATES','T107_C_3_Avg','Slr_kW_Avg','RH'], dayfirst=True)

    data = data.rename(columns={'DATES':'date',
                                 'Slr_kW_Avg':'global_radiation',
                                 'T107_C_3_Avg':'temperature_air',
                                 'RH':'relative_humidity'})
    # convert kW.m-2 to W.m-2
    data['global_radiation'] *= 1000. 
    index = pandas.DatetimeIndex(data['date']).tz_localize(localisation)
    data = data.set_index(index)
    return data


METEO = None

def get_meteo():
    global METEO
    if METEO is None:
        METEO = read_meteo()
    return METEO

SENSORS = None

def get_sensors_table(data_file = '../data/capteurspositions.csv'):
    global SENSORS
    if SENSORS is None:
        import pandas
        SENSORS = pandas.read_csv(data_file, delimiter = ';')
        SENSORS = SENSORS.set_index(SENSORS['Id'])
    return SENSORS

def get_sensors():
    from openalea.plantgl.all import Vector3
    data = get_sensors_table()
    results = {}
    for v in data.values:
        results[int(v[0])] = (Vector3(v[1],-v[2],-v[3]),Vector3(*v[4:7]))
    return results

def get_sensors_order():
    return get_sensors_table()['Sensor']


def view_sensors():
    import openalea.plantgl.all as pgl
    sensors = get_sensors()
    s = pgl.Scene('../data/lightedG3.bgeom')
    s2 = pgl.Scene([pgl.Shape(pgl.Translated(pos,pgl.Sphere(5)), pgl.Material((255,0,0)), sid) for sid,(pos,nml) in sensors.items() ])
    pgl.Viewer.display(s+s2)

def get_sensor_representation(firstid = 100000000, size = 2):
    import openalea.plantgl.all as pgl
    sensors = get_sensors()
    s2 = size/2.
    trianglepoints = [(-s2,-s2,0),(-s2,s2,0),(s2,s2,0),(s2,-s2,0)]
    triangles = [[0,1,2],[0,2,3]]
    s2 = pgl.Scene([pgl.Shape(pgl.Translated(pos,pgl.TriangleSet(trianglepoints, triangles)), pgl.Material((255,0,0)), firstid+sid) for sid,(pos,nml) in sensors.items() ])
    return s2

def view_sensors_representation(size = 2):
    import openalea.plantgl.all as pgl
    sensors = get_sensors()
    s = pgl.Scene('../data/lightedG3.bgeom')
    s2 = get_sensor_representation(size)
    pgl.Viewer.display(s+s2)



def associate_sensors(sensors, mtg = None, withleaf = True, nbnbg = 10):
    import mangoG3 as mg3
    if mtg is None:
        mtg = mg3.get_G3_mtg()

    pos = mtg.property("Position")

    from scipy.spatial import KDTree
    points = [[p.x,p.y,p.z] for vid,p in list(pos.items()) if mtg.edge_type(vid) == '<']
    kdtree = KDTree(points)
    guidmap = dict(enumerate([vid for vid in list(pos.keys()) if mtg.edge_type(vid) == '<']))

    sensorpos = [p for p,n in list(sensors.values())]
    if withleaf:
        distances, pids = kdtree.query(sensorpos,nbnbg)
        ndistance, npids = [],[]
        for sid, ldists, lpids in zip(list(range(len(pids))),distances, pids):
            for i,pid in enumerate(lpids):
                if mg3.get_gu_nb_leaf(mtg, guidmap[pid]) > 0:
                    ndistance.append(ldists[i])
                    npids.append(pid)
                    #print 'find leafy gu for', sid, pid
                    break
            else:
                ndistance.append(ldists[0])
                npids.append(lpids[0])
                #print 'find not leafy gu for', sid, lpids[0]
        distances, pids = ndistance, npids
    else:
        distances, pids = kdtree.query(sensorpos)




    gus = [guidmap[pid] for pid in pids]

    def find_closest(point, gu):
        from openalea.plantgl.all import closestPointToSegment
        d = closestPointToSegment(point,mg3.get_gu_bottom_position(mtg, gu),mg3.get_gu_top_position(mtg, gu))[1]
        sgu = gu
        for cgu in mg3.get_children(mtg,gu):
            cp, cd, cu = closestPointToSegment(point,mg3.get_gu_bottom_position(mtg, cgu),mg3.get_gu_top_position(mtg, cgu))
            if cd < d and (not withleaf or mg3.get_gu_nb_leaf(mtg, cgu) > 0):
                d = cd
                sgu = cgu
        return sgu

    gus = dict([( sid , find_closest(p,gu)) for sid, p,gu in zip(list(sensors.keys()), sensorpos, gus) ])
    return gus

def view_sensor_association(association = None, sensors = None):
    import openalea.plantgl.all as pgl
    from random import randint
    if sensors is None:
        sensors = get_sensors()
    if association is None:
        association = associate_sensors(sensors)
    cols = [pgl.Color3.fromHSV((float(randint(0,360)),100,100)) for i in range(32)]

    s = pgl.Scene('../data/consolidated_mango3d.bgeom')
    ns = s.todict()
    s1 = pgl.Scene()
    for sid,guid in list(association.items()):
        mat = pgl.Material(cols[sid-1])
        for sh in ns[guid]:
            sh.appearance = mat
            s1.add(sh)
    s2 = pgl.Scene([pgl.Shape(pgl.Translated(pos,pgl.Sphere(5)), pgl.Material(cols[sid-1]), sid) for sid,(pos,nml) in sensors.items() ])
    pgl.Viewer.display(s1+s2)


def sensors_associate_to_non_leafy_gus(association):
    import mangoG3 as mg3
    mtg = mg3.get_G3_mtg()
    return [sid for sid, guid in list(association.items()) if mg3.get_gu_nb_leaf(mtg, guid) == 0]



def plot_data(sensors = None, daterange = None, data = None, meteo = None):
    import  matplotlib.pyplot as plt
    import pandas
    if data is None:
        data = get_sensor_data()
    if meteo is None:
        meteo = get_meteo()
        ghi = meteo.loc[data.index,'global_radiation']
        data = data.join(ghi)
    if type(sensors) == int:
        if sensors < 0:
            del data['sensor_'+str(-int(sensors))]
        else:
            data = data['sensor_'+str(sensors),'global_radiation']
    elif not sensors is None:
        positive = sensors[0] >= 0
        for v in sensors:
            if (v >= 0) != positive:
                raise ValueError(sensors)
        if not positive:
            for v in sensors:
                del data['sensor_'+str(-int(v))]
        else:
            data = data[['sensor_'+str(v) for v in sensors]+['global_radiation']]
    if not daterange is None:
        dr = pandas.date_range(start=daterange[0], end = daterange[1], freq='H',tz=data.index.tzinfo)
        data = data.loc[dr,:]

    data.plot()
    plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    plt.show()



def read_simulateddata(rep = 'results', localisation = 'Indian/Reunion'):
    import os
    import glob
    #import datetime
    from pandas import concat, read_csv, DatetimeIndex

    files = glob.glob(os.path.join(rep, 'result*.csv'))
    print(files)
    df = concat([read_csv(f) for f in files])
    del df['Unnamed: 0']
    df.sort_values(by='date')
    print(df)
    index = DatetimeIndex(df['date']) #,tz='UTC').tz_convert(localisation)
    df = df.set_index(index)
    return df

SIMDATA = None
def get_simulateddata():
    global SIMDATA
    if SIMDATA is None:
        SIMDATA = read_simulateddata()
    return SIMDATA


def plotdatamain():
    import sys
    sensors = None
    if len(sys.argv) > 1:
        sensors = []
        for i in range(1,len(sys.argv)):
            sensors.append(eval(sys.argv[i]))
    #plot_data(sensors, daterange=('2017-07-06','2017-07-10'))
    plot_data(sensors, daterange=('2017-08-25','2017-08-28'))
    

if __name__ == '__main__':
    #sensors = get_sensors()
    #association = associate_sensors(sensors)
    #print association
    #print sensors_associate_to_non_leafy_gus(association)
    #view_sensors_representation()
    plotdatamain()