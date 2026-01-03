import pygame
import random

# Initialize pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
BG_COLOR = (0, 0, 0)
FPS = 60

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (100, 100, 100)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle City - Python Edition (Improved)")
clock = pygame.time.Clock()

# Load Tank Image (with direction rotation)
tank_img = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.polygon(tank_img, GREEN, [(20, 0), (10, 40), (30, 40)])
bullet_img = pygame.Surface((10, 10))
bullet_img.fill(YELLOW)

# Obstacle Class
class Obstacle:
    def __init__(self, x, y, destructible=False):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.destructible = destructible
        self.health = 1 if destructible else 999  # Indestructible = high health

    def draw(self, surface):
        color = DARK_GRAY if self.destructible else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

# Player Tank Class
class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.direction = "UP"
        self.bullets = []
        self.alive = True

    def move(self, keys, obstacles):
        if not self.alive:
            return

        new_x, new_y = self.x, self.y
        dx = dy = 0

        if keys[pygame.K_UP]:
            dy -= self.speed
            self.direction = "UP"
        if keys[pygame.K_DOWN]:
            dy += self.speed
            self.direction = "DOWN"
        if keys[pygame.K_LEFT]:
            dx -= self.speed
            self.direction = "LEFT"
        if keys[pygame.K_RIGHT]:
            dx += self.speed
            self.direction = "RIGHT"

        new_rect = pygame.Rect(new_x + dx, new_y + dy, 40, 40)

        # Check collision with obstacles
        if not any(obs.rect.colliderect(new_rect) for obs in obstacles):
            self.x += dx
            self.y += dy

        # Keep within screen bounds
        self.x = max(0, min(WIDTH - 40, self.x))
        self.y = max(0, min(HEIGHT - 40, self.y))

    def shoot(self):
        if len(self.bullets) < 5 and self.alive:
            offset_x = offset_y = 15
            if self.direction == "UP": offset_y = -10
            elif self.direction == "DOWN": offset_y = 40
            elif self.direction == "LEFT": offset_x = -10
            elif self.direction == "RIGHT": offset_x = 40
            self.bullets.append(Bullet(self.x + offset_x, self.y + offset_y, self.direction))

    def draw(self, surface):
        if not self.alive:
            return
        rotated = pygame.transform.rotate(tank_img, {"UP": 0, "DOWN": 180, "LEFT": 90, "RIGHT": 270}[self.direction])
        rect = rotated.get_rect(center=(self.x + 20, self.y + 20))
        surface.blit(rotated, rect.topleft)
        for bullet in self.bullets[:]:
            if not bullet.update(obstacles, enemies):
                self.bullets.remove(bullet)
            else:
                bullet.draw(surface)

# Bullet Class
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 10
        self.rect = pygame.Rect(x, y, 10, 10)

    def move(self):
        if self.direction == "UP": self.y -= self.speed
        elif self.direction == "DOWN": self.y += self.speed
        elif self.direction == "LEFT": self.x -= self.speed
        elif self.direction == "RIGHT": self.x += self.speed
        self.rect.topleft = (self.x, self.y)

    def update(self, obstacles, enemies):
        self.move()

        # Out of bounds
        if not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT):
            return False

        # Hit obstacle
        for obs in obstacles:
            if obs.rect.colliderect(self.rect):
                if obs.destructible:
                    obs.health -= 1
                    if obs.health <= 0:
                        obstacles.remove(obs)
                return False

        # Hit enemy
        for enemy in enemies[:]:
            if enemy.alive and enemy.rect.colliderect(self.rect):
                enemy.alive = False
                enemies.remove(enemy)
                return False

        return True

    def draw(self, surface):
        surface.blit(bullet_img, (self.x, self.y))

# Enemy Tank Class
class EnemyTank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.alive = True
        self.change_timer = 0
        self.rect = pygame.Rect(x, y, 40, 40)

    def move(self, obstacles, player):
        if not self.alive:
            return

        self.change_timer -= 1
        if self.change_timer <= 0:
            # Smarter AI: sometimes chase player
            if random.random() < 0.3:
                dx = player.x - self.x
                dy = player.y - self.y
                if abs(dx) > abs(dy):
                    self.direction = "RIGHT" if dx > 0 else "LEFT"
                else:
                    self.direction = "DOWN" if dy > 0 else "UP"
            else:
                self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            self.change_timer = random.randint(60, 120)

        new_x, new_y = self.x, self.y
        if self.direction == "UP": new_y -= self.speed
        elif self.direction == "DOWN": new_y += self.speed
        elif self.direction == "LEFT": new_x -= self.speed
        elif self.direction == "RIGHT": new_x += self.speed

        new_rect = pygame.Rect(new_x, new_y, 40, 40)

        if not any(obs.rect.colliderect(new_rect) for obs in obstacles):
            self.x, self.y = new_x, new_y
        else:
            # Avoid getting stuck: try perpendicular directions
            dirs = ["UP", "DOWN", "LEFT", "RIGHT"]
            dirs.remove(self.direction)
            self.direction = random.choice(dirs)
            self.change_timer = 30

        self.rect.topleft = (self.x, self.y)
        self.x = max(0, min(WIDTH - 40, self.x))
        self.y = max(0, min(HEIGHT - 40, self.y))

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, RED, (self.x, self.y, 40, 40))
            pygame.draw.circle(surface, WHITE, (self.x + 20, self.y + 20), 5)

# Initialize Game Objects
player = Tank(WIDTH // 2 - 20, HEIGHT - 80)
enemies = [EnemyTank(random.randint(50, WIDTH-90), random.randint(50, 200)) for _ in range(4)]
obstacles = [
    Obstacle(x * TILE_SIZE, y * TILE_SIZE, random.random() < 0.3)
    for x in range(WIDTH // TILE_SIZE)
    for y in range(HEIGHT // TILE_SIZE)
    if random.random() < 0.05 and not (x == WIDTH//TILE_SIZE//2 and y >= (HEIGHT//TILE_SIZE)-3)
][:15]

# Game Loop
running = True
font = pygame.font.SysFont(None, 36)
while running:
    dt = clock.tick(FPS)
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    keys = pygame.key.get_pressed()
    player.move(keys, obstacles)

    for enemy in enemies[:]:
        enemy.move(obstacles, player)
        enemy.draw(screen)

    for obstacle in obstacles:
        obstacle.draw(screen)

    player.draw(screen)

    # UI
    score = len([e for e in enemies if not e.alive])
    text = font.render(f"Enemies Left: {len([e for e in enemies if e.alive])}", True, WHITE)
    screen.blit(text, (10, 10))

    if all(not e.alive for e in enemies):
        win_text = font.render("YOU WIN!", True, YELLOW)
        screen.blit(win_text, (WIDTH//2 - 100, HEIGHT//2))
    elif not player.alive:
        lose_text = font.render("GAME OVER", True, RED)
        screen.blit(lose_text, (WIDTH//2 - 120, HEIGHT//2))

    pygame.display.flip()

pygame.quit()
