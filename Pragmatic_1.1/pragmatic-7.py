import pygame
import random

pygame.init()

# =====================
# CONSTANTS
# =====================
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
FPS = 60
PLAYER_LIVES = 3
POWERUP_SIZE = 30
POWERUP_TIME = 300  # frames
BOSS_HEALTH = 10

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (100, 100, 100)
BG_COLOR = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle City - Python Edition")
clock = pygame.time.Clock()

# =====================
# LEVEL MAPS
# =====================
LEVELS = {
    1: [
        "00000000000000000000",
        "01111100001111100000",
        "01000100001000100000",
        "01000100001000100000",
        "01111100001111100000",
        "00000000000000000000",
        "00011111111111000000",
        "00010000000001000000",
        "00010000000001000000",
        "00011111111111000000",
        "00000000000000000000",
        "00000000000000000000",
        "00000000000000000000",
        "00000000000000000000",
        "00000000000000000000",
    ],

    2: [
        "00000000000000000000",
        "01111111100111111100",
        "01000000100100000100",
        "01011110111101110100",
        "01010000100001000100",
        "01110111101111011100",
        "00000000000000000000",
        "00111100000000111100",
        "00100100000000100100",
        "00111100000000111100",
        "00000000000000000000",
        "00000000000000000000",
        "00000000000000000000",
        "00000000000000000000",
        "00000000000000000000",
    ],

    3: [
        "22222222222222222222",
        "20000000000000000002",
        "20111101111101111102",
        "20100001000001000002",
        "20101111011111011102",
        "20001000010000100002",
        "20111011110111101102",
        "20000000000000000002",
        "20000111101111100002",
        "20000000000000000002",
        "20111111111111111102",
        "20000000000000000002",
        "22222222222222222222",
        "00000000000000000000",
        "00000000000000000000",
    ],

    4: [
        "00000022222200000000",
        "01111120000021111100",
        "01000120000021000100",
        "01000121111121000100",
        "01111120000021111100",
        "00000020000020000000",
        "00111121111121111100",
        "00100120000020000100",
        "00100120000020000100",
        "00111121111121111100",
        "00000020000020000000",
        "00000020000020000000",
        "00000022222220000000",
        "00000000000000000000",
        "00000000000000000000",
    ],

    5: [
        "22222222222222222222",
        "21111111111111111112",
        "21000000000000000012",
        "21011111101111111012",
        "21010000101000001012",
        "21010111101111101012",
        "21010000000000001012",
        "21011111111111111012",
        "21000000000000000012",
        "21111111111111111112",
        "20000000000000000002",
        "22222222222222222222",
        "00000000000000000000",
        "00000000000000000000",
        "00000000000000000000",
    ]
}

# =====================
# IMAGES
# =====================
tank_img = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.polygon(tank_img, GREEN, [(20, 0), (10, 40), (30, 40)])

bullet_img = pygame.Surface((10, 10))
bullet_img.fill(YELLOW)

# =====================
# CLASSES
# =====================
class Obstacle:
    def __init__(self, x, y, destructible):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.destructible = destructible
        self.health = 1 if destructible else 999

    def draw(self, surface):
        color = DARK_GRAY if self.destructible else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

class Bullet:
    def __init__(self, x, y, direction):
        self.x, self.y = x, y
        self.direction = direction
        self.speed = 10
        self.rect = pygame.Rect(x, y, 10, 10)

    def update(self, obstacles, enemies):
        if self.direction == "UP": self.y -= self.speed
        if self.direction == "DOWN": self.y += self.speed
        if self.direction == "LEFT": self.x -= self.speed
        if self.direction == "RIGHT": self.x += self.speed

        self.rect.topleft = (self.x, self.y)

        if not screen.get_rect().colliderect(self.rect):
            return False

        for obs in obstacles[:]:
            if obs.rect.colliderect(self.rect):
                if obs.destructible:
                    obs.health -= 1
                    if obs.health <= 0:
                        obstacles.remove(obs)
                return False

        for enemy in enemies[:]:
            if enemy.rect.colliderect(self.rect):
                if isinstance(enemy, BossTank):  # Boss hits reduce health
                    enemy.health -= 1
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                else:
                    enemies.remove(enemy)
                return False

        return True

    def draw(self, surface):
        surface.blit(bullet_img, self.rect)

