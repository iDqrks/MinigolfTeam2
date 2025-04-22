import pygame
import sys
import math
from pygame.locals import *

# Initialiseren van Pygame
pygame.init()

# Scherm instellingen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BrainPutt")

# Kleuren
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (34, 139, 34)
BLUE = (70, 130, 180)
DARK_GREEN = (30, 100, 30)
GRAY = (150, 150, 150)
HOVER_COLOR = (100, 200, 100)
SHADOW_COLOR = (100, 100, 100, 100)
YELLOW = (255, 255, 0)
LIGHT_GREEN = (80, 180, 80)
GRID_COLOR = (220, 220, 220)
SLIDER_BG_COLOR = (200, 200, 200)
SLIDER_KNOB_COLOR = (70, 130, 180)
TEXT_COLOR = (50, 50, 50)
INPUT_BG_COLOR = (240, 240, 240)
BUTTON_COLOR = (100, 150, 200)
BUTTON_HOVER_COLOR = (120, 170, 220)
LOCKED_COLOR = (100, 100, 100)

# Fonts
title_font = pygame.font.Font(None, 120)
button_font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 45)
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)
font_input = pygame.font.Font(None, 28)

# Game states
MENU = 0
PLAYING = 1
LEVEL_COMPLETE = 2
GAME_COMPLETE = 3

# Arrow
ARROW_COLOR = (0, 0, 0)
ARROW_WIDTH = 4
ARROW_SCALE = 5
ARROW_HEAD_LEN = 12

# Homescreen Button klasse
class HomeButton:
    def __init__(self, text, x, y, width, height, font, locked=False):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GREEN if not locked else LOCKED_COLOR
        self.hover_color = HOVER_COLOR if not locked else LOCKED_COLOR
        self.font = font
        self.locked = locked

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if not self.locked and self.rect.collidepoint(mouse_pos):
            current_color = self.hover_color
        else:
            current_color = self.color

        shadow_rect = self.rect.move(5, 5)
        pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=20)
        pygame.draw.rect(screen, current_color, self.rect, border_radius=20)
        pygame.draw.rect(screen, DARK_GREEN, self.rect, 5, border_radius=20)

        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.locked:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# SkinOption klasse
class SkinOption:
    def __init__(self, x, y, color, type):
        self.rect = pygame.Rect(x, y, 100, 100)
        self.color = color
        self.type = type
        self.selected = False

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        for i in range(0, 100, 10):
            pygame.draw.line(screen, LIGHT_GREEN, (self.rect.x + i, self.rect.y),
                             (self.rect.x + i, self.rect.y + 100), 1)

        center_x, center_y = self.rect.center
        if self.type == "ball":
            pygame.draw.circle(screen, self.color, (center_x, center_y), 40)
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 40, 2)
        elif self.type == "club":
            pygame.draw.rect(screen, self.color, (center_x - 5, center_y - 40, 10, 60))
            pygame.draw.rect(screen, self.color, (center_x - 20, center_y + 20, 40, 10))
            pygame.draw.rect(screen, BLACK, (center_x - 5, center_y - 40, 10, 60), 2)
            pygame.draw.rect(screen, BLACK, (center_x - 20, center_y + 20, 40, 10), 2)
        elif self.type == "flag":
            pygame.draw.rect(screen, GRAY, (center_x - 5, center_y - 40, 10, 80))
            pygame.draw.polygon(screen, self.color, [(center_x, center_y - 40),
                                                     (center_x + 40, center_y - 20),
                                                     (center_x, center_y)])
            pygame.draw.rect(screen, BLACK, (center_x - 5, center_y - 40, 10, 80), 2)
            pygame.draw.polygon(screen, BLACK, [(center_x, center_y - 40),
                                                (center_x + 40, center_y - 20),
                                                (center_x, center_y)], 2)

        pygame.draw.rect(screen, RED if self.selected else DARK_GREEN, self.rect, 5 if self.selected else 2)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# Game Button klasse
class GameButton:
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

