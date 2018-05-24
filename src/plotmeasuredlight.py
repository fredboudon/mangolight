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


def read_data():
    import os
    import datetime
    import glob
    files = glob.glob('../data/*.dat')
    data = []
    for f in files:
        print 'process',f
        stream = open(f,'r')
        for l in stream.readlines():
            info = l.split(',')
            if len(info) != 37:
                print info
                continue
            dateinfo = info[1:4]
            if dateinfo[2] == '2400':
              dateinfo[2] = '2359'
            date = datetime.datetime.strptime(','.join(dateinfo),'%Y,%j,%H%M')
            #if isnullmeasures(info[5:]):
            #    print "remove", date
            #    continue
            data.append([date]+map(float,info[5:]))
    data.sort(key = lambda v : v[0])
    return data

def plot_data(sensors = None):
    import  matplotlib.pyplot as plt
    data = read_data()
    if sensors is None:
        sensors = xrange(1,len(data[0]))
    elif type(sensors) == int:
        if sensors < 0:
            v = sensors
            sensors = range(1,len(data[0]))
            sensors.remove(-v)
        else:
            sensors = [sensors]
    else:
        positive = sensors[0] >= 0
        for v in sensors:
            if (v >= 0) != positive:
                raise ValueError(sensors)
        if not positive:
            nsensors = sensors
            sensors = range(1,len(data[0]))
            for v in nsensors:
                sensors.remove(-v)

    for i in sensors:
        print i
        assert  1 <= i < len(data[0])
        capteuri = [d[i] for d in data]
        print [m for m in capteuri if m > 10]
        plt.plot([d[0] for d in data],capteuri)
    plt.show()


if __name__ == '__main__':
    #histodays(days())
    import sys
    sensors = None
    if len(sys.argv) > 1:
        sensors = []
        for i in range(1,len(sys.argv)):
            sensors.append(eval(sys.argv[i]))
    plot_data(sensors)
