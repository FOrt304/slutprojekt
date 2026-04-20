import pygame
import random
import math
import json
import os
# importer lägger vi i början!
from pygame.locals import (
    QUIT,
)

# Game state variables
MENU = 1
EXPLORATION = 2
BATTLE = 3
GAME_OVER = 4

# Constant definitions
WHITE = (255, 255, 255)
TURQUOISE = (75, 178, 164)
DARK_RED = (180, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
DARK_YELLOW = (180, 180, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500
PLAYER = dict(
        NAME="Player", # Player Name
        X=SCREEN_WIDTH // 2, # Player X position
        Y=200, # Player Y position
        WIDTH=10, # Player width 40
        HEIGHT=20, # Player height 40
        COLOR=TURQUOISE, # Player color
        RADIUS=15, # Player radius (for circle)
        SPEED=5, # Player speed
        HP=20, # Player HP
        MAX_HP=20, # Player Max HP
        ATTACK=5 # Player Attack
)
BORDER = dict(
        X=120, # Rectangle X position  (rect) 90
        Y=120, # Rectangle Y position  (rect) 50
        WIDTH=SCREEN_WIDTH*0.5, # Border width 0.7
        HEIGHT=SCREEN_HEIGHT*0.5, # Border height 0.7
        COLOR1=WHITE, # First (Rectangle) Border color
        COLOR2=BLACK, # Second (Rectangle) Border color
        )
REC = dict(
        Y=200, # Rectangle Y position  (rect)
        WIDTH=60, # Rectangle width
        HEIGHT=40, # Rectangle height
        COLOR=WHITE, # Rectangle color
        SPEED=10, # Rectangle speed
        DAMAGE=5, # Projectile damage
        RADIUS=20 # Circle radius
        )
BACKGROUND_COLOR = BLACK

class Enemy:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.hp = 15
        self.max_hp = 15
        self.attack = 3
        self.name = name

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))


def spawn_enemy_random(name="Dummy"):
    """Spawn a new enemy at a random free location on the exploration map."""
    attempts = 0
    while attempts < 50:
        x = random.randint(60, SCREEN_WIDTH - 100)
        y = random.randint(60, SCREEN_HEIGHT - 100)
        enemy_rect = pygame.Rect(x, y, 40, 40)
        collision = False
        for wall in walls:
            if enemy_rect.colliderect(wall):
                collision = True
                break
        if not collision:
            return Enemy(x, y, name)
        attempts += 1
    return Enemy(100, 150, name)

# ============= SAVE/LOAD SYSTEM =============
def save_game():
    """Save current game state to JSON"""
    save_data = {
        "player_name": PLAYER["NAME"],
        "player_hp": PLAYER["HP"],
        "enemies_defeated": enemies_defeated,
        "difficulty": difficulty,
    }
    with open(save_file, "w") as f:
        json.dump(save_data, f)

def load_game():
    """Load game state from JSON"""
    global enemies_defeated, difficulty
    if os.path.exists(save_file):
        try:
            with open(save_file, "r") as f:
                save_data = json.load(f)
                PLAYER["NAME"] = save_data.get("player_name", "Player")
                PLAYER["HP"] = save_data.get("player_hp", PLAYER["MAX_HP"])
                enemies_defeated = save_data.get("enemies_defeated", 0)
                difficulty = save_data.get("difficulty", 1)
            return True
        except:
            return False
    return False

def save_to_leaderboard(score):
    """Save score to leaderboard"""
    leaderboard = []
    if os.path.exists(leaderboard_file):
        try:
            with open(leaderboard_file, "r") as f:
                leaderboard = json.load(f)
        except:
            leaderboard = []
    
    leaderboard.append({"username": PLAYER["NAME"], "enemies_defeated": score, "difficulty": difficulty})
    leaderboard.sort(key=lambda x: x["enemies_defeated"], reverse=True)
    leaderboard = leaderboard[:10]  # Keep top 10
    
    with open(leaderboard_file, "w") as f:
        json.dump(leaderboard, f)

