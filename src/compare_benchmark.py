import pandas
import openalea.plantgl.all as pgl
from alinea.astk.sun_and_sky import sun_sky_sources, sun_sources, sky_discretisation
from math import radians
import numpy
import os

def retrieve_id(fname, pattern) : 
    if not pattern in fname : return 60
    return  int(fname.split(pattern)[1].split('.')[0])

def get_data(fname = 'results-rcrs-1000/result_2017-08-26.csv'):
    data = pandas.read_csv(fname)
    #data = pandas.read_csv('results_2017-08-26-r60.csv')
    data.drop(columns=['Unnamed: 0'], inplace=True)
    data.set_index('Entity', inplace=True)

    data.rename(columns={"DiffusRc-"+str(i): "DiffusRc-0"+str(i) for i in range(10)}, inplace = True)
    data.rename(columns={"DiffusRs-"+str(i): "DiffusRs-0"+str(i) for i in range(10)}, inplace = True)

    for i in range(10):
        if str(i)+'H-DirectRc' in data.columns.values:
            data.rename(columns={str(i)+'H-DirectRc': '0'+str(i)+'H-DirectRc' for i in range(10)}, inplace = True)
        if str(i)+'H-DirectRs' in data.columns.values:
            data.rename(columns={str(i)+'H-DirectRs': '0'+str(i)+'H-DirectRs' for i in range(10)}, inplace = True)
    return data 

def get_ds_datas(dir = 'benchmark-linux'):
    import glob
    pattern = 'result_10H_29682_ds'
    fnames = glob.glob(os.path.join(dir,pattern+'*.csv'))
    fnames.sort()
    fnames.append(os.path.join(dir,'result_10H_29682.csv'))
    datas = ([retrieve_id(fn,pattern) for fn in fnames],[ get_data(fn) for fn in fnames])
    return datas

def get_perf_datas(dir = 'benchmark-linux'):
    import glob
    pattern = 'performance_10H_29682_ds'
    fnames = glob.glob(os.path.join(dir,pattern+'*.txt'))
    fnames.sort()
    fnames.append(os.path.join(dir,'performance_10H_29682.txt'))
    def get_time(fn):
        with open(fn) as stream:
            return float(stream.read().split('-->')[1].strip())
    datas = dict(zip([retrieve_id(fn,pattern) for fn in fnames],[ get_time(fn) for fn in fnames]))
    return datas


def get_datas(direct = True, dirs = ['benchmark-darwin','benchmark-linux','benchmark-win32']):
    import glob
    pattern = 'result_direct_10H' if direct else 'result_10H'
    fnames = [set(map(os.path.basename,glob.glob(os.path.join(d,pattern+'_*.csv')))) for d in dirs]
    cfnames = fnames[0]
    for f in fnames[1:]:
        cfnames.intersection_update(f)
    cfnames = list(sorted(list(cfnames)))
    datas = [ [get_data(os.path.join(d,fn)) for d in dirs] for fn in cfnames]
    return datas



def plot_ds_comparison(ds, data, drange = None, performances = None):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(15,8), dpi=100)
    ax = plt.subplot(231)
    wavelength = '10H-DirectRc'
    ref = data[-1][wavelength]
    if drange is None:
        drange = slice(0,-1)
    for i,d in zip(ds[drange],data[drange]):
        plt.plot(d[wavelength],ref,'.',label='d_sphere '+str(i))
    plt.title('Comparison of simulated light energy')
    plt.ylabel('Rc')
    plt.xlabel('Rc d_sphere 60')
    plt.legend()

    ax = plt.subplot(232)
    wavelength = '10H-DirectRs'
    ref = data[-1][wavelength]
    for i,d in zip(ds[drange],data[drange]):
        plt.plot(d[wavelength],ref,'.',label='d_sphere '+str(i))
    plt.title('Comparison of simulated light energy')
    plt.ylabel('Rs')
    plt.xlabel('Rs d_sphere 60')
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    plt.legend()


    ax = plt.subplot(234)
    wavelength = '10H-DirectRc'
    ref = data[-1][wavelength]
    plt.boxplot([d[wavelength]-ref  for d in data[drange]], labels=ds[drange])
    plt.ylabel('Rc difference')
    #plt.legend()

    ax = plt.subplot(235)
    wavelength = '10H-DirectRs'
    ref = data[-1][wavelength]
    plt.boxplot([d[wavelength]-ref  for d in data[drange]], labels=ds[drange])
    plt.ylabel('Rs difference')
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    #plt.legend()

    ax = plt.subplot(233)
    plt.plot(list(performances.keys()), list(performances.values()))
    plt.ylabel('Computation time')
    plt.xlabel('d_sphere')
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()

    # ax = plt.subplot(222)
    # for d in reversed(datas):
    #     plt.plot(d[ref]['10H-DirectRc'],d[ref]['10H-DirectRc']-d[tgt]['10H-DirectRc'],'.')
    # plt.title('Difference of simulated light energy')
    # plt.xlabel('Rc : '+labels[ref])
    # plt.ylabel('Rc : '+labels[ref]+' - '+labels[tgt])
    # ax.yaxis.set_label_position("right")
    # ax.yaxis.tick_right()
    # ax = plt.subplot(223)
    # for d in reversed(datas):
    #     plt.plot(d[ref]['10H-DirectRs'],d[tgt]['10H-DirectRs'],'.')
    # plt.xlabel('Rs : '+labels[ref])
    # plt.ylabel('Rs : '+labels[tgt])
    # ax = plt.subplot(224)
    # for d in reversed(datas):
    #     plt.plot(d[ref]['10H-DirectRs'],d[ref]['10H-DirectRs']-d[tgt]['10H-DirectRs'],'.')
    # plt.xlabel('Rs : '+labels[ref])
    # plt.ylabel('Rs : '+labels[ref]+' - '+labels[tgt])
    plt.show()


if __name__ == '__main__':
    #plot_comparison(get_datas())
    plot_ds_comparison(*get_ds_datas(),slice(0,-1),get_perf_datas()) 