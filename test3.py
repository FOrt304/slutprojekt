import pygame
import random
from enum import Enum
import math

pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GRAY = (100, 100, 100)

class GameState(Enum):
    EXPLORATION = 1
    BATTLE = 2
    DIALOGUE = 3

def draw_heart(screen, x, y, size, color):
    # Draw a pixel heart shape like in Deltarune
    pixel_size = size // 5
    heart_pixels = [
        (2, 0),  # top point
        (1, 1), (3, 1),  # upper curves
        (0, 2), (4, 2),  # left and right top
        (0, 3), (4, 3),  # left and right bottom
        (1, 4), (3, 4)   # lower curves
    ]
    offset_x = x - 2 * pixel_size
    offset_y = y - 2 * pixel_size
    for dx, dy in heart_pixels:
        pygame.draw.rect(screen, color, (offset_x + dx * pixel_size, offset_y + dy * pixel_size, pixel_size, pixel_size))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.hp = 20
        self.max_hp = 20
        self.attack = 5
        self.speed = 3

    def draw(self, screen):
        draw_heart(screen, self.x + self.width // 2, self.y + self.height // 2, self.width, RED)

    def handle_input(self, keys):
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed

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

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Deltarune Style Game")
        self.clock = pygame.time.Clock()
        self.state = GameState.EXPLORATION
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = [Enemy(200, 150, "Dummy")]
        self.font = pygame.font.Font(None, 24)
        self.battle_turn = 0
        self.message = ""
        # Walls for Deltarune-like map
        self.walls = [
            pygame.Rect(0, 0, SCREEN_WIDTH, 50),  # Top wall
            pygame.Rect(0, 0, 50, SCREEN_HEIGHT),  # Left wall
            pygame.Rect(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT),  # Right wall
            pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),  # Bottom wall
            pygame.Rect(200, 100, 50, 200),  # Vertical wall
            pygame.Rect(400, 200, 200, 50),  # Horizontal wall
        ]
        # Initialize mixer for music
        pygame.mixer.init()
        # Add "Field of Hopes and Dreams" by Toby Fox
        # Make sure to have the mp3 file in the same directory
        pygame.mixer.music.load('field_of_hopes_and_dreams.mp3')
        pygame.mixer.music.play(-1)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.BATTLE and event.key == pygame.K_SPACE:
                    self.player_attack()
        return True

    def update(self):
        if self.state == GameState.EXPLORATION:
            old_x, old_y = self.player.x, self.player.y
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            
            # Check wall collisions
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            for wall in self.walls:
                if player_rect.colliderect(wall):
                    self.player.x, self.player.y = old_x, old_y
                    break
            
            for enemy in self.enemies:
                if self.check_collision(self.player, enemy):
                    self.state = GameState.BATTLE
                    self.message = f"Encountered {enemy.name}!"
        
        elif self.state == GameState.BATTLE:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            
            # Keep player within battle arena
            arena_rect = pygame.Rect(100, 100, 600, 400)
            self.player.x = max(arena_rect.left, min(self.player.x, arena_rect.right - self.player.width))
            self.player.y = max(arena_rect.top, min(self.player.y, arena_rect.bottom - self.player.height))

    def check_collision(self, obj1, obj2):
        return (obj1.x < obj2.x + obj2.width and
                obj1.x + obj1.width > obj2.x and
                obj1.y < obj2.y + obj2.height and
                obj1.y + obj1.height > obj2.y)

    def player_attack(self):
        if self.enemies:
            damage = self.player.attack + random.randint(-2, 2)
            self.enemies[0].hp -= damage
            self.message = f"Dealt {damage} damage!"
            
            if self.enemies[0].hp <= 0:
                self.message = f"Defeated {self.enemies[0].name}!"
                self.enemies.pop(0)
                self.state = GameState.EXPLORATION
            else:
                self.enemy_attack()

    def enemy_attack(self):
        if self.enemies:
            damage = self.enemies[0].attack + random.randint(-1, 1)
            self.player.hp -= damage
            self.message = f"{self.enemies[0].name} dealt {damage} damage!"
            
            if self.player.hp <= 0:
                self.message = "You were defeated!"

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == GameState.EXPLORATION:
            # Draw walls
            for wall in self.walls:
                pygame.draw.rect(self.screen, GRAY, wall)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
        
        elif self.state == GameState.BATTLE:
            # Draw battle arena like in Deltarune
            arena_rect = pygame.Rect(100, 100, 600, 400)
            pygame.draw.rect(self.screen, WHITE, arena_rect)
            pygame.draw.rect(self.screen, BLACK, arena_rect, 5)  # border
        
        self.player.draw(self.screen)
        
        # Draw UI
        hp_text = self.font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (10, 10))
        
        if self.state == GameState.BATTLE:
            battle_text = self.font.render("Press SPACE to attack", True, YELLOW)
            self.screen.blit(battle_text, (10, 50))
            
            if self.enemies:
                enemy_hp = self.font.render(f"{self.enemies[0].name} HP: {self.enemies[0].hp}", True, RED)
                self.screen.blit(enemy_hp, (SCREEN_WIDTH - 200, 10))
        
        message_text = self.font.render(self.message, True, WHITE)
        self.screen.blit(message_text, (10, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()