def load_leaderboard():
    """Load leaderboard from JSON"""
    if os.path.exists(leaderboard_file):
        try:
            with open(leaderboard_file, "r") as f:
                return json.load(f)
        except:
            return []
    return []

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Adventures of Fort Yukon") # Game window title
icon = pygame.Surface((32, 32)) # Game window icon (32x32 pixels)
icon.fill(TURQUOISE) # Fill the icon with a color
pygame.display.set_icon(icon) # Set the game window icon
game_state = { "rec_x" : 0, "rec_dir" : 1, "state" : MENU}
action_dead = False
action_quit = False
clock = pygame.time.Clock()
enemies = [Enemy(200, 150, "Dummy")] # List of enemies
font = pygame.font.Font(None, 24) # UI text Font
message = "Welcome to adventures of Fort Yukon!" # Message to display in UI
#state_label = f":3" # Label for bottom-right corner
projectiles = []
player_turn = False
enemy_turn = True
difficulty = 1
inventory = []
items = {
    "healing_potion": {"name": "Healing Potion", "effect": lambda: None},  # will define
}
enemy_attack_delay = 0  # Frames until enemy attacks (60 fps = 60 frames for 1 second)
enemy_attack_max_delay = 60  # 1 second at 60 FPS
enemies_defeated = 0  # Counter for total enemies defeated
save_file = "savegame.json"  # Save file name
leaderboard_file = "leaderboard.json"  # Leaderboard file
input_active = False  # Whether username input is active

# Aiming system variables (Deltarune-style)
aim_active = False
aim_position = 0
aim_target_zone_start = 35  # Green zone start in aim bar (pixels from left)
aim_target_zone_end = 65    # Green zone end in aim bar (pixels from left)
aim_speed = 3  # pixels per frame
# Walls for game world (x, y, width, height)
walls = [
    pygame.Rect(0, 0, SCREEN_WIDTH, 50),  # Top wall
    pygame.Rect(0, 0, 50, SCREEN_HEIGHT),  # Left wall
    pygame.Rect(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT),  # Right wall
    pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),  # Bottom wall
    pygame.Rect(200, 100, 50, 200),  # Vertical wall
    pygame.Rect(400, 200, 200, 50),  # Horizontal wall
]

# Function definitions

def dead():
    """returns True if dead event occur"""
    
    if PLAYER["HP"] <= 0:
        return True

def quit_is_pressed():
    """returns True if close event occur"""

    for event in pygame.event.get():
        if event.type == QUIT:
            return True

def move_rectangle():
    """Updates the position of the rectangle"""
    # 1 below represents the speed of the object
    game_state["rec_x"] += game_state["rec_dir"]*REC["SPEED"]

def change_rec_dir(current=None, limit=None):
    """Change direction of rectangle or aiming cursor when outside bounds"""
    global aim_speed
    if current is None:
        if game_state["rec_x"] >= SCREEN_WIDTH - REC["WIDTH"]:
            game_state["rec_dir"] = -1
        elif game_state["rec_x"] <= 0:
            game_state["rec_dir"] = 1
    else:
        if current >= limit:
            aim_speed = -abs(aim_speed)
        elif current <= 0:
            aim_speed = abs(aim_speed)

def draw_start_game_button():
    """Draws the menu with title, leaderboard, username input, and start/load buttons"""
    screen.fill(BACKGROUND_COLOR)
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title_text = title_font.render("Fort Yukon", True, TURQUOISE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 100, 10))
    
    # Leaderboard
    leaderboard = load_leaderboard()
    small_font = pygame.font.Font(None, 20)
    
    leaderboard_title = small_font.render("Leaderboard:", True, YELLOW)
    screen.blit(leaderboard_title, (10, 70))
    
    for idx, score in enumerate(leaderboard[:5]):
        username = score.get('username', 'Player')
        score_text = small_font.render(f"{idx+1}. {username}: {score['enemies_defeated']} enemies (Diff: {score['difficulty']:.1f})", True, WHITE)
        screen.blit(score_text, (10, 90 + idx * 25))
    
    # Username input
    username_label = small_font.render("Username:", True, WHITE)
    screen.blit(username_label, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 150))
    
    # Username input box
    input_width = 200
    input_height = 30
    input_x = SCREEN_WIDTH // 2 - 50
    input_y = SCREEN_HEIGHT - 140
    border_color = TURQUOISE if input_active else WHITE
    pygame.draw.rect(screen, border_color, (input_x, input_y, input_width, input_height), width=2)
    
    # Username text
    username_display = PLAYER["NAME"]
    if input_active and pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
        username_display += "|"
    username_text = small_font.render(username_display, True, WHITE)
    screen.blit(username_text, (input_x + 5, input_y + 5))
    
    # Start Game button (like the old style)
    button_width = 150
    button_height = 40
    button_x1 = SCREEN_WIDTH // 2 - 160
    button_y = SCREEN_HEIGHT - 80
    pygame.draw.rect(screen, WHITE, (button_x1, button_y, button_width, button_height), width=2)
    font = pygame.font.Font(None, 24)
    start_text = font.render("Start Game", True, WHITE)
    screen.blit(start_text, (button_x1 + 20, button_y + 8))
    
    # Load Game button (like the old style)
    button_x2 = SCREEN_WIDTH // 2 + 10
    pygame.draw.rect(screen, WHITE, (button_x2, button_y, button_width, button_height), width=2)
    load_text = font.render("Load Game", True, WHITE)
    screen.blit(load_text, (button_x2 + 20, button_y + 8))

