import pulp as pl
from typing import List, Dict, Set

def model_picking(data):
    adj_matrix = data["adj_matrix"]

    nb_locations = data["nb_locations"]

    max_pickers = data["max_pickers"]

    locations_pickers = data["locations_pickers"]

    # minimization problem creation
    model = pl.LpProblem("modele_picking", pl.LpMinimize)

    ## Variables

    # Decision variable indicating whether picker p travels from location i to location j
    x = pl.LpVariable.dicts("x", [(i,j,p) for p in range(max_pickers) for i in locations_pickers[p] for j in locations_pickers[p] if i != j], cat="Binary")

    # Continuous variable used to eliminate sub-tours
    u = pl.LpVariable.dicts("u", [(i,p) for p in range(max_pickers) for i in locations_pickers[p]], lowBound=0, upBound=nb_locations - 1, cat="Integer")

    ## Objective function
    model += pl.lpSum(adj_matrix[i][j] * x[i,j,p] for p in range(max_pickers) for i in locations_pickers[p] for j in locations_pickers[p] if i != j)

    ## Constraints

    # picker p must enter location j from exactly one other location i within their assigned batch
    for p in range(max_pickers):
        if locations_pickers[p]:
            for j in locations_pickers[p]:
                if j != 0:
                    model += pl.lpSum(x[i,j,p] for i in locations_pickers[p] if i != j) == 1 

    # picker p must leave location i to exactly one other location j within their assigned batch
    for p in range(max_pickers):
        if locations_pickers[p]:
            for i in locations_pickers[p]:
                if i != (locations_pickers[p][-1]):
                    model += pl.lpSum(x[i,j,p] for j in locations_pickers[p] if i != j) == 1

    # No arcs departing from the arrival point
    for p in range(max_pickers):
        if locations_pickers[p]:
            for j in locations_pickers[p]:
                if i != j:
                    model += x[locations_pickers[p][-1],j,p] == 0

    # constraint eliminating sub-tours
    for p in range(max_pickers):
        if locations_pickers[p]:
            for i in locations_pickers[p]:
                for j in locations_pickers[p]:
                    if i != j:
                        if j != 0:
                            if i != locations_pickers[p][-1]:
                                model += u[i,p] - u[j,p] + x[i,j,p] * len(locations_pickers[p]) <= len(locations_pickers[p]) - 1

    # departure from location 0
    for p in range(max_pickers):
        if locations_pickers[p]:
            model += u[0,p] == 0
            arrival = locations_pickers[p][-1]
            model += u[arrival, p] == nb_locations - 1

    model.solve()

    sol={}
    solution = {}
    for p in range(max_pickers):
        for i in locations_pickers[p]:
            sol[i,p] = u[i,p].varValue
            for j in locations_pickers[p]:
                if i != j:
                    solution[i,j,p] = x[i,j,p].varValue
    travel = {
    p: [(i, j) 
        for i in locations_pickers[p]
        for j in locations_pickers[p]
        if i != j and solution[i, j, p] > 0.5]
    for p in range(max_pickers)
    }
    u_values = {
    p: [sol[i,p] for i in locations_pickers[p]]
    for p in range(max_pickers) if locations_pickers[p]
}

    return travel, u_values


def model_batching(data) -> Dict:
    vol = data["vol"]

    nb_orders = data["nb_orders"]

    max_pickers = data["max_pickers"]
    max_nb_orders = data["max_nb_orders"]
    max_vol = data["max_vol"]

    a = data["common_locations"]

    # maximization problem creation
    model = pl.LpProblem("model_batching", pl.LpMaximize)

    ## Variables

    # decison variable that is equal to 1 if the picker p handles the order o
    y = pl.LpVariable.dicts("y", [(p,o) for p in range(max_pickers) for o in range(nb_orders)], cat="Binary")

    # Decision variable equal to the product of y_pc and y_pc'
    z = pl.LpVariable.dicts("z", [(p,o,o2) for p in range(max_pickers) for o in range(nb_orders) for o2 in range(nb_orders) if o<o2], lowBound=0, cat="Binary")

    ## Objective function
    model += sum(z[p,o,o2] * a[o,o2] for p in range(max_pickers) for o in range(nb_orders) for o2 in range(nb_orders) if o<o2)

    ## Constraints

    # a minimum of nb_orders must be done
    model += sum(y[p,o] for p in range(max_pickers) for o in range(nb_orders)) >= nb_orders

    # An order can only be done once
    for o in range(nb_orders):
        model += sum(y[p,o] for p in range(max_pickers)) == 1

    # A picker can't do more than max_nb_ord
    for p in range(max_pickers):
        model += sum(y[p,o] for o in range(nb_orders)) <= max_nb_orders

    # A picker can't carry more than max_vol
    for p in range(max_pickers):
        model += sum(y[p,o] * vol[o] for o in range(nb_orders)) <= max_vol

    # z[p, o, o2] is the product between y[p, o] and y[p, o2]
    for p in range(max_pickers):
        for o in range(nb_orders):
            for o2 in range(o+1, nb_orders):
                model += z[p,o,o2] <= y[p,o]
                model += z[p,o,o2] <= y[p,o2]
                model += z[p,o,o2] >= y[p,o] + y[p,o2] - 1
    
    status = model.solve()
    print("Solver status:", pl.LpStatus[status])

    solution = {}
    for p in range(max_pickers):
        for o in range(nb_orders):
            solution[p,o] = y[p,o].varValue or 0

    batches = {
        p : [o for o in range(nb_orders) if (solution[p,o] or 0) > 0.5]
        for p in range(max_pickers)
    }

    return batches