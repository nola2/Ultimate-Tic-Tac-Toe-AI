import pygame
import math
import sys
import copy

pygame.init()

# ===================== UI CONSTANTS =====================
WIDTH = HEIGHT = 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Tic Tac Toe AI")
CLOCK = pygame.time.Clock()

COLORS = {
    "bg": (254, 250, 236),
    "grid": (7, 5, 14),
    "x": (129, 43, 56),
    "o": (36, 32, 95),
    "highlight": (220, 215, 170),
    "overlay": (0, 0, 0, 200)   # darker overlay
}

# ===================== GAME CONSTANTS =====================
HUMAN = -1
AI = 1
EMPTY = 0
DRAW = 2

WIN_LINES = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]

# ===================== GAME STATE =====================
boards = [[EMPTY]*9 for _ in range(9)]
small_status = [EMPTY]*9
small_win_line = [None]*9
active_board = -1
current_turn = HUMAN
game_over = None

# ===================== GAME LOGIC =====================
def check_small_win(b, p):
    for line in WIN_LINES:
        a,c,d = line
        if boards[b][a] == boards[b][c] == boards[b][d] == p:
            small_win_line[b] = line
            return True
    return False

def is_small_full(b):
    return all(x != EMPTY for x in boards[b])

def check_big_win():
    for a,b,c in WIN_LINES:
        if small_status[a] == small_status[b] == small_status[c] and small_status[a] in (HUMAN, AI):
            return small_status[a]
    if all(x != EMPTY for x in small_status):
        return DRAW
    return None

def get_valid_moves():
    moves = []
    if active_board != -1 and small_status[active_board] == EMPTY:
        for i in range(9):
            if boards[active_board][i] == EMPTY:
                moves.append((active_board, i))
        return moves

    for b in range(9):
        if small_status[b] == EMPTY:
            for i in range(9):
                if boards[b][i] == EMPTY:
                    moves.append((b, i))
    return moves

def make_move(b, c, p):
    global active_board, game_over
    boards[b][c] = p

    if check_small_win(b, p):
        small_status[b] = p
    elif is_small_full(b):
        small_status[b] = DRAW

    active_board = c if small_status[c] == EMPTY else -1
    game_over = check_big_win()

# ===================== AI =====================
def evaluate():
    result = check_big_win()
    if result == AI: return 10000
    if result == HUMAN: return -10000
    if result == DRAW: return 0

    score = 0
    for i in range(9):
        if small_status[i] == AI: score += 200
        elif small_status[i] == HUMAN: score -= 200

    for a,b,c in WIN_LINES:
        line = [small_status[a], small_status[b], small_status[c]]
        if line.count(AI) == 2 and line.count(EMPTY) == 1:
            score += 500
        if line.count(HUMAN) == 2 and line.count(EMPTY) == 1:
            score -= 500
    return score

def minimax(depth, alpha, beta, maximizing):
    val = evaluate()
    if abs(val) >= 9000 or depth == 0:
        return val

    if maximizing:
        best = -math.inf
        for b,c in get_valid_moves():
            backup = copy.deepcopy((boards, small_status, small_win_line, active_board))
            make_move(b, c, AI)
            best = max(best, minimax(depth-1, alpha, beta, False))
            boards[:], small_status[:], small_win_line[:], globals()["active_board"] = copy.deepcopy(backup)
            alpha = max(alpha, best)
            if beta <= alpha: break
        return best
    else:
        best = math.inf
        for b,c in get_valid_moves():
            backup = copy.deepcopy((boards, small_status, small_win_line, active_board))
            make_move(b, c, HUMAN)
            best = min(best, minimax(depth-1, alpha, beta, True))
            boards[:], small_status[:], small_win_line[:], globals()["active_board"] = copy.deepcopy(backup)
            beta = min(beta, best)
            if beta <= alpha: break
        return best

def ai_move():
    best_val = -math.inf
    best = None
    for b,c in get_valid_moves():
        backup = copy.deepcopy((boards, small_status, small_win_line, active_board))
        make_move(b, c, AI)
        val = minimax(3, -math.inf, math.inf, False)
        boards[:], small_status[:], small_win_line[:], globals()["active_board"] = copy.deepcopy(backup)
        if val > best_val:
            best_val = val
            best = (b, c)
    return best

