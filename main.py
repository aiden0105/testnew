import pygame
import sys
import random
from collections import deque
import time

# Pygame initialization
pygame.init()

# Screen size configuration
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sokoban")

# Color settings
WHITE = (255, 255, 255)

# Image loading
player_image = pygame.image.load('./assets/player.png')
wall_image = pygame.image.load('./assets/wall.png')
box_image = pygame.image.load('./assets/box.png')
goal_image = pygame.image.load('./assets/goal.png')
floor_image = pygame.image.load('./assets/floor.png')
box_on_goal_image = pygame.image.load('./assets/box_with_x.png')

# Tile size configuration
tile_size = 100

# Map tile types
WALL = '#'
FLOOR = ' '
PLAYER = '@'
BOX = '$'
GOAL = '.'
BOX_ON_GOAL = '*'
PLAYER_ON_GOAL = '+'

# Direction vectors
DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# Game states
STATE_MENU = 0
STATE_GAME = 1
STATE_CONTROLS = 2
game_state = STATE_MENU

# Map data
level = []
player_pos = [0, 0]
goal_count = 0
player_history = deque()  # Storage for player's movement history

########################
######## PHASE 2 #######
########################
# Game timer and difficulty settings
game_timer = 0
start_time = 0
difficulty = 'easy'  # Default difficulty setting

def is_defeat():
    """Checks if the player has lost the game due to time running out."""
    font = pygame.font.SysFont(None, 100)
    message = font.render("Time's Up! You Lose!", True, (255, 0, 0))
    screen.blit(message, (screen_width // 2 - 300, screen_height // 2 - 50))
    pygame.display.flip()
    pygame.time.wait(2000)
    reset_game()

def display_timer(remaining_time):
    """Displays the remaining time on the screen."""
    font = pygame.font.SysFont(None, 50)
    timer_message = font.render(f"Time left: {remaining_time} seconds", True, (0, 0, 0))
    screen.blit(timer_message, (10, 10))

def choose_difficulty():
    """Allows the player to choose the difficulty which sets the game timer."""
    global game_timer, difficulty
    print("Choose difficulty: Easy (1), Normal (2), Hard (3)")
    choice = input("Enter your choice (1-3): ")
    if choice == '1':
        game_timer = 60
        difficulty = 'easy'
    elif choice == '2':
        game_timer = 30
        difficulty = 'normal'
    elif choice == '3
        game_timer = 15
        difficulty = 'hard'
    else:
        print("Invalid choice, defaulting to Easy.")
        game_timer = 60  # Default to easy if the choice is invalid

    reset_game()  # Reset the game along with the timer start

def reset_game():
    """Resets the game environment, including the timer and game map."""
    global level, player_pos, player_history, start_time, game_timer, goal_count
    level, player_pos, goal_count = generate_sokoban_map(10, 10, 3)
    player_history.clear()
    start_time = time.time()  # Reset the timer

def create_empty_map(width, height):
    """Creates an empty map with walls around the border."""
    return [[WALL if x == 0 or x == width - 1 or y == 0 or y == height - 1 else FLOOR for x in range(width)] for y in range(height)]

def place_player_and_goals(map_data, num_goals):
    """Places the player and goals randomly on the map."""
    global player_pos
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR]
    random.shuffle(free_spaces)

    temp_pos = free_spaces.pop()
    player_pos[0], player_pos[1] = temp_pos
    map_data[player_pos[0]][player_pos[1]] = PLAYER

    goals = []
    for _ in range(num_goals):
        goal_pos = free_spaces.pop()
        map_data[goal_pos[0]][goal_pos[1]] = GOAL
        goals.append(goal_pos)

    return player_pos, goals

def is_adjacent_to_wall(y, x, map_data):
    """Checks if a given position is adjacent to a wall."""
    adjacent_positions = [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]
    return any(map_data[ny][nx] == WALL for ny, nx in adjacent_positions)

def place_boxes(map_data, goals):
    """Places boxes on the map not adjacent to walls."""
    global goal_count
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR and not is_adjacent_to_wall(y, x, map_data)]
    random.shuffle(free_spaces)

    for goal in goals:
        box_pos = free_spaces.pop()
        map_data[box_pos[0]][box_pos[1]] = BOX
        goal_count += 1

    return map_data

def generate_sokoban_map(width, height, num_goals):
    """Generates a new game map with specified dimensions and number of goals."""
    map_data = create_empty_map(width, height)
    player_pos, goals = place_player_and_goals(map_data, num_goals)
    map_data = place_boxes(map_data, goals)
    return map_data, player_pos, len(goals)

def draw_level(map_data):
    """Draws the game level based on the current map data."""
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            screen.blit(floor_image, (x * tile_size, y * tile_size))
            if tile == WALL:
                screen.blit(wall_image, (x * tile_size, y * tile_size))
            elif tile == GOAL:
                screen.blit(goal_image, (x * tile_size, y * tile_size))
            elif tile == BOX:
                screen.blit(box_image, (x * tile_size, y * tile_size))
            elif tile == BOX_ON_GOAL:
                screen.blit(box_on_goal_image, (x * tile_size, y * tile_size))

def draw_player():
    """Draws the player at the current position."""
    screen.blit(player_image, (player_pos[0] * tile_size, player_pos[1] * tile_size))

def move_player(dx, dy):
    """Defines the movement of the player including pushing boxes."""
    global level
    new_x, new_y = player_pos[0] + dx, player_pos[1] + dy

    if level[new_y][new_x] == FLOOR:
        # Move player to new space
        level[player_pos[1]][player_pos[0]] = FLOOR
        player_history.append((player_pos[0], player_pos[1]))
        player_pos[0], player_pos[1] = new_x, new_y
        level[new_y][new_x] = PLAYER
    elif level[new_y][new_x] == BOX:
        # Move box if possible
        box_new_x, box_new_y = new_x + dx, new_y + dy
        if level[box_new_y][box_new_x] in [FLOOR, GOAL]:
            level[new_y][new_x] = FLOOR
            level[box_new_y][box_new_x] = BOX
            level[player_pos[1]][player_pos[0]] = FLOOR
            player_history.append((player_pos[0], player_pos[1]))
            player_pos[0], player_pos[1] = new_x, new_y
            level[new_y][new_x] = PLAYER

def run():
    """Main game loop."""
    global level, game_state, start_time
    running = True
    clock = pygame.time.Clock()
    choose_difficulty()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == STATE_MENU:
                    if event.key == pygame.K_RETURN:
                        level, player_pos, goal_count = generate_sokoban_map(10, 10, 3)
                        game_state = STATE_GAME
                    elif event.key == pygame.K_h:
                        game_state = STATE_CONTROLS
                elif game_state == STATE_CONTROLS:
                    if event.key == pygame.K_ESCAPE:
                        game_state = STATE_MENU
                        reset_game()
                elif game_state == STATE_GAME:
                    if event.key == pygame.K_ESCAPE:
                        game_state = STATE_MENU
                        reset_game()
                    elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                        move_dir = DIRS[event.key - pygame.K_UP]
                        move_player(*move_dir)
                        is_win()

        screen.fill(WHITE)
        if game_state == STATE_MENU:
            show_menu()
        elif game_state == STATE_CONTROLS:
            show_controls()
        elif game_state == STATE_GAME:
            draw_level(level)
            draw_player()
            display_timer(game_timer - (time.time() - start_time))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run()
