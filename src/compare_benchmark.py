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



def plot_comparison(datas, comparisons = [(0,1),(0,2),(1,2)]):
    import matplotlib.pyplot as plt
    labels = ['Mac','Linux','Window']
    for ref,tgt in comparisons:

        plt.figure(figsize=(10,8), dpi=100)
        ax = plt.subplot(221)
        for d in reversed(datas):
            plt.plot(d[ref]['10H-DirectRc'],d[tgt]['10H-DirectRc'],'.',label=str(len(d[ref]['10H-DirectRc'])-1)+' leaves')
        plt.title('Comparison of simulated light energy')
        plt.xlabel('Rc : '+labels[ref])
        plt.ylabel('Rc : '+labels[tgt])
        plt.legend()
        ax = plt.subplot(222)
        for d in reversed(datas):
            plt.plot(d[ref]['10H-DirectRc'],d[ref]['10H-DirectRc']-d[tgt]['10H-DirectRc'],'.')
        plt.title('Difference of simulated light energy')
        plt.xlabel('Rc : '+labels[ref])
        plt.ylabel('Rc : '+labels[ref]+' - '+labels[tgt])
        ax.yaxis.set_label_position("right")
        ax.yaxis.tick_right()
        ax = plt.subplot(223)
        for d in reversed(datas):
            plt.plot(d[ref]['10H-DirectRs'],d[tgt]['10H-DirectRs'],'.')
        plt.xlabel('Rs : '+labels[ref])
        plt.ylabel('Rs : '+labels[tgt])
        ax = plt.subplot(224)
        for d in reversed(datas):
            plt.plot(d[ref]['10H-DirectRs'],d[ref]['10H-DirectRs']-d[tgt]['10H-DirectRs'],'.')
        plt.xlabel('Rs : '+labels[ref])
        plt.ylabel('Rs : '+labels[ref]+' - '+labels[tgt])
        ax.yaxis.set_label_position("right")
        ax.yaxis.tick_right()
        plt.show()

if __name__ == '__main__':
    datas = get_datas()
    plot_comparison(datas)