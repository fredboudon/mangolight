from scipy.optimize import *
from mangoG3 import *
import numpy as np

def test():
    a = 8
    b = 4
    c = 1
    def eval(x):
        return abs(pow(a,x)-sum(pow(i,x) for i in [b,c]))
    x0 = [1]
    result = least_squares(eval, x0)
    x = result.x
    print(result)
    print(x, eval(x))


def process_mtg():
    mtg = get_G3_mtg()
    data = {}
    for gu in get_all_gus(mtg):
        if len(get_children(mtg, gu)) > 1: # not is_terminal(mtg, gu) and 
            data[gu] = (get_gu_diameter(mtg, gu)/2., [get_gu_diameter(mtg, vid)/2. for vid in get_children(mtg, gu)] )
    return data

def eval_pipemodel_on_mtg(data):
    def eval(x):
        cost = sum([abs(pow(gud,x)-sum(pow(chd,x) for chd in chdiams))/pow(gud,x) for gu,(gud,chdiams) in list(data.items())])
        print(x,cost)
        return cost

    x0 = [2]
    result = least_squares(eval, x0, bounds=([0],[np.inf]))
    x = result.x
    print(result)
    eval(x)


if __name__ == '__main__':
    eval_pipemodel_on_mtg(process_mtg())
