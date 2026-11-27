import random

import os

import math

import copy

import pygame

import animation

pygame.init()
pygame.mixer.init()

def load_sound(name, vol=1.0):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    try:
        s = pygame.mixer.Sound(path)
        s.set_volume(vol)
        return s
    except (pygame.error, FileNotFoundError):
        return None
def play(s):
    if s:
        s.play()

pick_snd = load_sound("pick.wav", 0.5)
place_snd = load_sound("place.wav", 0.7)
lava_snd = load_sound("lava.wav", 0.3)
lose_snd = load_sound("lose.wav", 0.8)
explosion_snd = load_sound("explosion.mp3", 0.8)
freeze_snd = load_sound("freeze.mp3", 1.0)
perfect_snd = load_sound("perfect.mp3", 0.8)
purple_snd = load_sound("purple.mp3", 0.8)
rewind_snd = load_sound("rewind.mp3", 1.0)
snap_snd = load_sound("snap", 0.8)
over9000_snd = load_sound("over9000", 0.7)

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
PIECE_COLORS = [(255, 120, 0), (255, 200, 0), (255, 60, 30), (255, 150, 40),
                (220, 40, 40), (255, 90, 0), (255, 230, 90), (200, 60, 0)]

GRID = 8
tray_y = GRID * CELL + 30

WIDTH_ = GRID * CELL
top = 100
MARGIN = 40
BOARD_X = MARGIN
BOARD_Y = 60 + top
WIDTH = GRID * CELL + MARGIN * 2
TRAY_Y = BOARD_Y + GRID * CELL + 30
HEIGHT = TRAY_Y + 170 + top
screen = pygame.display.set_mode((WIDTH,  HEIGHT))
board = [[0] * GRID for _ in range(GRID)]
pieces = [random.choice(SHAPES) for _ in range(3)]
lava_height = 0.0
heat_smooth = 0.0
lava_progress = 0.0
lava_interval = random.choice([4, 5])
turns = 0
game_over = False
dragging = None
mouse_x, mouse_y = 0, 0
font = pygame.font.SysFont(None, 26)
freeze_turns = 0
power_up = None
bomb_active = False
rounds = 0
timestop_timer = 0.0
TIMESTOP_TIME = 1.0
TRAY_CELL = 26
BLOCK_POINTS = 10
LINE_POINTS = 100
score = 0
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.txt")
try:
    with open(SAVE_FILE) as f:
        best = int(f.read())
except (FileNotFoundError, ValueError):
    best = 0
font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont("impact", 64)
def make_title(text):
    core = title_font.render(text, True, (255, 210, 50))
    edge = title_font.render(text, True, (150, 29, 0))
    glow = title_font.render(text, True, (255, 90, 0))
    size = (core.get_width() + 80, core.get_height() + 80)
    glow_layer = pygame.Surface(size, pygame.SRCALPHA)
    text_layer = pygame.Surface(size, pygame.SRCALPHA)
    cx, cy = size[0] // 2, size[1] // 2
    for size, alpha in [(14, 25), (9, 50), (5, 90)]:
        glow.set_alpha(alpha)
        for dx in range(-size, size + 1, 3):
            for dy in range(-size, size + 1, 3):
                glow_layer.blit(glow, glow.get_rect(center=(cx + dx, cy + dy)))
    text_layer.blit(edge, edge.get_rect(center=(cx + 3, cy + 4)))
    text_layer.blit(core, core.get_rect(center=(cx, cy)))
    return glow_layer, text_layer
glow_layer, text_layer = make_title("LAVA BLAST")
BLOCK_COLOR = (0, 200, 255)
COLORS = [(0, 200, 255), (0, 255,0), (255, 0, 0)]
game_over = False
banner_timer = 0
tray_x = [20, 150, 300]
slides = [animation.Animation(150, 0, 0.4 + i * 0.2) for i in range(3)]
effects = []                                                                                                                                                                                                                                                                     

dragging = None
offset_x = 0
offset_y = 0

def playable_rows():
    return max(0, GRID - int(lava_height))
def can_place(shape, row, col):
    pr = playable_rows()
    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c] == 1:
                rr, cc = row + r, col + c
                if rr < 0 or rr >= pr or cc < 0 or cc >= GRID or board[rr][cc] == 1:
                    return False
    return True
