import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BrainPutt - Game Completed")

# Colors (same as homescreen)
WHITE = (255, 255, 255)
GREEN = (50, 150, 50)
LIGHT_GREEN = (80, 180, 80)
BLUE = (70, 130, 180)
DARK_GREEN = (30, 100, 30)
GRAY = (150, 150, 150)
HOVER_COLOR = (100, 200, 100)
SHADOW_COLOR = (100, 100, 100, 100)

# Fonts (same as homescreen)
title_font = pygame.font.Font(None, 120)
button_font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 45)


# Button class (same as homescreen)
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


# Example statistics (replace with real data later)
stats = {
    "Total Strokes": 125,
    "Hole-in-Ones": 3,
    "Total Time (min)": 45,
    "Average Strokes per Hole": 4.2
}

# Create buttons
main_menu_button = Button("Main Menu", (SCREEN_WIDTH - 250) // 2, 600, 250, 75, button_font)


# Endscreen function
def endscreen():
    clock = pygame.time.Clock()
    running = True
    golfball_pos = [100, 100]
    ball_angle = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if main_menu_button.is_clicked(event):
                print("Returning to main menu...")
                running = False  # Replace with function to return to homescreen later

        # Draw background (same as homescreen)
        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        pygame.draw.rect(screen, LIGHT_GREEN, (0, SCREEN_HEIGHT // 2 + 50, SCREEN_WIDTH, 150))
        pygame.draw.ellipse(screen, DARK_GREEN, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 200, 200, 70))

        # Draw title
        title_shadow = title_font.render("Game Completed!", True, SHADOW_COLOR)
        title = title_font.render("Game Completed!", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_shadow, title_rect.move(5, 5))
        pygame.draw.rect(screen, DARK_GREEN, (title_rect.x - 40, title_rect.y - 25,
                                              title_rect.width + 80, title_rect.height + 50), border_radius=20)
        screen.blit(title, title_rect)

        # Draw "Congratulations!"
        congrats = button_font.render("Congratulations!", True, WHITE)
        congrats_rect = congrats.get_rect(center=(SCREEN_WIDTH // 2, 250))
        screen.blit(congrats, congrats_rect)

        # Draw statistics
        y_pos = 320
        for stat, value in stats.items():
            stat_text = small_font.render(f"{stat}: {value}", True, WHITE)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            screen.blit(stat_text, stat_rect)
            y_pos += 50

        # Draw animated golf ball (same as homescreen)
        ball_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(ball_surface, WHITE, (25, 25), 25)
        pygame.draw.circle(ball_surface, GRAY, (25, 25), 25, 2)
        rotated_ball = pygame.transform.rotate(ball_surface, ball_angle)
        ball_rect = rotated_ball.get_rect(center=golfball_pos)
        screen.blit(rotated_ball, ball_rect)
        ball_angle += 1

        # Draw button
        main_menu_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


# Start the endscreen
if __name__ == "__main__":
    endscreen()