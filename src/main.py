import time
import file_utils
import board_utils
import algorithm_utils


def menu_choice():
    print("1. 3x3 board")
    print("2. 4x4 board")
    print("3. 5x5 board")
    print("4. 6x6 board")
    print("5. 7x7 board")
    choice = int(input('Your choice: '))

    if choice == 1:
        return '../testcases/input_3x3.csv'
    elif choice == 2:
        return '../testcases/input_4x4.csv'
    elif choice == 3:
        return '../testcases/input_5x5.csv'
    elif choice == 4:
        return '../testcases/input_6x6.csv'
    return '../testcases/input_7x7.csv'


if __name__ == '__main__':
    print("1. Pysat\n2. A*\n3. Brute Force\n4. Backtracking")

    choice = int(input("Choose an option: "))

    input_file = menu_choice()

    start_time = time.time()

    assigned = {}
    unassigned = set()

    board, rows, cols = file_utils.load_board(input_file, assigned, unassigned)

    clauses = board_utils.generate_cnf(assigned, unassigned, cols)

    minezone = board_utils.get_minezone(assigned, unassigned)

    mine = []

    if choice == 1:
        solution = algorithm_utils.solve_with_pysat(clauses)

    elif choice == 2:
        solution = algorithm_utils.a_star(clauses, minezone, rows, cols)

    elif choice == 3:
        solution = algorithm_utils.brute_force(clauses, minezone, rows, cols)

    elif choice == 4:
        state = board_utils.initial_state(rows, cols)
        solution = algorithm_utils.backtracking(
            state, clauses, 0, minezone, cols)

    if solution != None:
        print("SOLVED!")
        for i in solution:
            if i > 0:
                mine.append(i)
    else:
        print("CAN NOT SOLVED!")

    output_file = input_file.replace('input', 'output')
    file_utils.save_board(mine, board, output_file)

    print(f"\nTime consumption: {(time.time()-start_time)*1000}ms")
