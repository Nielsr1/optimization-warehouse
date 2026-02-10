import numpy as np
from pathlib import Path
from typing import List, Dict, Set

def load_matrix(path: str | Path) -> np.ndarray:
    """
    Load a square adjacency matrix from a file.
    Supports text (.txt) with a header line, or NumPy binary (.npy).

    Text format expected:
        - First line: number of locations (optional, can be used for verification)
        - Remaining lines: square matrix (space, tab, or comma separated)

    Args:
        path (str | Path): Path to the matrix file.

    Returns:
        np.ndarray: Loaded square matrix.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the matrix is not square or size doesn't match header.
    """

    # Convert string paths to Path objects for cross-platform safety
    if isinstance(path, str):
        path = Path(path)

    # Ensure the file exists
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    if path.suffix == ".npy":
        # Binary format: fast and exact
        adj_mat = np.load(path)

        if adj_mat.ndim != 2 or adj_mat.shape[0] != adj_mat.shape[1]:
            raise ValueError("Loaded matrix must be 2D and square")
        
        adj_mat = adj_mat.tolist()  # convertit l'array en liste de listes Python
        return adj_mat
    
    # Text format: handle header line
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    # Boolean for
    header = False

    # Get number of location
    try:
        nb_loc = int(lines[0].strip())
        if nb_loc == len(lines) - 1:
            header = True
    except ValueError:
        pass

    
    # Initialize an empty NumPy array
    adj_mat = np.zeros((nb_loc, nb_loc), dtype=float)

    if header == True:
        # Fill in the matrix
        for i in range(nb_loc):
            row = [float(x) for x in lines[i + 1].strip().split()]
            adj_mat[i] = row

        adj_mat = adj_mat.tolist()  # convertit l'array en liste de listes Python
        return adj_mat

    else: 
        for i in range(nb_loc):
            row = [float(x) for x in lines[i].strip().split()]
            adj_mat[i] = row
        
        adj_mat = adj_mat.tolist()  # convertit l'array en liste de listes Python
        return adj_mat

def load_orders(path: str | Path):
    """
    Load a square adjacency matrix from a file.
    Supports text (.txt) with a header line, or NumPy binary (.npy).

    Text format expected:
        - First line: number of locations (optional, can be used for verification)
        - Remaining lines: square matrix (space, tab, or comma separated)

    Args:
        path (str | Path): Path to the matrix file.

    Returns:
        np.ndarray: Loaded square matrix.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the matrix is not square or size doesn't match header.
    """

    # Convert string paths to Path objects for cross-platform safety
    if isinstance(path, str):
        path = Path(path)

    # Ensure the file exists
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    
    # Text format: handle header line
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        
    lines = [line.strip() for line in lines]
    
    orders: List[Dict[str, object]] = []
    for i in range(1, len(lines), 2):
        info = lines[i].split()
        number = int(info[0])
        volume = int(info[1])
        nb_locations = int(info[2])

        spots = lines[i+1].split()
        locations_list = []
        for i in range(nb_locations):
            locations_list.append(spots[i])
        locations_list = list(map(int, locations_list))
        locations_set = set(locations_list)

        orders.append({
            "id": number,
            "volume": volume,
            "nb_locations": nb_locations,
            "locations_list": locations_list,
            "locations_set": locations_set
        })

    return orders

def load_constraints(path: str | Path):
    """
    Load a square adjacency matrix from a file.
    Supports text (.txt) with a header line, or NumPy binary (.npy).

    Text format expected:
        - First line: number of locations (optional, can be used for verification)
        - Remaining lines: square matrix (space, tab, or comma separated)

    Args:
        path (str | Path): Path to the matrix file.

    Returns:
        np.ndarray: Loaded square matrix.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the matrix is not square or size doesn't match header.
    """

    constraints = []

    if isinstance(path, str):
        path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    
    # Text format: handle header line
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    line = lines[0].strip().split()
    constraints.append(int(line[0]))
    constraints.append(int(line[1]))

    return constraints