def draw_board():
    pygame.draw.rect(screen, (110, 28, 0),
                     (BOARD_X - 8, BOARD_Y - 8, GRID * CELL + 16, GRID * CELL + 16),
                     border_radius=12)
    for row in range(GRID):
        for col in range(GRID):
            x = BOARD_X + col * CELL + 1
            y = BOARD_Y + row * CELL + 1
            if board[row][col] == 1:
                pygame.draw.rect(screen, (255, 110, 0), (x, y, CELL - 2, CELL - 2))
                pygame.draw.rect(screen, (255, 175, 30), (x + 8, y + 8, CELL - 18, CELL - 18))
            else:
                pygame.draw.rect(screen, (45, 18, 18), (x, y, CELL - 2, CELL - 2))
    h = min(GRID * CELL, int(lava_height * CELL))
    if h > 0:
        t = anim_time * 2.5
        w = GRID * CELL
        top = [(x, 4 + math.sin(x / 25 + t) * 3) for x in range(0, w + 1, 5)]
        lava = pygame.Surface((w, h + 8), pygame.SRCALPHA)
        if freeze_turns > 0:
            body_color = (80, 190, 255, 170)
            edge_color = (200, 245, 255)
        else:
            body_color = (255, 100, 0, 170)
            edge_color = (255, 210, 0)
        pygame.draw.polygon(lava, body_color, top + [(w, h + 8), (0, h + 8 )])
        pygame.draw.lines(lava, edge_color, False, top, 4)
        screen.blit(lava, (BOARD_X, BOARD_Y + w - h - 4))

def draw_hud():
    best_text = font.render(f"Best: {shown_best}", True, (255, 220, 100))
    screen.blit(best_text, (WIDTH - MARGIN - best_text.get_width(), 15 + top))
    screen.blit(font.render(f"Score: {shown_score}", True, (255, 255, 255)), (MARGIN, 15 + top))
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
        w = len(shape[0]) * TRAY_CELL
        h = len(shape) * TRAY_CELL
        x = i * slot_w + (slot_w - w) // 2
        y = TRAY_Y + (150 - h) // 2
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
rounds += 1
if rounds % 2 == 0 and power_up is None:
    power_up = random.choice(["freeze", "bomb"])
def slot_rect(i):
    w = GRID * CELL // 3
    return pygame.Rect(i * w, TRAY_Y + 40, w, 110)
def any_move_possible():
    for p in pieces:
        if p is None:
            continue
        for r in range(GRID):
            for c in range(GRID):
                if can_place(p, r, c):
                    return False
    return True
def board_empty():
    return all(board[r][c] == 0 for r in range(playable_rows()) for c in range(GRID))
