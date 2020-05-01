from openalea.mtg import *
from math import pi
from openalea.plantgl.all import Vector3, norm, direction


def read_G3_mtg(fname = "../data/consolidated_mango3d.mtg"):
    g = MTG(fname)

    def pos_prop(mtg):
        xx,yy,zz = mtg.property("XX"),mtg.property("YY"),mtg.property("ZZ")
        return dict ([(node,Vector3(x,-yy[node],-zz[node])) for node,x in xx.items()])

    g.property('Position').update(pos_prop(g))

    def diameter_prop(mtg):
        topdia = lambda x: mtg.property('Diameter').get(x)
        diameters = {}
        for vid in mtg.vertices(scale=3):
            td = topdia(vid)
            if td is None :
                if not mtg.parent(vid) is None:
                    diameters[vid] = diameters[mtg.parent(vid)]
            else:
                diameters[vid] = td
        return diameters

    g.property('Diameter').update(diameter_prop(g))

    return g

MTGG3 = None

def get_G3_mtg():
    global MTGG3
    if MTGG3 is None:
        MTGG3 = read_G3_mtg()
    return MTGG3


def is_gu_point(mtg, vid):
    """ A GU Point is a node in the graph that represent both a digitized point and a GU.
        Conversely, some point that mark the begining of a branch do not represent any GU."""
    return mtg.edge_type(vid) == '<'

def get_gu_bottom_point(mtg,vid):
    return mtg.parent(vid)

def get_gu_top_point(mtg,vid):
    return vid

def is_terminal(mtg,vid):
    return mtg.nb_children(vid) == 0

def is_pruned(mtg,vid):
    return not (mtg.property('Taille').get(vid) is None)

def get_all_gus(mtg):
    return [vid for vid in mtg.vertices(scale=3) if is_gu_point(mtg, vid)]

def get_all_terminal_gus(mtg):
    return [vid for vid in mtg.vertices(scale=3) if is_gu_point(mtg, vid) and is_terminal(mtg,vid)]

def get_all_pruned_gus(mtg):
    return mtg.property('Taille').keys()

def get_terminal_gus_from_ancestor(mtg, vid):
    return [vid for vid in mtg.Extremities(vid) if is_gu_point(mtg, vid)]

def get_descendants_gus_from_ancestor(mtg, vid):
    return [vid for vid in mtg.Descendants(vid) if is_gu_point(mtg, vid)]

def get_gu_diameter(mtg, vid):
    """ Diameter is stored in the bottom point.
        :return: diameter in mm  """
    return mtg.property('Diameter').get(get_gu_bottom_point(mtg,vid))*10

def set_gu_diameter(mtg, vid, value):
    """ Set diameter in the bottom point. """
    mtg.property('Diameter')[get_gu_bottom_point(mtg,vid)] = value/10.

def get_gu_section(mtg, vid):
    """ Return section value of the GU in mm2 """
    return pi*(get_gu_diameter(mtg, vid)**2)/4

def get_gu_nb_leaf(mtg, vid):
    """ NbLeaf is stored in the top point """
    return mtg.property('NbLeaf').get(get_gu_top_point(mtg,vid),0)

def get_gu_type(mtg, vid):
    """ NbLeaf is stored in the bottom point """
    return mtg.property('UnitType').get(get_gu_bottom_point(mtg,vid))

def get_gu_bottom_position(mtg, vid):
    return mtg.property('Position')[get_gu_bottom_point(mtg,vid)]

def get_gu_top_position(mtg, vid):
    return mtg.property('Position')[get_gu_top_point(mtg,vid)]

def set_gu_top_position(mtg, vid, value):
    mtg.property('Position')[get_gu_top_point(mtg,vid)] = value

def get_gu_direction(mtg, vid):
    """ Gives direction of the GU. Length of the returned vector represent the lenght of the GU """
    return (get_gu_top_position(mtg, vid) - get_gu_bottom_position(mtg, vid))

def get_gu_normed_direction(mtg, vid):
    """ Gives direction of the GU. Length of the returned vector represent the lenght of the GU """
    return direction(get_gu_direction(mtg, vid))

def get_gu_length(mtg, vid):
    return norm(get_gu_direction(mtg, vid))

def get_gu_depth(mtg, vid1, vid2):
    assert is_gu_point(mtg, vid1) and is_gu_point(mtg, vid2)
    return len([vid for vid in mtg.Path(vid1,vid2) if is_gu_point(mtg, vid)])-1

