import random

import pygame

import animation

pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
running = True
CELL = 50
L = [[1,0],[1,1]]
LINE = [[1,1,1]]
SQUARE = [[1,1],[1,1]]
SHAPES = [
    L, LINE, SQUARE,
    [[1]],
    [[1]], [[1], [1]],
    [[1], [1], [1]],
    [[1, 1, 1, 1]], [[1], [1], [1], [1]],
    [[1, 1, 1, 1, 1]], [[1], [1], [1], [1], [1]],
    [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
    [[1, 1, 1], [1, 1, 1], [1, 1, 1]], [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[0, 1], [1, 1]], [[1, 1], [0, 1]], [[1, 1], [1, 0]]
    ]
PIECE_COLORS = [(0, 200, 255), (0, 255, 0), (255, 60, 60), (255, 200, 0),
                (180, 80, 255), (255, 120, 0), (255, 80, 160), (80, 255, 200)]

GRID = 8
tray_y = GRID * CELL + 30

MARGIN = 40
BOARD_X = MARGIN
BOARD_Y = 60
WIDTH = GRID * CELL + MARGIN * 2
TRAY_Y = BOARD_Y + GRID * CELL + 30
HEIGHT = TRAY_Y + 170
screen = pygame.display.set_mode((WIDTH,  HEIGHT))
board = [[0] * GRID for _ in range(GRID)]
pieces = [random.choice(SHAPES) for _ in range(3)]
TRAY_CELL = 26
BLOCK_POINTS = 10
LINE_POINTS = 100
score = 0
font = pygame.font.SysFont(None, 36)
BLOCK_COLOR = (0, 200, 255)
COLORS = [(0, 200, 255), (0, 255,0), (255, 0, 0)]
game_over = False
tray_x = [20, 150, 300]
slides = [animation.Animation(150, 0, 0.4 + i * 0.2) for i in range(3)]
effects = [animation.popeffect(0, 0, CELL, color) for color in COLORS]                                                                                                                                                                                                                                                                         

dragging = None
offset_x = 0
offset_y = 0


def draw_board():
    panel = (BOARD_X - 8, BOARD_Y - 8, GRID * CELL +16, GRID * CELL + 16)
    pygame.draw.rect(screen, (20, 20, 40), panel, border_radius=12)
    for row in range(GRID):
        for col in range(GRID):
            color = (0, 200, 255) if board[row][col] == 1 else (40, 40, 50)
            pygame.draw.rect(screen, color, (BOARD_X + col * CELL + 1, BOARD_Y + row * CELL + 1, CELL -2, CELL -2))
    screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (MARGIN, 15))

def draw_piece(shape, x, y, color, size=CELL):
    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c] == 1:
                pygame.draw.rect(screen, color, (int(x + c * size), int(y + r * size), size -2, size -2))
def make_pieces():
    result = []
    slot_w = WIDTH // 3
    for i in range(3):
        k = random.randrange(len(SHAPES))
        shape = SHAPES[k]
        w = len(shape[0]) * CELL
        h = len(shape) * TRAY_CELL
        x = i * slot_w + (slot_w - w) // 2
        y = TRAY_Y + (150 - h) // 2
        slot_w = GRID * CELL // 3
        result.append({
            "shape": shape,
            "color": PIECE_COLORS[k % len(PIECE_COLORS)],
            "x": x,
            "y": y,
            "home_x": x,
            "home_y": y,
        })
    return result

pieces = make_pieces()
def slot_rect(i):
    w = GRID * CELL // 3
    return pygame.Rect(i * w, TRAY_Y + 40, w, 110)
def can_place(shape, row, col):
    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c] == 1:
                rr, cc = row + r, col + c
                if rr < 0 or rr >= GRID or cc < 0 or cc >= GRID:
                    return False
                if board[rr][cc] == 1:
                    return False
    return True       
def place_piece(shape, row, col):
    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c] == 1:
                board[row + r][col + c] = 1
def clear_lines():
    full_rows = [r for r in range(GRID) if all(board[r][c] == 1 for c in range(GRID))]
    full_cols = [c for c in range(GRID) if all(board[r][c] == 1 for r in range(GRID))]
    for r in full_rows:
        for c in range(GRID):
            board[r][c] = 0
    for c in full_cols:
        for r in range(GRID):
            board[r][c] = 0
    return len(full_rows) + len(full_cols) 
