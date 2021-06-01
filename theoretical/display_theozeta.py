import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle
from matplotlib import cm
import numpy as np

cmap = cm.get_cmap('summer')


def color_scene(scene, values, cmap = 'jet'):
    from openalea.plantgl.scenegraph.colormap import PglMaterialMap
    from openalea.plantgl.scenegraph import Scene, Shape, TriangleSet
    cmap = PglMaterialMap(0,max(1,max(values.values())), cmap)
    nsc = Scene()
    for sh in scene:
        geom = sh.geometry
        nsc.add(Shape(TriangleSet(geom.pointList,geom.indexList), cmap(values[sh.id]),sh.id))
    return nsc

def plot_surface(ax, sc, zetas):
    from openalea.plantgl.scenegraph import BoundingBox
    norm = mpl.colors.Normalize(vmin=0,vmax=max(1,max(zetas.values())))
    cmap = cm.get_cmap('jet')
    bbx = BoundingBox(sc)
    center = bbx.getCenter()
    dmax = max(bbx.getSize())
    for sh in sc:
        pointList = np.array(sh.geometry.pointList)
        #c = sh.appearance.ambient
        #color = (c.clampedRed(), c.clampedGreen(), c.clampedBlue(), 1-sh.appearance.transparency)
        color = cmap(norm(zetas[sh.id]))
        ax.plot_trisurf(pointList[:,0],pointList[:,1],pointList[:,2], triangles = np.array(sh.geometry.indexList), color=color)
    ax.set_xlim(center.x-dmax,center.x+dmax)
    ax.set_ylim(center.y-dmax,center.y+dmax)
    ax.set_zlim(center.z-dmax,center.z+dmax)

def plot_disks(values, ax, figcolorbar = None):
    m = len(values)
    norm = mpl.colors.Normalize(vmin=0,vmax=max(1,max(values)))
    for i, v in enumerate(values):
        color = cmap(norm(v)) if not np.isnan(v) else 'black'
        r = 1-(i/m)
        circle = plt.Circle((0, 0), r, facecolor=color , edgecolor='black')
        ax.add_patch(circle)
    ax.plot([0,0],[-2,-1.1],c='brown',linewidth=40)
    ax.set_xlim(-1.2,1.2)
    ax.set_ylim(-1.2,1.2)
    if figcolorbar:
        figcolorbar.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap),ax=ax)


def plot_zeta_analysis(par, r, fr, par_sky = None, r_sky = None, fr_sky = None):
    ranks = range(1001,(len(par)+1)*1000,1000)
    ranks = range(len(par))
    zetas = r/fr
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    (ax1, ax2, ax3), (ax4, ax5, ax6) = axes
    ax1.plot(par,zetas,linestyle='--', marker='o', label='zeta', color='blue')
    ax1.set_xlim(0,max(1,max(par)))
    ax1.set_ylim(0,max(1,max(zetas)))
    ax1.legend()
    ax2.plot(ranks,r,linestyle='--', marker='o', label='R_tr', color='red')
    if not r_sky:
        r_sky = [1 - sum(r)]
    ax2.plot([0],r_sky, marker='o', color='red')
    ax2.plot(ranks,fr,linestyle='--', marker='o', label='FR_tr', color='purple')
    if not fr_sky:
        fr_sky = [1 - sum(fr)]
    ax2.plot([0],fr_sky, marker='o', color='purple')
    ax2.plot(ranks,par,linestyle='--', marker='o', label='PAR_tr', color='green')
    if not par_sky:
        par_sky = [1 - sum(par)]
    ax2.plot([0],par_sky, marker='o', color='green')
    #ax2.plot(ranks,zetas,linestyle='--', marker='o', label='Zeta', color='blue')
    ax2.legend()
    #ax2.set_xlim(0,max(1,max(par)))
    ax2.set_ylim(0,max(1,max(par), max(r),max(fr)))#,max(zetas)))
    m = plot_disks(zetas, ax3, fig)
    ax3.set_title('Zeta')
    plot_disks(par, ax4, fig)
    ax4.set_title('PAR')
    plot_disks(r, ax5, fig)
    ax5.set_title('R')
    plot_disks(fr, ax6, fig)
    ax6.set_title('FR')
    #ax4.plot(np.full((m), 0.5),np.full((m), 0.5), marker='o', markersize=np.arange(1,m+1,1))
    plt.show()

layershift = 1000000


