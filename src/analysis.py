from pandas import *
from measuredlight import *



woodidshift = 100000

def select_simulateddata(data, gus = None):
    if gus is None:
        gus = associate_sensors(sensors) #,withleaf=False)    
    names = ['gu_'+str(gid) for gid in list(gus.values())]+['gu_'+str(woodidshift+gid) for gid in list(gus.values())]
    names = [n for n in names if n in data.columns]
    return data[names]

def simulated_days(data):
    return list(data.groupby(data.index.date).groups.keys())

def plot_each_day(data, dates = None):
    from matplotlib.pyplot import show, legend
    import datetime
    if not dates is None:
        convert = lambda sd : datetime.datetime.strptime(sd,'%Y-%m-%d').date()
        if type(dates) == str:
            dates = [convert(dates)]
        else:
            dates = list(map(convert, dates))
    daydata = list(data.groupby(data.index.date).groups.items())
    daydata.sort()
    print(daydata)
    for d, times in daydata:
        if len(times) > 0 and (dates is None or d in dates):
            df = data.loc[times,]
            df = df.join(meteo.loc[times,'global_radiation'])
            df.plot(title=d.strftime('%Y-%m-%d'))
            legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
            show()

def plot_all_day(data):
    from matplotlib.pyplot import show, legend, xticks
    import datetime

    meteo = get_meteo()

    ndf = data.join(meteo.loc[data.index,'global_radiation'])
    ndf = ndf.reset_index()
    dates = ndf['date']
    del ndf['date']
    ndf.plot()
    #df.plot(title=d.strftime('%Y-%m-%d'))
    xticks(ndf.index, [d.strftime('%m-%d:%HH') if d.hour == 12 else d.strftime('%HH') for d in dates], rotation=60)
    legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    show()


SensorGroups = [[1,2,3,13,14,15],
                [4,5,6,16,17,18],
                [7,8,9,19,20,21],
                [10,11,12,22,23,24],
                list(range(25,29)),list(range(29,33))]


SensorGroups = [[1,4,7,10],[13,16,19,22],
                [2,5,8,11],[14,17,20,23],
                [3,6,9,12],[15,18,21,24],
                list(range(29,33)),list(range(25,29))]

SensorGroupsNames = ['Bottom - Periphery','Up - Periphery',
                     'Bottom - Inside Foliage','Up - Inside Foliage',
                     'Bottom - Below Foliage','Up - Below Foliage',
                     'Inside Crown','Top Crown']


SensorGroups = [[13,16,19,22],[14,17,20,23],[15,18,21,24],list(range(25,29)),
                [1,4,7,10],[2,5,8,11],[3,6,9,12],list(range(29,33))]

SensorGroupsNames = [ 'Up - Periphery','Up - Inside Foliage','Up - Below Foliage','Top Crown',
                      'Bottom - Periphery','Bottom - Inside Foliage','Bottom - Below Foliage','Inside Crown']



