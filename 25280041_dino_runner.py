import pygame
import sys
import random

WIDTH, HEIGHT = 900, 400
FPS = 60
GRAVITY = 0.6
JUMP_VEL = -13
TERMINAL_VEL = 14
GROUND_Y = HEIGHT - 60
BASE_SPEED = 6
MAX_SPEED = 20
DAY_COLOR = (100, 149, 237)
NIGHT_COLOR = (23, 32, 42)
DAY_GROUND_COLOR = (128, 128, 128)
NIGHT_GROUND_COLOR = (50, 50, 50)
OBSTACLE_COLOR_DAY = (50, 50, 50)
OBSTACLE_COLOR_NIGHT = (200, 200, 200)
FONT_SIZE = 30

def load_high_score():
    try:
        with open('high_score.txt', 'r') as f:
            return int(f.read())
    except FileNotFoundError:
        return 0

def save_high_score(score):
    with open('high_score.txt', 'w') as f:
        f.write(str(score))

class Player:
    def __init__(self):
        self.x = 100
        self.y = GROUND_Y - 50
        self.vy = 0
        self.ducking = False
        self.rect = pygame.Rect(self.x, self.y, 50, 50)

    def jump(self):
        if self.vy == 0:
            self.vy = JUMP_VEL

    def duck(self):
        self.ducking = True
        self.rect.height = 25
        self.rect.y = GROUND_Y - 25

    def unduck(self):
        self.ducking = False
        self.rect.height = 50
        self.rect.y = GROUND_Y - 50

    def update(self):
        if self.vy < TERMINAL_VEL:
            self.vy += GRAVITY
        self.rect.y += self.vy
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vy = 0

    def get_rect(self):
        if self.ducking:
            return pygame.Rect(self.rect.x + 5, self.rect.y + 10, 40, 15)
        else:
            return pygame.Rect(self.rect.x + 10, self.rect.y + 10, 30, 30)

    def draw(self, screen, day):
        if day:
            color = (0, 0, 0)
        else:
            color = (255, 255, 255)
        pygame.draw.rect(screen, color, self.rect)

class Cactus:
    def __init__(self, x, clustered):
        self.x = x
        self.clustered = clustered
        if clustered:
            self.rects = [pygame.Rect(x, GROUND_Y - 48, 22, 48), pygame.Rect(x + 25, GROUND_Y - 48, 22, 48)]
        else:
            self.rects = [pygame.Rect(x, GROUND_Y - 48, 22, 48)]

    def update(self, speed):
        for rect in self.rects:
            rect.x -= speed
            if rect.x < -rect.width:
                return False
        return True

    def get_rects(self):
        return self.rects

    def draw(self, screen, day):
        for rect in self.rects:
            if day:
                color = OBSTACLE_COLOR_DAY
            else:
                color = OBSTACLE_COLOR_NIGHT
            pygame.draw.rect(screen, color, rect)

class Pterodactyl:
    def __init__(self, x):
        self.x = x
        self.rect = pygame.Rect(x, GROUND_Y // 2, 50, 50)
        self.wing_frame = 0

    def update(self, speed):
        self.rect.x -= speed
        self.wing_frame += 1
        if self.wing_frame >= 10:
            self.wing_frame = 0
        if self.rect.x < -self.rect.width:
            return False
        return True

    def get_rect(self):
        return pygame.Rect(self.rect.x + 10, self.rect.y + 10, 30, 30)

    def draw(self, screen, day):
        if day:
            color = OBSTACLE_COLOR_DAY
        else:
            color = OBSTACLE_COLOR_NIGHT
        pygame.draw.rect(screen, color, self.rect)
        if self.wing_frame < 5:
            pygame.draw.rect(screen, color, (self.rect.x, self.rect.y - 10, 50, 10))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, FONT_SIZE)

    high_score = load_high_score()
    player = Player()
    cacti = []
    pterodactyls = []
    speed = BASE_SPEED
    score = 0
    frame_count = 0
    day = True
    spawn_cooldown = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if player.vy == 0:
                        player.jump()
                elif event.key == pygame.K_DOWN:
                    player.duck()
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    player.unduck()

        player.update()

        for cactus in cacti[:]:
            if not cactus.update(speed):
                cacti.remove(cactus)
        for pterodactyl in pterodactyls[:]:
            if not pterodactyl.update(speed):
                pterodactyls.remove(pterodactyl)

        spawn_cooldown -= 1
        if spawn_cooldown <= 0:
            if random.random() < 0.35:
                cacti.append(Cactus(WIDTH, True))
            else:
                cacti.append(Cactus(WIDTH, False))
            spawn_cooldown = 250 // int(speed)
            if random.random() < 0.1:
                pterodactyls.append(Pterodactyl(WIDTH))

        for cactus in cacti:
            for rect in cactus.get_rects():
                if player.get_rect().colliderect(rect):
                    running = False
        for pterodactyl in pterodactyls:
            if player.get_rect().colliderect(pterodactyl.get_rect()) and not player.ducking:
                running = False

        score += 1
        frame_count += 1
        speed = min(speed + 0.002, MAX_SPEED)

        if score % 500 == 0:
            day = not day

        if day:
            screen.fill(DAY_COLOR)
            ground_color = DAY_GROUND_COLOR
            obstacle_color = OBSTACLE_COLOR_DAY
        else:
            screen.fill(NIGHT_COLOR)
            ground_color = NIGHT_GROUND_COLOR
            obstacle_color = OBSTACLE_COLOR_NIGHT
        pygame.draw.rect(screen, ground_color, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        player.draw(screen, day)
        for cactus in cacti:
            cactus.draw(screen, day)
        for pterodactyl in pterodactyls:
            pterodactyl.draw(screen, day)
        score_text = font.render(f"{score:06d}", True, (255, 255, 255) if not day else (0, 0, 0))
        screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
        high_score_text = font.render(f"High: {high_score:06d}", True, (255, 255, 255) if not day else (0, 0, 0))
        screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - score_text.get_width() - 20, 10))
        if day:
            day_text = font.render("DAY", True, (0, 0, 0))
        else:
            day_text = font.render("NIGHT", True, (255, 255, 255))
        screen.blit(day_text, (10, 10))
        speed_text = font.render(f"Speed: {int(speed)}", True, (255, 255, 255) if not day else (0, 0, 0))
        screen.blit(speed_text, (10, 50))

        pygame.display.flip()
        clock.tick(FPS)

    if score > high_score:
        high_score = score
    save_high_score(high_score)
    screen.fill((0, 0, 0))
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    score_text = font.render(f"Score: {score:06d}", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - score_text.get_height() // 2 + 50))
    high_score_text = font.render(f"High Score: {high_score:06d}", True, (255, 255, 255))
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 - high_score_text.get_height() // 2 + 100))
    restart_text = font.render("Press SPACE to restart", True, (255, 255, 255))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 - restart_text.get_height() // 2 + 150))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    waiting = False
                    main()

if __name__ == '__main__':
    main()