def sort_values(values):
    msphere = max([(tid // layershift) for tid in values.keys()])
    svalues = [[] for i in range(0,msphere)]
    for tid, v in values.items():
        svalues[(tid // layershift)-1].append(v)
    return svalues


def compute_angles(sc, polar = False):
    from openalea.plantgl.all import Vector3
    from math import degrees, pi
    svalues = {}
    for sh in sc:
        pcenter = sh.geometry.pointList.getCenter()
        v = Vector3.Spherical(pcenter)
        if not polar:
            svalues[sh.id] = degrees(v.phi)
        else:
            side =  (0 if -pi/2 <= v.theta <= pi/2 else 1)
            svalues[sh.id] = 2*pi - v.phi if side else v.phi
    return svalues

#jet = cm.get_cmap('jet')




from fitting import schnute, fit_schnute

def plot_zeta_analysis_per_triangles(par, r, fr, sc):
    #ranks = range(1,len(par)+1)
    from math import pi
    polar = True
    angles = sort_values(compute_angles(sc, polar))
    #norm = mpl.colors.Normalize(vmin=0,vmax=180)

    sr = sort_values(r)
    sfr = sort_values(fr)
    spar = sort_values(par)
    zetas = [np.array(ri)/np.array(fri) for ri,fri in zip(sr,sfr)]
    #fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    #(ax1, ax2, ax3), (ax4, ax5, ax6) = axes
    fig = plt.figure(figsize=(10,10))
    ax1 = plt.subplot(331)
    for i, (zetai, pari) in enumerate(zip(zetas,spar)):
        ax1.scatter(pari,zetai,label = 'layer '+str(i+1))

    try:
        popt, pcov = fit_schnute(np.concatenate(spar), np.concatenate(zetas))
        #print(popt)
        x = np.linspace(0, 1, 20)
        y = schnute(x,*popt)
        ax1.plot(x,y,'r',label='a:%.2f b:%.2f\nc:%.2f d:%.2f' % (tuple(popt)))
    except RuntimeError as re:
        pass

    ax1.set_xlim(0,max(1,max(par.values())))
    ax1.set_ylim(0,max(1,max([max(zetai) if len(zetai) > 0 else 0 for zetai in zetas])))
    ax1.set_ylabel('Zeta')
    ax1.set_xlabel('PAR')
    ax1.legend() #prop={'size': 8})
    ax1.set_title('Zeta')

    ax2 = plt.subplot(332)
    for i, (zetai, pari, anglesi) in enumerate(zip(zetas,spar,angles)):
        colvalue = 180-np.array(anglesi) if not polar else abs(np.array(anglesi)-pi)
        vmaxp = 180 if not polar else pi
        ax2.scatter(pari,zetai, c=colvalue, cmap='jet', vmin=0, vmax=vmaxp,label = 'angle') #, marker= MarkerStyle.filled_markers[i])
        
    ax2.set_xlim(0,max(1,max(par.values())))
    ax2.set_ylim(0,max(1,max([max(zetai) if len(zetai) > 0 else 0 for zetai in zetas])))
    #ax2.legend()
    ax2.set_ylabel('Zeta')
    ax2.set_xlabel('PAR')
    ax2.set_title('Zeta')
    ax2.legend()

    def plot_angle_distrib(ax, values, name):
        #ax4.set_title('PAR')
        for i, (valuei, anglesi) in enumerate(zip(values,angles)):
            vmax = max(1,max(valuei))
            ax.scatter(anglesi,valuei,label = 'layer '+str(i+1), c=valuei, cmap='jet', vmin=0, vmax=vmax) #, marker= MarkerStyle.filled_markers[i])
        if not polar:       
            ax.set_xlim(0,180)
        ax.set_ylim(0,max(1,max([max(valuei) if len(valuei) > 0 else 0 for valuei in values])))
        ax.set_ylabel(name)
        ax.set_xlabel('Elevation')
        ax.yaxis.labelpad = 25
        ax.set_theta_zero_location("N")
        #ax.legend()

    if polar:
        kwds = {'projection':'polar' }
    else:
        kwds = {}
    ax3 = plt.subplot(333, **kwds)
    plot_angle_distrib(ax3, zetas, 'Zeta')
    ax4 = plt.subplot(334, **kwds)
    plot_angle_distrib(ax4, spar, 'PAR')
    ax5 = plt.subplot(335, **kwds)
    plot_angle_distrib(ax5, sr, 'Red')
    ax6 = plt.subplot(336, **kwds)
    plot_angle_distrib(ax6, sfr, 'Far Red')
    ax7 = plt.subplot(3,1,3, projection='3d')
    plot_surface(ax7,sc, dict([(i,ri/fr[i]) for i, ri in r.items()]))

    fig.tight_layout()
    #plt.show()
    return fig
