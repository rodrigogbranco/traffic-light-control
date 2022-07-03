from classes.petri_util import PetriUtil
from classes.configuration import Configuration
from classes.logger import Logger
import logging

import itertools
import copy

from snakes.nets import Substitution

logger = None
marks = {}
i=0

def fire_recursible(pn,mark_call):
    global i
    global marks
    mark = frozenset(pn.get_marking())
    if mark not in marks:
        marks[mark] = i
        i += 1

    enable_trans = [t for t in pn.transition() if len(t.modes()) > 0 and t.enabled(t.modes()[0])]

    if len(enable_trans) == 0:
        logger.info('{} M{}'.format(mark_call,marks[mark]))
    else:
        for t in enable_trans:
            if len(t.modes()) > 0 and t.enabled(t.modes()[0]):
                #logger.info(t.modes())
                tmp = pn.copy()
                temp_t = tmp.transition(t.name)
                temp_t.fire(temp_t.modes()[0])
                fire_recursible(tmp,'{} M{} -> {} ->'.format(mark_call,marks[mark],temp_t.name))

if __name__ == "__main__":
    Logger.set_globals('tmp.log',logging.INFO)
    logger = Logger('Reachability').get()
    conf = Configuration(None,None,None)
    conf._edges_with_tl = ['']
    conf._edges = {}
    conf._edges[''] = {}
    conf._edges['']['tl'] = {}
    conf._edges['']['tl']['name'] = ''

    pn = PetriUtil().build_petri_net(conf,[''],0,{'' : 0 })

    pn.time(0)

    fire_recursible(pn,'')
    logger.info(marks)

    #first = ['initialtransition', 't5', 't3_']
    #not_first = ['t0_', 't1_', 't2_', 't4_', 't6_']

    #final = []

    #forbidden = {}
    #forbidden['t0_'] = set(['t1_','t2_','t4_'])
    #forbidden['t1_'] = set(['t2_','t4_'])
    #forbidden['t2_'] = set(['t4_'])
    #forbidden['t5'] = set(['t6_'])
    #forbidden['initialtransition'] = set()
    #forbidden['t3_'] = set()
    #forbidden['t4_'] = set()
    #forbidden['t6_'] = set()

    #final += [['initialtransition'] + list(l) for l in list(itertools.permutations(not_first + ['t5', 't3_']))]
    #final += [['t5'] + list(l) for l in list(itertools.permutations(not_first + ['initialtransition', 't3_']))]
    #final += [['t3_'] + list(l) for l in list(itertools.permutations(not_first + ['initialtransition', 't5']))]

    #for p in final:
    #    for i in range(1,len(p)):
    #        el = p[i]
    #        inters = forbidden[el].intersection(set(p[0:i]))
    #        logger.info('i:{} el:{} p:{} for:{} set:{} inters:{}'.format(i,el,p,forbidden[el],set(p[0:i]),inters))            
    #        if len(inters) > 0:
                #logger.info('p:{} inters:{}'.format(p,inters))
    #            final.remove(p)
    #            break
                

    #logger.info(len(final))