def get_gu_terminal_min_depth(mtg, vid):
    if is_terminal(mtg, vid) : return 0
    return min([get_gu_depth(mtg, vid, desc) for desc in get_terminal_gus_from_ancestor(mtg, vid)])

def get_gu_property(mtg, vid, propname, toppoint = True):
    return mtg.property(propname)[get_gu_top_point(mtg,vid) if toppoint else get_gu_bottom_point(mtg,vid)]

def set_gu_property(mtg, vid, propname, value, toppoint = True):
    mtg.property(propname)[get_gu_top_point(mtg,vid) if toppoint else get_gu_bottom_point(mtg,vid)] = value


def get_parent(mtg, vid):
    assert not vid is None
    vid = mtg.parent(vid)
    while not vid is None and not is_gu_point(mtg, vid):
        vid = mtg.parent(vid)
    assert vid is None or is_gu_point(mtg, vid)
    return vid

def get_children(mtg, vid):
    assert not vid is None
    fchildren = []
    for ch in mtg.children(vid):
        if not is_gu_point(mtg, ch):
            fchildren += get_children(mtg, ch)
        else:
            fchildren.append(ch)
    return fchildren


def get_ancestor(mtg, vid, order):
    assert order > 0
    for j in range(order):
        vid = get_parent(mtg, vid)
    return vid

eApical, eLateral = 1,2

def gu_position(mtg, vid):
    return eApical if mtg.edge_type(get_gu_bottom_point(mtg,vid)) == '<' else eLateral

def nbtotalleaves(mtg):
    return gu_recursive_property_from_terminal(mtg, lambda vid, childrenvalues : sum(childrenvalues)+get_gu_nb_leaf(mtg, vid), lambda vid: get_gu_nb_leaf(mtg, vid))

def gus_depth_from_terminal(mtg, agregation = min):
    return gu_recursive_property_from_terminal(mtg, lambda vid, childrenvalues : agregation(childrenvalues)+1, 0)

def gus_depth_from_root(mtg):
    return gu_recursive_property_from_root(mtg)

def gu_recursive_property_from_terminal(mtg, nodeaxiom = lambda vid, childrenvalues : sum(childrenvalues)+1, leafaxiom = lambda vid : 0, root = None):
    import mangoG3 as mg3
    from openalea.mtg.traversal import post_order2
    res = {}
    if root is None:
        root = mtg.roots(scale=mtg.max_scale())[0]
    for vid in post_order2(mtg, root):
        if mg3.is_terminal(mtg, vid): 
            res[vid] = leafaxiom(vid) if callable(leafaxiom) else leafaxiom
        elif mg3.is_gu_point(mtg,vid):
            children = mg3.get_children(mtg, vid)
            for child in children:
                assert mg3.is_gu_point(mtg,child)
            res[vid] = nodeaxiom(vid, [res[child] for child in children])
    return res

def gu_recursive_property_from_root(mtg, nodeaxiom = lambda vid, parentvalue : parentvalue+1, rootaxiom = lambda vid : 0, root = None):
    import mangoG3 as mg3
    from openalea.mtg.traversal import pre_order2
    res = {}
    if root is None:
        root = mtg.roots(scale=mtg.max_scale())[0]
    for vid in pre_order2(mtg, root):
        if mg3.get_parent(mtg, vid) is None: 
            res[vid] = rootaxiom(vid) if callable(rootaxiom) else rootaxiom
        elif mg3.is_gu_point(mtg,vid):
            parent = mg3.get_parent(mtg, vid)
            res[vid] = nodeaxiom(vid, res[parent])
    return res

def repare_mango_lighted():
    import openalea.plantgl.all as pgl
    s = pgl.Scene('../data/lightedG3.bgeom')
    s2 = pgl.Scene('../data/consolidated_mango3d.bgeom')

    pid2sid = {}
    points = []
    #key = lambda bbx : tuple([round(v,2) for v in bbx.getCenter()])
    key = lambda bbx :  bbx.getCenter()

    for i, (sid, lsh) in enumerate(s2.todict().items()):
        bbx = pgl.BoundingBox(pgl.Scene(lsh))
        c = key(bbx)
        points.append(c)
        pid2sid[i] = sid

    kdtree = pgl.ANNKDTree3(points)

    for i,sh in enumerate(s):
        bbx = pgl.BoundingBox(sh)
        res = kdtree.k_closest_points(key(bbx),1,pgl.norm(bbx.getSize()))
        sh.id = pid2sid[res[0]]

    pgl.Viewer.display(s)




