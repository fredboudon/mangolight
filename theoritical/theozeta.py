import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

def trans_m(p0, m, I0 = 1):
    if abs(p0) < 1e-5 : 
        if abs(m -1) < 1e-5 : return I0
        return 0.
    if abs(m -1) < 1e-5 : return I0* (1 - p0)
    return I0*pow(p0,m-1)  * (1 - p0)


def zeta_m(zeta_i, tR, tFR, m):
    return zeta_i * pow(tR/tFR,m-1) * (1 - tR) / (1 - tFR)


# Reflectance_Up, Transmittance_Up, Reflectance_Down, Transmittance_Down
leaf_prop = { 'Rc' : (0.05, 0.007, 0.078, 0.007), 
              'Rs' : (0.413, 0.36, 0.455, 0.353),
              'PAR' : (0.067, 0.025, 0.108, 0.023) }


channels = [1,3]
tR = np.mean([leaf_prop['Rc'][i] for i in channels])
tFR = np.mean([leaf_prop['Rs'][i] for i in channels])
tPAR = np.mean([leaf_prop['PAR'][i] for i in channels])
print(tR,tFR,tPAR)

channels = [0,2]
rR = np.mean([leaf_prop['Rc'][i] for i in channels])
rFR = np.mean([leaf_prop['Rs'][i] for i in channels])
rPAR = np.mean([leaf_prop['PAR'][i] for i in channels])
print(rR,rFR,rPAR)

tR, tFR, tPAR = 0.007, 0.35, 0.025 
rR, rFR, rPAR = 0.06, 0.435, 0.08

tR, tFR, tPAR = 0., 0.4, 0.0 
rR, rFR, rPAR = 0., 0.4, 0.0

def plot_zeta(tR = tR, tFR = tFR, tPAR = tPAR, m = 5, dm = 0.1):
    #print(tR,tFR,tPAR)
    ms = np.arange(1,m+1,dm)
    zetas = list(map(lambda n : zeta_m(1,tR,tFR,n), ms))
    par_transs = list(map(lambda n : percent_trans(tPAR,n), ms))
    r_transs = list(map(lambda n : percent_trans(tR,n), ms))
    fr_transs = list(map(lambda n : percent_trans(tFR,n), ms))
    #print(par_transs)
    #print(r_transs)
    #print(fr_transs)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.plot(par_transs,zetas,linestyle='--', marker='o', label='zeta')
    ax1.legend()
    ax2.plot(par_transs,r_transs,linestyle='--', marker='o', label='R_tr')
    ax2.plot(par_transs,fr_transs,linestyle='--', marker='o', label='FR_tr')
    ax2.legend()
    plt.show()


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



def transmitted(I0, nblayers, i, p0):
    d = np.array([0. for j in range(i+1)]+list(map(lambda n : trans_m(p0,n,I0), np.arange(1,nblayers-i))))
    rest = I0*pow(p0,nblayers-i)
    d2 = np.array(list(reversed(list(map(lambda n : trans_m(p0,n,rest), np.arange(nblayers))))))
    return d+d2, I0*pow(p0,2*nblayers-i-1)

def reflected(I0, nblayers, i, p0):
    d = list(reversed(list(map(lambda n : trans_m(p0,n+1,I0), range(0,i))))) + [0. for j in range(i,nblayers)]
    rest = I0*pow(p0,i) if abs(p0) > 0 else 0
    return d, rest

def direct(I0, nblayers, p0):
    return transmitted(I0, nblayers, -1, p0)

def iscattering(values, ref, tr):
    nb = len(values)
    inputlight = np.array([values[1]*ref]+
        [values[i+1]*ref + values[i-1]*tr for i in range(1,nb-1)] +
        [ values[nb-2]*tr ])
    outputlight = np.array([  values[i]*(ref+tr) for i in range(0,nb-1)] +
        [ values[nb-1]*ref])
    return inputlight, outputlight, values[0]*tr

def scattering(sclevel, values, ref, tr, gapfraction):
    in_scat = values
    sky = 0
    nvalues = values
    for i in range(sclevel):
        in_scat, out_scat, sky_i = iscattering(in_scat,ref, tr)
        nvalues = nvalues + in_scat - out_scat
        sky += sky_i
        maxscattering = max(out_scat)
        if maxscattering < 1e-5: 
            break
    return nvalues, sky


