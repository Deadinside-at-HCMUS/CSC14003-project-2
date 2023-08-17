import numpy as np
from board_utils import variable


def load_board(path, assigned, unassigned):
    board = np.loadtxt(path, delimiter=",", dtype=str)
    rows, cols = board.shape

    for i in range(rows):
        for j in range(cols):
            if int(board[i, j]) > 0:
                assigned[(i, j)] = int(board[i][j])
            else:
                unassigned.add((i, j))

    return board, rows, cols


def save_board(mine, board, path):
    rows, cols = board.shape

    for i in range(rows):
        for j in range(cols):
            if variable((i, j), cols) in mine:
                board[i][j] = 'X'

    np.savetxt(path, board, delimiter=',', fmt='%s')
