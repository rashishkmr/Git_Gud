import math
import pygame
import sys
import time

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

target_x, target_y = WIDTH - 50, HEIGHT - 50

projectile_x, projectile_y = cannon_x, cannon_y
projectile_angle = cannon_angle
projectile_velocity_x = 0
projectile_velocity_y = 0
projectile_in_flight = False
projectile_radius = 5

wind_velocity = 0

gravity = 0.1

score = 0

level = 1


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not projectile_in_flight:
                projectile_in_flight = True
                projectile_x, projectile_y = cannon_x, cannon_y
                projectile_angle = cannon_angle
                projectile_velocity_x = cannon_velocity * math.cos(math.radians(projectile_angle)) + wind_velocity
                projectile_velocity_y = -cannon_velocity * math.sin(math.radians(projectile_angle))
            elif event.key == pygame.K_UP:
                cannon_angle += 5
            elif event.key == pygame.K_DOWN:
                cannon_angle -= 5
            elif event.key == pygame.K_LEFT:
                cannon_velocity -= 5
            elif event.key == pygame.K_RIGHT:
                cannon_velocity += 5
            elif event.key == pygame.K_w:
                wind_velocity += 0.1
            elif event.key == pygame.K_s:
                wind_velocity -= 0.1

    if projectile_in_flight:
        projectile_x += projectile_velocity_x
        projectile_y -= projectile_velocity_y
        projectile_velocity_y += gravity

        if (projectile_x - target_x) ** 2 + (projectile_y - target_y) ** 2 < 50 ** 2:
            score += 1
            level += 1
            target_x = random.randint(0, WIDTH - 50)
            target_y = random.randint(0, HEIGHT - 50)
            print("Hit!")
            projectile_in_flight = False

        if projectile_x < 0 or projectile_x > WIDTH or projectile_y < 0 or projectile_y > HEIGHT:
            projectile_in_flight = False


    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, (cannon_x, cannon_y, 50, 50))
    pygame.draw.line(screen, BLACK, (cannon_x, cannon_y), (cannon_x + 50 * math.cos(math.radians(cannon_angle)), cannon_y - 50 * math.sin(math.radians(cannon_angle))))
    pygame.draw.rect(screen, GREEN, (target_x, target_y, 50, 50))
    if projectile_in_flight:
        pygame.draw.circle(screen, BLACK, (int(projectile_x), int(projectile_y)), projectile_radius)
    #text = font.render(f"Angle: {cannon_angle}, Velocity: {cannon_velocity}", True, BLACK)
    #screen.blit(text, (10, 10))

    pygame.display.flip()

    clock.tick(60)
