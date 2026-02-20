import logging
import os
import numpy as np
from typing import Dict, Any, Tuple

import data_loader as dl
import utils as ut
import solver_models as sm
import checker.instance_checker as ic
import checker.solution_checker as sc

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Data Loading
# -----------------------------------------------------------------------------

def load_data(adj_matrix_path: str, orders_path: str, constraints_path: str) -> Dict[str, Any]:
    """
    Load data.
    """

    logger.info("Loading Data...")
    
    adj_matrix = dl.load_matrix(adj_matrix_path)
    check_mat = ic.check_distance_matrix(adj_matrix)
    logger.debug("Check matrix %s: %s", adj_matrix_path, check_mat)
    if not check_mat[0]:
        logger.critical("Distance matrix %s is INVALID. Errors: %s", adj_matrix_path, check_mat[1])

    orders = dl.load_orders(orders_path)
    check_orders = ic.check_orders(orders)
    logger.debug("Check orders %s: %s", orders_path, check_orders)
    if not check_orders[0]:
        logger.critical("Orders %s are INVALID. Errors: %s", orders_path, check_orders[1])

    constraints = dl.load_constraints(constraints_path)
    check_constraints = ic.check_constraints(constraints)
    logger.debug("Check constraints %s: %s", constraints_path, check_constraints)
    if not check_constraints[0]:
        logger.critical("Constraints %s are INVALID. Erros: %s", constraints_path, check_constraints[1])

    # nb of locations and nb of orders
    nb_locations, nb_orders = ut.get_locations_and_orders_counts(adj_matrix, orders)

    # max for the number of orders in a batch and for the volume in a batch
    max_nb_orders, max_vol = constraints

    # volume of the orders
    vol = [orders[number]["volume"] for number in range(nb_orders)]

    # lower and upper bound for the number of pickers
    lower_bound, upper_bound = ut.max_pickers_bounds(orders, nb_orders, max_nb_orders, max_vol, vol)
    min_pickers = lower_bound
    max_pickers = upper_bound

    # binary data which takes 1 if the location is part of the order and 0 otherwise
    ifloc = ut.if_loc_in_order(nb_locations, orders)

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
    BASE_DIR = os.path.dirname(__file__)
    matrix_path = os.path.join(BASE_DIR, "toy_data", "matrix.txt")
    orders_path = os.path.join(BASE_DIR, "toy_data", "orders.txt")
    constraints_path = os.path.join(BASE_DIR, "toy_data", "constraints.txt")

    data = load_data(matrix_path, orders_path, constraints_path)
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