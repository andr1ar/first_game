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
SHAPES = [L, LINE, SQUARE]

GRID = 8
tray_y = GRID * CELL + 30
screen = pygame.display.set_mode((GRID * CELL, GRID * CELL +150))

board = [[0] * GRID for _ in range(GRID)]
pieces = [random.choice(SHAPES) for _ in range(3)]
BLOCK_COLOR = (0, 200, 255)
COLORS = [(0, 200, 255), (0, 255, 0), (255, 0, 0)]
tray_x = [20, 150, 300]
slides = [animation.Animation(150, 0, 0.4 + i * 0.2) for i in range(3)]
effects = [animation.popeffect(0, 0, CELL, color) for color in COLORS]
pieces[0] = {"shape": L, "x": 20, "y": tray_y, "color": (0, 200, 255)}
pieces[1] = {"shape": LINE, "x": 140, "y": tray_y, "color": (0, 255, 0)}
pieces[2] =                                                                                                                                                                                                                                                                                       {"shape": SQUARE, "x": 300, "y": tray_y, "color": (255, 0, 0)}

dragging = None
offset_x = 0
offset_y = 0


def draw_board():
    for row in range(GRID):
        for col in range(GRID):
            color = (0, 200, 255) if board[row][col] == 1 else (40, 40, 50)
            pygame.draw.rect(screen, color, (col *CELL + 1, row * CELL + 1, CELL - 2, CELL - 2))

def draw_piece(shape, x, y, color):
    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c] == 1:
                pygame.draw.rect(screen, color, (x + c * CELL, y + r * CELL, CELL - 2, CELL - 2))

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            col, row = mx // CELL, my // CELL
            if 0 <= row < GRID and 0 <= col < GRID:
                if board[row][col] == 1:
                    board[row][col] = 0
                    effects.append(animation.popeffect(row, col, CELL, BLOCK_COLOR))
                else:
                    board[row][col] = 1
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for p in pieces:
                w = len(p["shape"][0]) * CELL
                h = len(p["shape"]) * CELL
                if p["x"]  <= mx <= p["x"] + w and p["y"] <= my <= p["y"] + h:
                    dragging = p
                    offset_x = mx - p["x"]
                    offset_y = my - p["y"]
        elif event.type == pygame.MOUSEMOTION and dragging:
            dragging['x'] = event.pos[0] - offset_x
            dragging["y"] = event.pos[1] - offset_y      
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = None  
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
        draw_piece(p["shape"], p["x"], p["y"] + slides[i].value, p["color"])
    pygame.display.flip()

pygame.quit()




