import openalea.plantgl.all as pgl
from openalea.plantgl.all import *
import openalea.plantgl.scenegraph.colormap as cm
import pandas as pd
import numpy as np


idshift = 1000
mango = pgl.Scene('../../data/consolidated_mango3d-wd.bgeom')
mango = pgl.Scene([sh for sh in mango if sh.id % idshift > 0])

def apply_cmap_from_values(values, cmap = 'jet'):
    pmap = cm.PglMaterialMap(min(values),max(values), cmap)
    nsc = pgl.Scene()
    def toint(v):
        try:
            return int(v)
        except:
            return v
    values = dict([(toint(k),v) for k,v in values.items()])
    for sh in mango:
        nsc.add(pgl.Shape(sh.geometry,pmap(values[sh.id]),sh.id))
    nsc += pmap.pglrepr()
    return nsc

def read_data(fname):
    data = pd.read_csv(fname, index_col = 0)
    if 'Entity' in data.columns:
        data = data.set_index('Entity') 
    return data

def scene_from_data(fname_or_data, colname):
    if isinstance(fname_or_data, str):
        data = read_data(fname_or_data)
    else:
        data = fname_or_data
    return apply_cmap_from_values(data[colname])

def display_data(fname, colname):
    scene = scene_from_data(fname, colname)
    pgl.Viewer.display(scene)
    if 'XX' in data:
        zextent = data['ZZ'].max() - data['ZZ'].min()
        pgl.Viewer.add(Shape(Translated(data['XX'].mean(),data['YY'].mean(),data['ZZ'].mean()-zextent/2,Sphere(5)),Material((255,0,0))))


if __name__ == '__main__':
    import sys
    fname = "leafinfo.csv"
    colname = 'HorizontalDepth'
    if len(sys.argv) >= 3:
        fname = sys.argv[1]
        colname = sys.argv[2]
    else:
        colname = sys.argv[1]
    display_data(fname, colname)


