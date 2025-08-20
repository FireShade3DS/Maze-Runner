import pygame
import random
import argparse

# Grid settings
INNER_ROWS, INNER_COLS = 7, 7
ROWS, COLS = INNER_ROWS + 2, INNER_COLS + 2
CELL_SIZE = 60
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

# Directions: (dr, dc) and corresponding wall keys
DIRS = {
    (-1, 0): ('top', 'bottom'),
    (1, 0): ('bottom', 'top'),
    (0, -1): ('left', 'right'),
    (0, 1): ('right', 'left')
}

def in_bounds(r, c):
    return 1 <= r < ROWS - 1 and 1 <= c < COLS - 1

def initialize_walls():
    walls = {}
    for r in range(ROWS):
        for c in range(COLS):
            walls[(r, c)] = {'top': True, 'bottom': True, 'left': True, 'right': True}
    return walls

def generate_dual_graph():
    dual_edges = []
    for r in range(ROWS):
        for c in range(COLS):
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc):
                    wall = ((r, c), (nr, nc))
                    dual_edges.append(wall)
    return dual_edges

def carve_maze_via_dual(walls):
    visited = set()
    graph = {}

    def visit(cell):
        visited.add(cell)
        graph.setdefault(cell, [])
        neighbors = [(cell, (cell[0] + dr, cell[1] + dc)) for dr, dc in DIRS if in_bounds(cell[0] + dr, cell[1] + dc)]
        random.shuffle(neighbors)

        for a, b in neighbors:
            if b not in visited:
                dr, dc = b[0] - a[0], b[1] - a[1]
                wall_a, wall_b = DIRS[(dr, dc)]

                # ✅ This is the carving step: remove the wall between a and b
                walls[a][wall_a] = False
                walls[b][wall_b] = False

                graph[a].append(b)
                graph.setdefault(b, []).append(a)

                visit(b)

    visit((1, 1))  # Start from inside the padded area
    return walls, graph
def draw_maze(screen, walls):
    wall_color = (255, 191, 0)
    for (r, c), wall in walls.items():
        if not in_bounds(r, c):
            continue
        x, y = c * CELL_SIZE, r * CELL_SIZE
        if wall['top']:
            pygame.draw.line(screen, wall_color, (x, y), (x + CELL_SIZE, y), 2)
        if wall['bottom']:
            pygame.draw.line(screen, wall_color, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if wall['left']:
            pygame.draw.line(screen, wall_color, (x, y), (x, y + CELL_SIZE), 2)
        if wall['right']:
            pygame.draw.line(screen, wall_color, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
def draw_dual_graph(screen, graph):
    for (r, c), neighbors in graph.items():
        x1, y1 = c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, (255, 215, 0), (x1, y1), 5)  # Node in F

        for nr, nc in neighbors:
            x2, y2 = nc * CELL_SIZE + CELL_SIZE // 2, nr * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 1)  # Edge in F
def collision_detection(player_pos, direction, walls):
    r, c = player_pos
    wall_key = DIRS[direction][0]  # Which wall blocks movement in this direction
    return not walls[(r, c)][wall_key]

def pick_start_end(graph): #this is the buckleys of algorithms
    dead_ends = [node for node in graph if len(graph[node]) == 1]
    max_distance = (INNER_ROWS + INNER_COLS) // 2  # Half the average of inner dimensions

    while True:
        start, end = random.sample(dead_ends, 2)

        if start == end:
            continue

        same_row = start[0] == end[0]
        same_col = start[1] == end[1]
        diagonal = abs(start[0] - end[0]) == abs(start[1] - end[1]
        )
        manhattan = abs(start[0] - end[0]) + abs(start[1] - end[1])

        if not same_row and not same_col and not diagonal and manhattan > max_distance:
            return start, end
def handle_movement(key, player_pos, walls, score):
    direction = None
    if key == pygame.K_UP:
        direction = (-1, 0)
    elif key == pygame.K_DOWN:
        direction = (1, 0)
    elif key == pygame.K_LEFT:
        direction = (0, -1)
    elif key == pygame.K_RIGHT:
        direction = (0, 1)

    if direction:
        new_r = player_pos[0] + direction[0]
        new_c = player_pos[1] + direction[1]
        new_pos = (new_r, new_c)

        if in_bounds(new_r, new_c) and collision_detection(player_pos, direction, walls):
            player_pos = new_pos
            if player_pos not in visited_nodes:
                score += points_map.get(player_pos, 0)
                visited_nodes.add(player_pos)
                print(f"Player gained {points_map.get(player_pos, 0)} points at {player_pos}")
                points_map[player_pos] = 0

    return player_pos, score
# CLI setup
parser = argparse.ArgumentParser(description="Maze Game with Debug Mode")
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
args = parser.parse_args()

DEBUG_MODE = args.debug
# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dual Graph Maze")
font = pygame.font.SysFont("Courier New", 24)
def make_new_maze():
    walls = initialize_walls()
    walls, maze = carve_maze_via_dual(walls)
    start, end = pick_start_end(maze)
    points_map = {}
    for node in maze:
        if node != start and node != end:
            if len(maze[node]) == 1:  # dead end
                points_map[node] = 5
            else:
                points_map[node] = random.choice([0, 1, 2])
    return walls, maze, start, end, points_map
walls, maze, start, end, points_map = make_new_maze()
player_pos = start
last_direction = None
prompt = font.render(">> Navigate the maze with arrow keys", True, (255, 255, 255))
screen.blit(prompt, (10, HEIGHT - 100))
time_limit = 15  # seconds
start_ticks = pygame.time.get_ticks()
score = 0
visited_nodes = set()
#states for state machine
def show_title_screen():
    while True:
        screen.fill((0, 0, 0))
        title_text = font.render("🏁 Maze Runner", True, (255, 255, 255))
        prompt_text = font.render("Press SPACE to start", True, (200, 200, 200))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
def show_game_over_screen(score):
    while True:
        screen.fill((20, 0, 0))
        over_text = font.render("⛔ You ran out of time!", True, (255, 0, 0))
        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        time_text = font.render(f"Total Time Survived: {total_time} seconds", True, (200, 200, 200))
        retry_text = font.render("Press R to retry or Q to quit", True, (150, 150, 150))
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 3))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 + 40))
        screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + 80))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    return False