class Tank:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.x, self.y = x, y
        self.direction = "UP"
        self.speed = 5
        self.bullets = []
        self.lives = PLAYER_LIVES
        self.invincible = 120  # frames
        self.rapid_fire = 0

    def respawn(self):
        self.x, self.y = self.start_x, self.start_y
        self.invincible = 120

    def move(self, keys, obstacles):
        dx = dy = 0
        if keys[pygame.K_UP]: dy, self.direction = -self.speed, "UP"
        if keys[pygame.K_DOWN]: dy, self.direction = self.speed, "DOWN"
        if keys[pygame.K_LEFT]: dx, self.direction = -self.speed, "LEFT"
        if keys[pygame.K_RIGHT]: dx, self.direction = self.speed, "RIGHT"

        new_rect = pygame.Rect(self.x + dx, self.y + dy, 40, 40)
        if screen.get_rect().contains(new_rect) and not any(o.rect.colliderect(new_rect) for o in obstacles):
            self.x += dx
            self.y += dy

    def shoot(self):
        limit = 10 if self.rapid_fire > 0 else 5
        if len(self.bullets) < limit:
            self.bullets.append(Bullet(self.x + 15, self.y + 15, self.direction))

    def hit(self):
        if self.invincible <= 0:
            self.lives -= 1
            self.respawn()

    def draw(self, surface, obstacles, enemies):
        if self.invincible > 0:
            self.invincible -= 1
            if self.invincible % 10 < 5:
                return  # blinking

        rot = {"UP": 0, "DOWN": 180, "LEFT": 90, "RIGHT": 270}[self.direction]
        img = pygame.transform.rotate(tank_img, rot)
        surface.blit(img, (self.x, self.y))

        for b in self.bullets[:]:
            if not b.update(obstacles, enemies):
                self.bullets.remove(b)
            else:
                b.draw(surface)

class PowerUp:
    def __init__(self, x, y, kind):
        self.rect = pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE)
        self.kind = kind  # "shield" or "rapid"

    def draw(self, surface):
        if self.kind == "shield":
            color = BLUE
        else:
            color = YELLOW
        pygame.draw.rect(surface, color, self.rect)

class EnemyTank:
    def __init__(self, x, y, type="regular"):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.speed = 2
        self.type = type
        self.health = 3 if self.type == "regular" else BOSS_HEALTH

    def move(self, obstacles):
        dx = dy = 0
        if self.direction == "UP": dy = -self.speed
        if self.direction == "DOWN": dy = self.speed
        if self.direction == "LEFT": dx = -self.speed
        if self.direction == "RIGHT": dx = self.speed

        new_rect = self.rect.move(dx, dy)
        if not any(o.rect.colliderect(new_rect) for o in obstacles):
            self.rect = new_rect
        else:
            self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)

class BossTank(EnemyTank):
    def __init__(self, x, y):
        super().__init__(x, y, "boss")
        self.health = BOSS_HEALTH  # Boss has more health

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 255), self.rect)  # Boss color purple


# =====================
# LEVEL LOADER
# =====================
def load_level(level):
    obstacles = []
    enemies = []

    for y, row in enumerate(LEVELS[level]):
        for x, tile in enumerate(row):
            px, py = x * TILE_SIZE, y * TILE_SIZE
            if tile == "1":
                obstacles.append(Obstacle(px, py, True))
            elif tile == "2":
                obstacles.append(Obstacle(px, py, False))

    if level % 3 == 0:  # Boss level
        enemies.append(BossTank(WIDTH // 2 - 30, HEIGHT // 2 - 30))
    else:
        for _ in range(level + 2):
            x = random.randint(0, WIDTH - 40)
            y = random.randint(0, 200)
            enemy_type = random.choice(["regular", "heavy", "shooter"])
            enemies.append(EnemyTank(x, y, enemy_type))

    return obstacles, enemies

# =====================
# LEVEL TRANSITION
# =====================
def show_level_transition(level):
    transition_text = font.render(f"Stage {level} Complete!", True, WHITE)
    screen.fill(BG_COLOR)
    screen.blit(transition_text, (WIDTH // 2 - transition_text.get_width() // 2, HEIGHT // 2 - 50))
    pygame.display.flip()
    pygame.time.delay(1500)  # Wait 1.5 seconds

    press_key = font.render("Press any key to continue", True, WHITE)
    screen.blit(press_key, (WIDTH // 2 - press_key.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# =====================
# GAME SETUP
# =====================
current_level = 1
player = Tank(WIDTH // 2 - 20, HEIGHT - 60)
obstacles, enemies = load_level(current_level)
font = pygame.font.SysFont(None, 36)

# =====================
# GAME LOOP
# =====================
running = True
while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.shoot()

    keys = pygame.key.get_pressed()
    player.move(keys, obstacles)

    for e in enemies:
        e.move(obstacles)
        e.draw(screen)

    for o in obstacles:
        o.draw(screen)

    player.draw(screen, obstacles, enemies)

    if not enemies:
        show_level_transition(current_level)
        current_level += 1
        if current_level > 5:
            current_level = 1
        obstacles, enemies = load_level(current_level)

    screen.blit(font.render(f"Level: {current_level}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (10, 40))

    pygame.display.flip()

pygame.quit()

