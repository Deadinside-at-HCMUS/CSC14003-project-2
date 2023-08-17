import numpy as np
from itertools import combinations


def variable(cell, cols):
    i = int(cell[0])
    j = int(cell[1])
    return (i * cols) + j + 1


def unassigned_neighbor(cell, unassigned):
    row = int(cell[0])
    col = int(cell[1])
    neighbor = []

    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if (row+i, col+j) in unassigned:
                neighbor.append((row+i, col+j))

    return neighbor


def generate_cnf(assigned, unassigned, cols):
    clauses = []

    # If it in assigned, it must not be mine (False)
    for clause in assigned:
        clauses.append([-int(variable(clause, cols))])

    # A numbered cell is surround by other numbered cells and mines, so what we do here is check every assigned cell to get CNF
    for cell, value in assigned.items():

        neighbors = unassigned_neighbor(cell, unassigned)

        # If the cell dont have any unassigned neighbors, move to another cell
        if len(neighbors) == 0:
            continue

        # If the cell's number is equal with the number of surrounded unassigned cells, all that unassigned cells must be mines
        if len(neighbors) == value:
            for clause in neighbors:
                clauses.append([int(variable(clause, cols))])

        # Else if the number of surrounded unassigned cells is larger than the assigned cell's value, we gonna do combinations of every cells
        elif len(neighbors) > value:

            neighbors_var = []
            # Turn tuple into integer to push into clauses
            for i in range(len(neighbors)):
                neighbors_var.append(int(variable(neighbors[i], cols)))
            # The idea is every surrounded unassigned cells is potential mine (True OR True OR True ...)
            clauses.append(neighbors_var)

            # The maximum mines in the neighbors is not more than the assigned cell's value
            # So we gonna do here combinations of negative cells which every combination have (value+1) elements (False) (False OR False OR False ...)
            neg = combinations(neighbors, value+1)
            for clause in neg:
                clauses.append([-int(variable(liter, cols))
                               for liter in clause])

            # The minimum mines in the neighbors is not less than the assigned cell's value
            # So we gonna do here combinations of positive cells which every combination have (neighbors-value+1) elements (True) (True OR True OR True ...)
            pos = combinations(neighbors, len(neighbors)-value+1)
            for clause in pos:
                clauses.append([int(variable(liter, cols))
                               for liter in clause])

    return clauses


def get_minezone(assigned, unassigned):
    minezone = []

    for cell, value in assigned.items():
        neighbors = unassigned_neighbor(cell, unassigned)

        if len(neighbors) > 0:
            minezone.append([cell, value, neighbors])

    return minezone


def initial_state(rows, cols):
    initial_state = []

    for i in range(rows):
        for j in range(cols):
            initial_state.append(-int(variable((i, j), cols)))

    return initial_state


def check_state(state, cnf):
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


def heuristic(state, cnf):
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


def child_state(state, minezone, cell_parent, cols):
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
        locations_var.append(int(variable(locations[i], cols)))

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
        c_state = state.copy()

        for i in range(len(state)):
            if -state[i] in child:
                c_state[i] = -c_state[i]

        children_state.append(c_state)

    return children_state, cell, mines, flag


def all_possible_states(state, minezone, cols):
    all = []

    for minezone_i in minezone:
        cell, mines, locations = minezone_i

        locations_var = []

        for i in range(len(locations)):
            locations_var.append(int(variable(locations[i], cols)))

        if len(all) == 0:
            children = combinations(locations_var, mines)
            for child in children:
                c_state = state.copy()

                for i in range(len(state)):
                    if -state[i] in child:
                        c_state[i] = -c_state[i]

                all.append(c_state)

        else:
            all_temp = all.copy()

            all.clear()

            for state_temp in all_temp:

                children = combinations(locations_var, mines)

                for child in children:
                    c_state = state_temp.copy()

                    for i in range(len(state)):
                        if -state_temp[i] in child:
                            c_state[i] = -c_state[i]

                    all.append(c_state)

            all_temp.clear()

    return all
