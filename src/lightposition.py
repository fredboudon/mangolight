import openalea.plantgl.all as pgl
from openalea.plantgl.all import *
from math import radians


localisation={'latitude':-21.32, 'longitude':55.5, 'timezone': 'Indian/Reunion'}

mango = Scene('../data/consolidated_mango3d-wd.bgeom')
mango.add(Shape(Translated(500,0,0,Box(20)), Material((0,0,0))))
mango.add(Shape(pgl.Text('North', (500,0,20), fontstyle=Font(size=20)), Material((255,0,0))))
axis,north = (0,0,1), -(90-53)
mango = Scene([Shape(AxisRotated(axis,radians(-north),sh.geometry),sh.appearance,sh.id,sh.parentId) for sh in mango])
xcenter = -21
xsize = 250+7
xmin, xmax = -xcenter-xsize, -xcenter+xsize
ycenter = -40
ymin, ymax = -ycenter-300,-ycenter+300
zsoil = 0
p = pgl.QuadSet([(xmin,ymin,zsoil),(xmax,ymin,zsoil),(xmax,ymax,zsoil),(xmin,ymax,zsoil)],[range(4)])
mango.add(p)


def get_sun_light_direction(day, hour):
    import pandas
    from alinea.astk.sun_and_sky import sun_sources
    from alinea.caribu.light import light_sources
    daydate = pandas.Timestamp(day+' '+str(hour).zfill(2), tz=localisation['timezone'])
    el, az, intensity = sun_sources(irradiance=1, dates=daydate, **localisation)
    res = light_sources(el, az, intensity, orientation = north)
    return -Vector3(*res[0][1])

def sun_positions_display(date = '2017-08-26'):
    bbx = pgl.BoundingBox(mango)
    dist = 1.15*pgl.norm(bbx.getSize())

    scene = Scene()
    for hour in range(7,19):
        pgldir = get_sun_light_direction(date, hour)
        mat = pgl.Material((50,50,0)) if hour != 12 else pgl.Material((200,200,0))
        scene.add(pgl.Shape(pgl.Translated(pgldir*dist,pgl.Sphere(dist/50)), mat))
    return scene

Viewer.display(mango+ sun_positions_display())
Viewer.camera.setOrthographic()
Viewer.camera.set((4.5,67,1000), -180-north, -90)