# ===================== DRAWING =====================
def draw_small_win_lines():
    size = WIDTH // 3
    cell = size // 3

    for b in range(9):
        if small_win_line[b]:
            a,c,d = small_win_line[b]
            bx = (b % 3) * size
            by = (b // 3) * size

            ax = bx + (a % 3) * cell + cell//2
            ay = by + (a // 3) * cell + cell//2
            dx = bx + (d % 3) * cell + cell//2
            dy = by + (d // 3) * cell + cell//2

            color = COLORS["x"] if small_status[b] == AI else COLORS["o"]
            pygame.draw.line(SCREEN, color, (ax, ay), (dx, dy), 5)

def draw_big_win_line(winner):
    size = WIDTH // 3
    center = size // 2

    for a,b,c in WIN_LINES:
        if small_status[a] == small_status[b] == small_status[c] == winner:
            ax, ay = (a % 3) * size + center, (a // 3) * size + center
            cx, cy = (c % 3) * size + center, (c // 3) * size + center
            pygame.draw.line(
                SCREEN,
                COLORS["x"] if winner == AI else COLORS["o"],
                (ax, ay), (cx, cy), 8
            )

def draw_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(COLORS["overlay"])
    SCREEN.blit(overlay, (0,0))

def draw_game_result():
    font = pygame.font.SysFont("Arial", 96, True)
    text = "AI Wins!" if game_over == AI else "You Win!" if game_over == HUMAN else "Draw!"
    surf = font.render(text, True, (255,255,255))
    SCREEN.blit(surf, surf.get_rect(center=(WIDTH//2, HEIGHT//2)))

def draw():
    SCREEN.fill(COLORS["bg"])
    size = WIDTH // 3
    cell = size // 3

    if active_board != -1:
        bx = (active_board % 3) * size
        by = (active_board // 3) * size
        pygame.draw.rect(SCREEN, COLORS["highlight"], (bx, by, size, size))


    for i in range(1,3):
        pygame.draw.line(SCREEN, COLORS["grid"], (i*size,0),(i*size,HEIGHT),3)
        pygame.draw.line(SCREEN, COLORS["grid"], (0,i*size),(WIDTH,i*size),3)

    for b in range(9):
        bx = (b % 3) * size
        by = (b // 3) * size
        for i in range(1,3):
            pygame.draw.line(SCREEN, COLORS["grid"], (bx+i*cell,by),(bx+i*cell,by+size),1)
            pygame.draw.line(SCREEN, COLORS["grid"], (bx,by+i*cell),(bx+size,by+i*cell),1)

    font = pygame.font.SysFont(None, 40)
    big_font = pygame.font.SysFont(None, 110)

    for b in range(9):
        if small_status[b] in (AI, HUMAN):
            cx = (b%3)*size + size//2
            cy = (b//3)*size + size//2
            txt = "X" if small_status[b]==AI else "O"
            col = COLORS["x"] if txt=="X" else COLORS["o"]
            SCREEN.blit(big_font.render(txt, True, col),
                        big_font.render(txt, True, col).get_rect(center=(cx,cy)))

        for c in range(9):
            v = boards[b][c]
            if v != EMPTY:
                x = (b%3)*size + (c%3)*cell + cell//2
                y = (b//3)*size + (c//3)*cell + cell//2
                txt = "X" if v==AI else "O"
                col = COLORS["x"] if txt=="X" else COLORS["o"]
                SCREEN.blit(font.render(txt, True, col),
                            font.render(txt, True, col).get_rect(center=(x,y)))

    draw_small_win_lines()

    if game_over is not None:
        if game_over in (AI, HUMAN):
            draw_big_win_line(game_over)
        draw_overlay()
        draw_game_result()

    pygame.display.flip()

# ===================== MAIN LOOP =====================
while True:
    CLOCK.tick(60)
    draw()

    if game_over is not None:
        pygame.time.delay(30000)
        pygame.quit()
        sys.exit()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.MOUSEBUTTONDOWN and current_turn == HUMAN:
            mx, my = pygame.mouse.get_pos()
            size = WIDTH // 3
            cell = size // 3
            b = (mx//size) + (my//size)*3
            c = ((mx%size)//cell) + ((my%size)//cell)*3

            if (b,c) in get_valid_moves():
                make_move(b, c, HUMAN)
                current_turn = AI

    if current_turn == AI and game_over is None:
        move = ai_move()
        if move:
            make_move(move[0], move[1], AI)
        current_turn = HUMAN
