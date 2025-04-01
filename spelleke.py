import pygame
import sys
import math
from pygame.locals import *

# Initialisatie
pygame.init()
screen = pygame.display.set_mode((900, 600))
clock = pygame.time.Clock()

# Kleuren
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (34, 139, 34)  # Forest green
BLUE = (0, 0, 255)
GRID_COLOR = (220, 220, 220)
SLIDER_BG_COLOR = (200, 200, 200)
SLIDER_KNOB_COLOR = (70, 130, 180)  # Steelblue
TEXT_COLOR = (50, 50, 50)
INPUT_BG_COLOR = (240, 240, 240)
BUTTON_COLOR = (100, 150, 200)
BUTTON_HOVER_COLOR = (120, 170, 220)

# Fonts
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)
font_input = pygame.font.Font(None, 28)

# Game states
MENU = 0
PLAYING = 1
LEVEL_COMPLETE = 2
GAME_COMPLETE = 3

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)

        text_surf = font_medium.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            return self.action
        return None

class MovingBarrier:
    def __init__(self, start_pos, end_pos, speed, vertical=False):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.speed = speed
        self.current_pos = list(start_pos)
        self.direction = 1  # 1 for moving towards end_pos, -1 for moving towards start_pos
        self.vertical = vertical

    def update(self):
        # Update the current position based on the direction
        if self.vertical:
            self.current_pos[1] += self.speed * self.direction
            if self.current_pos[1] >= self.end_pos[1] or self.current_pos[1] <= self.start_pos[1]:
                self.direction *= -1
        else:
            self.current_pos[0] += self.speed * self.direction
            if self.current_pos[0] >= self.end_pos[0] or self.current_pos[0] <= self.start_pos[0]:
                self.direction *= -1

    def draw(self, surface):
        barrier_rect = pygame.Rect(self.current_pos[0], self.current_pos[1], 20, 100)  # Example size
        pygame.draw.rect(surface, (255, 0, 0), barrier_rect)  # Red color for the barrier

    @property
    def rect(self):
        return pygame.Rect(self.current_pos[0], self.current_pos[1], 20, 100)  # Example size

class Level:
    def __init__(self, hole_pos, obstacles, moving_obstacles, par, start_pos=(50, 50)):
        self.hole_pos = hole_pos
        self.obstacles = obstacles
        self.moving_obstacles = moving_obstacles
        self.par = par
        self.strokes = 0
        self.start_pos = start_pos

# Level designs
levels = [
    #lvl 1
    Level(
        hole_pos=[700, 450],
        obstacles=[
            pygame.Rect(0, 100, 600, 25),
            pygame.Rect(200, 300, 600, 25),
            pygame.Rect(600, 400, 25, 100)
        ],
        moving_obstacles=[],  # No moving obstacles in this level
        par=3,
        start_pos=(50, 50)
    ),
    #lvl 2
    Level(
        hole_pos=[650, 300],
        obstacles=[
            pygame.Rect(200, 100, 400, 25),
            pygame.Rect(200, 500, 400, 25),
        ],
        moving_obstacles=[
            MovingBarrier(start_pos=[400, 125], end_pos=[400, 400], speed=2, vertical=True),  # Vertical moving barrier
        ],
        par=4,
        start_pos=(100, 300)
    ),
    #lvl 3
    Level(
        hole_pos=[500, 300],
        obstacles=[ #Geen obstakels
        ],
        moving_obstacles=[
            MovingBarrier(start_pos=[300, 200], end_pos=[400, 200], speed=2, vertical=False),   # Horizontal moving barrier
            MovingBarrier(start_pos=[300, 300], end_pos=[400, 300], speed=2, vertical=False),   # Horizontal moving barrier
            MovingBarrier(start_pos=[600, 200], end_pos=[700, 200], speed=2, vertical=False),   # Horizontal moving barrier
            MovingBarrier(start_pos=[600, 300], end_pos=[700, 300], speed=2, vertical=False)   # Horizontal moving barrier
        ],
        par=5,
        start_pos=(100, 300)
    ),
    #lvl 4
    Level(
        hole_pos=[500, 325],
        obstacles=[
            pygame.Rect(0, 100, 700, 25),
            pygame.Rect(675, 100, 25, 400),
            pygame.Rect(100, 500, 600, 25),
            pygame.Rect(100, 225, 25, 300),
            pygame.Rect(100, 225, 475, 25),
            pygame.Rect(575, 225, 25, 175),
            pygame.Rect(200, 400, 400, 25)
        ],
        moving_obstacles=[],  # No moving obstacles in this level
        par=6,
        start_pos=(50, 50)
    ),
    #lvl5
    Level(
        hole_pos=[400, 300],
        obstacles=[
            pygame.Rect(100, 100, 600, 20),
            pygame.Rect(100, 480, 600, 20),
            pygame.Rect(100, 100, 20, 400),
            pygame.Rect(680, 100, 20, 400),
            pygame.Rect(300, 200, 200, 200)
        ],
        moving_obstacles=[],  # No moving obstacles in this level
        par=7,
        start_pos=(50, 50)
    ),
    # lvl6
    Level(
        hole_pos=[200, 300],
        obstacles=[
            pygame.Rect(100, 100, 600, 25),
            pygame.Rect(100, 500, 600, 25),
            pygame.Rect(100, 100, 25, 400)
        ],
        moving_obstacles=[
            MovingBarrier(start_pos=[300, 125], end_pos=[300, 400], speed=4, vertical=True),  # Vertical moving barrier
            MovingBarrier(start_pos=[400, 125], end_pos=[400, 400], speed=6, vertical=True),  # Vertical moving barrier
            MovingBarrier(start_pos=[500, 125], end_pos=[500, 400], speed=8, vertical=True),  # Vertical moving barrier
            MovingBarrier(start_pos=[600, 125], end_pos=[600, 400], speed=10, vertical=True)  # Vertical moving barrier
        ],
        par=8,
        start_pos=(50, 50)
    )
]