# MovingBarrier klasse
class MovingBarrier:
    def __init__(self, start_pos, end_pos, speed, vertical=False):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.speed = speed
        self.current_pos = list(start_pos)
        self.direction = 1
        self.vertical = vertical

    def update(self):
        if self.vertical:
            self.current_pos[1] += self.speed * self.direction
            if self.current_pos[1] >= self.end_pos[1] or self.current_pos[1] <= self.start_pos[1]:
                self.direction *= -1
        else:
            self.current_pos[0] += self.speed * self.direction
            if self.current_pos[0] >= self.end_pos[0] or self.current_pos[0] <= self.start_pos[0]:
                self.direction *= -1

    def draw(self, surface):
        barrier_rect = pygame.Rect(self.current_pos[0], self.current_pos[1], 20, 100)
        pygame.draw.rect(surface, RED, barrier_rect)

    @property
    def rect(self):
        return pygame.Rect(self.current_pos[0], self.current_pos[1], 20, 100)

# Level klasse
class Level:
    def __init__(self, hole_pos, obstacles, moving_obstacles, par, start_pos=(50, 50)):
        self.hole_pos = hole_pos
        self.obstacles = obstacles
        self.moving_obstacles = moving_obstacles
        self.par = par
        self.strokes = 0
        self.start_pos = start_pos

# Level designs (9 levels)
levels = [
    Level(hole_pos=[800, 600], 
          obstacles=[pygame.Rect(300, 300, 200, 25)], 
          moving_obstacles=[], 
          par=2, 
          start_pos=(50, 50)),
    Level(hole_pos=[700, 500], 
          obstacles=[pygame.Rect(0, 350, 400, 25), pygame.Rect(500, 350, 400, 25)], 
          moving_obstacles=[MovingBarrier(start_pos=[450, 400], end_pos=[450, 450], speed=2, vertical=True)], 
          par=3, 
          start_pos=(50, 50)),
    Level(hole_pos=[600, 400], 
          obstacles=[pygame.Rect(0, 250, 400, 25), pygame.Rect(500, 250, 400, 25)], 
          moving_obstacles=[MovingBarrier(start_pos=[450, 300], end_pos=[450, 350], speed=2, vertical=True)], 
          par=4, 
          start_pos=(50, 50)),
    Level(hole_pos=[750, 550], 
          obstacles=[pygame.Rect(0, 300, 300, 25), pygame.Rect(400, 300, 350, 25)], 
          moving_obstacles=[MovingBarrier(start_pos=[350, 350], end_pos=[350, 450], speed=3, vertical=True)], 
          par=4, 
          start_pos=(50, 50)),
    Level(hole_pos=[650, 450], 
          obstacles=[pygame.Rect(0, 200, 350, 25), pygame.Rect(450, 200, 450, 25), pygame.Rect(350, 200, 25, 200)], 
          moving_obstacles=[MovingBarrier(start_pos=[400, 250], end_pos=[400, 300], speed=2, vertical=True),
                           MovingBarrier(start_pos=[500, 350], end_pos=[500, 400], speed=2, vertical=True)], 
          par=5, 
          start_pos=(50, 50)),
    Level(hole_pos=[700, 600], 
          obstacles=[pygame.Rect(0, 450, 550, 25), pygame.Rect(650, 450, 250, 25)], 
          moving_obstacles=[MovingBarrier(start_pos=[600, 350], end_pos=[600, 400], speed=2, vertical=True),
                           MovingBarrier(start_pos=[575, 500], end_pos=[575, 550], speed=2, vertical=True)], 
          par=6, 
          start_pos=(50, 50)),
    Level(hole_pos=[800, 500], 
          obstacles=[pygame.Rect(0, 250, 300, 25), pygame.Rect(400, 250, 500, 25), pygame.Rect(0, 400, 600, 25), pygame.Rect(700, 400, 200, 25)], 
          moving_obstacles=[MovingBarrier(start_pos=[350, 300], end_pos=[350, 350], speed=2, vertical=True),
                           MovingBarrier(start_pos=[650, 350], end_pos=[650, 400], speed=2, vertical=True),
                           MovingBarrier(start_pos=[500, 450], end_pos=[500, 500], speed=3, vertical=True)], 
          par=7, 
          start_pos=(50, 50)),
    Level(hole_pos=[750, 650], 
          obstacles=[pygame.Rect(0, 300, 400, 25), pygame.Rect(500, 300, 400, 25), pygame.Rect(400, 0, 25, 250), pygame.Rect(0, 500, 600, 25), pygame.Rect(700, 500, 200, 25)], 
          moving_obstacles=[MovingBarrier(start_pos=[450, 350], end_pos=[450, 400], speed=3, vertical=True),
                           MovingBarrier(start_pos=[650, 400], end_pos=[650, 450], speed=2, vertical=True),
                           MovingBarrier(start_pos=[550, 550], end_pos=[550, 600], speed=2, vertical=True)], 
          par=8, 
          start_pos=(50, 50)),
    Level(hole_pos=[100, 700], 
          obstacles=[pygame.Rect(0, 200, 350, 25), pygame.Rect(450, 200, 450, 25), pygame.Rect(0, 400, 550, 25), pygame.Rect(650, 400, 250, 25), pygame.Rect(0, 600, 700, 25)], 
          moving_obstacles=[MovingBarrier(start_pos=[400, 250], end_pos=[400, 300], speed=2, vertical=True),
                           MovingBarrier(start_pos=[600, 350], end_pos=[600, 400], speed=2, vertical=True),
                           MovingBarrier(start_pos=[725, 450], end_pos=[725, 500], speed=2, vertical=True),
                           MovingBarrier(start_pos=[775, 600], end_pos=[775, 650], speed=2, vertical=True)], 
          par=9, 
          start_pos=(50, 50))
]

