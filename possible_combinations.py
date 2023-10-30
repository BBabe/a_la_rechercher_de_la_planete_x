# C = Comète
# A = Astéroide
# PN = Planète Naine
# NG = Nuage de Gaz
# X = planète X
# SRV = Secteur Réellement Vide
import numpy as np
from itertools import combinations
import pandas as pd
##


def adjacent(i, j):
    ''' test if sectors i and j are adjacent '''
    return abs(j-i) in [1,Nsectors-1] # (1, Nsectors) are adjacent


def l1_in_l2(l1, l2):
    ''' test if all elements of l1 are also in l2 '''
    return set(l1) <= set(l2)


def rule_a(asteroids):
    ''' test if asteroids fulfill their position rule '''
    Na = len(asteroids)
    for ind in range(Na): # some tests may be done several times, but easy writing
        bool_a = adjacent(asteroids[ind], asteroids[(ind-1)%Na]) or adjacent(asteroids[ind], asteroids[(ind+1)%Na]) # adjacent with previous or following neighbour ?
        if not bool_a: # instead of using a while loop
            break
    return bool_a


def rule_ng(ngs, srvs):
    ''' test if gas clouds and voids fulfill their position rule '''
    for ng in ngs:
        bool_ng = any([adjacent(ng, srv) for srv in srvs]) # each ng must have at least one srv neighbour
        if not bool_ng:
            break
    return bool_ng


def fun_remove(inds, indices_in):
    ''' remove already used indices from the remaining ones '''
    indices_out = indices_in.copy()
    for ind in inds:
        indices_out.remove(ind)
    return indices_out


def fun_x(ind_x, indices_in):
    ''' temporary indices list so that pn is not adjacent to x '''
    indices_int = fun_remove([ind_x], indices_in)
    indices_out = indices_int.copy()
    ind_tmp = ind_x-1 # go back to [0,..] convention for "%" function
    ind0 = 1+ (ind_tmp-1)%Nsectors
    ind1 = 1+ (ind_tmp+1)%Nsectors
    if ind0 in indices_out: # otherwise, error if remove non-existent element
        indices_out.remove(ind0)
    if ind1 in indices_out:
        indices_out.remove(ind1)
    return indices_int, indices_out


def possible_ngs():
    ''' all possible combinations of ngs '''
    list_pn = []
    for i in range(1,14):
        j = i+5 # extreme ngs are exactly 5-sectors apart
        for ks in combinations(range(i+1,j), 2): # 2 remaining ngs inside
            list_pn.append([i,*list(ks), j]) # *list gets rid of brackets
    return list_pn


def list_possible_ngs(indzz):
    ''' remaining possible ngs combinations, inside remaining indices
        Function created because not the same number of loops in the two modes '''
    if bool_diff:
        valid = [] # instead of removing elements from initial list (problems of loop indices)
        for ngs in list_ngs:
            if l1_in_l2(ngs, indzz):
                valid.append(tuple(ngs)) # everything in tuple
    else:
        valid = combinations(indzz, 1)
    return valid


def inds2list(inds):
    ''' convert indices format in system format '''
    ind_invert_copy = ind_invert.copy() # otherwise, all list elements are the same
    for ind_obj, obj in enumerate(objects_types):
        for ind in inds[ind_obj]:
            ind_invert_copy[ind-1] = obj
    list_systems.append(ind_invert_copy)


##

bool_save = 0

# 0 = easy 12 sectors ; 1 = difficult 18 sectors
bool_diff = 0
if bool_diff:
    Nsectors = 18
    objects_N = [2,1,4,4,2,5]
    comets_places = [2,3,5,7,11,13,17]
else:
    Nsectors = 12
    objects_N = [2,1,1,4,2,2]
    comets_places = [2,3,5,7,11]

objects_types = ['c', 'x', 'pn', 'a', 'ng', 'srv']

if bool_diff: # init list of possible ngs only once
    list_ngs = possible_ngs()

ind_invert = Nsectors*['c'] # init list only once

##

indices0= list(range(1,Nsectors+1)) # list in order to use remove
list_systems = []

# use of combinations in order to avoid checking same lists multiple times
for ind_c in combinations(comets_places, objects_N[0]): # easier to begin with c, instead of checking if comets_places <= indices_remaining
    print('comets', ind_c) # check progress
    indices_c = fun_remove(ind_c, indices0) # create new copy of indices in order to use it throughout loop
    for ind_a in combinations(indices_c, objects_N[3]): # method 1) forall combi, test if fulfills condition
        if rule_a(ind_a):
            indices_a = fun_remove(ind_a, indices_c)
            for ind_x in combinations(indices_a, objects_N[1]):
                indices_x, indices_xm2 = fun_x(ind_x[0], indices_a) # use of temp indices to avoid adjacent
                for ind_pn in list_possible_ngs(indices_xm2): # method 2) forall combi, test if one of the possible combis
                    indices_pn = fun_remove(ind_pn, indices_x)
                    for ind_ng in combinations(indices_pn, objects_N[4]):
                        ind_srv = fun_remove(ind_ng, indices_pn) # ind_srv = remaining indices
                        if rule_ng(ind_ng, ind_srv):

                            inds2list([ind_c, ind_x, ind_pn, ind_a, ind_ng, ind_srv])

# easy = 4 446 ; difficult = 815 394
print(len(list_systems))
l0 = list_systems.copy()

##

if bool_save:
    labels = ['standard', 'experte']
    df = pd.DataFrame(data = list_systems, columns = range(1,Nsectors+1)) # less heavy than numpy)
    df.to_csv('poss_{}.csv'.format(labels[bool_diff]), index = False, sep = ";")

##

# dg = pd.read_csv(labels[bool_diff], sep = ";")

def detect(sys, args):
    deb, fin, obj, nb = args
    if deb > fin:
        t1 = fin
        t2 = deb-1
        nb = objects_N[objects_types.index(obj)] - nb
    else:
        t1 = deb-1
        t2 = fin
    return sys[t1:t2].count(obj) == nb


def sond(sys, args):
    sector, obj = args
    return sys[sector-1] == obj


def indice_start(sys, args):
    sector, obj = args
    return sys[sector-1] != obj


def guess(l1):
    ind_x = l1[0].index('x')
    ind0 = (ind_x-1)%Nsectors
    ind1 = (ind_x+1)%Nsectors
    obj0 = l1[0][ind0]
    obj1 = l1[0][ind1]
    for sys in l1[1:]:
        if [sys[ind0], sys[ind_x], sys[ind1]] != [obj0, 'x', obj1]:
            return False
    return True


def loop_test(l0, fun, args):
    l1 = []
    for sys in l0:
        if fun(sys, args):
            l1.append(sys)
    print(len(l1))
    print(guess(l1))
    return l1.copy()
