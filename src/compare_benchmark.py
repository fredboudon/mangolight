import pandas
import openalea.plantgl.all as pgl
from alinea.astk.sun_and_sky import sun_sky_sources, sun_sources, sky_discretisation
from math import radians
import numpy
import os

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

def get_datas(dirs = ['benchmark-darwin','benchmark-linux']):
    import glob
    fnames = [set(map(os.path.basename,glob.glob(os.path.join(d,'result_10H_*.csv')))) for d in dirs]
    cfnames = fnames[0]
    for f in fnames[1:]:
        cfnames.intersection_update(f)
    cfnames = list(sorted(list(cfnames)))
    datas = [ [get_data(os.path.join(d,fn)) for d in dirs] for fn in cfnames]
    return datas



def plot_comparison(datas):
    import matplotlib.pyplot as plt
    for d in reversed(datas):
        plt.plot(d[0]['10H-DirectRc'],d[1]['10H-DirectRc'],'.')
    plt.show()
    for d in reversed(datas):
        plt.plot(d[0]['10H-DirectRc'],d[0]['10H-DirectRc']-d[1]['10H-DirectRc'],'.')
    plt.show()
    for d in reversed(datas):
        plt.plot(d[0]['10H-DirectRs'],d[1]['10H-DirectRs'],'.')
    plt.show()
    for d in reversed(datas):
        plt.plot(d[0]['10H-DirectRs'],d[0]['10H-DirectRs']-d[1]['10H-DirectRs'],'.')
    plt.show()

if __name__ == '__main__':
    datas = get_datas()
    plot_comparison(datas)