# Game loop
if not show_title_screen():
    exit()
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(30)
    elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000
    remaining_time = max(0, time_limit - elapsed_seconds)
    screen.fill((0, 0, 0))  # Black background
    draw_maze(screen, walls)
    if DEBUG_MODE:
        draw_dual_graph(screen, maze)

   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            player_pos, score = handle_movement(event.key, player_pos, walls, score)
    if player_pos == end:
        time_limit = remaining_time + score  # next round's time is equal to current score + previous time limit
        print(f"🕒 New round time: {time_limit} seconds")
        #increase maze size
        INNER_ROWS += 2
        INNER_COLS += 2
        walls, maze, start, end, points_map = make_new_maze()
        player_pos = start
        score = 0
        visited_nodes = set()
        start_ticks = pygame.time.get_ticks()  # reset timer
    if remaining_time == 0:
        if not show_game_over_screen(score):
            exit()
        walls, maze, start, end, points_map = make_new_maze()
        player_pos = start
        visited_nodes = set()
        score = 0

    pygame.draw.circle(screen, (0, 255, 0), (end[1] * CELL_SIZE + CELL_SIZE // 2, end[0] * CELL_SIZE + CELL_SIZE // 2), 10)  # End in green
    pygame.draw.circle(screen, (255, 0, 0), (start[1] * CELL_SIZE + CELL_SIZE // 2, start[0] * CELL_SIZE + CELL_SIZE // 2), 10)  # Start in red
    def draw_pointballs(screen, points_map):
        for node, value in points_map.items():
            y, x = node
            px = x * CELL_SIZE + CELL_SIZE // 2
            py = y * CELL_SIZE + CELL_SIZE // 2

            if value == 1:
                size_multiplier = 1
            elif value == 2:
                size_multiplier = 2
            elif value == 5:
                size_multiplier = 3  # gold for dead-end bonus
            else:
                continue

            pygame.draw.circle(screen, (255, 215, 0), (px, py), CELL_SIZE // 10 * size_multiplier)
    draw_pointballs(screen, points_map)
    pygame.draw.circle(screen, (0, 0, 255), (player_pos[1] * CELL_SIZE + CELL_SIZE // 2, player_pos[0] * CELL_SIZE + CELL_SIZE // 2), 10)  # Player in blue
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(prompt, (10, HEIGHT - 110))
    time_text = font.render(f"Time: {remaining_time}", True, (255, 255, 255))
    screen.blit(time_text, (WIDTH - 150, 10))
    pygame.display.flip()

   

pygame.quit()