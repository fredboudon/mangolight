# -*- coding: utf-8 -*-
from alinea.caribu.CaribuScene import CaribuScene
from openalea.plantgl.all import *
from alinea.caribu.sky_tools import GenSky, GetLight, Gensun, GetLightsSun
import numpy as np
import time, datetime

# Calcul poids du ciel
def create_sky(energy, model, azimuts, zenits):
    """
    Set the light positions and energy for diffuse light sources

    :Parameters:
        - `energy` (:class:`int`) - The incident energy.
        - `model` (:class:`string`) - The kind of diffuse model, either soc or uoc.
        - `azimuts` (:class:`int`) - The number of azimutal positions.
        - `zenits` (:class:`int`) - The number of zenital positions.

    :Returns:
        sky_list: a list with the energy and positions of the source for each sector

    :Returns Type:
        :class:`list`
    """
    # Get the energy and positions of the source for each sector as a string
    sky = GenSky.GenSky()(energy, model, azimuts, zenits)
    sky_str = GetLight.GetLight(sky)

    # Convert string to list in order to be compatible with CaribuScene input format
    sky_list = []
    for string in sky_str.split('\n'):
        if len(string)!=0:
            string_split = string.split(' ')
            t = tuple((float(string_split[0]), tuple((float(string_split[1]), float(string_split[2]), float(string_split[3])))))
            sky_list.append(t)
    return sky_list

def determine_sky(nb_azim, nb_haut, elev_sol, azim_sol):
    tupl_sky = []

    i = 0
    while i < (nb_azim):
        phi = i * (360 / nb_azim)

        j = 0
        while j < nb_haut:
            Elev = j * (90 / nb_haut)
            Zenit_mes = 90 - Elev
            Zenit_sol = 90 - elev_sol

            Psi = np.arccos(
                np.cos(np.radians(Zenit_mes)) * np.cos(np.radians(Zenit_sol)) + np.sin(np.radians(Zenit_mes)) * np.sin(
                    np.radians(Zenit_sol)) * np.cos(np.radians(phi)))

            Energie = 0.0361 * (6.3 + ((1 + np.cos(Psi) * np.cos(Psi)) / (1 - np.cos(Psi)))) * (
                        1 - np.exp(-0.31 / (np.cos(np.radians(Zenit_mes)))))
            dphi = np.radians(360 / nb_azim)
            dteta = np.radians(90 / nb_haut)
            Energie = Energie * np.cos(np.radians(Zenit_mes)) * np.sin(np.radians(Zenit_mes)) * dphi * dteta

            x_cos = np.cos(np.radians(phi)) * np.sin(np.radians(Zenit_mes))
            y_cos = np.sin(np.radians(phi)) * np.sin(np.radians(Zenit_mes))
            z_cos = np.cos(np.radians(Zenit_mes))

            t_sky = tuple((float(Energie), tuple((float(x_cos), float(y_cos), float(-z_cos)))))
            tupl_sky.append(t_sky)

            j += 1

        i += 1
    return tupl_sky

def Sky_turtle6():
    # Calcul poids ciel 5 direction
    sky_list = []

    ls_poids = [1. / 6.] + [5. / (6. * 4)] * 4
    alfa_turtle6 = 0.4637
    effet_sin = [np.sin(np.pi / 2)] + [np.sin(alfa_turtle6)] * 4
    x = np.array(ls_poids) * effet_sin
    ls_poids = x / sum(x)

    Azym = [0, 0, 90, 180, 270]

    for i in range(0, 5):
        azimuth = Azym[i]
        Energie = ls_poids[i]

        if i != 0:
            x_dir = np.cos(np.radians(azimuth)) * np.sin(alfa_turtle6)
            y_dir = np.sin(np.radians(azimuth)) * np.sin(alfa_turtle6)
            z_dir = np.cos(alfa_turtle6)
        else:
            x_dir = 0
            y_dir = 0
            z_dir = 1

        t_sky = tuple((float(Energie), tuple((float(x_dir), float(y_dir), float(-z_dir)))))

        sky_list.append(t_sky)

    return sky_list

sky_list = []
#sky_list = determine_sky(120, 9, 22, 45)
#sky_list = Sky_turtle6()
sky_list = create_sky(1,'soc',24,30)
print('poids du ciel calcul')


#soleil
soleil=Gensun.Gensun()(1,344,14,43)
soleil=GetLightsSun.GetLightsSun(soleil)
soleil=soleil.split(' ')
soleil=[tuple((float(soleil[0]), tuple((float(soleil[1]), float(soleil[2]), float(soleil[3])))))]
#Soleil vertical
#soleil = [(1.0, (0., -0.0, -1))]

#strategie des m spheres concentriques
scene_spheres = Scene()

m = 1

for m in range(m):
    scene_spheres.add(Sphere(m+1))




rc = (0.15, 0.15)#(0.10, 0.07, 0.10, 0.07)  # Combes et al
rs = (0.45,0.45)#(0.41, 0.43, 0.41, 0.43)
po_capt = (0.0001,0.0001)

opt = {'rs':{}, 'rc':{}}
count_sh=0
s_prov=Scene()
for sh in scene_spheres:
    opt['rs'][count_sh] = rs
    opt['rc'][count_sh] = rc
    s_prov.add(Shape(geometry=sh.geometry, id=count_sh))
    #print(count_sh)
    count_sh += 1

#Viewer.display(s_prov)
#s_prov=Scene()
cc_scene=CaribuScene(scene=s_prov, opt=opt, light=soleil)

print('Direct')
current_time_of_the_system = time.time()
_,aggregated_direct=cc_scene.run(direct=False, infinite=False, split_face=True)#,sensors=dico_capt)#,screen_resolution=12000)
execution_time = int(time.time() - current_time_of_the_system)
print('Execution time',execution_time)
#print aggregated_direct
print('RC ',aggregated_direct['rc'])
print('RS ',aggregated_direct['rs'])

# cc_scene=CaribuScene(scene=s_prov, opt=opt, light=sky_list)
# print('Diffus')
# current_time_of_the_system = time.time()
# _,aggregated_diffus=cc_scene.run(direct=False, infinite=False, split_face=True)#,sensors=dico_capt)#,screen_resolution=12000)
# execution_time = int(time.time() - current_time_of_the_system)
# print('Execution time',execution_time)
# #print aggregated_diffus['rs'].keys()
# print('RC ',aggregated_diffus['rc'])
# print('RS ',aggregated_diffus['rs'])
#

#print('RC = ',aggregated_direct['rc']['sensors']['Ei'][0])
#print('RS = ',aggregated_direct['rs']['sensors']['Ei'][0])
#print('Zeta : ',aggregated_direct['rc']['sensors']['Ei'][0]/aggregated_direct['rs']['sensors']['Ei'][0])

#for nsh in [21180]: #hemispherique
##for nsh in [21380]:#,21381]:#range(len(s_prov)):#directionnel
##    print('RC direct RC diffus RS direct RS diffus',aggregated_direct['rc']['Ei'][nsh], aggregated_diffus['rc']['Ei'][nsh],aggregated_direct['rs']['Ei'][nsh],aggregated_diffus['rs']['Ei'][nsh])
##    print('Zeta Capteur',(aggregated_direct['rc']['Ei'][nsh]+aggregated_diffus['rc']['Ei'][nsh])/(aggregated_direct['rs']['Ei'][nsh]+aggregated_diffus['rs']['Ei'][nsh]))
##    #print('Triangle No', nsh, (aggregated_direct['rs']['Ei'][nsh]))
