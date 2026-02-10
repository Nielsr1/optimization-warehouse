import src.data_loader as dl
import src.utils as ut
import src.solver_models as sm
import src.checker.instance_checker as ic
import src.checker.solution_checker as sc

def load_data():
    ## data loading
    
    adj_matrix = dl.load_matrix(r"src\toy_data\matrix.txt")
    check_mat = ic.check_distance_matrix(adj_matrix)
    print(check_mat)
    orders = dl.load_orders(r"src\toy_data\orders.txt")
    check_orders = ic.check_orders(orders)
    print(check_orders)
    constraints = dl.load_constraints(r"src\toy_data\constraints.txt")
    check_constraints = ic.check_constraints(constraints)
    print(check_constraints)
    
    ### big instance 
    # adj_matrix = dl.load_matrix(r"projet-base\Projet_pro-main\data\real_warehouse_data\warehouse_A\adjacencyMatrix.txt")
    # check_mat = ic.check_distance_matrix(adj_matrix)
    # print(check_mat)
    # orders = dl.load_orders(r"projet-base\Projet_pro-main\data\real_warehouse_data\warehouse_A\data_2023-05-22\supportList.txt")
    # check_orders = ic.check_orders(orders)
    # print(check_orders)
    # constraints = dl.load_constraints(r"projet-base\Projet_pro-main\data\real_warehouse_data\warehouse_A\data_2023-05-22\constraints.txt")
    # check_constraints = ic.check_constraints(constraints)
    # print(check_constraints)

    # nb of locations and nb of orders
    nb_locations, nb_orders = ut.get_locations_and_orders_counts(adj_matrix, orders)

    # max for the number of orders in a batch and for the volume in a batch
    max_nb_orders, max_vol = constraints

    # volume of the orders
    vol = [orders[number]["volume"] for number in range(nb_orders)]

    print("vol done")

    # lower and upper bound for the number of pickers
    lower_bound, upper_bound = ut.max_pickers_bounds(orders, nb_orders, max_nb_orders, max_vol, vol)
    min_pickers = lower_bound
    max_pickers = upper_bound

    print("bounds done")

    # binary data which takes 1 if the location is part of the order and 0 otherwise
    ifloc = ut.if_loc_in_order(nb_locations, orders)

    print("ifloc done")

    # Vector containing the number of locations shared by each pair of orders
    common_locations = ut.common_elements(ifloc, nb_orders, nb_locations)

    data = {
        "adj_matrix": adj_matrix,
        "ifloc": ifloc,
        "vol": vol,
        "nb_locations": nb_locations,
        "nb_orders": nb_orders,
        "min_pickers": min_pickers,
        "max_pickers": max_pickers,
        "max_nb_orders": max_nb_orders,
        "max_vol": max_vol,
        "common_locations": common_locations
    }
    return data

def add_data(data, batches, locations_pickers):
    data["batches"] = batches
    data["locations_pickers"] = locations_pickers
    return data

def test_picking(data):
    travel = sm.model_picking(data)
    return travel

def test_batching(data):
    batches = sm.model_batching(data)
    # checker
    check_batching = sc.check_batching_solution(batches, data["vol"], data["max_nb_orders"], data["max_vol"])
    print(check_batching)
    # get locations for each picker
    locations_pickers = ut.get_picker_locations_from_ifloc(batches, data["ifloc"], data["nb_locations"])
    return batches, locations_pickers

def main():
    data = load_data()
    print("load data done")
    tests = {
        "picking": test_picking,
        "batching" : test_batching
    }
    # batches, locations_pickers = tests["batching"](data)
    # print(batches, locations_pickers)
    # data = add_data(data, batches, locations_pickers)
    # test model picking
    # travel, u = tests["picking"](data)
    # print(travel, u)
    # check_picking = sc.check_picking_solution(travel, data["nb_locations"])
    # print(check_picking)

if __name__ == "__main__":
    main()