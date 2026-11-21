import random

import pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))
running = True
CELL = 50
L = [[1,0],[1,1]]
LINE = [[1,1,1]]
SQUARE = [[1,1],[1,1]]
SHAPES = [L, LINE, SQUARE]

GRID = 8
screen = pygame.display.set_mode((GRID * CELL, GRID * CELL +150))

board = [[0] * GRID for _ in range(GRID)]
pieces = [random.choice(SHAPES) for _ in range(3)]

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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))
    draw_piece(L, 50, 50, (0, 200, 255))
    draw_piece(LINE, 150, 50, (0, 255, 0))
    draw_piece(SQUARE, 250, 50, (255, 0, 0))
    pygame.display.flip()

pygame.quit()




def draw_piece(shape, x, y, color):
    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c] == 1:
                pygame.draw.rect(screen, color, (x + c * CELL, y + r * CELL, CELL - 2, CELL - 2))