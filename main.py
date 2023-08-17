import numpy as np
from itertools import combinations
from pysat.formula import CNF
from pysat.solvers import Solver

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

def getMinezone(assigned, unassigned):
    minezone = []
    
    for cell, value in assigned.items():
        neighbors = unassigned_neighbor(cell, unassigned)
        
        if len(neighbors) > 0:           
            minezone.append([cell, value, neighbors])
            
    return minezone
        
        
def InitialState(rows, cols):
    initial_state = []
    
    for i in range(rows):
        for j in range(cols):
            initial_state.append(-int(variable((i, j))))
                
    return initial_state

def checkState(state, cnf):
    check = []
    
    for i in range(len(cnf)):
        for j in range(len(state)):
            if state[j] in cnf[i]:
                check.append([True])
                break
            elif j + 1 == len(state) and state[j] not in cnf[i]:
                check.append([False])
        
    
    if [False] in check:
        return False
    
    return True

def Heuristic(state, cnf):
    check = []
    
    for i in range(len(cnf)):
        for j in range(len(state)):
            if state[j] in cnf[i]:
                check.append([True])
                break
            elif j + 1 == len(state) and state[j] not in cnf[i]:
                check.append([False])
    
    heuristic = len(cnf)
                
    for i in range(len(check)):
        if check[i] == [True]:
            heuristic = heuristic - 1

    return heuristic    

def ChildState(state, minezone, cell_parent):
    
    if cell_parent == 0:
        cell, mines, locations = minezone[0]
    else:
        for i in range(len(minezone)):
            cell, mines, locations = minezone[i]
            
            if cell == cell_parent:
                if i < len(minezone) - 1:
                    cell, mines, locations = minezone[i + 1]
                    break
                else:
                    return None
    
    locations_var = []
    
    for i in range(len(locations)):
        locations_var.append(int(variable(locations[i])))
    
    children = combinations(locations_var, mines)
    
    children_state = []
    
    flag = False
    
    check = 0
    for cellstate in state:
        if cellstate > 0 and abs(cellstate) in locations_var:
            check = check + 1
    
    if check == mines:
        flag = True
    
    for child in children:
        child_state = state.copy()
        
        for i in range(len(state)):
            if -state[i] in child:
                child_state[i] = -child_state[i]
                
        children_state.append(child_state)
    
    return children_state, cell, mines, flag


def LowestF_Score(open):
    index = 0
    current_state, g_current, h_current, cell_current = open[index]
    
    for i in range(len(open)):
        temp_state, g_temp, h_temp, cell_temp = open[i]
        
        if (g_current + h_current) > (g_temp + h_temp):
            current_state, g_current, h_current, cell_current = open[i]
            index = i
            
    return current_state, g_current, h_current, cell_current, index
         
def checkStateInList(state, f_score, list):
    for element in list:
        if state in element:
            if f_score > (element[1] + element[2]):
                return True
        
    return False


def AStar(cnf):
    open = []
    close = []
    
    initial_state = InitialState(rows, cols)
    
    h_start = Heuristic(initial_state, cnf)
    
    g_start = 0
    
    cell_start = 0
    
    open.append([initial_state, g_start, h_start, cell_start])
    
    while len(open) > 0:
       
        current_state, g_current, h_current, cell_current, index = LowestF_Score(open)   
        
        if checkState(current_state, clauses): 
            return current_state
        
        open.pop(index)
                
        children_states_comb = ChildState(current_state, minezone, cell_current)        
        
        if children_states_comb == None:
            continue        
        
        children_states, cell, mines, flag = children_states_comb
        
        if flag == True:
            open.append([current_state, g_current, h_current, cell])
            close.append([current_state, g_current, h_current, cell_current])
            continue

        for index in range(len(children_states)):
            
            if checkState(children_states[index], clauses): 
                return children_states[index]
            
            g_child = g_current + mines
            
            h_child = Heuristic(children_states[index], clauses)
            
            f_child = g_child + h_child
                
            if checkStateInList(children_states[index], f_child, open):
                continue
            
            elif checkStateInList(children_states[index], f_child, close):
                continue
            
            else: 
                open.append([children_states[index], g_child, h_child, cell])
                
        close.append([current_state, g_current, h_current, cell_current])
            
    
def AllPossibleState(state, minezone):
    all = []
    
    for minezone_i in minezone:
        cell, mines, locations = minezone_i
        
        locations_var = []
    
        for i in range(len(locations)):
            locations_var.append(int(variable(locations[i])))
        
        if len(all) == 0:
            children = combinations(locations_var, mines)
            for child in children:
                child_state = state.copy()
                
                for i in range(len(state)):
                    if -state[i] in child:
                        child_state[i] = -child_state[i]
                        
                all.append(child_state)
        
        else:
            all_temp = all.copy()
            
            all.clear()
            
            for state_temp in all_temp:
                
                children = combinations(locations_var, mines)
                
                for child in children:
                    child_state = state_temp.copy()
                    
                    for i in range(len(state)):
                        if -state_temp[i] in child:
                            child_state[i] = -child_state[i]
                            
                    all.append(child_state)
                  
            all_temp.clear()
       
    return all
        
    
def BruteForce(cnf):
    initial_state = InitialState(rows, cols)
    
    allstate = AllPossibleState(initial_state, minezone)
    
    for state in allstate:
        if checkState(state, cnf):
            return state
        
    return None

def Backtracking(state, cnf, cell_parent):
    if checkState(state, cnf):
        return state
    
    children = ChildState(state, minezone, cell_parent) 
    
    if children != None:
    
        childstates, cell, mines, flag = children
        
        for child in childstates:
            result = Backtracking(child, cnf, cell)
            
            if result != None:
                return result
        
        
    return None
    

assigned = {}
unassigned = set()

board, rows, cols = getBoard('7x7.csv', assigned, unassigned)

clauses = generate_cnf(assigned, unassigned)
# print(clauses)

minezone = getMinezone(assigned, unassigned)

mine = []

print("1. Pysat\n2. A*\n3. Brute Force\n4. Backtracking")

choice = int(input("Choose an option: "))

if choice == 1:
    cnf = CNF(from_clauses=clauses)
    with Solver(bootstrap_with=cnf) as solver:
        satisfy = solver.solve()
        
        solution = solver.get_model()
        
        # print(solver.get_model())
                    
elif choice == 2:
    solution = AStar(clauses)
                    
elif choice == 3:
    solution = BruteForce(clauses)
                    
elif choice == 4:
    state = InitialState(rows, cols)
    solution = Backtracking(state, clauses, 0)
    
if solution != None:
    print("SOLVED!")
    for i in solution:
        if i > 0:
            mine.append(i)
            
else:
    print("CAN NOT SOLVED!")

# print(mine)

output(mine, board, 'output.csv')