def draw_menu():
    """Displays the menu - all interaction handling is done in main.py"""
    draw_start_game_button()
    pygame.display.flip()
    
    # Check for quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
    
    return False

def draw_border():
    """Draw a rectangle in a rectangle as a border in game window (rectangle outline)"""
    pygame.draw.rect(screen, BORDER["COLOR1"], pygame.Rect(BORDER["X"], 
                                                           BORDER["Y"], 
                                                           BORDER["WIDTH"], 
                                                           BORDER["HEIGHT"]), 
                                                           width=2)
'''    pygame.draw.rect(screen, BORDER["COLOR1"], BORDER["X"],
                                                     BORDER["Y"], 
                                                     BORDER["WIDTH"], 
                                                     BORDER["HEIGHT"])
    pygame.draw.rect(screen, BORDER["COLOR2"], BORDER["X"],
                                                     BORDER["Y"]+5,
                                                     BORDER["WIDTH"]*0.6, 
                                                     BORDER["HEIGHT"]*0.6)'''
def draw_buttons():
    """Draw battle buttons under the border"""
    button_y = BORDER["Y"] + BORDER["HEIGHT"] + 10
    button_width = 80
    button_height = 30
    button_x1 = BORDER["X"]
    button_x2 = button_x1 + button_width + 10
    button_x3 = button_x2 + button_width + 10
    
    pygame.draw.rect(screen, GRAY, (button_x1, button_y, button_width, button_height))
    pygame.draw.rect(screen, DARK_GRAY, (button_x1, button_y, button_width, button_height), 2)
    fight_text = font.render("FIGHT", True, BLACK)
    screen.blit(fight_text, (button_x1 + 10, button_y + 5))
    
    pygame.draw.rect(screen, GRAY, (button_x2, button_y, button_width, button_height))
    pygame.draw.rect(screen, DARK_GRAY, (button_x2, button_y, button_width, button_height), 2)
    items_text = font.render("ITEMS", True, BLACK)
    screen.blit(items_text, (button_x2 + 10, button_y + 5))
    
    pygame.draw.rect(screen, GRAY, (button_x3, button_y, button_width, button_height))
    pygame.draw.rect(screen, DARK_GRAY, (button_x3, button_y, button_width, button_height), 2)
    act_text = font.render("ACT", True, BLACK)
    screen.blit(act_text, (button_x3 + 10, button_y + 5))