# Homescreen knoppen
start_button = HomeButton("Start Game", (SCREEN_WIDTH - 250) // 2, 350, 250, 120, button_font)
levels_button = HomeButton("Levels", 50, 650, 200, 60, small_font)
achievements_button = HomeButton("Achievements", 750, 650, 250, 60, small_font)
customize_button = HomeButton("Customize", (SCREEN_WIDTH - 250) // 2, 500, 250, 75, button_font)
score_button = HomeButton("Scorebord", (SCREEN_WIDTH - 250) // 2, 600, 250, 75, button_font)
buttons = [start_button, levels_button, achievements_button, customize_button, score_button]

# Customize scherm knoppen
customize_options = [
    HomeButton("Bal Skins", (SCREEN_WIDTH - 250) // 2, 250, 250, 75, button_font),
    HomeButton("Club Skins", (SCREEN_WIDTH - 250) // 2, 350, 250, 75, button_font),
    HomeButton("Vlag Skins", (SCREEN_WIDTH - 250) // 2, 450, 250, 75, button_font),
    HomeButton("Terug", (SCREEN_WIDTH - 250) // 2, 550, 250, 75, button_font)
]

# Voorbeeld skins
ball_skins = [
    SkinOption(300, 250, WHITE, "ball"),
    SkinOption(450, 250, RED, "ball"),
    SkinOption(600, 250, YELLOW, "ball")
]
club_skins = [
    SkinOption(300, 250, GRAY, "club"),
    SkinOption(450, 250, GREEN, "club"),
    SkinOption(600, 250, BLUE, "club")
]
flag_skins = [
    SkinOption(300, 250, RED, "flag"),
    SkinOption(450, 250, WHITE, "flag"),
    SkinOption(600, 250, BLUE, "flag")
]

# Level knoppen (3x3 raster) met lock-status
unlocked_levels = [True] + [False] * 8  # Alleen Level 1 is unlocked bij start
level_buttons = []
for i in range(9):
    row = i // 3
    col = i % 3
    x = 250 + col * 200
    y = 200 + row * 150
    level_buttons.append(HomeButton(f"Level {i+1}", x, y, 150, 100, button_font, locked=not unlocked_levels[i]))

level_back_button = HomeButton("Terug", (SCREEN_WIDTH - 250) // 2, 650, 250, 75, button_font)

# Homescreen
def homescreen():
    clock = pygame.time.Clock()
    running = True
    golfball_pos = [100, 100]
    ball_angle = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for button in buttons:
                if button.is_clicked(event):
                    print(f"{button.text} clicked!")
                    if button.text == "Start Game":
                        game_screen(0)
                    elif button.text == "Levels":
                        level_screen()
                    elif button.text == "Achievements":
                        print("Showing achievements...")
                    elif button.text == "Customize":
                        customize_screen()
                    elif button.text == "Scorebord":
                        print("Showing scoreboard...")

        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        pygame.draw.rect(screen, LIGHT_GREEN, (0, SCREEN_HEIGHT // 2 + 50, SCREEN_WIDTH, 150))
        pygame.draw.ellipse(screen, DARK_GREEN, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 200, 200, 70))

        title_shadow = title_font.render("BrainPutt", True, SHADOW_COLOR)
        title = title_font.render("BrainPutt", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_shadow, title_rect.move(5, 5))
        pygame.draw.rect(screen, DARK_GREEN, (title_rect.x - 40, title_rect.y - 25,
                                              title_rect.width + 80, title_rect.height + 50), border_radius=20)
        screen.blit(title, title_rect)

        ball_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(ball_surface, WHITE, (25, 25), 25)
        pygame.draw.circle(ball_surface, GRAY, (25, 25), 25, 2)
        rotated_ball = pygame.transform.rotate(ball_surface, ball_angle)
        ball_rect = rotated_ball.get_rect(center=golfball_pos)
        screen.blit(rotated_ball, ball_rect)
        ball_angle += 1

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Customize scherm
def customize_screen():
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for button in customize_options:
                if button.is_clicked(event):
                    print(f"{button.text} clicked!")
                    if button.text == "Terug":
                        return
                    elif button.text == "Bal Skins":
                        skin_selection_screen(ball_skins, "Ball Skins")
                    elif button.text == "Club Skins":
                        skin_selection_screen(club_skins, "Club Skins")
                    elif button.text == "Vlag Skins":
                        skin_selection_screen(flag_skins, "Flag Skins")

        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        customize_title = title_font.render("Customize", True, WHITE)
        title_rect = customize_title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(customize_title, title_rect)

        for button in customize_options:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

# Skin selectie scherm
def skin_selection_screen(skins, skin_type):
    clock = pygame.time.Clock()
    running = True
    back_button = HomeButton("Terug", (SCREEN_WIDTH - 250) // 2, 600, 250, 75, button_font)
    selected_skin = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if back_button.is_clicked(event):
                return
            for skin in skins:
                if skin.is_clicked(event):
                    for s in skins:
                        s.selected = False
                    skin.selected = True
                    selected_skin = skin
                    print(f"Selected {skin_type} with color {skin.color}")

        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        title = title_font.render(f"Choose {skin_type}", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)

        for skin in skins:
            skin.draw(screen)

        back_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

# Levelscherm
def level_screen():
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if level_back_button.is_clicked(event):
                return
            for button in level_buttons:
                if button.is_clicked(event):
                    level_num = int(button.text.split()[1]) - 1
                    print(f"Starting Level {level_num + 1}...")
                    game_screen(level_num)

        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        title = title_font.render("Select Level", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)

        for button in level_buttons:
            button.draw(screen)

        level_back_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

# Game scherm
def game_screen(level_num):
    global unlocked_levels
    clock = pygame.time.Clock()
    running = True
    back_button = GameButton((SCREEN_WIDTH - 250) // 2, 650, 250, 75, "Terug", "back")
    hit_button = GameButton(910, 550, 80, 40, "Slaag!", "hit")  # Grotere, duidelijke knop

    if level_num >= len(levels) or not unlocked_levels[level_num]:
        print(f"Level {level_num + 1} is locked or not implemented yet.")
        return
    current_level = level_num
    ball_radius = 15
    ball_speed = [0, 0]
    hole_radius = 25
    ball_pos = list(levels[current_level].start_pos)
    total_strokes = 0
    game_state = PLAYING

    # Breedere zijbalk instellingen
    sidebar_width = 150
    slider_width = 30
    slider_height = 300
    slider_x = SCREEN_WIDTH - sidebar_width + 60
    slider_y = 150
    slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
    slider_knob_radius = 15
    slider_knob_y = slider_y + slider_height
    force = 0
    min_force = 0
    max_force = 25

    # Breeder en mooier invoerveld
    input_box = pygame.Rect(SCREEN_WIDTH - sidebar_width + 10, 80, 130, 40)
    input_text = ""
    active = False

    next_button = GameButton(SCREEN_WIDTH // 2 - 100, 450, 200, 60, "Next Level", "next")
    menu_button = GameButton(SCREEN_WIDTH // 2 - 100, 550, 200, 60, "Main Menu", "menu")

    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def draw_grid():
        for x in range(0, SCREEN_WIDTH - sidebar_width, 100):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT), 2)
            if x != 0:
                text = font_small.render(str(x), True, TEXT_COLOR)
                screen.blit(text, (x - 15, 5))
        for y in range(0, SCREEN_HEIGHT, 100):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH - sidebar_width, y), 2)
            if y != 0:
                text = font_small.render(str(y), True, TEXT_COLOR)
                screen.blit(text, (5, y - 10))
        for x in range(0, SCREEN_WIDTH - sidebar_width, 25):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 25):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH - sidebar_width, y), 1)

    def check_collision(ball_pos, ball_radius, obstacles):
        for obstacle in obstacles:
            closest_x = max(obstacle.left, min(ball_pos[0], obstacle.right))
            closest_y = max(obstacle.top, min(ball_pos[1], obstacle.bottom))
            if distance(ball_pos, (closest_x, closest_y)) < ball_radius:
                return obstacle
        return None

    def reset_level():
        nonlocal ball_speed, force, slider_knob_y
        ball_speed = [0, 0]
        force = 0
        slider_knob_y = slider_y + slider_height

    def load_level(level_num):
        nonlocal current_level, ball_pos
        current_level = level_num
        ball_pos = list(levels[current_level].start_pos)
        reset_level()

    def hit_ball():
        try:
            coords = input_text.replace("(", "").replace(")", "").split(",")
            x, y = map(int, coords)
            if 0 <= x <= SCREEN_WIDTH - sidebar_width and 0 <= y <= SCREEN_HEIGHT:
                vector = [x - ball_pos[0], y - ball_pos[1]]
                length = math.sqrt(vector[0]**2 + vector[1]**2)
                if length > 0:
                    ball_speed[0] = vector[0] / length * force
                    ball_speed[1] = vector[1] / length * force
                    levels[current_level].strokes += 1
                    return True
        except:
            pass
        return False

    def draw_game():
        screen.fill(GREEN)
        pygame.draw.rect(screen, INPUT_BG_COLOR, (SCREEN_WIDTH - sidebar_width, 0, sidebar_width, SCREEN_HEIGHT))  # Sidebar achtergrond
        draw_grid()
        for obstacle in levels[current_level].obstacles:
            pygame.draw.rect(screen, (139, 69, 19), obstacle)
        for moving_obstacle in levels[current_level].moving_obstacles:
            moving_obstacle.update()
            moving_obstacle.draw(screen)
        pygame.draw.circle(screen, BLACK, levels[current_level].hole_pos, hole_radius)
        pygame.draw.circle(screen, (50, 50, 50), levels[current_level].hole_pos, hole_radius - 5)

        if force > 0 and input_text:
            try:
                # conversion input to coords list
                coords = input_text.replace("(", "").replace(")", "").split(",") #Replacing input "()" by empty space so they don't get added to the list

                input_x = int(coords[0])
                input_y = int(coords[1])

                max_screen_width = SCREEN_WIDTH - sidebar_width

                # check if input coordinates are inside playing field
                if 0 <= input_x <= max_screen_width and 0 <= input_y <= SCREEN_HEIGHT:

                    # distance from ball to target
                    horizontal_distance = input_x - ball_pos[0]
                    vertical_distance = input_y - ball_pos[1]
                    distance_ball_to_target = math.hypot(horizontal_distance, vertical_distance)

                    if distance_ball_to_target > 0:
                        # arrow direction toward target
                        direction_x = horizontal_distance / distance_ball_to_target
                        direction_y = vertical_distance / distance_ball_to_target

                        # where arrow tip ends
                        arrow_length = force * ARROW_SCALE
                        arrow_tip_x = ball_pos[0] + direction_x * arrow_length
                        arrow_tip_y = ball_pos[1] + direction_y * arrow_length

                        # drawing arrow shaft
                        pygame.draw.line(
                            screen,
                            ARROW_COLOR,
                            (int(ball_pos[0]), int(ball_pos[1])),
                            (int(arrow_tip_x), int(arrow_tip_y)),
                            ARROW_WIDTH
                        )

                        # drawing arrow head
                        arrow_angle = math.atan2(direction_y, direction_x)
                        arrow_angle_left = arrow_angle + math.radians(150)
                        arrow_angle_right = arrow_angle - math.radians(150)

                        arrow_head_point1 = (
                            arrow_tip_x + math.cos(arrow_angle_left) * ARROW_HEAD_LEN,
                            arrow_tip_y + math.sin(arrow_angle_left) * ARROW_HEAD_LEN
                        )
                        arrow_head_point2 = (
                            arrow_tip_x + math.cos(arrow_angle_right) * ARROW_HEAD_LEN,
                            arrow_tip_y + math.sin(arrow_angle_right) * ARROW_HEAD_LEN
                        )

                        pygame.draw.polygon(
                            screen,
                            ARROW_COLOR,
                            [
                                (arrow_tip_x, arrow_tip_y),
                                arrow_head_point1,
                                arrow_head_point2
                            ]
                        )
            except (ValueError, IndexError):
                pass

        pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
        pygame.draw.circle(screen, (255, 100, 100),
                           (int(ball_pos[0] - ball_radius / 3), int(ball_pos[1] - ball_radius / 3)),
                           ball_radius / 3)
        pygame.draw.rect(screen, SLIDER_BG_COLOR, slider_rect)
        pygame.draw.circle(screen, SLIDER_KNOB_COLOR,
                           (slider_x + slider_width // 2, slider_knob_y), slider_knob_radius)
        force_text = font_small.render(f"Power: {force:.1f}", True, TEXT_COLOR)
        screen.blit(force_text, (slider_x - 10, slider_y - 30))
        strokes_text = font_medium.render(f"Strokes: {levels[current_level].strokes}", True, BLACK)
        screen.blit(strokes_text, (20, 20))
        level_text = font_medium.render(f"Level: {current_level + 1}/{len(levels)}", True, BLACK)
        screen.blit(level_text, (20, 60))
        par_text = font_medium.render(f"Par: {levels[current_level].par}", True, BLACK)
        screen.blit(par_text, (20, 100))
        coord_text = font_small.render("Target (x,y):", True, BLACK)
        screen.blit(coord_text, (SCREEN_WIDTH - sidebar_width + 10, 50))
        pygame.draw.rect(screen, WHITE, input_box, border_radius=5)
        pygame.draw.rect(screen, BLACK, input_box, 2, border_radius=5)
        text_surface = font_input.render(input_text, True, TEXT_COLOR)
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        hit_button.draw(screen)
        back_button.draw(screen)

    def draw_level_complete():
        screen.fill(GREEN)
        pygame.draw.rect(screen, LIGHT_GREEN, (100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200), border_radius=20)
        level = levels[current_level]
        title = title_font.render(f"Level {current_level + 1} Complete!", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        pygame.draw.rect(screen, SHADOW_COLOR, title_rect.move(5, 5), border_radius=10)
        screen.blit(title, title_rect)
        strokes_text = font_medium.render(f"Your strokes: {level.strokes}", True, BLACK)
        screen.blit(strokes_text, (SCREEN_WIDTH // 2 - strokes_text.get_width() // 2, 300))
        par_text = font_medium.render(f"Par: {level.par}", True, BLACK)
        screen.blit(par_text, (SCREEN_WIDTH // 2 - par_text.get_width() // 2, 350))
        if level.strokes < level.par:
            result_text = font_medium.render(f"{level.par - level.strokes} under par!", True, BLUE)
        elif level.strokes > level.par:
            result_text = font_medium.render(f"{level.strokes - level.par} over par", True, RED)
        else:
            result_text = font_medium.render("Par!", True, GREEN)
        screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 400))
        if current_level < len(levels) - 1:
            next_button.draw(screen)
        else:
            complete_text = font_large.render("Game Completed!", True, BLACK)
            screen.blit(complete_text, (SCREEN_WIDTH // 2 - complete_text.get_width() // 2, 450))
            total_text = font_medium.render(f"Total strokes: {total_strokes}", True, BLACK)
            screen.blit(total_text, (SCREEN_WIDTH // 2 - total_text.get_width() // 2, 500))
        menu_button.draw(screen)
        back_button.draw(screen)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        if game_state == PLAYING:
            back_button.check_hover(mouse_pos)
            hit_button.check_hover(mouse_pos)
        elif game_state == LEVEL_COMPLETE:
            if current_level < len(levels) - 1:
                next_button.check_hover(mouse_pos)
            menu_button.check_hover(mouse_pos)
            back_button.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            action = back_button.handle_event(event)
            if action == "back":
                return
            if game_state == LEVEL_COMPLETE:
                action = None
                if current_level < len(levels) - 1:
                    action = next_button.handle_event(event) or menu_button.handle_event(event)
                else:
                    action = menu_button.handle_event(event)
                if action == "next":
                    if current_level + 1 < len(unlocked_levels):
                        unlocked_levels[current_level + 1] = True
                        level_buttons[current_level + 1].locked = False
                        level_buttons[current_level + 1].color = GREEN
                        level_buttons[current_level + 1].hover_color = HOVER_COLOR
                    game_state = PLAYING
                    load_level(current_level + 1)
                elif action == "menu":
                    return
            elif game_state == PLAYING:
                if event.type == MOUSEBUTTONDOWN:
                    if hit_button.handle_event(event) == "hit":
                        if hit_ball():
                            input_text = ""
                    if slider_rect.collidepoint(event.pos):
                        slider_knob_y = event.pos[1]
                        slider_knob_y = max(slider_y, min(slider_knob_y, slider_y + slider_height))
                        force = ((slider_y + slider_height - slider_knob_y) / slider_height) * max_force
                    if input_box.collidepoint(event.pos):
                        active = True
                    else:
                        active = False
                elif event.type == MOUSEMOTION:
                    if event.buttons[0] and slider_rect.collidepoint(event.pos):
                        slider_knob_y = event.pos[1]
                        slider_knob_y = max(slider_y, min(slider_knob_y, slider_y + slider_height))
                        force = ((slider_y + slider_height - slider_knob_y) / slider_height) * max_force
                elif event.type == KEYDOWN:
                    if active:
                        if event.key == K_RETURN:
                            if hit_ball():
                                input_text = ""
                        elif event.key == K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            input_text += event.unicode

        if game_state == PLAYING:
            for moving_obstacle in levels[current_level].moving_obstacles:
                moving_obstacle.update()
            ball_pos[0] += ball_speed[0]
            ball_pos[1] += ball_speed[1]
            if ball_pos[0] - ball_radius < 0:
                ball_pos[0] = ball_radius
                ball_speed[0] = -ball_speed[0] * 0.8
            elif ball_pos[0] + ball_radius > SCREEN_WIDTH - sidebar_width:
                ball_pos[0] = SCREEN_WIDTH - sidebar_width - ball_radius
                ball_speed[0] = -ball_speed[0] * 0.8
            if ball_pos[1] - ball_radius < 0:
                ball_pos[1] = ball_radius
                ball_speed[1] = -ball_speed[1] * 0.8
            elif ball_pos[1] + ball_radius > SCREEN_HEIGHT:
                ball_pos[1] = SCREEN_HEIGHT - ball_radius
                ball_speed[1] = -ball_speed[1] * 0.8
            collided_obstacle = check_collision(ball_pos, ball_radius, levels[current_level].obstacles)
            if collided_obstacle:
                if ball_pos[0] <= collided_obstacle.left or ball_pos[0] >= collided_obstacle.right:
                    ball_speed[0] = -ball_speed[0] * 0.8
                if ball_pos[1] <= collided_obstacle.top or ball_pos[1] >= collided_obstacle.bottom:
                    ball_speed[1] = -ball_speed[1] * 0.8
                while check_collision(ball_pos, ball_radius, levels[current_level].obstacles):
                    ball_pos[0] += ball_speed[0] * 0.1
                    ball_pos[1] += ball_speed[1] * 0.1
            for moving_obstacle in levels[current_level].moving_obstacles:
                if moving_obstacle.rect.colliderect(pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)):
                    if ball_pos[0] <= moving_obstacle.rect.left or ball_pos[0] >= moving_obstacle.rect.right:
                        ball_speed[0] = -ball_speed[0] * 0.8
                    if ball_pos[1] <= moving_obstacle.rect.top or ball_pos[1] >= moving_obstacle.rect.bottom:
                        ball_speed[1] = -ball_speed[1] * 0.8
                    while check_collision(ball_pos, ball_radius, levels[current_level].obstacles) or moving_obstacle.rect.colliderect(pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)):
                        ball_pos[0] += ball_speed[0] * 0.1
                        ball_pos[1] += ball_speed[1] * 0.1
            ball_speed[0] *= 0.98
            ball_speed[1] *= 0.98
            if distance(ball_pos, levels[current_level].hole_pos) < hole_radius - ball_radius:
                total_strokes += levels[current_level].strokes
                game_state = LEVEL_COMPLETE

        if game_state == PLAYING:
            draw_game()
        elif game_state == LEVEL_COMPLETE:
            draw_level_complete()

        pygame.display.flip()
        clock.tick(60)

# Start de homescreen
if __name__ == "__main__":
    homescreen()