# Game variabelen
current_level = 0
game_state = MENU
total_strokes = 0
ball_radius = 15
ball_speed = [0, 0]
hole_radius = 25
ball_pos = [50, 50]  # Initial position

# Schuifbalk properties
slider_width = 25
slider_height = 250
slider_x = 840
slider_y = 150
slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
slider_knob_radius = 15
slider_knob_y = slider_y + slider_height  # Blijft hetzelfde, maar nu is dit minimale kracht
force = 0

# Kracht instellingen
min_force = 0
max_force = 25
force = 0

# Invoerveld properties
input_box = pygame.Rect(820, 80, 70, 32)
input_text = ""
active = False

# UI elementen
start_button = Button(350, 250, 200, 50, "Start Game", "start")
next_button = Button(350, 350, 200, 50, "Next Level", "next")
exit_button = Button(350, 450, 200, 50, "Exit", "exit")
menu_button = Button(350, 450, 200, 50, "Main Menu", "menu")

show_arrow = False
arrow_end = (0, 0)

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def draw_grid():
    # Dikkere lijnen om de 100 pixels
    for x in range(0, 800, 100):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, 600), 2)
        if x != 0:
            text = font_small.render(str(x), True, TEXT_COLOR)
            screen.blit(text, (x - 15, 5))

    for y in range(0, 600, 100):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (800, y), 2)
        if y != 0:
            text = font_small.render(str(y), True, TEXT_COLOR)
            screen.blit(text, (5, y - 10))

    # Dunne lijnen om de 25 pixels
    for x in range(0, 800, 25):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, 600), 1)

    for y in range(0, 600, 25):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (800, y), 1)

def draw_arrow(start_pos, end_pos):
    pygame.draw.line(screen, BLUE, start_pos, end_pos, 2)
    angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
    arrow_length = 15
    pygame.draw.line(screen, BLUE, end_pos,
                     (end_pos[0] - arrow_length * math.cos(angle - math.pi / 6),
                      end_pos[1] - arrow_length * math.sin(angle - math.pi / 6)), 2)
    pygame.draw.line(screen, BLUE, end_pos,
                     (end_pos[0] - arrow_length * math.cos(angle + math.pi / 6),
                      end_pos[1] - arrow_length * math.sin(angle + math.pi / 6)), 2)

def check_collision(ball_pos, ball_radius, obstacles):
    for obstacle in obstacles:
        closest_x = max(obstacle.left, min(ball_pos[0], obstacle.right))
        closest_y = max(obstacle.top, min(ball_pos[1], obstacle.bottom))

        if distance(ball_pos, (closest_x, closest_y)) < ball_radius:
            return obstacle
    return None

def reset_level():
    global ball_speed, show_arrow, force, slider_knob_y
    ball_speed = [0, 0]
    show_arrow = False
    force = 0
    slider_knob_y = slider_y + slider_height

def load_level(level_num):
    global current_level, ball_pos
    current_level = level_num
    ball_pos = list(levels[current_level].start_pos)
    reset_level()

def draw_menu():
    screen.fill(GREEN)
    title = font_large.render("Mini Golf Challenge", True, BLACK)
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))

    start_button.draw(screen)
    exit_button.draw(screen)

