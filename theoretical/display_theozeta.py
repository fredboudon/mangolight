import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

cmap = cm.get_cmap('summer')

def plot_disks(values, ax, figcolorbar = None):
    m = len(values)
    norm = mpl.colors.Normalize(vmin=0,vmax=max(1,max(values)))
    ax.plot([0,0],[-2,-1.1],c='brown',linewidth=40)
    for i, v in enumerate(values):
        if not np.isnan(v):
          r = 1-(i/(m-1))
          circle = plt.Circle((0, 0), r, color= cmap(norm(v)))
          ax.add_patch(circle)
    ax.set_xlim(-1.2,1.2)
    ax.set_ylim(-1.2,1.2)
    if figcolorbar:
        figcolorbar.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap),ax=ax)


def plot_zeta_analysis(par, r, fr, par_sky = None, r_sky = None, fr_sky = None):
    ranks = range(1001,(len(par)+1)*1000,1000)
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
