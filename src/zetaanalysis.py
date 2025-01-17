import pandas
import openalea.plantgl.all as pgl
from alinea.astk.sun_and_sky import sun_sky_sources, sun_sources, sky_discretisation
from math import radians
import numpy
import os


date = '2017-08-26'
localisation={'latitude':-21.32, 'longitude':55.5, 'timezone': 'Indian/Reunion'}
mango = pgl.Scene('../data/consolidated_mango3d-wd.bgeom')



def get_data(fname = 'results-rcrs-mac/result_2017-08-26.csv'):
    data = pandas.read_csv(fname)
    #data = pandas.read_csv('results_2017-08-26-r60.csv')
    data.drop(columns=['Unnamed: 0'], inplace=True)
    data.set_index('Entity', inplace=True)

    return data        

# -X represent the North

ratiovalues = [0.0404, 0.0348, 0.0248, 0.0173]
meanratio = numpy.mean(ratiovalues)
ratiovalues = [v/meanratio for v in  ratiovalues]
rcdirectei, rsdirectei, rcdiffuseei, rsdiffuseei = ratiovalues

def generate_rcrs(data, hour=12, rcdirectei = rcdirectei, rsdirectei = rsdirectei, rcdiffuseei = rcdiffuseei, rsdiffuseei = rsdiffuseei):

    diffusrcname = [name for name in data.columns.values if 'DiffusRc' in name]
    diffusrsname = [name for name in data.columns.values if 'DiffusRc' in name]
    directrcname = [name for name in data.columns.values if 'DirectRc' in name]
    directrsname = [name for name in data.columns.values if 'DirectRs' in name]

    if len(diffusrcname) > 0:
        diffusrc = sum([data[n] for n in diffusrcname])
        diffusrc *= rcdiffuseei

    if len(diffusrsname) > 0:
        diffusrs = sum([data[n] for n in diffusrsname])
        diffusrs *= rsdiffuseei

    if len(directrcname) > 0 :
        directrc = data[str(hour).zfill(2)+'H-DirectRc']*rcdirectei
        directrs = data[str(hour).zfill(2)+'H-DirectRs']*rsdirectei
        if len(diffusrcname) == 0:
            return directrc,directrs
    else:
        return diffusrc, diffusrs

    rc = diffusrc+directrc
    rs = diffusrs+directrs

    return rc,rs

def show_mar_relation( data, hour=None):
    import matplotlib.pyplot as plt
    if hour is None:
        for h in range(17,8,-1):
            rc,rs = generate_rcrs(data,h)
            plt.plot(rc,rc/rs,'.', label=str(h).zfill(2)+'H')
    else:
        rc,rs = generate_rcrs(data,hour)
        plt.plot(rc,rc/rs,'.', label=str(hour).zfill(2)+'H')
    #plt.ylim((-10,40))
    plt.legend()
    plt.show()


#rc,rs = generate_rcrs(data)

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


def plot_value(scene, values, data = None, pattern = None, display = True, minvalue = None, maxvalue = None):
    if type(values) is str:
        vname = values
        #values = data[values]
        print('incident',data[values]['incident'])
        values = data[values]/data[values]['incident']
    else:
        vname = None
    bbx = None
    sdict = scene.todict()
    if maxvalue is None:
        maxvalue = values.max()
    if minvalue is None:
        minvalue = values.min()
    print(vname, minvalue, maxvalue)
    mmap = pgl.PglMaterialMap(minvalue, maxvalue)
    scene = pgl.Scene([pgl.Shape(sh.geometry, mmap(v), int(sid)) for sid, v in values.items() if sid != 'incident' and int(sid) in sdict and minvalue <= v <= maxvalue  for sh in sdict[int(sid)] ])
    #scene += mmap.pglrepr()
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
        dist = 1.15*pgl.norm(bbx.getSize())
        azel2pos = lambda az,el : pgl.Vector3.Spherical(dist,radians(-az),radians(90-el))
        pgldir = azel2pos(az,el)
        scene.add(pgl.Translated(pgldir,pgl.Sphere(dist/50)))
        if 'Direct' in vname:
            for hour in range(8,19):
                el, az = get_sun_light_direction(date, hour)
                pgldir = azel2pos(az,el)
                scene.add(pgl.Shape(pgl.Translated(pgldir,pgl.Sphere(dist/80)), pgl.Material((0,0,0))))
        else:
            for dirid in range(46):
                el, az = get_sky_light_direction(dirid)
                pgldir = azel2pos(az,el)
                scene.add(pgl.Shape(pgl.Translated(pgldir,pgl.Sphere(dist/80)), pgl.Material((0,0,0))))

    if display:
        pgl.Viewer.display(scene)
    return scene



