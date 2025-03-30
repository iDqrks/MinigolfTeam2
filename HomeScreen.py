import pygame
import sys

# Initialiseren van Pygame
pygame.init()

# Scherm instellingen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BrainPutt")

# Kleuren
WHITE = (255, 255, 255)
GREEN = (50, 150, 50)
LIGHT_GREEN = (80, 180, 80)
BLUE = (70, 130, 180)
DARK_GREEN = (30, 100, 30)
GRAY = (150, 150, 150)
HOVER_COLOR = (100, 200, 100)
SHADOW_COLOR = (100, 100, 100, 100)
RED = (200, 50, 50)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Fonts
title_font = pygame.font.Font(None, 120)
button_font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 45)


# Knop klasse
class Button:
    def __init__(self, text, x, y, width, height, font):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GREEN
        self.hover_color = HOVER_COLOR
        self.font = font

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# Skin keuze klasse
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


# Maak knoppen voor homescreen
start_button = Button("Start Game", (SCREEN_WIDTH - 250) // 2, 350, 250, 120, button_font)  # Gecentreerd
levels_button = Button("Levels", 50, 650, 200, 60, small_font)
achievements_button = Button("Achievements", 750, 650, 250, 60, small_font)  # Breder voor tekst
customize_button = Button("Customize", (SCREEN_WIDTH - 250) // 2, 500, 250, 75, button_font)  # Gecentreerd
score_button = Button("Scorebord", (SCREEN_WIDTH - 250) // 2, 600, 250, 75, button_font)  # Gecentreerd

buttons = [start_button, levels_button, achievements_button, customize_button, score_button]

# Customize scherm knoppen
customize_options = [
    Button("Bal Skins", (SCREEN_WIDTH - 250) // 2, 250, 250, 75, button_font),
    Button("Club Skins", (SCREEN_WIDTH - 250) // 2, 350, 250, 75, button_font),
    Button("Vlag Skins", (SCREEN_WIDTH - 250) // 2, 450, 250, 75, button_font),
    Button("Terug", (SCREEN_WIDTH - 250) // 2, 550, 250, 75, button_font)
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


# Hoofdloop homescreen
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
                        print("Starting game...")
                    elif button.text == "Levels":
                        print("Going to level selection...")
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
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))  # Exact gecentreerd
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
    back_button = Button("Terug", (SCREEN_WIDTH - 250) // 2, 600, 250, 75, button_font)
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


# Start de homescreen
if __name__ == "__main__":
    homescreen()