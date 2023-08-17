from pysat.formula import CNF
from pysat.solvers import Solver
from board_utils import initial_state, check_state, heuristic, child_state, all_possible_states


def solve_with_pysat(clauses):
    cnf = CNF(from_clauses=clauses)
    with Solver(bootstrap_with=cnf) as solver:
        satisfy = solver.solve()

        if satisfy:
            solution = solver.get_model()
            return solution
        else:
            return None


def lowest_f_score(open):
    index = 0
    current_state, g_current, h_current, cell_current = open[index]

    for i in range(len(open)):
        temp_state, g_temp, h_temp, cell_temp = open[i]

        if (g_current + h_current) > (g_temp + h_temp):
            current_state, g_current, h_current, cell_current = open[i]
            index = i

    return current_state, g_current, h_current, cell_current, index


def check_state_in_list(state, f_score, state_list):
    for element in state_list:
        if state in element:
            if f_score > (element[1] + element[2]):
                return True
    return False


def a_star(clauses, minezone, rows, cols):
    open = []
    close = []
    init_state = initial_state(rows, cols)

    h_start = heuristic(init_state, clauses)
    g_start = 0
    cell_start = 0

    open.append([init_state, g_start, h_start, cell_start])

    while len(open) > 0:
        current_state, g_current, h_current, cell_current, index = lowest_f_score(
            open)

        if check_state(current_state, clauses):
            return current_state

        open.pop(index)

        children_states_comb = child_state(
            current_state, minezone, cell_current, cols)

        if children_states_comb == None:
            continue

        children_states, cell, mines, flag = children_states_comb

        if flag == True:
            open.append([current_state, g_current, h_current, cell])
            close.append([current_state, g_current, h_current, cell_current])
            continue

        for index in range(len(children_states)):

            if check_state(children_states[index], clauses):
                return children_states[index]

            g_child = g_current + mines

            h_child = heuristic(children_states[index], clauses)

            f_child = g_child + h_child

            if check_state_in_list(children_states[index], f_child, open):
                continue

            elif check_state_in_list(children_states[index], f_child, close):
                continue

            else:
                open.append([children_states[index], g_child, h_child, cell])

        close.append([current_state, g_current, h_current, cell_current])


def brute_force(cnf, minezone, rows, cols):
    init_state = initial_state(rows, cols)
    allstate = all_possible_states(init_state, minezone, cols)

    for state in allstate:
        if check_state(state, cnf):
            return state

    return None


def backtracking(state, cnf, cell_parent, minezone, cols):
    if check_state(state, cnf):
        return state

    children = child_state(state, minezone, cell_parent, cols)

    if children != None:
        childstates, cell, mines, flag = children
        for child in childstates:
            result = backtracking(child, cnf, cell, minezone, cols)

            if result != None:
                return result

    return None
