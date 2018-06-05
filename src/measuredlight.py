def isnullmeasures(m):
    if sum(map(lambda x : float(x),m)) < 1: return True
    return False

def days():
    import os
    import datetime
    import glob
    files = glob.glob('../data/*.dat')
    dayset = []
    for f in files:
        print 'process',f
        stream = open(f,'r')
        for l in stream.readlines():
            info = l.split(',')
            dateinfo = info[1:4]
            if dateinfo[2] == '2400':
              dateinfo[2] = '2359'
            date = datetime.datetime.strptime(','.join(dateinfo),'%Y,%j,%H%M')
            if isnullmeasures(info[5:]):
                print "remove", date
                continue
            dayset.append(date)
    dayset.sort()
    return dayset

def histodays(dayset):
    import datetime
    from collections import Counter
    import  matplotlib.pyplot as plt
    days = map(datetime.datetime.date, dayset)
    c = Counter(days)
    c = c.items()
    c.sort(key = lambda x : x[0])
    print range(len(c)), [v[1] for v in c]
    plt.bar(range(len(c)),[v[1] for v in c], 1)
    plt.xticks(range(len(c)),[v[0] for v in c],rotation=90)
    plt.show()


def read_data(timezone = 'Indian/Reunion'):
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
            data.append([date]+map(float,info[5:]))
    data.sort(key = lambda v : v[0])
    data = DataFrame(data,columns=['date']+['sensor_'+str(i) for i in xrange(1,33)])
    index = DatetimeIndex(data['date'])
    if timezone:
        index = index.tz_localize(timezone)
    data = data.set_index(index)
    return data

def convert_data(df):
    from pandas import DataFrame, to_datetime, DatetimeIndex
    from datetime import timedelta
    idx = df.index-timedelta(minutes=1)
    timeid = DatetimeIndex(to_datetime(DataFrame({'year' : idx.year, 'month' : idx.month, 'day' : idx.day, 'hour' : idx.hour+1})))
    timeid = timeid.tz_localize(idx.tzinfo)
    mumol_m2_s_to_wat_m2 = (1200 / 60) / (4.6*0.48)
    ndf = df.groupby(timeid).mean() * mumol_m2_s_to_wat_m2
    return ndf

def filter_data(data, toremove = [8,9]):
    for v in toremove:
        del data['sensor_'+str(int(v))]
    return data

def get_data():
    return filter_data(convert_data(read_data()))


def get_meteo(data_file='../data/MeteoBassinPlat2017.csv', localisation = 'Indian/Reunion'):
    """ reader for mango meteo files """
    import pandas
    data = pandas.read_csv(data_file, parse_dates=['DATES'],
                               delimiter = ';',
                               usecols=['DATES','T107_C_3_Avg','Slr_MJ_Tot','RH'], dayfirst=True)

    data = data.rename(columns={'DATES':'date',
                                 'Slr_MJ_Tot':'global_radiation',
                                 'T107_C_3_Avg':'temperature_air',
                                 'RH':'relative_humidity'})
    # convert kW.m-2 to W.m-2
    data['global_radiation'] *= 1000. 
    index = pandas.DatetimeIndex(data['date']).tz_localize(localisation)
    data = data.set_index(index)
    return data


def get_sensors_table(data_file = '../data/capteurspositions.csv'):
    import pandas
    data = pandas.read_csv(data_file, delimiter = ';')
    data = data.set_index(data['Id'])
    return data

def get_sensors(data_file = '../data/capteurspositions.csv'):
    from openalea.plantgl.all import Vector3
    data = get_sensors_table(data_file)
    results = {}
    for v in data.values:
        results['sensor_'+str(int(v[0]))] = (Vector3(*v[1:4]),Vector3(*v[4:]))
    return results


def plot_data(sensors = None, daterange = None, data = None, meteo = None):
    import  matplotlib.pyplot as plt
    import pandas
    if data is None:
        data = get_data()
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
    plt.show()


if __name__ == '__main__':
    #histodays(days())
    import sys
    sensors = None
    if len(sys.argv) > 1:
        sensors = []
        for i in range(1,len(sys.argv)):
            sensors.append(eval(sys.argv[i]))
    plot_data(sensors, daterange=('2017-07-03','2017-07-08'))
    #df = read_data()