def scattering(sclevel, values, ref, tr, gapfraction):
    nblayers = len(values)
    trfactors  = [transmitted(1, nblayers, i, gapfraction) for i in range(nblayers)]
    reffactors = [reflected(1, nblayers, i, gapfraction) for i in range(nblayers)]
    sky_tr_fct  = np.array([sk  for fct,sk in trfactors])
    sky_ref_fct = np.array([sk  for fct,sk in reffactors])
    trfactors   = np.array([fct for fct,sk in trfactors]).T
    reffactors  = np.array([fct for fct,sk in reffactors]).T
    in_scat = np.array(values)
    sky = 0
    nvalues = values
    #print(trfactors)
    #print(sky_ref_fct)
    for i in range(sclevel):
        ref_scat_i0 = np.array(in_scat) * ref 
        ref_scat = reffactors.dot(ref_scat_i0)
        tr_scat_i0 = np.array(in_scat) * tr
        tr_scat = trfactors.dot(tr_scat_i0)
        in_scat = ref_scat + tr_scat
        out_scat = ref_scat_i0 + tr_scat_i0
        sky += sum(np.multiply(sky_ref_fct,ref_scat_i0))
        sky += sum(np.multiply(sky_tr_fct, tr_scat_i0))
        nvalues = nvalues + in_scat - out_scat
        maxscattering = max(out_scat)
        if maxscattering < 1e-5: 
            break
    return nvalues, sky


def plot_zeta_scattering(gapfraction = 0, 
                      tR = tR, tFR = tFR, tPAR = tPAR,
                      rR = rR, rFR = rFR, rPAR = rPAR, 
                      nblayers = 5, scatteringlevel = 50):
    assert (tR+rR) <= 1
    assert (tFR+rFR) <= 1
    assert (tPAR+rPAR) <= 1
    diffcoef = 1
    ranks = np.arange(1,nblayers+1,1)
    #init = [1]+[0 for i in range(maxdepth-1)]
    init, sky = direct(1, nblayers, gapfraction) 
    par = np.array(init) # list(map(lambda n : percent_par_trans_m(tPAR,n), ms)))
    r = np.array(init)
    fr = np.array(init)
    #print('PAR')
    par, par_sky_scat = scattering(scatteringlevel, par, rPAR, tPAR, gapfraction)
    #print('R')
    r, r_sky_scat = scattering(scatteringlevel, r, rR, tR, gapfraction)
    #print('FR')
    fr, fr_sky_scat = scattering(scatteringlevel, fr, rFR, tFR, gapfraction)
    par_sky, r_sky, fr_sky = sky+par_sky_scat, sky+r_sky_scat, sky+fr_sky_scat

    zetas = r/fr
    fig, axes = plt.subplots(3, 2, figsize=(14, 18))
    (ax1, ax2), (ax3, ax4), (ax5, ax6) = axes
    ax1.plot(par,zetas,linestyle='--', marker='o', label='zeta', color='blue')
    ax1.set_xlim(0,max(1,max(par)))
    ax1.set_ylim(0,max(1,max(zetas)))
    ax1.legend()
    ax2.plot(ranks,r,linestyle='--', marker='o', label='R_tr', color='red')
    ax2.plot([0],r_sky, marker='o', color='red')
    ax2.plot(ranks,fr,linestyle='--', marker='o', label='FR_tr', color='purple')
    ax2.plot([0],fr_sky, marker='o', color='purple')
    ax2.plot(ranks,par,linestyle='--', marker='o', label='PAR_tr', color='green')
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


def plot_zeta_scattering_simp(gapfraction = 0, 
                      pR = (tR+rR)/2, pFR = (tFR+rFR)/2, pPAR = (tPAR+rPAR)/2,
                      nblayers = 5, scatteringlevel = 50):
    plot_zeta_scattering(gapfraction = gapfraction, 
                      tR = pR, tFR = pFR, tPAR = pPAR,
                      rR = pR, rFR = pFR, rPAR = pPAR, 
                      nblayers = nblayers, scatteringlevel = scatteringlevel)


if __name__ == '__main__':
    import sys
    args = [tR, tFR, tPAR]
    if len(sys.argv) > 1:
        for i, v in enumerate(sys.argv[1:]):
            args[i] = float(v)
    plot_zeta(*args)