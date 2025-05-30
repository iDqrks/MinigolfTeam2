import pygame
import sys
import math
import time
import requests
from pygame.locals import *

# Initialiseren van Pygame
pygame.init()

# API url
API_URL = "https://brain-putt.vercel.app/"

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
GRID_COLOR = (170, 220, 170)
SLIDER_BG_COLOR = (200, 200, 200)
SLIDER_KNOB_COLOR = (70, 130, 180)
TEXT_COLOR = (50, 50, 50)
INPUT_BG_COLOR = (240, 240, 240)
BUTTON_COLOR = (100, 150, 200)
BUTTON_HOVER_COLOR = (120, 170, 220)
LOCKED_COLOR = (100, 100, 100)
ARROW_COLOR = (0, 0, 0)

# Standaard waarde bal en vlag
selected_ball_color = WHITE
selected_flag_color = RED

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
NAME_INPUT = 3

# Arrow
ARROW_WIDTH = 4
ARROW_SCALE = 12
ARROW_HEAD_LEN = 12

# Timer variabelen
game_start_time = 0
total_elapsed_time = 0
level_start_time = 0
timer_active = False

# Cursor in input_box
cursor_visible = True
cursor_timer = 0

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

# Homescreen knoppen
start_button = HomeButton("Start Spel", (SCREEN_WIDTH - 250) // 2, 350, 250, 120, button_font)
levels_button = HomeButton("Levels", 50, 650, 200, 60, small_font)
customize_button = HomeButton("Personaliseer", (SCREEN_WIDTH - 250) // 2, 500, 250, 75, small_font)
score_button = HomeButton("Scorebord", (SCREEN_WIDTH - 250) // 2, 600, 250, 75, button_font)
buttons = [start_button, levels_button, customize_button, score_button]

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
        if self.type == "bal":
            pygame.draw.circle(screen, self.color, (center_x, center_y), 40)
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 40, 2)
        elif self.type == "vlag":
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

# Customize scherm knoppen
customize_options = [
    HomeButton("Bal Skins", (SCREEN_WIDTH - 250) // 2, 300, 250, 75, button_font),
    HomeButton("Vlag Skins", (SCREEN_WIDTH - 250) // 2, 400, 250, 75, button_font),
    HomeButton("Terug", (SCREEN_WIDTH - 250) // 2, 500, 250, 75, button_font)
]

# Voorbeeld skins
ball_skins = [
    SkinOption(300, 250, WHITE, "bal"),
    SkinOption(450, 250, RED, "bal"),
    SkinOption(600, 250, YELLOW, "bal")
]
flag_skins = [
    SkinOption(300, 250, RED, "vlag"),
    SkinOption(450, 250, WHITE, "vlag"),
    SkinOption(600, 250, BLUE, "vlag")
]

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
        self.elapsed_time = 0

# Level designs (9 levels)
levels = [
    Level(hole_pos=[800, 600],
          obstacles=[pygame.Rect(300, 300, 200, 25)],
          moving_obstacles=[],
          par=2,
          start_pos=(50, 50)),
    Level(hole_pos=[700, 500],
          obstacles=[pygame.Rect(0, 350, 400, 25), pygame.Rect(500, 350, 350, 25)],
          moving_obstacles=[MovingBarrier(start_pos=[450, 400], end_pos=[450, 450], speed=2, vertical=True)],
          par=3,
          start_pos=(50, 50)),
    Level(hole_pos=[600, 400],
          obstacles=[pygame.Rect(0, 250, 400, 25), pygame.Rect(500, 250, 350, 25)],
          moving_obstacles=[MovingBarrier(start_pos=[450, 300], end_pos=[450, 350], speed=2, vertical=True)],
          par=4,
          start_pos=(50, 50)),
    Level(hole_pos=[750, 550],
          obstacles=[pygame.Rect(0, 300, 300, 25), pygame.Rect(400, 300, 450, 25)],
          moving_obstacles=[MovingBarrier(start_pos=[350, 350], end_pos=[350, 450], speed=3, vertical=True)],
          par=4,
          start_pos=(50, 50)),
    Level(hole_pos=[650, 450],
          obstacles=[pygame.Rect(0, 200, 350, 25), pygame.Rect(450, 200, 400, 25), pygame.Rect(350, 200, 25, 200)],
          moving_obstacles=[MovingBarrier(start_pos=[400, 250], end_pos=[400, 300], speed=2, vertical=True),
                            MovingBarrier(start_pos=[500, 350], end_pos=[500, 400], speed=2, vertical=True)],
          par=5,
          start_pos=(50, 50)),
    Level(hole_pos=[700, 600],
          obstacles=[pygame.Rect(0, 450, 550, 25), pygame.Rect(650, 450, 200, 25)],
          moving_obstacles=[MovingBarrier(start_pos=[600, 350], end_pos=[600, 400], speed=2, vertical=True),
                           MovingBarrier(start_pos=[575, 500], end_pos=[575, 550], speed=2, vertical=True)],
          par=6,
          start_pos=(50, 50)),
    Level(hole_pos=[800, 500],
          obstacles=[pygame.Rect(0, 250, 300, 25), pygame.Rect(400, 250, 450, 25), pygame.Rect(0, 400, 600, 25), pygame.Rect(700, 400, 150, 25)],
          moving_obstacles=[MovingBarrier(start_pos=[350, 300], end_pos=[350, 350], speed=2, vertical=True),
                           MovingBarrier(start_pos=[650, 350], end_pos=[650, 400], speed=2, vertical=True),
                           MovingBarrier(start_pos=[500, 450], end_pos=[500, 500], speed=3, vertical=True)],
          par=7,
          start_pos=(50, 50)),
    Level(hole_pos=[750, 650],
          obstacles=[pygame.Rect(0, 300, 400, 25), pygame.Rect(500, 300, 350, 25), pygame.Rect(400, 0, 25, 250), pygame.Rect(0, 500, 600, 25), pygame.Rect(700, 500, 150, 25)],
          moving_obstacles=[MovingBarrier(start_pos=[450, 350], end_pos=[450, 400], speed=3, vertical=True),
                           MovingBarrier(start_pos=[650, 400], end_pos=[650, 450], speed=2, vertical=True),
                           MovingBarrier(start_pos=[550, 550], end_pos=[550, 600], speed=2, vertical=True)],
          par=8,
          start_pos=(50, 50)),
    Level(hole_pos=[100, 700],
          obstacles=[pygame.Rect(0, 200, 350, 25), pygame.Rect(450, 200, 400, 25), pygame.Rect(0, 400, 550, 25), pygame.Rect(650, 400, 200, 25), pygame.Rect(0, 600, 700, 25)],
          moving_obstacles=[MovingBarrier(start_pos=[400, 250], end_pos=[400, 300], speed=2, vertical=True),
                           MovingBarrier(start_pos=[600, 350], end_pos=[600, 400], speed=2, vertical=True),
                           MovingBarrier(start_pos=[725, 450], end_pos=[725, 500], speed=2, vertical=True),
                           MovingBarrier(start_pos=[775, 600], end_pos=[775, 650], speed=2, vertical=True)],
          par=9,
          start_pos=(50, 50))
]

# Homescreen
def homescreen():
    global game_start_time, total_elapsed_time, timer_active
    clock = pygame.time.Clock()
    running = True
    golfball_pos = [100, 100]
    ball_angle = 0

    # Reset timer when starting a new game session
    game_start_time = 0
    total_elapsed_time = 0
    timer_active = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for button in buttons:
                if button.is_clicked(event):
                    print(f"{button.text} geklikt!")
                    if button.text == "Start Spel":
                        game_start_time = time.time()
                        timer_active = True
                        game_screen(0)
                    elif button.text == "Levels":
                        level_screen()
                    elif button.text == "Personaliseer":
                        customize_screen()
                    elif button.text == "Scorebord":
                        scoreboard_screen()

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
        ball_rect = ball_surface.get_rect(center=golfball_pos)
        screen.blit(ball_surface, ball_rect)

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
                    print(f"{button.text} geklikt!")
                    if button.text == "Terug":
                        return
                    elif button.text == "Bal Skins":
                        skin_selection_screen(ball_skins, "Bal Skins")
                    elif button.text == "Vlag Skins":
                        skin_selection_screen(flag_skins, "Vlag Skins")

        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        # Titel
        customize_title = title_font.render("Personaliseer", True, WHITE)
        title_rect = customize_title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(customize_title, title_rect)

        # Achtergrond voor knoppen
        pygame.draw.rect(screen, LIGHT_GREEN, (SCREEN_WIDTH // 2 - 150, 250, 300, 300), border_radius=20)
        pygame.draw.rect(screen, DARK_GREEN, (SCREEN_WIDTH // 2 - 150, 250, 300, 300), 5, border_radius=20)

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
                    print(f"Geselecteerd {skin_type} met kleur {skin.color}")
                    global selected_ball_color, selected_flag_color
                    if skin.type == "bal":
                        selected_ball_color = skin.color
                    elif skin.type == "vlag":
                        selected_flag_color = skin.color

        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        title = title_font.render(f"Kies {skin_type}", True, WHITE)
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
                    print(f"Start Level {level_num + 1}...")
                    game_start_time = time.time()
                    timer_active = True
                    game_screen(level_num)

        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        title = title_font.render("Selecteer Level", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)

        for button in level_buttons:
            button.draw(screen)

        level_back_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

# Scoreboard scherm
def scoreboard_screen():
    clock = pygame.time.Clock()
    running = True
    back_button = HomeButton("Terug", (SCREEN_WIDTH - 250) // 2, 650, 250, 75, button_font)

    # Haal scores op van de server
    try:
        response = requests.get(f"{API_URL}/scores/", timeout=5)
        response.raise_for_status()
        scores = response.json()
    except requests.RequestException as e:
        print(f"Fout bij ophalen scores: {e}")
        scores = []

    # Tabelinstellingen
    table_x = 200
    table_y = 150
    table_width = 600
    table_height = 400
    row_height = 50
    col_widths = [80, 250, 120, 150]  # Breedtes voor Rank, Naam, Strokes, Tijd
    header_color = (50, 100, 50)  # Donkergroen voor header
    row_colors = [(255, 255, 255), (240, 240, 240)]  # Afwisselend wit en lichtgrijs

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if back_button.is_clicked(event):
                return

        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        # Titel
        title = title_font.render("Scoreboard", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        pygame.draw.rect(screen, DARK_GREEN, title_rect.inflate(60, 30), border_radius=10)
        screen.blit(title, title_rect)

        # Tabelachtergrond
        pygame.draw.rect(screen, WHITE, (table_x, table_y, table_width, table_height), border_radius=10)
        pygame.draw.rect(screen, BLACK, (table_x, table_y, table_width, table_height), 2, border_radius=10)

        # Header
        headers = ["Rank", "Naam", "Strokes", "Tijd"]
        for i, header in enumerate(headers):
            pygame.draw.rect(screen, header_color, (table_x + sum(col_widths[:i]), table_y, col_widths[i], row_height))
            pygame.draw.rect(screen, BLACK, (table_x + sum(col_widths[:i]), table_y, col_widths[i], row_height), 1)
            text = font_medium.render(header, True, WHITE)
            text_rect = text.get_rect(left=table_x + sum(col_widths[:i]) + 10, centery=table_y + row_height // 2)
            screen.blit(text, text_rect)

        # Scores
        if not scores:
            no_scores_text = font_medium.render("Nog geen scores beschikbaar", True, BLACK)
            screen.blit(no_scores_text, (SCREEN_WIDTH // 2 - no_scores_text.get_width() // 2, table_y + row_height * 2))
        else:
            for i, score in enumerate(scores[:5], 1):  # Beperk tot top 5
                row_y = table_y + row_height * (i)
                row_color = row_colors[i % 2]
                pygame.draw.rect(screen, row_color, (table_x, row_y, table_width, row_height))
                pygame.draw.rect(screen, BLACK, (table_x, row_y, table_width, row_height), 1)

                # Rank
                rank_text = font_small.render(str(i), True, BLACK)
                screen.blit(rank_text, (table_x + 10, row_y + row_height // 2 - rank_text.get_height() // 2))

                # Naam
                name_text = font_small.render(score['username'][:20], True, BLACK)  # Beperk lengte
                screen.blit(name_text, (table_x + col_widths[0] + 10, row_y + row_height // 2 - name_text.get_height() // 2))

                # Strokes
                strokes_text = font_small.render(str(score['score']), True, BLACK)
                screen.blit(strokes_text, (table_x + sum(col_widths[:2]) + 10, row_y + row_height // 2 - strokes_text.get_height() // 2))

                # Tijd
                time_text = font_small.render(f"{score['time_seconds']}s", True, BLACK)
                screen.blit(time_text, (table_x + sum(col_widths[:3]) + 10, row_y + row_height // 2 - time_text.get_height() // 2))

        back_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

# Game scherm
def game_screen(level_num):
    global unlocked_levels, total_elapsed_time, level_start_time, timer_active, selected_ball_color, selected_flag_color
    clock = pygame.time.Clock()
    running = True
    back_button = GameButton(875, 680, 100, 50, "Terug", "back")
    hit_button = GameButton(875, 570, 100, 50, "Slaag!", "hit")

    if level_num >= len(levels) or not unlocked_levels[level_num]:
        print(f"Level {level_num + 1} is vergrendeld of nog niet geïmplementeerd")
        return

    # Timer initialiseren voor het level
    level_start_time = time.time()
    levels[level_num].elapsed_time = 0
    current_level = level_num
    ball_radius = 15
    ball_speed = [0, 0]
    hole_radius = 25
    ball_pos = list(levels[current_level].start_pos)
    total_strokes = 0
    game_state = PLAYING
    END_SCREEN = 4  # Nieuwe staat voor eindscherm

    # Breedere zijbalk instellingen
    sidebar_width = 150
    slider_width = 30
    slider_height = 300
    slider_x = SCREEN_WIDTH - sidebar_width + 60
    slider_y = 235
    slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
    slider_knob_radius = 15
    slider_knob_y = slider_y + slider_height
    force = 0
    min_force = 0
    max_force = 25

    # Breeder en mooier invoerveld
    input_box = pygame.Rect(SCREEN_WIDTH - sidebar_width + 10, 130, 130, 40)
    input_text = ""
    active = False

    # Cursor in invoerveld
    cursor_visible = True
    last_cursor_switch = pygame.time.get_ticks()
    BLINK_INTERVAL = 500

    next_button = GameButton(SCREEN_WIDTH // 2 - 100, 470, 200, 60, "Volgend Level", "next")
    menu_button = GameButton(SCREEN_WIDTH // 2 - 100, 550, 200, 60, "Hoofdmenu", "menu")
    submit_button = GameButton(SCREEN_WIDTH // 2 - 100, 500, 200, 60, "Indienen", "submit")
    end_menu_button = HomeButton("Hoofdmenu", (SCREEN_WIDTH - 250) // 2, 600, 250, 75, button_font)

    # Variabelen voor naam invoer na game voltooiing
    name_input_active = False
    name_input_text = ""
    name_input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 350, 300, 50)
    name_submitted = False
    error_message = ""

    # Variabelen voor eindscherm
    golfball_pos = [100, 100]
    ball_angle = 0

    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def draw_grid():
        for x in range(0, SCREEN_WIDTH - sidebar_width, 25):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 25):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH - sidebar_width, y), 1)
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
        levels[current_level].strokes = 0
        levels[current_level].elapsed_time = 0
        level_start_time = time.time()

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
        pygame.draw.rect(screen, INPUT_BG_COLOR, (SCREEN_WIDTH - sidebar_width, 0, sidebar_width, SCREEN_HEIGHT))
        draw_grid()

        # Bereken verstreken tijd voor het huidige level
        if timer_active:
            levels[current_level].elapsed_time = time.time() - level_start_time
        current_time = int(levels[current_level].elapsed_time)

        for obstacle in levels[current_level].obstacles:
            pygame.draw.rect(screen, (139, 69, 19), obstacle)
        for moving_obstacle in levels[current_level].moving_obstacles:
            moving_obstacle.update()
            moving_obstacle.draw(screen)

        # Teken de hole
        pygame.draw.circle(screen, BLACK, levels[current_level].hole_pos, hole_radius)
        pygame.draw.circle(screen, (50, 50, 50), levels[current_level].hole_pos, hole_radius - 5)

        # Teken de vlag bovenop de hole
        hole_center_x, hole_center_y = levels[current_level].hole_pos
        flagpole_height = 80
        flag_width = 40
        flag_height = 20
        # Vlaggenstok
        pygame.draw.rect(screen, GRAY, (hole_center_x - 5, hole_center_y - flagpole_height, 10, flagpole_height))
        # Vlag
        pygame.draw.polygon(screen, selected_flag_color, [
            (hole_center_x, hole_center_y - flagpole_height),
            (hole_center_x + flag_width, hole_center_y - flagpole_height + flag_height // 2),
            (hole_center_x, hole_center_y - flagpole_height + flag_height)
        ])
        # Randen
        pygame.draw.rect(screen, BLACK, (hole_center_x - 5, hole_center_y - flagpole_height, 10, flagpole_height), 2)
        pygame.draw.polygon(screen, BLACK, [
            (hole_center_x, hole_center_y - flagpole_height),
            (hole_center_x + flag_width, hole_center_y - flagpole_height + flag_height // 2),
            (hole_center_x, hole_center_y - flagpole_height + flag_height)
        ], 2)

        if force > 0 and input_text:
            try:
                coords = input_text.replace("(", "").replace(")", "").split(",")
                input_x = int(coords[0])
                input_y = int(coords[1])
                max_screen_width = SCREEN_WIDTH - sidebar_width
                if 0 <= input_x <= max_screen_width and 0 <= input_y <= SCREEN_HEIGHT:
                    horizontal_distance = input_x - ball_pos[0]
                    vertical_distance = input_y - ball_pos[1]
                    distance_ball_to_target = math.hypot(horizontal_distance, vertical_distance)
                    if distance_ball_to_target > 0:
                        direction_x = horizontal_distance / distance_ball_to_target
                        direction_y = vertical_distance / distance_ball_to_target
                        arrow_length = force * ARROW_SCALE
                        arrow_tip_x = ball_pos[0] + direction_x * arrow_length
                        arrow_tip_y = ball_pos[1] + direction_y * arrow_length
                        pygame.draw.line(
                            screen,
                            ARROW_COLOR,
                            (int(ball_pos[0]), int(ball_pos[1])),
                            (int(arrow_tip_x), int(arrow_tip_y)),
                            ARROW_WIDTH
                        )
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

        # Teken de bal met de geselecteerde kleur
        pygame.draw.circle(screen, selected_ball_color, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
        # Teken het rode puntje alleen als de bal niet wit of geel is
        if selected_ball_color not in [WHITE, YELLOW]:
            pygame.draw.circle(screen, (255, 100, 100),
                               (int(ball_pos[0] - ball_radius / 3), int(ball_pos[1] - ball_radius / 3)),
                               ball_radius / 3)

        coord_text = font_input.render("Doel (x,y):", True, BLACK)
        screen.blit(coord_text, (SCREEN_WIDTH - sidebar_width + 10, 100))
        pygame.draw.rect(screen, WHITE, input_box, border_radius=5)
        pygame.draw.rect(screen, BLACK, input_box, 2, border_radius=5)
        text_surface = font_input.render(input_text, True, TEXT_COLOR)
        screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
        if active and cursor_visible:
            cursor_x = input_box.x + 10 + text_surface.get_width()
            cursor_y = input_box.y + 7
            cursor_height = font_input.get_height() + 5
            pygame.draw.line(screen, TEXT_COLOR,
                             (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

        force_text = font_input.render(f"Kracht: {force:.1f}", True, TEXT_COLOR)
        screen.blit(force_text, (SCREEN_WIDTH - sidebar_width + 10, 205))
        pygame.draw.rect(screen, SLIDER_BG_COLOR, slider_rect)
        pygame.draw.circle(screen, SLIDER_KNOB_COLOR, (slider_x + slider_width // 2, slider_knob_y), slider_knob_radius)

        strokes_text = font_input.render(f"Slagen: {levels[current_level].strokes}", True, BLACK)
        screen.blit(strokes_text, (SCREEN_WIDTH - sidebar_width + 10, 10))
        level_text = font_input.render(f"Level: {current_level + 1}/{len(levels)}", True, BLACK)
        screen.blit(level_text, (SCREEN_WIDTH - sidebar_width + 10, 30))
        par_text = font_input.render(f"Par: {levels[current_level].par}", True, BLACK)
        screen.blit(par_text, (SCREEN_WIDTH - sidebar_width + 10, 50))
        time_text = font_input.render(f"Tijd: {current_time}s", True, BLACK)
        screen.blit(time_text, (SCREEN_WIDTH - sidebar_width + 10, 70))

        hit_button.draw(screen)
        back_button.draw(screen)

    def draw_end_screen():
        nonlocal ball_angle
        # Statistieken berekenen
        total_strokes = sum(l.strokes for l in levels)
        hole_in_ones = sum(1 for l in levels if l.strokes == 1)
        total_time_min = int(total_elapsed_time // 60)
        avg_strokes = total_strokes / len(levels) if levels else 0
        stats = {
            "Totale Slagen": total_strokes,
            "Hole-in-Ones": hole_in_ones,
            "Totale Tijd (min)": total_time_min,
            "Gemiddelde Slagen per Hole": round(avg_strokes, 1)
        }

        # Achtergrond
        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        pygame.draw.rect(screen, LIGHT_GREEN, (0, SCREEN_HEIGHT // 2 + 50, SCREEN_WIDTH, 150))
        pygame.draw.ellipse(screen, DARK_GREEN, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 200, 200, 70))

        # Titel
        title_shadow = title_font.render("Spel Voltooid!", True, SHADOW_COLOR)
        title = title_font.render("Spel Voltooid!", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_shadow, title_rect.move(5, 5))
        pygame.draw.rect(screen, DARK_GREEN, (title_rect.x - 40, title_rect.y - 25,
                                              title_rect.width + 80, title_rect.height + 50), border_radius=20)
        screen.blit(title, title_rect)

        # Gefeliciteerd
        congrats = button_font.render("Gefeliciteerd!", True, WHITE)
        congrats_rect = congrats.get_rect(center=(SCREEN_WIDTH // 2, 250))
        screen.blit(congrats, congrats_rect)

        # Statistieken
        y_pos = 320
        for stat, value in stats.items():
            stat_text = small_font.render(f"{stat}: {value}", True, WHITE)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            screen.blit(stat_text, stat_rect)
            y_pos += 50

        # Geanimeerde golfbal
        ball_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(ball_surface, selected_ball_color, (25, 25), 25)
        if selected_ball_color not in [WHITE, YELLOW]:
            pygame.draw.circle(ball_surface, (255, 100, 100), (25 - 25 / 3, 25 - 25 / 3), 25 / 3)
        pygame.draw.circle(ball_surface, GRAY, (25, 25), 25, 2)
        rotated_ball = pygame.transform.rotate(ball_surface, ball_angle)
        ball_rect = rotated_ball.get_rect(center=golfball_pos)
        screen.blit(rotated_ball, ball_rect)
        ball_angle += 1

        # Knop
        end_menu_button.draw(screen)

    def draw_name_input():
        nonlocal error_message
        screen.fill(GREEN)
        # Achtergrondkader
        pygame.draw.rect(screen, LIGHT_GREEN, (100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200), border_radius=20)
        pygame.draw.rect(screen, BLACK, (100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200), 2, border_radius=20)

        # Titel
        title = title_font.render("Spel Voltooid!", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        pygame.draw.rect(screen, GRID_COLOR, title_rect.inflate(60, 30), border_radius=10)
        screen.blit(title, title_rect)

        # Instructietekst
        prompt = font_medium.render("Voer je naam in:", True, BLACK)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, 300))
        screen.blit(prompt, prompt_rect)

        # Invoerveld
        pygame.draw.rect(screen, WHITE, name_input_box, border_radius=5)
        pygame.draw.rect(screen, BLACK, name_input_box, 2, border_radius=5)
        name_surface = font_input.render(name_input_text, True, TEXT_COLOR)
        screen.blit(name_surface, (name_input_box.x + 10, name_input_box.y + 10))
        if name_input_active and cursor_visible:
            cursor_x = name_input_box.x + 10 + name_surface.get_width()
            cursor_y = name_input_box.y + 7
            cursor_height = font_input.get_height() + 5
            pygame.draw.line(screen, TEXT_COLOR,
                             (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

        # Foutmelding
        if error_message:
            error_text = font_small.render(error_message, True, RED)
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, 420))
            screen.blit(error_text, error_rect)

        # Knoppen
        submit_button.draw(screen)
        back_button.draw(screen)

    def draw_level_complete():
        global timer_active, total_elapsed_time, level_start_time
        if timer_active:
            levels[current_level].elapsed_time = time.time() - level_start_time
            total_elapsed_time += levels[current_level].elapsed_time
            timer_active = False

        screen.fill(GREEN)
        pygame.draw.rect(screen, LIGHT_GREEN, (100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200), border_radius=20)

        level = levels[current_level]
        title = title_font.render(f"Level {current_level + 1} compleet!", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        pygame.draw.rect(screen, GRID_COLOR, title_rect.inflate(60, 30), border_radius=10)
        screen.blit(title, title_rect)

        strokes_text = font_medium.render(f"Jouw slagen: {level.strokes}", True, WHITE)
        strokes_rect = strokes_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        par_text = font_medium.render(f"Par: {level.par}", True, WHITE)
        par_rect = par_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        if level.strokes < level.par:
            result_text = font_medium.render(f"{level.par - level.strokes} onder par!", True, BLUE)
        elif level.strokes > level.par:
            result_text = font_medium.render(f"{level.strokes - level.par} boven par", True, RED)
        else:
            result_text = font_medium.render("Par!", True, GREEN)
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        group_rect = strokes_rect.union(par_rect).union(result_rect)
        pygame.draw.rect(screen, GRID_COLOR, group_rect.inflate(60, 30), border_radius=10)
        screen.blit(strokes_text, strokes_rect)
        screen.blit(par_text, par_rect)
        screen.blit(result_text, result_rect)

        if current_level < len(levels) - 1:
            next_button.draw(screen)
        else:
            complete_text = font_large.render("Spel Voltooid!", True, BLACK)
            screen.blit(complete_text, (SCREEN_WIDTH // 2 - complete_text.get_width() // 2, 550))
            total_text = font_medium.render(f"Totale slagen: {sum(l.strokes for l in levels)}", True, BLACK)
            screen.blit(total_text, (SCREEN_WIDTH // 2 - total_text.get_width() // 2, 600))

        menu_button.draw(screen)
        back_button.draw(screen)

    while running:
        now = pygame.time.get_ticks()
        if (active or name_input_active) and now - last_cursor_switch >= BLINK_INTERVAL:
            cursor_visible = not cursor_visible
            last_cursor_switch = now

        mouse_pos = pygame.mouse.get_pos()

        if game_state == PLAYING:
            back_button.check_hover(mouse_pos)
            hit_button.check_hover(mouse_pos)
        elif game_state == LEVEL_COMPLETE:
            if current_level < len(levels) - 1:
                next_button.check_hover(mouse_pos)
            menu_button.check_hover(mouse_pos)
            back_button.check_hover(mouse_pos)
        elif game_state == NAME_INPUT:
            submit_button.check_hover(mouse_pos)
            back_button.check_hover(mouse_pos)
        elif game_state == END_SCREEN:
            end_menu_button.draw(screen)  # HomeButton handelt hover zelf

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            action = back_button.handle_event(event)
            if action == "back":
                if timer_active:
                    levels[current_level].elapsed_time = time.time() - level_start_time
                    total_elapsed_time += levels[current_level].elapsed_time
                    timer_active = False
                return

            if game_state == PLAYING:
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
                elif event.type == KEYDOWN and active:
                    if event.key == K_RETURN:
                        if hit_ball():
                            input_text = ""
                    elif event.key == K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

            elif game_state == NAME_INPUT:
                if event.type == MOUSEBUTTONDOWN:
                    if name_input_box.collidepoint(event.pos):
                        name_input_active = True
                    else:
                        name_input_active = False
                if event.type == KEYDOWN and name_input_active:
                    if event.key == K_RETURN and name_input_text.strip():
                        total_strokes = sum(l.strokes for l in levels)
                        try:
                            response = requests.post(
                                f"{API_URL}/scores/add/",
                                json={
                                    "username": name_input_text.strip(),
                                    "score": total_strokes,
                                    "time_seconds": int(total_elapsed_time)
                                },
                                timeout=5
                            )
                            response.raise_for_status()
                            print(f"Score verzonden: {name_input_text}, {total_strokes} slagen, {int(total_elapsed_time)} seconden")
                            name_submitted = True
                            game_state = END_SCREEN
                        except requests.RequestException as e:
                            error_message = f"Fout bij verzenden score: {str(e)}"
                            print(error_message)
                    elif event.key == K_BACKSPACE:
                        name_input_text = name_input_text[:-1]
                    else:
                        name_input_text += event.unicode
                if submit_button.handle_event(event) == "submit" and name_input_text.strip():
                    total_strokes = sum(l.strokes for l in levels)
                    try:
                        response = requests.post(
                            f"{API_URL}/scores/add/",
                            json={
                                "username": name_input_text.strip(),
                                "score": total_strokes,
                                "time_seconds": int(total_elapsed_time)
                            },
                            timeout=5
                        )
                        response.raise_for_status()
                        print(f"Score verzonden: {name_input_text}, {total_strokes} slagen, {int(total_elapsed_time)} seconden")
                        name_submitted = True
                        game_state = END_SCREEN
                    except requests.RequestException as e:
                        error_message = f"Fout bij verzenden score: {str(e)}"
                        print(error_message)

            elif game_state == LEVEL_COMPLETE:
                action = None
                if current_level < len(levels) - 1:
                    action = next_button.handle_event(event) or menu_button.handle_event(event)
                else:
                    action = menu_button.handle_event(event)
                if action == "next":
                    game_state = PLAYING
                    load_level(current_level + 1)
                    timer_active = True
                    level_start_time = time.time()
                elif action == "menu":
                    timer_active = False
                    return

            elif game_state == END_SCREEN:
                if end_menu_button.is_clicked(event):
                    timer_active = False
                    return

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
                # Ontgrendel het volgende level direct
                if current_level + 1 < len(unlocked_levels):
                    unlocked_levels[current_level + 1] = True
                    level_buttons[current_level + 1].locked = False
                    level_buttons[current_level + 1].color = GREEN
                    level_buttons[current_level + 1].hover_color = HOVER_COLOR
                game_state = LEVEL_COMPLETE if current_level < len(levels) - 1 else NAME_INPUT

        if game_state == PLAYING:
            draw_game()
        elif game_state == LEVEL_COMPLETE:
            draw_level_complete()
        elif game_state == NAME_INPUT:
            draw_name_input()
        elif game_state == END_SCREEN:
            draw_end_screen()

        pygame.display.flip()
        clock.tick(60)

# Start de homescreen
if __name__ == "__main__":
    homescreen()