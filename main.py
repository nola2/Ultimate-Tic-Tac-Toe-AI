import math

HUMAN = 'X'
AI = 'O'
EMPTY = '.'

# board[big][small]
board = [[EMPTY for _ in range(9)] for _ in range(9)]
small_status = [EMPTY for _ in range(9)]  # X / O / D / .
next_board = -1  # -1 means any board allowed


def print_board():
    for r in range(3):
        for i in range(3):
            row = []
            for c in range(3):
                b = r * 3 + c
                row.append(" ".join(board[b][i*3:(i+1)*3]))
            print(" | ".join(row))
        if r < 2:
            print("-" * 21)
    print()


def check_win(cells):
    wins = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    for a,b,c in wins:
        if cells[a] == cells[b] == cells[c] != EMPTY:
            return cells[a]
    if EMPTY not in cells:
        return 'D'
    return EMPTY


def update_small_board(b):
    small_status[b] = check_win(board[b])


def check_big_win():
    return check_win(small_status)


def valid_moves():
    moves = []
    if next_board != -1 and small_status[next_board] == EMPTY:
        boards = [next_board]
    else:
        boards = [i for i in range(9) if small_status[i] == EMPTY]

    for b in boards:
        for i in range(9):
            if board[b][i] == EMPTY:
                moves.append((b, i))
    return moves


def evaluate():
    result = check_big_win()
    if result == AI:
        return 100
    if result == HUMAN:
        return -100
    return 0


def minimax(depth, alpha, beta, maximizing):
    score = evaluate()
    if abs(score) == 100 or depth == 0:
        return score

    if maximizing:
        best = -math.inf
        for b, i in valid_moves():
            board[b][i] = AI
            prev = next_board
            update_small_board(b)
            nb = i if small_status[i] == EMPTY else -1
            globals()['next_board'] = nb

            best = max(best, minimax(depth-1, alpha, beta, False))
            alpha = max(alpha, best)

            board[b][i] = EMPTY
            small_status[b] = EMPTY
            globals()['next_board'] = prev

            if beta <= alpha:
                break
        return best
    else:
        best = math.inf
        for b, i in valid_moves():
            board[b][i] = HUMAN
            prev = next_board
            update_small_board(b)
            nb = i if small_status[i] == EMPTY else -1
            globals()['next_board'] = nb

            best = min(best, minimax(depth-1, alpha, beta, True))
            beta = min(beta, best)

            board[b][i] = EMPTY
            small_status[b] = EMPTY
            globals()['next_board'] = prev

            if beta <= alpha:
                break
        return best


def ai_move():
    best_score = -math.inf
    best_move = None

    for b, i in valid_moves():
        board[b][i] = AI
        prev = next_board
        update_small_board(b)
        nb = i if small_status[i] == EMPTY else -1
        globals()['next_board'] = nb

        score = minimax(3, -math.inf, math.inf, False)

        board[b][i] = EMPTY
        small_status[b] = EMPTY
        globals()['next_board'] = prev

        if score > best_score:
            best_score = score
            best_move = (b, i)

    return best_move


# ---------------- MAIN GAME ----------------
print("Ultimate Tic-Tac-Toe (Human = X, AI = O)")
print_board()

while True:
    # Human move
    while True:
        b, i = map(int, input("Enter board (0-8) and cell (0-8): ").split())
        if (b, i) in valid_moves():
            break
        print("Invalid move. Try again.")

    board[b][i] = HUMAN
    update_small_board(b)
    next_board = i if small_status[i] == EMPTY else -1
    print_board()

    if check_big_win() == HUMAN:
        print("Human wins!")
        break

    if not valid_moves():
        print("Draw!")
        break

    # AI move
    b, i = ai_move()
    print(f"AI plays: Board {b}, Cell {i}")
    board[b][i] = AI
    update_small_board(b)
    next_board = i if small_status[i] == EMPTY else -1
    print_board()

    if check_big_win() == AI:
        print("AI wins!")
        break

    if not valid_moves():
        print("Draw!")
        break