def fits_anywhere(shape):
    for row in range(GRID):
        for col in range(GRID):
            if can_place(shape, row, col):
                return True
        return False
def snap_position(shape, mx, my):
    w = len(shape[0])
    h = len(shape)
    col = round((mx - w * CELL / 2) / CELL)
    row = round((my - h * CELL / 2) / CELL)
    return row, col
def draw_tray():
    for i in range(3):
        shape = pieces[i]
        if shape is None or i == dragging:
            continue
        rect = slot_rect(i)
        w = len(shape[0]) * TRAY_CELL
        h = len(shape) * TRAY_CELL
        draw_piece(shape, rect.x + (rect.w - w) // 2, rect.y + (rect.h - h) // 2, COLORS[SHAPES.index(shape)], TRAY_CELL)

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            board = [[0] * GRID for _ in range (GRID)]
            pieces = make_pieces()
            score = 0
            dragging = None
            game_over = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            slot_w = WIDTH // 3
            for i in range(3):
                p = pieces[i]
                if p is None:
                    continue
                if i * slot_w <= event.pos[0] < (i + 1) * slot_w and event.pos[1] >= TRAY_Y - 20:
                    dragging = i
                    offset_x = len(p["shape"][0]) * CELL // 2
                    offset_y = len(p["shape"]) * CELL // 2
                    p["x"] = event.pos[0] - offset_x
                    p["y"] = event.pos[1] - offset_y
                    break
        elif event.type == pygame.MOUSEMOTION and dragging is not None:
            pieces[dragging]["x"] = event.pos[0] - offset_x
            pieces[dragging]["y"] = event.pos[1] - offset_y
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging is not None:
            p = pieces[dragging]
            row = round((p["y"] - BOARD_Y) / CELL)
            col = round((p["x"] - BOARD_X) / CELL)
            if can_place(p["shape"], row,col):
               place_piece(p["shape"], row, col)
               score += sum(sum(line) for line in p["shape"]) * BLOCK_POINTS
               score += clear_lines() * LINE_POINTS
               pieces[dragging] = None
               if all(q is None for q in pieces):
                   pieces = make_pieces()
               if not any(q is not None and fits_anywhere(q["shape"]) for q in pieces):     
                   game_over = True
            else:
                p["x"], p["y"] = p["home_x"], p["home_y"]
            dragging = None
        for i, p in enumerate(pieces):
            if p is None:
                continue
            draw_piece(p["shape"], p["x"], p["y"] + slides[i].value, p["color"])
    for s in slides:
         s.update(dt)
    for fx in effects:
            fx.update(dt)
    effects = [fx for fx in effects if not fx.finished]  
    screen.fill((30, 30, 30))
    draw_board()
    for fx in effects:
        fx.draw(screen) 
    for i, p in enumerate(pieces):
        if p is None:
            continue
        size = CELL if i == dragging else TRAY_CELL
        draw_piece(p["shape"], p["x"], p["y"] +  slides[i].value, p["color"], size)
    if game_over:
        text = font.render("GAME OVER - press R", True, (255, 255, 255))
        screen.blit(text, ((GRID * CELL - text.get_width()) // 2, 180))
    background = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
            t = y / HEIGHT
            pygame.draw.line(background, (int(25 + 45 * t), int(15 + 20 * t), int(60 + 70 * t)), (0, y), (WIDTH, y))
    
            bubble_colors = [(255, 100, 180), (100, 220, 255), (255, 220, 100),  (140, 255, 160)]
            bubbles = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(9, 30), random.uniform(10, 30)] for _ in range(14)]
    
    def draw_background():
            screen.blit(background, (0, 0))
            layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for i, b in enumerate(bubbles):
                b[1] -= b[3] / 60
                if b[1] < -b[2]:
                    b[1] = HEIGHT + b[2]
                    b[0] = random.randint(0, WIDTH)
                pygame.draw.circle(layer, bubble_colors[i % 4] + (50,), (int(b[0])), (int(b[1])), b[2])
            screen.blit(layer, (0, 0))
        
    pygame.display.flip()

pygame.quit()