def plot_all_day_groups(data, dayids = None, gus = None):
    import matplotlib.pyplot as plt
    import datetime
    from numpy import array, add

    sensors = get_sensors()

    if gus is None:
        gus = associate_sensors(sensors) #,withleaf=False)

    days = simulated_days(data)
    days.sort()

    if not dayids is None:
        if type(dayids) == int:
            days = [days[dayids]]
        else:
            days = [days[did] for did in dayids]

    meteo = get_meteo()
    selection = array([meteo.index.date == d  for d in days]).any(axis=0)
    base = meteo.loc[selection,('global_radiation',)]

    measureddata = get_sensor_data()
    selection = array([measureddata.index.date == d  for d in days]).any(axis=0)
    measureddata = measureddata.loc[selection,:]

    ndf = base.join(data)
    ndf = ndf.join(measureddata)
    #ndf = data.join(meteo.loc[data.index,'global_radiation'])
    ndf = ndf.reset_index()
    dates = ndf['date']
    #del ndf['date']
    cols = ['r','g','b','y']

    fig = 1
    title = ' , '.join([d.strftime('%m-%d') for d in days])
    plt.suptitle(title, fontsize=16)
    for group, gname in zip(SensorGroups,SensorGroupsNames):
        plt.subplot(4,4,0+fig)
        fig += 1
        names = ['gu_'+str(gus[i]) for i in group]+['sensor_'+str(i) for i in group]
        names = [n for n in names if n in ndf.columns]
        ndf1 = ndf[names+['global_radiation']]


        for i,sid in enumerate(group):
            if 'gu_'+str(gus[sid]) in ndf.columns:
                plt.plot(ndf.index, ndf['gu_'+str(gus[sid])], cols[i]+'-',label = str(gus[sid]))
            if 'gu_'+str(gus[sid]+woodidshift) in ndf.columns:
                plt.plot(ndf.index, ndf['gu_'+str(gus[sid]+woodidshift)], cols[i]+'-.',label = 'W'+str(gus[sid]))
            #else:
            #    print 'cannot find '+'gu_'+str(gus[sid]+woodidshift)

        plt.ylim(0,550)
        plt.title(gname+' - GUs')

        #xticks(ndf1.index, [d.strftime('%m/%d:%H') if d.hour == 12 else d.strftime('%H') for d in dates], rotation=60)
        plt.xticks(ndf1.index, ['' for d in dates], rotation=60)
        plt.legend(bbox_to_anchor=(0.71, 1), loc=2, borderaxespad=0.)

        plt.subplot(4,4,0+fig)
        fig += 1
        for i,sid in enumerate(group):
            if 'sensor_'+str(sid) in ndf.columns:
                plt.plot(ndf.index, ndf['sensor_'+str(sid)], cols[i]+'-',label = str(sid))
        plt.ylim(0,550)
        #plot(ndf.index, ndf['global_radiation'])
        plt.title(gname+' - Sensors')
        #df.plot(title=d.strftime('%Y-%m-%d'))
        #xticks(ndf1.index, [d.strftime('%m/%d:%H') if d.hour == 12 else d.strftime('%H') for d in dates], rotation=60)
        plt.xticks(ndf1.index, ['' for d in dates], rotation=60)
        plt.legend(bbox_to_anchor=(0.71, 1), loc=2, borderaxespad=0.)
    plt.show()



def plot_all_day_groupmeans(data, dayids = None, gus = None):
    import matplotlib.pyplot as plt
    import datetime
    from numpy import array, add

    sensors = get_sensors()
    if gus is None:
        gus = associate_sensors(sensors) #,withleaf=False)

    days = simulated_days(data)
    days.sort()

    if not dayids is None:
        if type(dayids) == int:
            print('Plot day',dayids,'from set of',len(days),'days.')
            days = [days[dayids]]
        else:
            days = [days[did] for did in dayids]

    meteo = get_meteo()
    selection = array([meteo.index.date == d  for d in days]).any(axis=0)
    base = meteo.loc[selection,('global_radiation',)]

    measureddata = get_sensor_data()
    selection = array([measureddata.index.date == d  for d in days]).any(axis=0)
    measureddata = measureddata.loc[selection,:]

    ndf = base.join(data)
    ndf = ndf.join(measureddata)
    #ndf = data.join(meteo.loc[data.index,'global_radiation'])
    ndf = ndf.reset_index()
    dates = ndf['date']
    del ndf['date']

    fig = 1
    title = ' , '.join([d.strftime('%m-%d') for d in days])
    dpi = 100
    plt.figure(figsize=(1200/dpi,400/dpi), dpi=dpi)
    #plt.suptitle(title, fontsize=16)
    for group, gname in zip(SensorGroups,SensorGroupsNames):
        plt.subplot(2,4,0+fig)
        names = ['gu_'+str(gus[i]) for i in group]# +['sensor_'+str(i) for i in group]
        names = [n for n in names if n in ndf.columns]
        ndf1 = ndf[names].mean(axis=1)*4.6
        plt.plot(ndf1.index, ndf1.values,'-',color='black',label = 'GUs')

        names = ['sensor_'+str(i) for i in group]
        names = [n for n in names if n in ndf.columns]
        ndf1 = ndf[names].mean(axis=1)*4.6
        plt.plot(ndf1.index, ndf1.values, '-',color='grey',label = 'Sensors')

        plt.ylim(0,1200)
        plt.title(gname)
        
        #xticks(ndf1.index, [d.strftime('%m/%d:%H') if d.hour == 12 else d.strftime('%H') for d in dates], rotation=60)
        if fig in [1]:
            plt.ylabel(r'Irradiance ($\mu$mol.m-2.s-1)')
        if fig >= 5:
            plt.xticks(ndf1.index, [ d.strftime('%H') for d in dates], rotation=90, fontsize=6)
            plt.xlabel('Time (h)')
        else:
            plt.xticks(ndf1.index, ['' for d in dates], rotation=60)
            #plt.xlabel(' ')
        if fig in [1]:
            plt.legend(bbox_to_anchor=(0.02, 0.95), loc=2, borderaxespad=0.)
        plt.yticks(list(range(0,1201,200)))
        fig += 1

    plt.tight_layout()
    plt.show()




