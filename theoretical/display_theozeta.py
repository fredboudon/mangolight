import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle
from matplotlib import cm
import numpy as np

cmap = cm.get_cmap('summer')

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
    ranks = range(1,len(par)+1)
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


def compute_angles(sc):
    from openalea.plantgl.all import Vector3
    from math import degrees
    svalues = {}
    for sh in sc:
        pcenter = sh.geometry.pointList.getCenter()
        v = Vector3.Spherical(pcenter)
        svalues[sh.id] = degrees(v.phi)
    return svalues

#jet = cm.get_cmap('jet')

def plot_zeta_analysis_per_triangles(par, r, fr, sc):
    #ranks = range(1,len(par)+1)
    angles = sort_values(compute_angles(sc))
    #norm = mpl.colors.Normalize(vmin=0,vmax=180)

    sr = sort_values(r)
    sfr = sort_values(fr)
    spar = sort_values(par)
    zetas = [np.array(ri)/np.array(fri) for ri,fri in zip(sr,sfr)]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    (ax1, ax2, ax3), (ax4, ax5, ax6) = axes

    for i, (zetai, pari) in enumerate(zip(zetas,spar)):
        ax1.scatter(pari,zetai,label = 'layer '+str(i+1))

    ax1.set_xlim(0,max(1,max(par.values())))
    ax1.set_ylim(0,max(1,max([max(zetai) if len(zetai) > 0 else 0 for zetai in zetas])))
    ax1.set_ylabel('Zeta')
    ax1.set_xlabel('PAR')
    ax1.legend()
    ax1.set_title('Zeta')

    for i, (zetai, pari, anglesi) in enumerate(zip(zetas,spar,angles)):
        ax2.scatter(pari,zetai, c=anglesi , cmap='jet', vmin=0, vmax=180) #, marker= MarkerStyle.filled_markers[i])
        
    ax2.set_xlim(0,max(1,max(par.values())))
    ax2.set_ylim(0,max(1,max([max(zetai) if len(zetai) > 0 else 0 for zetai in zetas])))
    #ax2.legend()
    ax2.set_ylabel('Zeta')
    ax2.set_xlabel('PAR')
    ax2.set_title('Zeta')

    for i, (zetai, anglesi) in enumerate(zip(zetas,angles)):
        ax3.scatter(anglesi,zetai,label = 'layer '+str(i+1)) #, marker= MarkerStyle.filled_markers[i])
    ax3.set_xlim(0,180)
    ax3.set_ylim(0,max(1,max([max(zetai) if len(zetai) > 0 else 0 for zetai in zetas])))
    ax3.legend()
    ax3.set_ylabel('Zeta')
    ax3.set_xlabel('Elevation')
    ax3.set_title('Zeta')

    #ax4.set_title('PAR')
    ax4.boxplot(spar)
    ax4.set_ylabel('PAR')
    ax4.set_xlabel('Layer')
    
    #ax5.set_title('R')
    ax5.boxplot(sr)
    ax5.set_ylabel('R')
    ax5.set_xlabel('Layer')

    #ax6.set_title('FR')
    ax6.boxplot(sfr)
    ax6.set_ylabel('FR')
    ax6.set_xlabel('Layer')
    plt.show()
