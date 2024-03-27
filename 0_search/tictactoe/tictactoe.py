"""
Tic Tac Toe Player
"""

import math
import random

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
    x_count = 0
    o_count = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == "O":
                o_count += 1
            if board[i][j] == "X":
                x_count += 1
    return "X" if x_count == o_count else "O"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i,j))
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] != EMPTY:
        raise ValueError("Invalid move")
    else:
        new_board = [row.copy() for row in board]
        new_board[action[0]][action[1]] = player(board)
        return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if board[0][0] == board[0][1] and board[0][0] == board[0][2]:
        return board[0][0]

    elif board[1][0] == board[1][1] and board[1][0] == board[1][2]:
        return board[1][0]

    elif board[2][0] == board[2][1] and board[2][0] == board[2][2]:
        return board[2][0]

    elif board[0][0] == board[1][0] and board[0][0] == board[2][0]:
        return board[0][0]

    elif board[0][1] == board[1][1] and board[0][1] == board[2][1]:
        return board[0][1]

    elif board[0][2] == board[1][2] and board[0][2] == board[2][2]:
        return board[0][2]

    elif board[0][0] == board[1][1] and board[0][0] == board[2][2]:
        return board[0][0]
    
    elif board[2][0] == board[1][1] and board[2][0] == board[0][2]:
        return board[2][0]
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) or not actions(board):
      return True
    else:
      return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == "X":
        return 1
    elif win == "O":
        return -1
    else: return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    def max_value(board, alpha, beta):
        if terminal(board):
            return utility(board), None
        
        v = float('-inf')
        best_actions = []

        for action in actions(board):
            new_board = result(board, action)
            score,_ = min_value(result(board, action), alpha, beta)          
            
            if score > v:
                v = score
                best_actions = [action]
            elif score == v:
                best_actions.append(action)

            alpha = max(alpha, v)
            if beta <= alpha:
                break  # Beta cutoff
        return v, random.choice(best_actions)
    
    def min_value(board, alpha, beta):
        if terminal(board):
            return utility(board), None
        
        v = float('inf')
        best_actions = []

        for action in actions(board):
            new_board = result(board, action)
            score,_ = max_value(result(board, action), alpha, beta)
            print(f"score is {score} and v is {v}")
            if score < v:
                v = score
                best_actions = [action]
            elif score == v:
                best_actions.append(action)

            beta = min(beta, v)
            if beta <= alpha:
                break  # Alpha cutoff
        return v, random.choice(best_actions)

    current_player = player(board)

    if current_player == "X":
        _, best_move = max_value(board, float('-inf'), float('inf'))
    else:  # current_player == "O"
        _, best_move = min_value(board, float('-inf'), float('inf'))

    return best_move