def write_attribute_table(data):
    import mangoG3 as mg3
    mtg = mg3.get_G3_mtg()

    def get_leafarea(nbleaf, position):
        if nbleaf == 0: return 0
        if position == mg3.eApical:
          la  = sum(np.random.normal( 17.06 , 2.7, nbleaf) ** 2)*0.164
        else:
          la =  sum(np.random.normal( 14.87 , 2.7, nbleaf) ** 2)*0.164
        return la


    vids = []
    parents = []
    lights = []
    diameters = []
    lengths = []
    cumulativelengthprop = mg3.gu_recursive_property_from_terminal(mtg, lambda vid, childrenvalues : sum(childrenvalues)+mg3.get_gu_length(mtg, vid), lambda vid : mg3.get_gu_length(mtg, vid))
    cumulativelength = []
    nbleaves = []
    terminals = []
    depthprop = mg3.gus_depth_from_terminal(mtg,max)
    depth = []
    rootdepthprop = mg3.gus_depth_from_root(mtg)
    rootdepth = []
    nbtotalleavesprop = mg3.nbtotalleaves(mtg)
    nbtotalleaves = []
    nbdays = len(simulated_days(data))
    positions = []
    leafareas = []
    totleafareas = []
    pruned = []

    leafareaprop = { vid: get_leafarea(mg3.get_gu_nb_leaf(mtg, vid), mg3.gu_position(mtg, vid)) for vid in mg3.get_all_gus(mtg) }
    totalleafareaprop = mg3.gu_recursive_property_from_terminal(mtg, lambda vid, childrenvalues : sum(childrenvalues)+leafareaprop[vid], lambda vid : leafareaprop[vid])

    nbdescendantsprop = mg3.gu_recursive_property_from_terminal(mtg, lambda vid, childrenvalues : sum(childrenvalues)+1, lambda vid : 1)
    nbdescendants = []

    nbdaughters = []

    for vid in mg3.get_all_gus(mtg):
        vids.append(vid)
        parents.append(mg3.get_parent(mtg,vid))
        lights.append(sum(data['gu_'+str(vid)])/(24*nbdays))
        diameters.append(mg3.get_gu_diameter(mtg, vid))
        lengths.append(mg3.get_gu_length(mtg, vid))
        cumulativelength.append(cumulativelengthprop[vid])
        nbleaves.append(mg3.get_gu_nb_leaf(mtg, vid))
        terminals.append(1 if mg3.is_terminal(mtg,vid) else 0)
        depth.append(depthprop[vid])
        rootdepth.append(rootdepthprop[vid])
        nbtotalleaves.append(nbtotalleavesprop[vid])
        positions.append(mg3.gu_position(mtg, vid))
        leafareas.append(leafareaprop[vid])
        totleafareas.append(totalleafareaprop[vid])
        nbdescendants.append(nbdescendantsprop[vid])
        pruned.append(1 if mg3.is_pruned(mtg,vid) else 0)
        nbdaughters.append(mtg.nb_children(vid))

    df = DataFrame({'GU' : vids, 'mother' : parents, 'pruned' : pruned, 'light' : lights, 'diameter' : diameters, 'length' : lengths, 'cumulatedlength' : cumulativelength, 'nbleaf' : nbleaves, 'nbtotalleaf' : nbtotalleaves, 'terminal' : terminals, 'depth' : depth, 'rootdepth' : rootdepth, 'position' : positions, 'leafarea' : leafareas, 'totleafarea' : totleafareas, 'nbdescendants' : nbdescendants, 'nbdaughters' : nbdaughters })
    df = df.set_index(df['GU'])
    del df['GU']
    df.to_csv('attributeG3.csv')
    return df

import numpy as np

