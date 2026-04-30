import pygame
import heapq
import random

pygame.init()

# Screen
WIDTH, HEIGHT = 500, 650
GRID = 80
ROWS = 5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shadow Escape AI")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# Colors
BG = (40, 40, 60)
GRID_COLOR = (60, 60, 80)
PLAYER_COLOR = (80, 200, 255)
GUARD_COLOR = (255, 80, 80)
GOAL_COLOR = (80, 200, 120)
TEXT = (255,255,255)

# Positions
player = [2,2]
guard = [0,0]
goal = [4,4]

moves = 0
game_started = False
game_over = False

# AI
state = "patrol"
last_seen = None

# Guard timing (IMPORTANT FIX)
guard_timer = 0
guard_delay = 10

# A* Algorithm
def astar(start, goal):
    def h(a,b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    open_set = []
    heapq.heappush(open_set, (0, start))
    came = {}
    g = {tuple(start):0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while tuple(current) in came:
                path.append(current)
                current = came[tuple(current)]
            return path[::-1]

        x,y = current
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<ROWS and 0<=ny<ROWS:
                new_g = g[tuple(current)] + 1
                if (nx,ny) not in g or new_g < g[(nx,ny)]:
                    g[(nx,ny)] = new_g
                    f = new_g + h([nx,ny], goal)
                    heapq.heappush(open_set,(f,[nx,ny]))
                    came[(nx,ny)] = current
    return []

# Vision
def can_see():
    return abs(player[0]-guard[0]) + abs(player[1]-guard[1]) <= 2

# Patrol movement
def patrol():
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    dx,dy = random.choice(dirs)
    nx,ny = guard[0]+dx, guard[1]+dy
    if 0<=nx<ROWS and 0<=ny<ROWS:
        return [nx,ny]
    return guard

# Guard AI
def update_guard():
    global state, last_seen, guard

    if can_see():
        state = "chase"
        last_seen = player.copy()
    elif state == "chase":
        state = "search"

    if state == "chase":
        path = astar(guard, player)
        if path:
            guard = path[0]

    elif state == "search":
        if last_seen:
            path = astar(guard, last_seen)
            if path:
                guard = path[0]
            if guard == last_seen:
                state = "patrol"
                last_seen = None

    else:
        guard = patrol()

# Draw grid
def draw_grid():
    for y in range(ROWS):
        for x in range(ROWS):
            rect = pygame.Rect(x*GRID+50, y*GRID+120, GRID-10, GRID-10)
            pygame.draw.rect(screen, GRID_COLOR, rect, border_radius=10)

# Draw objects
def draw_objects():
    # Player
    px, py = player[0]*GRID+50, player[1]*GRID+120
    pygame.draw.rect(screen, PLAYER_COLOR, (px, py, GRID-10, GRID-10), border_radius=10)
    screen.blit(font.render("P", True, (0,0,0)), (px+25, py+20))

    # Guard
    gx, gy = guard[0]*GRID+50, guard[1]*GRID+120
    pygame.draw.rect(screen, GUARD_COLOR, (gx, gy, GRID-10, GRID-10), border_radius=10)
    screen.blit(font.render("G", True, (0,0,0)), (gx+25, gy+20))

    # Goal
    ex, ey = goal[0]*GRID+50, goal[1]*GRID+120
    pygame.draw.rect(screen, GOAL_COLOR, (ex, ey, GRID-10, GRID-10), border_radius=10)
    screen.blit(font.render("E", True, (0,0,0)), (ex+25, ey+20))

# Reset
def reset():
    global player, guard, moves, state, last_seen, game_over
    player = [2,2]
    guard = [0,0]
    moves = 0
    state = "patrol"
    last_seen = None
    game_over = False

# Main loop
running = True
while running:
    clock.tick(10)
    screen.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game_started = True

            if event.key == pygame.K_r:
                reset()

            if game_started and not game_over:
                dx,dy = 0,0
                if event.key == pygame.K_UP: dy = -1
                if event.key == pygame.K_DOWN: dy = 1
                if event.key == pygame.K_LEFT: dx = -1
                if event.key == pygame.K_RIGHT: dx = 1

                nx, ny = player[0]+dx, player[1]+dy
                if 0<=nx<ROWS and 0<=ny<ROWS:
                    player = [nx,ny]
                    moves += 1

    # 🔥 Continuous Guard Movement 
    if game_started and not game_over:
        guard_timer += 1
        if guard_timer >= guard_delay:
            guard_timer = 0
            update_guard()

    # UI
    screen.blit(font.render("Stealth Escape Game", True, TEXT), (150,20))
    screen.blit(font.render(f"Moves: {moves}", True, TEXT), (200,60))
    screen.blit(font.render("P=Player  G=Guard  E=Exit", True, (200,200,200)), (110,90))

    if not game_started:
        screen.blit(font.render("Press ENTER to Start", True, TEXT), (130,300))
    else:
        draw_grid()
        draw_objects()

    # Win/Lose
    if player == goal:
        screen.blit(font.render("YOU ESCAPED!", True, GOAL_COLOR), (140,580))
        game_over = True

    if player == guard:
        screen.blit(font.render("CAUGHT!", True, GUARD_COLOR), (180,580))
        game_over = True

    pygame.display.update()

pygame.quit()