#


def compare_mar_relation( rc, rs, rc2, rs2):
    import matplotlib.pyplot as plt
    plt.plot(rc,rc/rs,'.')
    plt.plot(rc2,rc2/rs2,'.')
    #plt.ylim((-10,40))
    plt.show()


def compute_view(scene : pgl.Scene, imgsize : tuple = (800,800), bbx : pgl.BoundingBox = None, azimuth : float = 0, elevation : float = 0 ) -> numpy.ndarray:
    """
    Compute an orthographic view of a scene.
    :param scene: The scene to render
    :param imgsize: The size of the image
    :param azimuth: The azimuth (in degrees) of view to render
    :param elevation: The elevation (in degrees) of view to render
    :return: The resulting image
    """
    from math import radians
    z = pgl.ZBufferEngine(imgsize[0],imgsize[1], (255,255,255), pgl.eColorBased)
    
    if bbx is None:    
        bbx = pgl.BoundingBox(scene)
    else:
        bbx = pgl.BoundingBox(bbx.lowerLeftCorner, bbx.upperRightCorner)
    center = bbx.getCenter()
    bbx.translate(-center)

    v  = pgl.Vector3(pgl.Vector3.Spherical(-1, radians(azimuth), radians(90-elevation)))
    up  = pgl.Vector3(pgl.Vector3.Spherical(-1, radians(azimuth), radians(180-elevation)))
    right = pgl.cross(up,v)

    frame = [v, right, up]

    m = pgl.Matrix4(pgl.Matrix3(*frame))

    bbx.transform(m.inverse())

    xmin = bbx.lowerLeftCorner.x
    xmax = bbx.upperRightCorner.x
    size = bbx.getSize()
    msize = max(size[1],size[2])*1.05
    dist = 1

    v *= (size[0]+dist)

    z.setOrthographicCamera(-msize, msize, -msize, msize, dist, dist + xmax - xmin)


    position = center+v
    z.lookAt(position,center,up)
    z.setLight(position, (255,255,255))

    z.process(scene)

    i = z.getImage()
    return i

def generate_all(outputdir = 'images'):
    names = sorted(data.columns.values)
    prevc = names[0]
    bbx = pgl.BoundingBox(mango)
    bbx = pgl.BoundingBox(bbx.getCenter()-1.3*bbx.getSize(),bbx.getCenter()+1.3*bbx.getSize())
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    for c in names[:2]:
        #if not 'Direct' in c and not 'DiffusRc' in c:
            scene = plot_value(mango, c, display=False)
            #pgl.Viewer.display(scene)
            i = compute_view(scene, bbx=bbx, elevation=80)
            i.save(os.path.join(outputdir,'view_'+c+'.png'))
            #res = pgl.Viewer.dialog.question(prevc,prevc)
            #prevc = c
            #if not res:
            #    break

def plot_all(mango, data):
    from random import sample
    #mango = pgl.Scene(sample([sh for sh in mango],5000))
    names = sorted(data.columns.values)
    prevc = names[0]
    scene = plot_value(mango, prevc, data=data, display=False, minvalue = 0.5)
    for c in names[1:]:
        #if not 'Direct' in c and not 'DiffusRc' in c:
            pgl.Viewer.display(scene)
            scene = plot_value(mango, c, data=data, display=False, minvalue = 0.5)
            res = pgl.Viewer.dialog.question(prevc,prevc)
            prevc = c
            if not res:
                break

