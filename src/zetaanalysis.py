import pandas
import openalea.plantgl.all as pgl
from alinea.astk.sun_and_sky import sun_sky_sources, sun_sources, sky_discretisation
from math import radians

#data = pandas.read_csv('results-rcrs2/result_2017-08-26.csv')
date = '2017-08-26'
data = pandas.read_csv('results_2017-08-26-r60.csv')
data.drop(columns=['Unnamed: 0'], inplace=True)
data.set_index('Entity', inplace=True)

# Y represent the North

def generate_rcrs(data, hour=12, rcdirectei = 1, rsdirectei = 1, rcdiffuseei = 1, rsdiffuseei = 1):

    diffusrcname = [name for name in data.columns.values if 'DiffusRc' in name]
    diffusrsname = [name for name in data.columns.values if 'DiffusRc' in name]
    directrcname = [name for name in data.columns.values if 'DirectRc' in name]
    directrsname = [name for name in data.columns.values if 'DirectRs' in name]

    diffusrc = sum([data[n] for n in diffusrcname])
    diffusrc *= rcdiffuseei

    diffusrs = sum([data[n] for n in diffusrsname])
    diffusrs *= rsdiffuseei

    directrc = data[str(hour)+'H-DirectRc']*rcdirectei
    directrs = data[str(hour)+'H-DirectRs']*rsdirectei

    rc = diffusrc+directrc
    rs = diffusrs+directrs

    return rc,rs

rc,rs = generate_rcrs(data)

mango = pgl.Scene('../data/consolidated_mango3d-wd.bgeom')
localisation={'latitude':-21.32, 'longitude':55.5, 'timezone': 'Indian/Reunion'}

def get_sky_light_direction(i):
    source_elevation, source_azimuth, source_fraction = sky_discretisation()
    return source_elevation[i], source_azimuth[i]

def get_sun_light_direction(day, hour):
    import datetime
    #day = datetime.strptime(,'%Y-%m-%d %H')
    daydate = pandas.Timestamp(day+' '+str(hour).zfill(2), tz=localisation['timezone'])
    #daydate = pandas.Timestamp(day, tz=localisation['timezone'])
    el, az, intensity = sun_sources(irradiance=1, dates=daydate, **localisation)
    return el[0],az[0]


def plot_value(scene, values, pattern = None, display = True):
    if type(values) is str:
        vname = values
        #values = data[values]
        print('incident',data[values]['incident'])
        values = data[values]/data[values]['incident']
    else:
        vname = None
    bbx = None
    sdict = scene.todict()
    maxvalue = values.max()
    minvalue = values.min()
    print(vname, minvalue, maxvalue)
    mmap = pgl.PglMaterialMap(minvalue, maxvalue)
    scene = pgl.Scene([pgl.Shape(sh.geometry, mmap(v), int(sid)) for sid, v in values.items() if sid !='incident' for sh in sdict[int(sid)] ])
    scene += mmap.pglrepr()
    if pattern:
        bbx = pgl.BoundingBox(scene)
        zmin, zmax = bbx.lowerLeftCorner.z,bbx.upperRightCorner.z
        xmin,ymin,xmax,ymax = pattern
        p = pgl.QuadSet([(xmin,ymin,zmin),(xmax,ymin,zmin),(xmin,ymax,zmin),(xmax,ymax,zmin),(xmin,ymin,zmax),(xmax,ymin,zmax),(xmin,ymax,zmax),(xmax,ymax,zmax)],[[0,1,5,4],[0,2,6,4],[1,3,7,5],[2,3,7,6]])
        scene.add(p)
    if not vname is None:
        if bbx is None:
            bbx = pgl.BoundingBox(scene)
        if 'Diffus' in vname:
            dirid = int(vname[9:])
            source_dir = get_sky_light_direction(dirid)
        else:
            dirid = int(vname.split('H')[0])
            print(dirid)
            source_dir = get_sun_light_direction(date, dirid)
        el, az = source_dir
        print(az, el)
        dist = 1.5*pgl.norm(bbx.getSize())
        pgldir = pgl.Vector3.Spherical(dist,radians(180+az),radians(90-el))
        scene.add(pgl.Translated(pgldir,pgl.Sphere(dist/100)))
    if display:
        pgl.Viewer.display(scene)
    return scene

#plot_value(mango,rc)


#import matplotlib.pyplot as plt
#plt.plot(rc/rs,'.')
#plt.ylim((-10,40))
#plt.show()

def plot_all():
    names = sorted(data.columns.values)
    prevc = names[0]
    scene = plot_value(mango, prevc, display=False)
    for c in names[1:]:
        if not 'Direct' in c and not 'DiffusRc' in c:
            pgl.Viewer.display(scene)
            scene = plot_value(mango, c, display=False)
            res = pgl.Viewer.dialog.question(prevc,prevc)
            prevc = c
            if not res:
                break

if __name__ == '__main__':
    plot_all()