def tray_rect(i):
    return pygame.Rect(i * (WIDTH_ // 3), GRID * CELL + 40, WIDTH_ // 3, 110)
def explode(row, col):
    play(explosion_snd)
    for r in range(row - 1, row + 2):
        for c in range(col - 1, col + 2):
            if 0 <= r < len(board) and 0 <= c < len(board[0]):
                board[r][c] = 0
    explosions.append([BOARD_X + col * CELL + CELL // 2,
                       BOARD_Y + row * CELL + CELL // 2,
                       EXPLOSION_TIME])
def hollow_purple(row, col):
    play(purple_snd)
    play(explosion_snd)
    for i in range(GRID):
        board[row][i] = 0
        board[i][col] = 0
    purple_fx.append([row, col, 0.7])
def thanos_snap():
    plau(snap_sound)
    global snap_text_timer
    play(explosion_snd)
    filled = [(r, c) for r in range(GRID) for c in range(GRID) if board[r][c] == 1]
    for r, c in random.sample(filled, len(filled) // 2):
        board[r][c] = 0
        for _ in range(6):
            dust.append([BOARD_X + c * CELL + random.randint(0, CELL),
            BOARD_Y + r * CELL + random.randint(0, CELL),
            random.uniform(20, 80), random.uniform(-70, -10),
            random.uniform(0.6, 1.2)])
    snap_text_timer = 1.5
def place_piece(shape, row, col):
    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c] == 1:
                board[row + r][col + c] = 1
def clear_lines():
    pr = playable_rows()
    full_rows = [r for r in range(GRID) if all(board[r][c] == 1 for c in range(GRID))]
    full_cols = [c for c in range(GRID) if pr > 0 and all(board[r][c] == 1 for r in range(pr))]
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
        
if lava_snd:
    lava_snd.play(-1)

power_rect = pygame.Rect(WIDTH // 2 - 60, TRAY_Y + 165, 120, 40)
power_font = pygame.font.SysFont(None, 26)
explosions = []
EXPLOSION_TIME = 0.5
anim_time = 0.0
shown_score = 0
shown_best = best
POWERUPS = ["freeze", "bomb", "rewind", "snap", "purple"]
purple_active = False
last_state = None
rewind_timer = 0.0
REWIND_TIME = 1.0
over9000_shown = False
over9000_timer = 0.0
snap_text_timer = 0.0
dust = []
purple_fx = []
over_font = pygame.font.SysFont("impact", 46)

running = True
while running:
    dt = clock.tick(60) / 1000
    if freeze_turns == 0 or game_over:
        shown_score = score
        shown_best = best
    if freeze_turns == 0:
        anim_time += dt
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            board = [[0] * GRID for _ in range (GRID)]
            pieces = make_pieces()
            score = 0
            dragging = None
            game_over = False
            lava_height = 0.0
            lava_progress = 0.0
            lava_interval = random.choice([4, 5])
            turns = 0
            power_up = None
            freeze_turns = 0
            bomb_active = False
            timestop_timer = 0.0
            rounds = 1
            purple_active = False
            last_state = None
            rewind_timer = 0.0
            over9000_shown = False
            over9000_timer = 0.0
            snap_text_timer = 0.0
            dust.clear()
            purple_fx.clear()
            explosions.clear()
            if lava_snd:
                lava_snd.stop()
                lava_snd.play(-1)
                lava_snd.set_volume(0.15)
        elif event.type == pygame.MOUSEBUTTONDOWN and bomb_active and (event.button == 3 or (event.button == 1 and power_rect.collidepoint(event.pos))):
            bomb_active = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and bomb_active:
            row = (event.pos[1] - BOARD_Y) // CELL
            col = (event.pos[0] - BOARD_X) // CELL
            if 0 <= row < len(board) and 0 <= col < len(board[0]):
                explode(row, col)
                bomb_active = False
                power_up = None
        elif event.type == pygame.MOUSEBUTTONDOWN and purple_active and (event.button == 3 or (event.button == 1 and power_rect.collidepoint(event.pos))):
                    purple_active = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and purple_active:
                    row = (event.pos[1] - BOARD_Y) // CELL
                    col = (event.pos[0] - BOARD_X) // CELL
                    if 0 <= row < GRID and 0 <= col < GRID:
                        hollow_purple(row, col)
                        purple_active = False
                        power_up = None
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and power_rect.collidepoint(event.pos) and power_up:
            if power_up == "freeze":
                freeze_turns = 5
                play(freeze_snd)
                timestop_timer = TIMESTOP_TIME
                power_up = None
            elif power_up == "bomb":
                bomb_active = True
            elif power_up == "purple":
                purple_active = True
            elif power_up == "snap":
                thanos_snap()
                power_up = None
            elif power_up == "rewind" and last_state:
                play(rewind_snd)
                board = last_state["board"]
                pieces = last_state["pieces"]
                score = last_state["score"]
                lava_height = last_state["lava_height"]
                lava_progress = last_state["lava_progress"]
                lava_interval = last_state["lava_interval"]
                turns = last_state["turns"]
                freeze_turns = last_state["freeze_turns"]
                for q in pieces:
                    if q:
                        q["x"], q["y"] = q["home_x"], q["home_y"]
                    if game_over and lava_snd:
                        lava_snd.play(-1)
                    game_over = False
                    rewind_timer = REWIND_TIME
                    last_state = None
                    power_up = None

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            slot_w = WIDTH // 3
            for i in range(3):
                p = pieces[i]
                if p is None:
                    continue
                if i * slot_w <= event.pos[0] < (i + 1) * slot_w and event.pos[1] >= TRAY_Y - 20:
                    dragging = i
                    play(pick_snd)
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
               last_state = {"board": copy.deepcopy(board), "pieces": copy.deepcopy(pieces),
                                         "score": score, "lava_height": lava_height,
                                         "lava_progress": lava_progress, "lava_interval": lava_interval,
                                         "turns": turns, "freeze_turns": freeze_turns}
               place_piece(p["shape"], row, col)
               play(place_snd)
               gained = sum(sum(line) for line in p["shape"]) * BLOCK_POINTS
               cleared = clear_lines()
               gained += cleared * LINE_POINTS
               if cleared and not any(any(row) for row in board):
                gained += 3
                banner_timer = 90
                play(perfect_snd)
               score += gained
               if score > 9000 and not over9000_shown:
                   over9000_shown = True
                   over9000_timer = 2.5
                   play(over9000_snd)
               if score > best:
                   best = score
                   with open(SAVE_FILE, "w") as f:
                       f.write(str(best))
               pieces[dragging] = None
               if all (p is None for p in pieces):
                   rounds += 1
               if rounds % 5 == 0 and power_up is None:
                   power_up = random.choice(POWERUPS)
               speed = min(4.0, 1.1 + 0.1 * (turns // 10))
               turns += 1
               for d in dust[:]:
                    d[0] += d[2] * dt
                    d[1] += d[3] * dt
                    d[4] -= dt
                    if d[4] <= 0:
                        dust.remove(d)
                        continue
                    s = pygame.Surface((6, 6), pygame.SRCALPHA)
                    s.fill((170, 160, 160, int(255 * min(1, d[4]))))
                    screen.blit(s, (d[0], d[1]))
               for pf in purple_fx[:]:
                   pf[2] -= dt
                   if pf[2] <= 0:
                       purple_fx.remove(pf)
                       continue
                   a = int(255 * pf[2] / 0.7)
                   beam = pygame.Surface((GRID * CELL, CELL), pygame.SRCALPHA)
                   beam.fill((170, 60, 255, a))
                   screen.blit(beam, (BOARD_X + pf[1] * CELL, BOARD_Y))
               if snap_text_timer > 0:
                   snap_text_timer -= dt
                   t = font.render("PERFECTLY BALANCED", True, (200, 160, 255))
                   t.set_alpha(int(255 * min(1, snap_text_timer)))
                   screen.blit(t, t.get_rect(center=(WIDTH // 2, BOARD_Y + GRID * CELL // 2)))
               if rewind_timer > 0:
                   rewind_timer -= dt
                   rt = 1 - max(rewind_timer, 0) / REWIND_TIME
                   cx, cy = WIDTH // 2, BOARD_Y + GRID * CELL // 2
                   for k in range(3):
                       rad = int((1 - rt) * 250) + k * 45
                       if rad > 0:
                           pygame.draw.circle(screen, (255, 170, 0), (cx, cy), rad, 4)
                   t = font.render("REWIND", True, (255, 200, 60))
                   screen.blit(t, t.get_rect(center=(cx, cy)))
               if over9000_timer > 0:
                over9000_timer -= dt
                sh = int(6 * min(1, over9000_timer))
                ox, oy = random.randint(-sh, sh), random.randint(-sh, sh)
                al = int(255 * min(1, over9000_timer))
                back = over_font.render("IT'S OVER 9000!", True, (200, 30, 0))
                front = over_font.render("IT'S OVER 9000!", True, (255, 230, 60))
                back.set_alpha(al)
                front.set_alpha(al)
                pos = (WIDTH // 2 + ox, BOARD_Y + 120 + oy)
                screen.blit(back, back.get_rect(center=(pos[0] + 3, pos[1] + 3)))
                screen.blit(front, front.get_rect(center=pos))

               if freeze_turns > 0:
                   freeze_turns -= 1
               else:
                   speed = min(4.0, 1.1 + 0.1 * (turns // 10))
                   lava_progress += speed
                   while lava_progress >= lava_interval:
                       lava_progress -= lava_interval
                       lava_height += 1
                       lava_interval = random.choice([4, 5])
               if cleared:
                   lava_height = max(0.0, lava_height - 0.5 * cleared)
                   if board_empty():
                       lava_height = 0.0
                       lava_progress = 0.0
               for r in range(playable_rows(), GRID):
                   board[r] = [0] * GRID
               if lava_snd:
                   lava_snd.set_volume(min(0.5, 0.15 + lava_height * 0.04))
               if all(q is None for q in pieces):
                   pieces = make_pieces()
               if not any(q is not None and fits_anywhere(q["shape"]) for q in pieces):
                   game_over = True
                   play(lose_snd)
                   if lava_snd:
                       lava_snd.stop()
            else:
                p["x"], p["y"] = p["home_x"], p["home_y"]
            dragging = None
    for s in slides:
         s.update(dt)
    for fx in effects:
            fx.update(dt)
    effects = [fx for fx in effects if not fx.finished]  
    heat = min(1.0, lava_height / 6)
    heat_smooth += (heat - heat_smooth) * min(1, dt * 3)
    screen.fill((int(25 + 70 * heat_smooth), int(5 + 12 * heat_smooth), 5))

    pulse = (math.sin(anim_time * 2.857) + 1) / 2
    glow_layer.set_alpha(int(100 + 155 * pulse))
    title_rect = glow_layer.get_rect(center=(WIDTH // 2, top // 2 + 5))
    screen.blit(glow_layer, title_rect)
    screen.blit(text_layer, title_rect)
    draw_board()
    for fx in effects:
        fx.draw(screen) 
    draw_hud()
    if dragging is not None:
        gp = pieces[dragging]
        grow = round((gp["y"] - BOARD_Y) / CELL)
        gcol = round((gp["x"] - BOARD_X) / CELL)
        if can_place(gp["shape"], grow, gcol):
            ghost = pygame.Surface((CELL - 2, CELL - 2), pygame.SRCALPHA)
            ghost.fill((255, 230, 120, 110))
            for r in range(len(gp["shape"])):
                for c in range(len(gp["shape"][r])):
                    if gp["shape"][r][c] == 1:
                        screen.blit(ghost, (BOARD_X + (gcol + c) * CELL + 1, BOARD_Y + (grow + r) * CELL +1))
    for i, p in enumerate(pieces):
        if p is None:
            continue
        size = CELL if i == dragging else TRAY_CELL
        slide = 0 if i == dragging else slides[1].value
        draw_piece(p["shape"], p["x"], p["y"] + slide, p["color"], size)
    if banner_timer > 0:
        banner_timer -= 1
        t = font.render("PERFECT CLEAR 3x", True, (255, 230, 0))
        screen.blit(t, t.get_rect(center=(WIDTH // 2, BOARD_Y + GRID * CELL // 2)))
    if game_over:
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 150))
        screen.blit(shade, (0, 0))
        text = font.render("GAME OVER - press R", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(WIDTH // 2, BOARD_Y + GRID * CELL // 2)))
    if bomb_active:
        color, label = (255, 80, 0), "CLICK BOARD"
    elif power_up == "freeze":
        color, label = (80, 160, 255), "FREEZE"
    elif power_up == "bomb":
        color, label = (255, 140, 0), "BOMB"
    elif power_up == "rewind":
        color, label = (255, 170, 0), "REWIND"
    elif power_up == "snap":
        color, label = (130, 80, 200), "SNAP"
    elif power_up == "purple":
        color, label = (150, 40, 255), "PURPLE"
    else:
        color,label = (70, 70, 70), "NO POWER"
    pygame.draw.rect(screen, color, power_rect, border_radius=8)
    text = power_font.render(label, True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=power_rect.center))
    for ex in explosions[:]:
        ex[2] -= dt
        if ex[2] <= 0:
            explosions.remove(ex)
            continue
        t = 1 - ex[2] / EXPLOSION_TIME
        radius = int(CELL * 1.8 * t) + 5
        pygame.draw.circle(screen, (255, 230, 120), (ex[0], ex[1]), radius, max(1, int(8 * (1 - t))))
        pygame.draw.circle(screen, (255, 120, 0), (ex[0], ex[1]), int(radius * 0.7), max(1, int(5 * (1 - t))))
    if freeze_turns > 0:
        gray = pygame.transform.grayscale(screen)
        gray.set_alpha(140)
        screen.blit(gray, (0, 0))
    if timestop_timer > 0:
        timestop_timer -= dt
        ts = 1 - max(timestop_timer, 0) / TIMESTOP_TIME
        cx, cy = WIDTH // 2, BOARD_Y + GRID * CELL // 2
        radius = int(min(1, ts / 0.4) * math.hypot(WIDTH, HEIGHT))
        inv =  pygame.Surface((WIDTH, HEIGHT))
        inv.fill((255, 255, 255))
        inv.blit(screen, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
        inv = inv.convert_alpha()
        mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (cx, cy), radius)
        inv.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        inv.set_alpha(int(255 * min(1, (1 - ts) / 0.4)))
        screen.blit(inv, (0, 0))
        if ts < 0.4:
            pygame.draw.circle(screen, (210, 245, 255), (cx, cy), radius, 5)
        if ts < 0.9:
            label = font.render("TIME STOP", True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=(cx, cy - 30)))
        
    pygame.display.flip()

pygame.quit()




