import numpy as np
from itertools import combinations
from pysat.formula import CNF
from pysat.solvers import Solver
# import brute_force
# import AStar

# Get the cell's numerical order (from left to right, top to bottom) from its location
def variable(cell):
    i = int(cell[0])
    j = int(cell[1])
    return (i * cols) + j + 1

# Get board, rows and columns
def getBoard(path, assigned, unassigned):
    board = np.loadtxt(path, delimiter=",", dtype=str)

    rows, cols = board.shape

    for i in range(rows):
        for j in range(cols):
            if int(board[i, j]) > 0:
                assigned[(i, j)] = int(board[i][j])
            else:
                unassigned.add((i, j))
                
    return board, rows, cols

# Get unassigned neighbors of a cell
def unassigned_neighbor(cell, unassigned):
    row = int(cell[0]) 
    col = int(cell[1])
    neighbor = []
    
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if (row+i, col+j) in unassigned:
                neighbor.append((row+i, col+j))
                
    return neighbor

# Generate CNF
def generate_cnf(assigned, unassigned):
    clauses = []
    
    # If it in assigned, it must not be mine (False)
    for clause in assigned:
        clauses.append([-int(variable(clause))])
    
    # A numbered cell is surround by other numbered cells and mines, so what we do here is check every assigned cell to get CNF
    for cell, value in assigned.items():
        
        neighbors = unassigned_neighbor(cell, unassigned)
        
        # If the cell dont have any unassigned neighbors, move to another cell
        if len(neighbors) == 0:
            continue
        
        # If the cell's number is equal with the number of surrounded unassigned cells, all that unassigned cells must be mines
        if len(neighbors) == value:
            for clause in neighbors:
                clauses.append([int(variable(clause))])
        
        # Else if the number of surrounded unassigned cells is larger than the assigned cell's value, we gonna do combinations of every cells 
        elif len(neighbors) > value:    
            
            neighbors_var = []
            # Turn tuple into integer to push into clauses
            for i in range(len(neighbors)):
                neighbors_var.append(int(variable(neighbors[i])))
            # The idea is every surrounded unassigned cells is potential mine (True OR True OR True ...)
            clauses.append(neighbors_var)    
            
            # The maximum mines in the neighbors is not more than the assigned cell's value 
            # So we gonna do here combinations of negative cells which every combination have (value+1) elements (False) (False OR False OR False ...)
            neg = combinations(neighbors,value+1)
            for clause in neg:
                clauses.append([-int(variable(liter)) for liter in clause])
            
            # The minimum mines in the neighbors is not less than the assigned cell's value    
            # So we gonna do here combinations of positive cells which every combination have (neighbors-value+1) elements (True) (True OR True OR True ...)
            pos = combinations(neighbors,len(neighbors)-value+1)
            for clause in pos:
                clauses.append([int(variable(liter)) for liter in clause])           
            
    return clauses
        
def output(mine, board, path):
    rows, cols = board.shape
    
    for i in range(rows):
        for j in range(cols):
            if variable((i,j)) in mine:
                board[i][j] = 'X'   
                
    np.savetxt(path, board, delimiter=',',fmt='%s')    
        

assigned = {}
unassigned = set()

board, rows, cols = getBoard('input.csv', assigned, unassigned)

clauses = generate_cnf(assigned, unassigned)
print(clauses)

mine = []

cnf = CNF(from_clauses=clauses)
with Solver(bootstrap_with=cnf) as solver:
    satisfy = solver.solve()
    
    solution = solver.get_model()
    
    print(solver.get_model())
    
    if solution != None:
        for i in solution:
            if i > 0:
                mine.append(i)


# print(mine)

output(mine, board, 'output.csv')
