#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
from operator import attrgetter
import numpy as np
import cvxopt
import cvxopt.glpk
cvxopt.glpk.options['msg_lev'] = 'GLP_MSG_OFF'

Item = namedtuple("Item", ['index', 'value', 'weight','density'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []
    
    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        v, w = int(parts[0]), int(parts[1]) # value, weight
        items.append(Item(i-1, v, w, 1.0 * v / w))
    
    ## greeky algorithm
    #obj, opt, taken = greedy(capacity, items)
    
    # # dynamic programming
    # obj, opt, taken = dp(capacity, items)
    
    # # mip
    # obj, opt, taken = mip(capacity, items)
    
    if np.log10(capacity * len(items)) <= 8:
        obj, opt, taken = dp(capacity, items)
    else:
        obj, opt, taken = mip(capacity, items)
    
    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(opt) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


def greedy(cap, items):
    taken = [0] * len(items)
    filled = 0
    value = 0
    for item in sorted(items, key=attrgetter('density')):
        if filled + item.weight <= cap:
            taken[item.index] = 1
            value += item.value
            filled += item.weight
            
    return(value, 0, taken)

def dp(cap, items):
    n = len(items)
    taken = [0] * n
    values = [[0 for j in range(cap+1)] for i in range(n+1)]
    for i in range(n+1):
        if i > 0:
            value = items[i - 1].value
            weight = items[i - 1].weight
        for j in range(cap+1):
            if i == 0 or j == 0:
                continue
            elif weight > j:
                values[i][j] = values[i-1][j]
            else:
                vTake = values[i-1][j-weight] + value
                vNotTake = values[i-1][j]
                values[i][j] = max(vTake, vNotTake)
    
    totalWeight = cap
    for i in reversed(range(n)):
        if values[i][totalWeight] == values[i+1][totalWeight]:
            continue
        else:
            taken[i] = 1
            totalWeight -= items[i].weight
    
    return(values[-1][-1], 1, taken)        

def mip(cap, items):
    item_count = len(items)
    values = np.zeros(item_count)
    weights = np.zeros([1, item_count])

    for i in range(item_count):
        values[i] = items[i].value
        weights[0][i] = items[i].weight

    binVars=set()
    for var in range(item_count):
        binVars.add(var)

    status, isol = cvxopt.glpk.ilp(c = cvxopt.matrix(-values, tc='d'),
                                   G = cvxopt.matrix(weights, tc='d'),
                                   h = cvxopt.matrix(cap, tc='d'),
                                   I = binVars,
                                   B = binVars)
    taken = [int(val) for val in isol]
    value = int(np.dot(values, np.array(taken)))
    return value, 0, taken




if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

