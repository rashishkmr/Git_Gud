import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
CANNON_WIDTH, CANNON_HEIGHT = 50, 50
TARGET_WIDTH, TARGET_HEIGHT = 50, 50
GRAVITY = 0.1

# Set up some colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the font
font = pygame.font.Font(None, 36)

# Set up the clock
clock = pygame.time.Clock()

class Cannon:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT - CANNON_HEIGHT - 50
        self.angle = 45
        self.velocity = 50

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, CANNON_WIDTH, CANNON_HEIGHT))
        end_x = self.x + CANNON_WIDTH + 50 * math.cos(math.radians(self.angle))
        end_y = self.y + CANNON_HEIGHT // 2 - 50 * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, BLUE, (self.x + CANNON_WIDTH, self.y + CANNON_HEIGHT // 2), (end_x, end_y), 5)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.angle += 1
        if keys[pygame.K_DOWN]:
            self.angle -= 1
        if keys[pygame.K_LEFT]:
            self.velocity -= 5
        if keys[pygame.K_RIGHT]:
            self.velocity += 5

class Ball:
    def __init__(self, cannon):
        self.x = cannon.x + CANNON_WIDTH
        self.y = cannon.y + CANNON_HEIGHT // 2
        self.speed_x = cannon.velocity * math.cos(math.radians(cannon.angle))
        self.speed_y = -cannon.velocity * math.sin(math.radians(cannon.angle))
        self.angle = cannon.angle

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), BALL_RADIUS)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += GRAVITY

        if self.y > HEIGHT - BALL_RADIUS:
            self.y = HEIGHT - BALL_RADIUS
            self.speed_y = -self.speed_y * 0.8

class Target:
    def __init__(self):
        self.x = WIDTH - TARGET_WIDTH - 50
        self.y = HEIGHT // 2
        self.angle_x = 0
        self.angle_y = 0
        self.radius_x = 100
        self.radius_y = 50

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, TARGET_WIDTH, TARGET_HEIGHT))

    def update(self):
        self.x = WIDTH - TARGET_WIDTH - 50 + self.radius_x * math.cos(math.radians(self.angle_x))
        self.y = HEIGHT // 2 + self.radius_y * math.sin(math.radians(self.angle_y))
        self.angle_x += 1
        self.angle_y += 1

def main():
    try:
        cannon = Cannon()
        balls = []
        target = Target()
        score = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        balls.append(Ball(cannon))

            screen.fill(WHITE)

            cannon.draw()
            cannon.update()

            for ball in balls:
                ball.draw()
                ball.update()
                if math.hypot(ball.x - target.x, ball.y - target.y) < BALL_RADIUS + TARGET_WIDTH // 2:
                    score += 1
                    balls.remove(ball)

            target.draw()
            target.update()

            text = font.render(f'Score: {score}', True, BLUE)
            screen.blit(text, (10, 10))

            pygame.display.flip()
            clock.tick(60)

    except pygame.error as e:
        print(f'Pygame error: {e}')
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    main()
