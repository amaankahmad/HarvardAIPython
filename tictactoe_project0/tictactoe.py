"""
Tic Tac Toe Player
"""

from math import inf as infinity
import copy
import sys
import numpy as np

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Initialise number of turns each player has had
    number_of_X = 0
    number_of_O = 0
    for row in board:
        for cell in row:
            if cell == X:
                number_of_X += 1
            elif cell == O:
                number_of_O += 1
    
    # If statement to show who goes next
    if number_of_X <= number_of_O:
        return X
    else: 
        return O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Put actions in a set
    res = set()
    # Check what actions available to play
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == EMPTY: 
                res.add((i,j))
    return res

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Initialising variables indicating the action played
    i = action[0]
    j = action[1]

    # Raise Exception if action not valid
    if board[i][j]!= EMPTY:
        raise Exception("Action not valid! - Cell Occupied")

    # Adding action to board and show new board
    res = copy.deepcopy(board)
    res[i][j] = player(board)
    return res

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    
    # Checks Horizonally
    for r in rows(board):
        if check_same(r) and r[0] != EMPTY:
            return r[0]

    # Checks Vertically
    for c in columns(board):
        if check_same(c) and c[0] != EMPTY:
            return c[0]
    
    # Checks Diagonals
    for d in diagonals(board):
        if check_same(d) and d[0] != EMPTY:
            return d[0]
    # No winner
    return None
 
def rows(board):
    """
    Returns an array of all the rows 
    """
    res = []
    for row in board:
        res.append(row)
    return res

def columns(board):
    """
    Returns an array of all of the columns
    """
    res = []
    for n in range(len(board[0])):
        col = []
        for m in range(len(board)):
            col.append(board[m][n])
        res.append(col)
    return res

def diagonals(board):
    res = []
    diag1 = []
    diag2 = []
    for n in range(len(board)):
        diag1.append(board[n][n])
        diag2.append(board[n][len(board) - n - 1])
    res.append(diag2)
    res.append(diag1)
    return res

def check_same(array):
    """
    Check if X or O same for row, column and diagonal arrays
    """
    return all(i == array[0] for i in array)

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Checks for goal state
    if winner(board) != None:
        return True
    # Checks if board is full
    return is_full(board)

def is_full(board):
    """
    Returns True of False depending if the board is full
    """
    numpyBoard = np.array(board)
    emptCount = np.count_nonzero(numpyBoard == EMPTY)
    if (emptCount == 0):
        return True
    return False

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Initialise winner_name variable to store winner of game
    winner_name = winner(board)

    # X has won
    if winner_name == X:
        return 1
    # O has won
    elif winner_name == O:
        return -1
    # Tie!
    return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Checks if terminal so has exceeded maximum depth
    if terminal(board):
        return None
    else:
    # Minimax continues depth
        curr_player = player(board)
        if curr_player == X:
            return max_value(board)[1]
        else:
            return min_value(board)[1]

def max_value(board):
    """
    Minimax for obtaining max value 
    """
    # If the board is a terminal board then None to avoid this action
    if terminal(board):
        return (utility(board), None)

    # Intitialise the best action and value
    best_action = None
    val = -sys.maxsize

    # Calculating best action
    for action in actions(board):
        # Get the minimum score that can be made by taking such action
        potentialRes = min_value(result(board, action))
        # If this action is better update the best action and the new value 
        if potentialRes[0] > val:
            val = potentialRes[0]
            best_action = action
    return (val, best_action)

def min_value(board):
    """
    Minimax for obtaining min value 
    """
    # If the board is a terminal board then None to avoid this action
    if terminal(board):
        return (utility(board), None)

    # Intitialise the best action and value
    best_action = None
    val = sys.maxsize

    # Calculating best action
    for action in actions(board):
        # Get the minimum score that can be made by taking such action
        potentialRes = max_value(result(board, action))
        # If this action is better update the best action and the new value 
        if potentialRes[0] < val:
            val = potentialRes[0]
            best_action = action
    return (val, best_action)