import pygame
import sys

# Initialiseren van Pygame
pygame.init()

# Kleuren
WHITE = (255, 255, 255)
GREEN = (50, 150, 50)
HOVER_COLOR = (100, 200, 100)
SHADOW_COLOR = (100, 100, 100, 100)
DARK_GREEN = (30, 100, 30)
BLUE = (70, 130, 180)

# Fonts
title_font = pygame.font.Font(None, 120)
button_font = pygame.font.Font(None, 50)  # Verklein de fontgrootte van 60 naar 50


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


# Win scherm functie
def win_screen(screen, level, strokes):
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    clock = pygame.time.Clock()
    running = True

    # Knoppen (maak ze breder: van 250 naar 300)
    home_button = Button("Ga naar Home", (SCREEN_WIDTH - 300) // 2 - 350, 500, 300, 75, button_font)
    retry_button = Button("Probeer Opnieuw", (SCREEN_WIDTH - 300) // 2, 500, 300, 75, button_font)
    next_button = Button("Volgend Level", (SCREEN_WIDTH - 300) // 2 + 350, 500, 300, 75, button_font)

    buttons = [home_button, retry_button, next_button]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return "quit"

            for button in buttons:
                if button.is_clicked(event):
                    if button.text == "Ga naar Home":
                        return "home"
                    elif button.text == "Probeer Opnieuw":
                        return "retry"
                    elif button.text == "Volgend Level":
                        return "next"

        # Teken achtergrond
        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        # Win tekst
        win_title = title_font.render("Proficiat!", True, WHITE)
        win_title_rect = win_title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(win_title, win_title_rect)

        # Level en slagen info
        level_text = button_font.render(f"Level {level} behaald in {strokes} slagen", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        screen.blit(level_text, level_rect)

        # Teken knoppen
        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(60)


# Voor testdoeleinden (optioneel)
if __name__ == "__main__":
    # Maak een test-scherm
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 750
    test_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Win Screen Test")

    # Roep win_screen aan met voorbeeldwaarden
    result = win_screen(test_screen, 1, 5)
    print(f"Result: {result}")
    pygame.quit()
    sys.exit()