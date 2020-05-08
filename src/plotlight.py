from openalea.plantgl.all import *
from openalea.plantgl.codec.js import *

s = Scene('../data/lightedG3.bgeom')
#s = Scene([s[i] for i in range(10)])
fname = 'mangodisplay.html'
plot_js(s, fname)