def save_all_image(mango, data, outdir = 'images-res'):
    from random import sample
    #mango = pgl.Scene(sample([sh for sh in mango],5000))
    names = sorted(data.columns.values)
    firstc = names[0]
    scene = plot_value(mango, firstc, data=data, display=False)
    pgl.Viewer.display(scene)
    res = pgl.Viewer.dialog.question("Setup","Please fix view and display mode.")
    pgl.Viewer.saveSnapshot(os.path.join(outdir,firstc+'.png'))
    if not res:
        return
    for c in names[1:]:
            scene = plot_value(mango, c, data=data, display=False)
            pgl.Viewer.display(scene)
            pgl.Viewer.saveSnapshot(os.path.join(outdir,c+'.png'),'PNG')

def plot_benchmark():
    import glob
    prefix = 'results-rcrs-testlen60/scene_'
    fnames = glob.glob(prefix+'*.bgeom')
    #fnames = [prefix+'10000.bgeom']
    for fname in sorted(fnames):
        sc = pgl.Scene(fname)
        idn = fname[len(prefix):-6]
        data = pandas.read_csv('results-rcrs-testlen60/result_10H_%s.csv' % idn)
        data.drop(columns=['Unnamed: 0'], inplace=True)
        data.set_index('Entity', inplace=True)
        plot_value(sc,'10H-DirectRc',data=data)
        res = pgl.Viewer.dialog.question('Rc '+idn,'Rc '+idn)
        if not res:
            break
        plot_value(sc,'10H-DirectRs',data=data)
        res = pgl.Viewer.dialog.question('Rs '+idn,'Rs '+idn)
        if not res:
            break

def plot_benchmark():
    import glob
    dirname = 'benchmark-linux'
    dirname2 = 'benchmark-darwin'
    prefix = os.path.join('benchmark-all','scene_')
    #fnames = glob.glob(prefix+'*.bgeom')
    #fnames = [prefix+'29682.bgeom']
    fnames = [prefix+'10000.bgeom']
    for fname in sorted(fnames):
        sc = pgl.Scene(fname)
        idn = fname[len(prefix):-6]
        data = pandas.read_csv(os.path.join(dirname,'result_10H_%s.csv' % idn))
        data.drop(columns=['Unnamed: 0'], inplace=True)
        data.set_index('Entity', inplace=True)
        data2 = pandas.read_csv(os.path.join(dirname2,'result_10H_%s.csv' % idn))
        data2.drop(columns=['Unnamed: 0'], inplace=True)
        data2.set_index('Entity', inplace=True)
        # plot_value(sc,'10H-DirectRc',data=data)
        # res = pgl.Viewer.dialog.question('Rc '+idn,'Rc '+idn)
        # if not res:
        #     break
        # plot_value(sc,'10H-DirectRs',data=data)
        # res = pgl.Viewer.dialog.question('Rs '+idn,'Rs '+idn)
        # if not res:
        #     break
        plot_value(sc,data2['10H-DirectRc']-data['10H-DirectRc'])
        res = pgl.Viewer.dialog.question('Rc '+idn,'Rc '+idn)
        if not res:
            break

if __name__ == '__main__':
    import sys
    #plot_all(mango, get_data())
    #save_all_image(mango, get_data())
    #generate_all('images-1000')
    #plot_benchmark()
    #rc,rs = generate_rcrs(get_data('results-rcrs-testlen/result_10H_29682.csv'),10)
    #show_mar_relation(rc,rs)
    #rc2,rs2 = generate_rcrs(get_data('results-rcrs-testlen60/result_10H_29682.csv'),10)
    #compare_mar_relation(rc,rs,rc2,rs2)    
    show_mar_relation(get_data('results-rcrs-60-linux/result_2017-08-26.csv'),sys.argv[1] if len(sys.argv)>1 else None)