import sys
import random
import getopt

# Board: array of 9 int, positionally numbered like this:
#  0   1   2   3
#  4   5   6   7
#  8   9  10  11
# 12  13  14  15

# total variants is 16! == 20922789888000

# Well-known board positions
WIND = ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15),
        (0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
        (0, 5, 10, 15), (3, 6, 9, 12))

PRINT_TABLE = ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15))
# The order in which CASES get checked for absence of a player's token:
CASES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)

# Internal-use values.  Chosen so that the "gagnant" of a finished
# game has an appropriate value, as X minimizes and O maximizes
# the board's value (function board_valuation() defines "value")
# Internally, the computer always plays Os, even though the markers[]
# array can change based on -r command line flag.
x_tok = -1
place_empty = 0
o_tok = 1

# Strings for output: player's markers, phrase for end-of-game
MARKERS = ['_', 'O', 'X']
END_PHRASE = ('draw', 'win', 'loss')

HUMAN = 1
COMPUTER = 0

BOARD_WIDTH = 4


def print_board(board):
    """
        Print the board in human-readable format.
        Called with current board (array of 9 ints).
    """
    for row in PRINT_TABLE:
        for hole in row:
            print MARKERS[board[hole]],
        print


def gagnant(board):
    for triad in WIND:
        row_sum = 0
        for cell in triad:
            row_sum += board[cell]

        if abs(row_sum) == BOARD_WIDTH:
            return board[triad[0]]
    return 0


def move_left(board):
    """ Returns True if a legal move remains, False if not. """

    for slot in CASES:
        if board[slot] == place_empty:
            return True
    return False


def board_valuation(board, player, next_player, alpha, beta, depth=0):
    """ Dynamic and static evaluation of board position. """
    # Static evaluation - value for next_player
    wnnr = gagnant(board)
    if wnnr != place_empty:
        # Not a draw or a move left: someone won
        return wnnr
    elif not move_left(board):
        # Draw - no moves left
        return 0  # Cat
    # we need to calc depth level
    # and skip too deep moves
    # or we will never end :)
    elif depth > 5:
        return 0

    # If flow-of-control gets here, no gagnant yet, not a draw.
    # Check all legal moves for "player"
    for move in CASES:
        if board[move] == place_empty:
            board[move] = player
            val = board_valuation(board, next_player, player, alpha, beta, depth + 1)
            board[move] = place_empty
            if player == o_tok:  # Maximizing player
                if val > alpha:
                    alpha = val
                if alpha >= beta:
                    return beta
            else:  # x_tok player, minimizing
                if val < beta:
                    beta = val
                if beta <= alpha:
                    return alpha
    if player == o_tok:
        return alpha
    else:
        return beta


def determine_move(board):
    best_val = -2  # 1 less than min of o_tok, x_tok
    my_moves = []
    for move in CASES:
        if board[move] == place_empty:
            board[move] = o_tok
            val = board_valuation(board, x_tok, o_tok, -2, 2)
            board[move] = place_empty
            if val > best_val:
                best_val = val
                my_moves = [move]
            if val == best_val:
                my_moves.append(move)
    return random.choice(my_moves)


def recv_human_move(board):
    """
        Encapsulate human's input reception and validation.
        Call with current board configuration. Returns
        an int of value 1..9, the Human's move.
    """
    looping = True
    yrmv = -1

    while looping:
        try:
            inp = input("Your move: ")
            yrmv = int(inp)
            if 0 <= yrmv <= 15:
                if board[yrmv] == place_empty:
                    looping = False
                else:
                    print "Spot already filled."
            else:
                print "Bad move, no donut."

        except EOFError:
            print
            sys.exit(0)
        except NameError:
            print "Not 0-9, try again."
        except SyntaxError:
            print "Not 0-9, try again."

        if looping:
            print_board(board)

    return yrmv


def usage(progname):
    """ Call with name of program, to explain its usage. """
    print progname + ": Tic Tac Toe in python"
    print "Usage:", progname, "[-h] [-c] [-r] [-x] [-X]"
    print "Flags:"
    print "-x, -X:   print this usage message, then exit."
    print "-h:  human goes first (default)"
    print "-c:  computer goes first"
    print "-r:  computer is X, human is O"
    print "The computer O and the human plays X by default."


def main():
    """ Call without arguments from __main__ context. """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "chrxX",
                                   ["human", "computer", "help"])
    except getopt.GetoptError:
        # print help information and exit:
        usage(sys.argv[0])
        sys.exit(2)

    next_move = HUMAN  # Human goes first by default

    for opt, arg in opts:
        if opt == "-h":
            next_move = HUMAN
        if opt == "-c":
            next_move = COMPUTER
        if opt == "-r":
            MARKERS[-1] = 'O'
            MARKERS[1] = 'X'
        if opt in ("-x", "-X", "--help"):
            usage(sys.argv[0])
            sys.exit(1)

    # Initial state of board: all open spots.
    board = [place_empty, place_empty, place_empty, place_empty,
             place_empty, place_empty, place_empty, place_empty,
             place_empty, place_empty, place_empty, place_empty,
             place_empty, place_empty, place_empty, place_empty]

    # State machine to decide who goes next, and when the game ends.
    # This allows letting computer or human go first.
    while move_left(board) and gagnant(board) == place_empty:
        print
        print_board(board)

        if next_move == HUMAN and move_left(board):
            humanmv = recv_human_move(board)
            board[humanmv] = x_tok
            next_move = COMPUTER

        if next_move == COMPUTER and move_left(board):
            mymv = determine_move(board)
            print "I choose", mymv
            board[mymv] = o_tok
            next_move = HUMAN

    print_board(board)
    # Final board state/gagnant and congratulatory output.
    try:
        # "You won" should never appear on output: the program
        # should always at least draw.
        print ["nobody win ", "computer won", "You won"][gagnant(board)]
    except IndexError:
        print "tres grave problem, gagnant est", gagnant(board)

    sys.exit(0)


# -------
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print
        sys.exit(1)
