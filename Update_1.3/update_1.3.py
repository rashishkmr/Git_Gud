import math
import sys
import time
import random  # Added missing import

try:
    import pygame
except ModuleNotFoundError:
    print("Error: pygame module not found. Please install it using 'pip install pygame'.")
    sys.exit(1)

pygame.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

cannon_x, cannon_y = 50, HEIGHT - 50
cannon_angle = 45
cannon_velocity = 50

# Randomize target position initially
target_x, target_y = random.randint(600, WIDTH - 50), random.randint(400, HEIGHT - 50)

def reset_game():
    global projectile_x, projectile_y, projectile_velocity_x, projectile_velocity_y, projectile_in_flight
    global target_x, target_y
    projectile_x, projectile_y = cannon_x, cannon_y
    projectile_velocity_x = 0
    projectile_velocity_y = 0
    projectile_in_flight = False
    target_x, target_y = random.randint(600, WIDTH - 50), random.randint(400, HEIGHT - 50)

reset_game()

wind_velocity = 0
gravity = 0.1
score = 0
level = 1

running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not projectile_in_flight:
                projectile_in_flight = True
                projectile_x, projectile_y = cannon_x, cannon_y
                projectile_velocity_x = cannon_velocity * math.cos(math.radians(cannon_angle)) + wind_velocity
                projectile_velocity_y = -cannon_velocity * math.sin(math.radians(cannon_angle))
            elif event.key == pygame.K_UP:
                cannon_angle = min(90, cannon_angle + 5)
            elif event.key == pygame.K_DOWN:
                cannon_angle = max(0, cannon_angle - 5)
            elif event.key == pygame.K_LEFT:
                cannon_velocity = max(5, cannon_velocity - 5)
            elif event.key == pygame.K_RIGHT:
                cannon_velocity = min(100, cannon_velocity + 5)
            elif event.key == pygame.K_w:
                wind_velocity += 0.1
            elif event.key == pygame.K_s:
                wind_velocity -= 0.1
            elif event.key == pygame.K_r:
                reset_game()

    if projectile_in_flight:
        projectile_x += projectile_velocity_x
        projectile_y -= projectile_velocity_y
        projectile_velocity_y += gravity

        # Improved hit detection to match the square target
        if target_x <= projectile_x <= target_x + 50 and target_y <= projectile_y <= target_y + 50:
            score += 1
            level += 1
            print("Hit! Score:", score)
            reset_game()

        if projectile_x < 0 or projectile_x > WIDTH or projectile_y < 0 or projectile_y > HEIGHT:
            projectile_in_flight = False

    pygame.draw.rect(screen, RED, (cannon_x, cannon_y, 50, 50))
    pygame.draw.line(screen, BLACK, (cannon_x, cannon_y), (cannon_x + 50 * math.cos(math.radians(cannon_angle)), cannon_y - 50 * math.sin(math.radians(cannon_angle))))
    pygame.draw.rect(screen, GREEN, (target_x, target_y, 50, 50))
    
    if projectile_in_flight:
        pygame.draw.circle(screen, BLACK, (int(projectile_x), int(projectile_y)), 5)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