def plot_relationship(df, xname = 'radius', yname = 'nbleaf', xscaling = lambda v : v, yscaling = lambda v : v, xlim = None, ylim = None):
    import matplotlib.pyplot as plt
    depths = df['depth'].unique()
    depths.sort()
    depths = depths[:9]
    for d in depths:
        ndf = df[df['depth'] == d]
        plt.plot(xscaling(ndf[xname]),yscaling(ndf[yname]),'.',label='depth='+str(d))
    ndf = df[df['depth'] > depths[-1]]
    plt.plot(xscaling(ndf[xname]),yscaling(ndf[yname]),'.',label='depth>'+str(depths[-1]))
    plt.legend()
    if xscaling == np.log :
        xname = 'log('+xname+')'
    if yscaling == np.log :
        yname = 'log('+yname+')'
    plt.xlabel(xname)
    plt.ylabel(yname)
    if xlim : plt.xlim(xlim)
    if ylim : plt.ylim(ylim)
    plt.show()

def hist_relationship(df, yname = 'light', yscaling = lambda v : v, xlim = None, ylim = None):
    import matplotlib.pyplot as plt
    depths = df['depth'].unique()
    depths.sort()
    depths = depths[:9]
    nbdepths = len(depths+1)
    delta = 1./(nbdepths+1)
    nbleafvalues = df['nbleaf'].unique()
    nbleafvalues.sort()
    colors = list(plt.rcParams['axes.prop_cycle'].by_key()['color'])

    for nbl in nbleafvalues:
        ndf = df[df['nbleaf'] == nbl]
        bplots = plt.boxplot([ yscaling(ndf[ndf['depth'] == d][yname]) for d in depths], positions = [nbl+i*delta for i in range(nbdepths)], widths=delta )
        for patch, color in zip(bplots['boxes'], colors):
            patch.set_color(color)

    ndf = df[df['nbleaf'] > nbleafvalues[-1]]
    bplots = plt.boxplot([ yscaling(ndf[ndf['depth'] == d][yname]) for d in depths], positions = [nbl+i*delta for i in range(nbdepths)], widths=delta )
    for patch, color in zip(bplots['boxes'], colors):
        patch.set_color(color)

    plt.legend()
    if yscaling == np.log :
        yname = 'log('+yname+')'
    plt.xlabel('nbleaf')
    plt.ylabel(yname)
    if xlim : plt.xlim(xlim)
    else: plt.xlim((0,nbleafvalues[-1]+1))
    if ylim : plt.ylim(ylim)
    plt.show()

def plot_given_day():
    sensors = get_sensors()
    gus = associate_sensors(sensors,withleaf=False)
    data = get_simulateddata()
    monitored = select_simulateddata(data, gus)
    #plot_all_day_groups(monitored,gus=gus)
    import sys    
    dayid = 6
    if len(sys.argv) == 2:
        dayid = int(sys.argv[1])
    plot_all_day_groupmeans(monitored,dayid,gus=gus)

def plot_light_gu_groups(df):
    import openalea.plantgl.all as pgl
    from itertools import chain
    s = pgl.Scene('../data/lightedG3id.bgeom')
    #pgl.Viewer.display(s)
    s = s.todict()
    limit1 = 10
    limit2 = 50
    colorlevel = 200
    gus = df[(df.depth == 0)].index
    s0 = pgl.Scene(list(chain(*[s[gu] for gu in gus if gu in s])))
    gus = df[(df.depth > 0) & (df.depth <= 5) & (df.light <limit1) ].index
    s1 = pgl.Scene(list(chain(*[s[gu] for gu in gus if gu in s])))
    gus = df[(df.depth > 0) & (df.depth <= 5) & (df.light >limit1) & (df.light <limit2)].index
    s2 = pgl.Scene(list(chain(*[s[gu] for gu in gus if gu in s])))
    gus = df[(df.depth > 0) & (df.depth <= 5) & (df.light >limit2)].index
    s3 = pgl.Scene(list(chain(*[s[gu] for gu in gus if gu in s])))
    ns = pgl.Scene()
    for ls, m in zip([s1,s2,s3,s0],[pgl.Material((0,0,colorlevel),1),pgl.Material((0,colorlevel,0),1),pgl.Material((colorlevel,0,0),1),pgl.Material((100,100,100),1,transparency=0.8)]):
        for sh in ls:
            ns.add(pgl.Shape(pgl.TriangleSet(sh.geometry.pointList,sh.geometry.indexList), m, sh.id))
    pgl.Viewer.display(ns)


if __name__ == '__main__':
    plot_given_day()
    #data = get_simulateddata()
    #df = write_attribute_table(data)
    #plot_light_gu_groups(df)