def draw_game():
    screen.fill(GREEN)

    # Teken het raster
    draw_grid()

    # Teken obstakels
    for obstacle in levels[current_level].obstacles:
        pygame.draw.rect(screen, (139, 69, 19), obstacle)

    # Teken bewegende obstakels
    for moving_obstacle in levels[current_level].moving_obstacles:
        moving_obstacle.update()  # Update the position of the moving barrier
        moving_obstacle.draw(screen)  # Draw the moving barrier

    # Teken de hole
    pygame.draw.circle(screen, BLACK, levels[current_level].hole_pos, hole_radius)
    pygame.draw.circle(screen, (50, 50, 50), levels[current_level].hole_pos, hole_radius - 5)

    # Teken de bal
    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
    pygame.draw.circle(screen, (255, 100, 100),
                       (int(ball_pos[0] - ball_radius / 3), int(ball_pos[1] - ball_radius / 3)),
                       ball_radius / 3)

    # Teken richtingspijl
    if show_arrow and sum(abs(s) for s in ball_speed) < 0.1:
        draw_arrow(levels[current_level].start_pos, arrow_end)

    # Teken de schuifbalk
    pygame.draw.rect(screen, SLIDER_BG_COLOR, slider_rect)
    pygame.draw.circle(screen, SLIDER_KNOB_COLOR,
                       (slider_x + slider_width // 2, slider_knob_y), slider_knob_radius)

    # Toon krachtniveau
    force_text = font_small.render(f"Power: {force:.1f}", True, TEXT_COLOR)
    screen.blit(force_text, (slider_x - 10, slider_y - 30))

    # Toon strokes
    strokes_text = font_medium.render(f"Strokes: {levels[current_level].strokes}", True, BLACK)
    screen.blit(strokes_text, (20, 20))

    # Toon level info
    level_text = font_medium.render(f"Level: {current_level + 1}/5", True, BLACK)
    screen.blit(level_text, (20, 60))

    # Toon par
    par_text = font_medium.render(f"Par: {levels[current_level].par}", True, BLACK)
    screen.blit(par_text, (20, 100))

    # Toon coordinaten input
    coord_text = font_small.render("Enter target (x,y):", True, BLACK)
    screen.blit(coord_text, (820, 60))

    # Invoerveld
    pygame.draw.rect(screen, INPUT_BG_COLOR, input_box)
    pygame.draw.rect(screen, BLACK, input_box, 2)
    text_surface = font_input.render(input_text, True, TEXT_COLOR)
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

def draw_level_complete():
    screen.fill(GREEN)

    level = levels[current_level]
    title = font_large.render(f"Level {current_level + 1} Complete!", True, BLACK)
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))

    strokes_text = font_medium.render(f"Your strokes: {level.strokes}", True, BLACK)
    screen.blit(strokes_text, (screen.get_width() // 2 - strokes_text.get_width() // 2, 200))

    par_text = font_medium.render(f"Par: {level.par}", True, BLACK)
    screen.blit(par_text, (screen.get_width() // 2 - par_text.get_width() // 2, 250))

    # Toon of je onder of boven par bent
    if level.strokes < level.par:
        result_text = font_medium.render(f"{level.par - level.strokes} under par!", True, BLUE)
    elif level.strokes > level.par:
        result_text = font_medium.render(f"{level.strokes - level.par} over par", True, RED)
    else:
        result_text = font_medium.render("Par!", True, GREEN)
    screen.blit(result_text, (screen.get_width() // 2 - result_text.get_width() // 2, 300))

    if current_level < len(levels) - 1:
        next_button.draw(screen)
    else:
        complete_text = font_large.render("Game Completed!", True, BLACK)
        screen.blit(complete_text, (screen.get_width() // 2 - complete_text.get_width() // 2, 350))

        total_text = font_medium.render(f"Total strokes: {total_strokes}", True, BLACK)
        screen.blit(total_text, (screen.get_width() // 2 - total_text.get_width() // 2, 400))

    menu_button.draw(screen)

# Main game loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    # UI interacties
    if game_state == MENU:
        start_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)
    elif game_state == LEVEL_COMPLETE:
        if current_level < len(levels) - 1:
            next_button.check_hover(mouse_pos)
        menu_button.check_hover(mouse_pos)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # Button handling
        if game_state == MENU:
            action = start_button.handle_event(event) or exit_button.handle_event(event)
            if action == "start":
                game_state = PLAYING
                load_level(0)
            elif action == "exit":
                running = False

        elif game_state == LEVEL_COMPLETE:
            action = None
            if current_level < len(levels) - 1:
                action = next_button.handle_event(event) or menu_button.handle_event(event)
            else:
                action = menu_button.handle_event(event)

            if action == "next":
                game_state = PLAYING
                load_level(current_level + 1)
            elif action == "menu":
                game_state = MENU

        # Gameplay handling
        elif game_state == PLAYING:
            if event.type == MOUSEBUTTONDOWN:
                # Check if clicking on ball (when stationary)
                if sum(abs(s) for s in ball_speed) < 0.1:
                    if distance(ball_pos, event.pos) <= ball_radius:
                        show_arrow = True
                        arrow_end = event.pos

                if slider_rect.collidepoint(event.pos):
                    slider_knob_y = event.pos[1]
                    slider_knob_y = max(slider_y, min(slider_knob_y, slider_y + slider_height))
                    force = ((slider_y + slider_height - slider_knob_y) / slider_height) * max_force

                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False

            elif event.type == MOUSEMOTION:
                if show_arrow:
                    arrow_end = event.pos

                if event.buttons[0] and slider_rect.collidepoint(event.pos):
                    slider_knob_y = event.pos[1]
                    slider_knob_y = max(slider_y, min(slider_knob_y, slider_y + slider_height))
                    force = ((slider_y + slider_height - slider_knob_y) / slider_height) * max_force

            elif event.type == MOUSEBUTTONUP:
                if show_arrow:
                    vector = [ball_pos[0] - arrow_end[0], ball_pos[1] - arrow_end[1]]
                    length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
                    if length > 0:
                        ball_speed = [vector[0] / length * force, vector[1] / length * force]
                        levels[current_level].strokes += 1
                    show_arrow = False

            elif event.type == KEYDOWN:
                if active:
                    if event.key == K_RETURN:
                        try:
                            coords = input_text.replace("(", "").replace(")", "").split(",")
                            x, y = map(int, coords)

                            if 0 <= x <= 800 and 0 <= y <= 600:
                                vector = [x - ball_pos[0], y - ball_pos[1]]
                                length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
                                if length > 0:
                                    ball_speed = [vector[0] / length * force, vector[1] / length * force]
                                    levels[current_level].strokes += 1
                                input_text = ""
                        except (ValueError, IndexError):
                            input_text = ""

                    elif event.key == K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

    # Update game state
    if game_state == PLAYING:
        # Update moving obstacles
        for moving_obstacle in levels[current_level].moving_obstacles:
            moving_obstacle.update()

        # Update bal positie
        ball_pos[0] += ball_speed[0]
        ball_pos[1] += ball_speed[1]

        # Collision detection met de randen
        if ball_pos[0] - ball_radius < 0:
            ball_pos[0] = ball_radius
            ball_speed[0] = -ball_speed[0] * 0.8
        elif ball_pos[0] + ball_radius > 800:
            ball_pos[0] = 800 - ball_radius
            ball_speed[0] = -ball_speed[0] * 0.8

        if ball_pos[1] - ball_radius < 0:
            ball_pos[1] = ball_radius
            ball_speed[1] = -ball_speed[1] * 0.8
        elif ball_pos[1] + ball_radius > 600:
            ball_pos[1] = 600 - ball_radius
            ball_speed[1] = -ball_speed[1] * 0.8

        # Collision detection met obstakels
        collided_obstacle = check_collision(ball_pos, ball_radius, levels[current_level].obstacles)
        if collided_obstacle:
            # Determine which side was hit
            if ball_pos[0] <= collided_obstacle.left or ball_pos[0] >= collided_obstacle.right:
                ball_speed[0] = -ball_speed[0] * 0.8  # Reverse X direction with damping
            if ball_pos[1] <= collided_obstacle.top or ball_pos[1] >= collided_obstacle.bottom:
                ball_speed[1] = -ball_speed[1] * 0.8  # Reverse Y direction with damping

            # Move ball slightly out of collision to avoid sticking
            while check_collision(ball_pos, ball_radius, levels[current_level].obstacles):
                ball_pos[0] += ball_speed[0] * 0.1
                ball_pos[1] += ball_speed[1] * 0.1

        # Collision detection with moving obstacles
        for moving_obstacle in levels[current_level].moving_obstacles:
            if moving_obstacle.rect.colliderect(pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)):
                # Determine which side was hit
                if ball_pos[0] <= moving_obstacle.rect.left or ball_pos[0] >= moving_obstacle.rect.right:
                    ball_speed[0] = -ball_speed[0] * 0.8  # Reverse X direction with damping
                if ball_pos[1] <= moving_obstacle.rect.top or ball_pos[1] >= moving_obstacle.rect.bottom:
                    ball_speed[1] = -ball_speed[1] * 0.8  # Reverse Y direction with damping

                # Move ball slightly out of collision to avoid sticking
                while check_collision(ball_pos, ball_radius, levels[current_level].obstacles) or moving_obstacle.rect.colliderect(pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)):
                    ball_pos[0] += ball_speed[0] * 0.1
                    ball_pos[1] += ball_speed[1] * 0.1

        # Snelheid verminderen
        ball_speed[0] *= 0.98
        ball_speed[1] *= 0.98

        # Controleer of de bal in de hole is
        if distance(ball_pos, levels[current_level].hole_pos) < hole_radius - ball_radius:
            total_strokes += levels[current_level].strokes
            game_state = LEVEL_COMPLETE

    # Drawing
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_game()
    elif game_state == LEVEL_COMPLETE:
        draw_level_complete()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