def draw_player():
    """Draws the player (cat head) in game window (Draws a (rätvinklig) triangle in game window)"""
    player_center_x = PLAYER["X"] + PLAYER["WIDTH"] // 2
    player_center_y = PLAYER["Y"] + PLAYER["HEIGHT"] // 2
    radius = PLAYER["RADIUS"] // 2 if game_state["state"] == BATTLE else PLAYER["RADIUS"]
    
    if game_state["state"] == BATTLE:
        # Draw cat head: main circle
        pygame.draw.circle(screen, PLAYER["COLOR"], (player_center_x, player_center_y), radius)
        # Ears: two small circles above
        ear_radius = radius // 2
        pygame.draw.circle(screen, PLAYER["COLOR"], (player_center_x - radius//2, player_center_y - radius + ear_radius), ear_radius)
        pygame.draw.circle(screen, PLAYER["COLOR"], (player_center_x + radius//2, player_center_y - radius + ear_radius), ear_radius)
        # Eyes: two small black circles
        eye_radius = max(1, radius // 5)
        pygame.draw.circle(screen, BLACK, (player_center_x - radius//3, player_center_y - radius//3), eye_radius)
        pygame.draw.circle(screen, BLACK, (player_center_x + radius//3, player_center_y - radius//3), eye_radius)
    else:
        pygame.draw.circle(screen, PLAYER["COLOR"], 
                           (player_center_x, 
                            player_center_y), 
                           radius)
        points1 = [
            (player_center_x - PLAYER["RADIUS"] - 2, player_center_y - PLAYER["RADIUS"] - 3),
            (player_center_x - PLAYER["RADIUS"] + 3, player_center_y + PLAYER["RADIUS"] / 2),
            (player_center_x + PLAYER["RADIUS"] / 2, player_center_y + PLAYER["RADIUS"] / 2)
        ]
        points2 = [
            (player_center_x + PLAYER["RADIUS"] + 2, player_center_y - PLAYER["RADIUS"] - 3),
            (player_center_x + PLAYER["RADIUS"] - 3, player_center_y + PLAYER["RADIUS"] / 2),
            (player_center_x - PLAYER["RADIUS"] / 2, player_center_y + PLAYER["RADIUS"] / 2)
        ]
        pygame.draw.polygon(screen, PLAYER["COLOR"], points1)
        pygame.draw.polygon(screen, PLAYER["COLOR"], points2)

'''    center_y = BORDER["Y"] + BORDER["HEIGHT"] // 2
    points = [
        (center_x, center_y - PLAYER["RADIUS"]),
        (center_x - PLAYER["RADIUS"], center_y + PLAYER["RADIUS"]),
        (center_x + PLAYER["RADIUS"], center_y + PLAYER["RADIUS"])
    ]
    pygame.draw.polygon(screen, PLAYER["COLOR"], points)''' 

#    pygame.draw.rect(screen, PLAYER["COLOR"], pygame.Rect(BORDER["X"] + BORDER["WIDTH"] // 2 - PLAYER["WIDTH"] // 2,
#                                                     BORDER["Y"] + BORDER["HEIGHT"] // 2 - PLAYER["HEIGHT"] // 2,
#                                                     PLAYER["WIDTH"], 
#                                                     PLAYER["HEIGHT"]))

def use_item(item_key):
    global message
    if item_key == "healing_potion":
        old_hp = PLAYER["HP"]
        PLAYER["HP"] = min(PLAYER["HP"] + 10, PLAYER["MAX_HP"])
        message = f"Healed {PLAYER['HP'] - old_hp} HP!"
        inventory.remove(item_key)
    # add more items

def check_collision(obj1, obj2):
    return (obj1.x < obj2.x + obj2.width and
            obj1.x + obj1.width > obj2.x and
            obj1.y < obj2.y + obj2.height and
            obj1.y + obj1.height > obj2.y)

# ============= PROJECTILE PATTERN FUNCTIONS =============
def spawn_circle_pattern():
    """Classic circle pattern - projectiles spread out in all directions"""
    ex = BORDER["X"] + BORDER["WIDTH"] // 2
    ey = BORDER["Y"] + BORDER["HEIGHT"] // 2
    num_proj = int(8 + difficulty * 2)
    speed = 3 + difficulty * 0.5
    for i in range(num_proj):
        angle = i * (2 * math.pi / num_proj)
        proj_dx = math.cos(angle) * speed
        proj_dy = math.sin(angle) * speed
        projectiles.append({"x": ex, "y": ey, "dx": proj_dx, "dy": proj_dy, "speed": speed, "damage": 3})

def spawn_spiral_pattern():
    """Spiral pattern - projectiles move in a spiral"""
    ex = BORDER["X"] + BORDER["WIDTH"] // 2
    ey = BORDER["Y"] + BORDER["HEIGHT"] // 2
    num_proj = int(6 + difficulty)
    speed = 2.5 + difficulty * 0.3
    for i in range(num_proj):
        angle = i * (2 * math.pi / num_proj)
        # Add rotation component for spiral effect
        proj_dx = math.cos(angle) * speed + random.uniform(-0.5, 0.5)
        proj_dy = math.sin(angle) * speed + random.uniform(-0.5, 0.5)
        projectiles.append({"x": ex, "y": ey, "dx": proj_dx, "dy": proj_dy, "speed": speed, "damage": 3, "rotation": 0})

def spawn_line_pattern():
    """Line pattern - projectiles come in organized rows"""
    ex = BORDER["X"] + BORDER["WIDTH"] // 2
    ey = BORDER["Y"] + BORDER["HEIGHT"] // 2
    speed = 3 + difficulty * 0.4
    num_rows = int(3 + difficulty // 2)
    for row in range(num_rows):
        for col in range(4):
            angle = random.uniform(0, 2 * math.pi)
            offset_x = (col - 1.5) * 20
            offset_y = (row - 1) * 20
            proj_dx = math.cos(angle) * speed * 0.8
            proj_dy = math.sin(angle) * speed * 0.8
            projectiles.append({"x": ex + offset_x, "y": ey + offset_y, "dx": proj_dx, "dy": proj_dy, 
                              "speed": speed, "damage": 3, "offset_x": offset_x, "offset_y": offset_y})

def spawn_wave_pattern():
    """Wave pattern - projectiles come in waves from edges"""
    speed = 3.5 + difficulty * 0.5
    sides = random.randint(2, 4)  # Come from 2-4 sides
    
    if sides >= 1:  # From top
        for i in range(int(5 + difficulty)):
            x = BORDER["X"] + (i * BORDER["WIDTH"] // (5 + difficulty))
            y = BORDER["Y"]
            projectiles.append({"x": x, "y": y, "dx": random.uniform(-0.5, 0.5), "dy": speed, 
                              "speed": speed, "damage": 3})
    if sides >= 2:  # From left
        for i in range(int(5 + difficulty)):
            x = BORDER["X"]
            y = BORDER["Y"] + (i * BORDER["HEIGHT"] // (5 + difficulty))
            projectiles.append({"x": x, "y": y, "dx": speed, "dy": random.uniform(-0.5, 0.5), 
                              "speed": speed, "damage": 3})
    if sides >= 3:  # From right
        for i in range(int(5 + difficulty)):
            x = BORDER["X"] + BORDER["WIDTH"]
            y = BORDER["Y"] + (i * BORDER["HEIGHT"] // (5 + difficulty))
            projectiles.append({"x": x, "y": y, "dx": -speed, "dy": random.uniform(-0.5, 0.5), 
                              "speed": speed, "damage": 3})
    if sides >= 4:  # From bottom
        for i in range(int(5 + difficulty)):
            x = BORDER["X"] + (i * BORDER["WIDTH"] // (5 + difficulty))
            y = BORDER["Y"] + BORDER["HEIGHT"]
            projectiles.append({"x": x, "y": y, "dx": random.uniform(-0.5, 0.5), "dy": -speed, 
                              "speed": speed, "damage": 3})

def spawn_aimed_pattern():
    """Aimed pattern - projectiles aim at player position"""
    ex = BORDER["X"] + BORDER["WIDTH"] // 2
    ey = BORDER["Y"] + BORDER["HEIGHT"] // 2
    px = PLAYER["X"] + PLAYER["WIDTH"] // 2
    py = PLAYER["Y"] + PLAYER["HEIGHT"] // 2
    
    num_proj = int(5 + difficulty)
    speed = 3 + difficulty * 0.4
    
    for i in range(num_proj):
        # Add some spread to not be too accurate
        spread = random.uniform(-0.3, 0.3)
        dx = (px - ex) + spread * 50
        dy = (py - ey) + spread * 50
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            dx = (dx / distance) * speed
            dy = (dy / distance) * speed
        projectiles.append({"x": ex, "y": ey, "dx": dx, "dy": dy, "speed": speed, "damage": 4})

def spawn_random_pattern():
    """Chaotic pattern - random projectiles from random positions"""
    speed = 3 + difficulty * 0.3
    num_proj = int(10 + difficulty * 2)
    
    for i in range(num_proj):
        x = random.uniform(BORDER["X"], BORDER["X"] + BORDER["WIDTH"])
        y = random.uniform(BORDER["Y"], BORDER["Y"] + BORDER["HEIGHT"])
        angle = random.uniform(0, 2 * math.pi)
        proj_dx = math.cos(angle) * speed
        proj_dy = math.sin(angle) * speed
        projectiles.append({"x": x, "y": y, "dx": proj_dx, "dy": proj_dy, "speed": speed, "damage": 2})

# ============= AIM SYSTEM FUNCTIONS =============
def start_aiming():
    """Start the aiming minigame"""
    global aim_active, aim_position
    aim_active = True
    aim_position = 0

def draw_aim_bar(screen):
    """Draw the Deltarune-style aiming bar"""
    bar_width = 100
    bar_height = 20
    bar_x = (SCREEN_WIDTH - bar_width) // 2
    bar_y = BORDER["Y"] - bar_height - 15
    
    # Draw background
    pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Draw target zone (green zone)
    zone_width = aim_target_zone_end - aim_target_zone_start
    pygame.draw.rect(screen, GREEN, (bar_x + aim_target_zone_start, bar_y + 2, zone_width, bar_height - 4))
    
    # Draw cursor
    cursor_x = bar_x + aim_position
    pygame.draw.rect(screen, YELLOW, (cursor_x - 2, bar_y - 5, 4, bar_height + 10), 0)
    
    return bar_x, bar_y, bar_width, bar_height

def update_aim():
    """Update aim position (moves back and forth)"""
    global aim_position
    aim_position += aim_speed
    
    # Bounce back and forth using the same side-to-side logic as the rectangle
    change_rec_dir(current=aim_position, limit=100)
    if aim_position >= 100:
        aim_position = 100
    elif aim_position <= 0:
        aim_position = 0

def check_aim_accuracy():
    """Check where the cursor is and return damage multiplier"""
    center = 50
    distance = abs(aim_position - center)
    max_distance = center
    normalized = max(0.0, 1.0 - distance / max_distance)
    multiplier = 0.8 + normalized * 1.2
    
    if distance <= 5:
        accuracy = "CRITICAL HIT!"
    elif distance <= 15:
        accuracy = "Great hit!"
    elif distance <= 30:
        accuracy = "Good hit!"
    else:
        accuracy = "Off target..."
    
    return multiplier, accuracy

def check_collision(obj1, obj2):
    return (obj1.x < obj2.x + obj2.width and
            obj1.x + obj1.width > obj2.x and
            obj1.y < obj2.y + obj2.height and
            obj1.y + obj1.height > obj2.y)

def player_attack():
    global message, enemy_turn, player_turn, aim_active
    if enemies:
        # Start aiming minigame
        aim_active = True
        start_aiming()
        player_turn = False  # Aiming phase

def finish_player_attack(damage_multiplier, accuracy_text):
    """Complete the attack after aiming"""
    global message, enemy_turn, player_turn, aim_active, difficulty, enemy_attack_delay, enemies_defeated
    aim_active = False
    
    if enemies:
        base_damage = PLAYER["ATTACK"]
        damage = int(base_damage * damage_multiplier) + random.randint(-1, 1)
        enemies[0].hp -= damage
        message = f"{accuracy_text} {damage} damage!"
        
        if enemies[0].hp <= 0:
            message = f"Defeated {enemies[0].name}!"
            enemies_defeated += 1  # Increment counter
            save_game()  # Save progress
            enemies.pop(0)
            # Spawn new enemy at a random map location and return to exploration
            enemies.append(spawn_enemy_random())
            if random.random() < 0.5:  # 50% chance
                inventory.append("healing_potion")
                message += " Got a Healing Potion!"
            game_state["state"] = EXPLORATION
            player_turn = False
            enemy_turn = False
        else:
            enemy_turn = True
            player_turn = False
            enemy_attack_delay = enemy_attack_max_delay  # Start delay before enemy attacks

def enemy_attack():
    global message
    if enemies:
        damage = enemies[0].attack + random.randint(-1, 1)
        PLAYER["HP"] -= damage
        message = f"{enemies[0].name} dealt {damage} damage!"
        
        if PLAYER["HP"] <= 0:
            message = "GAME OVER!"

def update():
    """Updates game state"""
    global enemy_turn, player_turn, difficulty, enemy_attack_delay
    if game_state["state"] == EXPLORATION:
        old_x, old_y = PLAYER["X"], PLAYER["Y"]
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w or pygame.K_UP]:
            PLAYER["Y"] -= PLAYER["SPEED"]
        if keys[pygame.K_s or pygame.K_DOWN]:
            PLAYER["Y"] += PLAYER["SPEED"]
        if keys[pygame.K_a or pygame.K_LEFT]:
            PLAYER["X"] -= PLAYER["SPEED"]
        if keys[pygame.K_d or pygame.K_RIGHT]:
            PLAYER["X"] += PLAYER["SPEED"]
        
        # Check wall collisions
        player_rect = pygame.Rect(PLAYER["X"], PLAYER["Y"], PLAYER["WIDTH"], PLAYER["HEIGHT"])
        for wall in walls:
            if player_rect.colliderect(wall):
                PLAYER["X"], PLAYER["Y"] = old_x, old_y
                break
        
        for enemy in enemies:
            if check_collision(type('obj', (), {'x': PLAYER["X"], 'y': PLAYER["Y"], 'width': PLAYER["WIDTH"], 'height': PLAYER["HEIGHT"]})(), enemy):
                game_state["state"] = BATTLE
                # Center player in the border
                PLAYER["X"] = BORDER["X"] + BORDER["WIDTH"] // 2 - PLAYER["WIDTH"] // 2
                PLAYER["Y"] = BORDER["Y"] + BORDER["HEIGHT"] // 2 - PLAYER["HEIGHT"] // 2
                player_turn = False
                enemy_turn = True
                global message
                message = f"Encountered {enemy.name}!"
    
    elif game_state["state"] == BATTLE:
        # Allow player movement in battle
        old_x, old_y = PLAYER["X"], PLAYER["Y"]
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w or pygame.K_UP]:
            PLAYER["Y"] -= PLAYER["SPEED"]
        if keys[pygame.K_s or pygame.K_DOWN]:
            PLAYER["Y"] += PLAYER["SPEED"]
        if keys[pygame.K_a or pygame.K_LEFT]:
            PLAYER["X"] -= PLAYER["SPEED"]
        if keys[pygame.K_d or pygame.K_RIGHT]:
            PLAYER["X"] += PLAYER["SPEED"]
        
        # Keep player within battle border
        PLAYER["X"] = max(BORDER["X"], min(PLAYER["X"], BORDER["X"] + BORDER["WIDTH"] - PLAYER["WIDTH"]))
        PLAYER["Y"] = max(BORDER["Y"], min(PLAYER["Y"], BORDER["Y"] + BORDER["HEIGHT"] - PLAYER["HEIGHT"]))
        
        # Update aiming cursor whenever aiming is active
        if aim_active:
            update_aim()

        if enemy_turn:
            if enemy_attack_delay > 0:
                # Count down before enemy attacks
                enemy_attack_delay -= 1
            elif enemies and len(projectiles) == 0:
                # Spawn sequence of projectiles from center of border
                # Choose random pattern
                pattern = random.randint(1, 6)
                
                if pattern == 1:
                    spawn_circle_pattern()
                elif pattern == 2:
                    spawn_spiral_pattern()
                elif pattern == 3:
                    spawn_line_pattern()
                elif pattern == 4:
                    spawn_wave_pattern()
                elif pattern == 5:
                    spawn_aimed_pattern()
                else:
                    spawn_random_pattern()
                
                enemy_turn = False
                player_turn = True
                difficulty += 0.5  # Increase difficulty gradually
            elif len(projectiles) > 0:
                # Move projectiles
                for proj in projectiles[:]:
                    proj["x"] += proj["dx"]
                    proj["y"] += proj["dy"]
                    # Check hit player
                    proj_rect = pygame.Rect(proj["x"] - 5, proj["y"] - 5, 10, 10)
                    player_rect = pygame.Rect(PLAYER["X"], PLAYER["Y"], PLAYER["WIDTH"], PLAYER["HEIGHT"])
                    if proj_rect.colliderect(player_rect):
                        PLAYER["HP"] -= proj["damage"]
                        PLAYER["HP"] = max(0, PLAYER["HP"])  # Don't let HP go below 0
                        message = f"Hit by projectile! -{proj['damage']} HP"
                        projectiles.remove(proj)
                        if PLAYER["HP"] <= 0:
                            message = "GAME OVER!"
                    elif proj["x"] < 0 or proj["x"] > SCREEN_WIDTH or proj["y"] < 0 or proj["y"] > SCREEN_HEIGHT:
                        projectiles.remove(proj)
                if len(projectiles) == 0:
                    enemy_turn = False
                    player_turn = True
        elif player_turn:
            # Player can attack or aim
            if not aim_active:
                # Waiting for player input (handled in main.py)
                pass

def draw_menu():
    """Displays the menu and waits for the player to start the game"""
    screen.fill(BACKGROUND_COLOR)
    draw_start_game_button()
    pygame.display.flip()
        
    for event2 in pygame.event.get():
        if event2.type == pygame.QUIT:
            return "quit"
        if event2.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event2.pos
            button_width = 200
            button_height = 50
            button_x = (SCREEN_WIDTH - button_width) // 2
            button_y = (SCREEN_HEIGHT - button_height) // 2
            if (button_x <= mouse_x <= button_x + button_width and 
                button_y <= mouse_y <= button_y + button_height):
                return True
    return False

def draw_game_over():
    """Displays the game over screen"""
    screen.fill(BACKGROUND_COLOR)
    game_over_text = pygame.font.Font(None, 72).render("GAME OVER", True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(game_over_text, game_over_rect)
    
    restart_text = pygame.font.Font(None, 36).render("Click to return to menu", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.MOUSEBUTTONDOWN:
            return True
    return False

def draw():
    """Draws game world"""
    screen.fill(LIGHT_GRAY)
    
    if game_state["state"] == EXPLORATION:
        screen.fill(LIGHT_GRAY)
        # Draw walls
        for wall in walls:
            pygame.draw.rect(screen, DARK_GREEN, wall)
        
        for enemy in enemies:
            enemy.draw(screen)
    
    elif game_state["state"] == BATTLE:
        screen.fill(BACKGROUND_COLOR)
        # Draw battle arena
        draw_border()
        
        # Draw projectiles (visible during aiming and normal turns)
        for proj in projectiles:
            pygame.draw.circle(screen, WHITE, (int(proj["x"]), int(proj["y"])), 5)
        
        # Draw aiming minigame if active
        if aim_active:
            draw_aim_bar(screen)
            aim_text = font.render("Click to hit!", True, YELLOW)
            screen.blit(aim_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 30))
        else:
            draw_buttons()

    draw_player()
    
    # Draw UI
    display_hp = max(0, PLAYER['HP'])  # Don't show negative HP
    hp_text = font.render(f"HP: {display_hp}/{PLAYER['MAX_HP']}", True, WHITE)
    screen.blit(hp_text, (10, 10))
    
    # Draw enemies defeated counter
    defeated_text = font.render(f"Enemies Defeated: {enemies_defeated}", True, YELLOW)
    screen.blit(defeated_text, (10, 35))
    
    if game_state["state"] == BATTLE:
        if not player_turn:
            battle_text = font.render("Enemy's turn", True, WHITE)
            screen.blit(battle_text, (10, 40))
        
        if enemies:
            enemy_hp = font.render(f"{enemies[0].name} HP: {enemies[0].hp}", True, RED)
            screen.blit(enemy_hp, (SCREEN_WIDTH - 200, 10))
    message_text = font.render(message, True, WHITE)
    screen.blit(message_text, (10, SCREEN_HEIGHT - 30))
    
    
    # Bottom-right label
#    label_text = font.render(state_label, True, WHITE)
#    screen.blit(label_text, (SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30)) # 150
    
    pygame.display.flip()

def game_over():
    """Returns True if you die and transitions to game over screen"""
    if PLAYER["HP"] <= 0:
        if game_state["state"] != GAME_OVER:
            game_state["state"] = GAME_OVER
        return True
    
    return False


def stop_when():
    """Returns True if game should stop"""

    action_quit=quit_is_pressed()
    
    return action_quit

