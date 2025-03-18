import pygame
import sys
import math

# Initialisatie
pygame.init()
screen = pygame.display.set_mode((900, 600))  # Breedte verhoogd voor schuifbalk
clock = pygame.time.Clock()

# Kleuren
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0)  # Donkergroen voor de achtergrond
BLUE = (0, 0, 255)
GRID_COLOR = (200, 200, 200)  # Lichtgrijs voor het raster
SLIDER_COLOR = (255, 165, 0)  # Oranje voor de schuifbalk

# Bal properties
ball_pos = [100, 100]
ball_radius = 10
ball_speed = [0, 0]

# Hole properties
hole_pos = [700, 500]
hole_radius = 20

# Schuifbalk properties
slider_width = 20
slider_height = 200
slider_x = 850
slider_y = 200
slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
slider_knob_radius = 10
slider_knob_y = slider_y  # Startpositie van de knop

# Kracht (afgeleid van de schuifbalk)
min_force = 0
max_force = 20
force = 0

# Invoerveld properties
input_box = pygame.Rect(820, 50, 60, 32)
input_text = ""
active = False
font = pygame.font.Font(None, 32)

# Functie om afstand tussen twee punten te berekenen
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Functie om een raster te tekenen
def draw_grid():
    for x in range(0, 800, 50):  # Verticale lijnen om de 50 pixels
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, 600))
        # Teken x-coördinaten
        if x != 0:  # Voorkom het tekenen van een label op (0, 0)
            text = font.render(str(x), True, BLACK)
            screen.blit(text, (x - 15, 5))
    for y in range(0, 600, 50):  # Horizontale lijnen om de 50 pixels
        pygame.draw.line(screen, GRID_COLOR, (0, y), (800, y))
        # Teken y-coördinaten
        if y != 0:  # Voorkom het tekenen van een label op (0, 0)
            text = font.render(str(y), True, BLACK)
            screen.blit(text, (5, y - 10))

# Game loop
running = True
while running:
    screen.fill(GREEN)  # Achtergrondkleur groen

    # Teken het raster
    draw_grid()

    # Teken de hole
    pygame.draw.circle(screen, BLACK, hole_pos, hole_radius)

    # Teken de bal
    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    # Teken de schuifbalk
    pygame.draw.rect(screen, SLIDER_COLOR, slider_rect)  # Oranje schuifbalk
    pygame.draw.circle(screen, GREEN, (slider_x + slider_width // 2, slider_knob_y), slider_knob_radius)

    # Teken het invoerveld
    pygame.draw.rect(screen, BLACK, input_box, 2)
    text_surface = font.render(input_text, True, BLACK)
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Schuifbalk interactie
            if slider_rect.collidepoint(event.pos):
                slider_knob_y = event.pos[1]
                # Zorg dat de knop binnen de schuifbalk blijft
                if slider_knob_y < slider_y:
                    slider_knob_y = slider_y
                elif slider_knob_y > slider_y + slider_height:
                    slider_knob_y = slider_y + slider_height
                # Bereken de kracht op basis van de positie van de knop
                force = ((slider_knob_y - slider_y) / slider_height) * max_force
            # Invoerveld interactie
            if input_box.collidepoint(event.pos):
                active = True
            else:
                active = False
        elif event.type == pygame.MOUSEMOTION:
            # Schuif de knop als de muis wordt gesleept
            if event.buttons[0] and slider_rect.collidepoint(event.pos):
                slider_knob_y = event.pos[1]
                if slider_knob_y < slider_y:
                    slider_knob_y = slider_y
                elif slider_knob_y > slider_y + slider_height:
                    slider_knob_y = slider_y + slider_height
                force = ((slider_knob_y - slider_y) / slider_height) * max_force
        elif event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    # Verwerk de ingegeven coördinaten
                    try:
                        x, y = map(int, input_text.strip("()").split(","))
                        # Bereken de vector tussen de bal en de ingegeven coördinaten
                        vector = [x - ball_pos[0], y - ball_pos[1]]
                        # Normaliseer de vector en pas de snelheid aan
                        length = math.sqrt(vector[0]**2 + vector[1]**2)
                        if length != 0:
                            ball_speed = [vector[0] / length * force, vector[1] / length * force]
                        input_text = ""  # Reset het invoerveld
                    except ValueError:
                        print("Ongeldige invoer! Gebruik het formaat (x,y)")
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

    # Update bal positie
    ball_pos[0] += ball_speed[0]
    ball_pos[1] += ball_speed[1]

    # Collision detection met de randen
    if ball_pos[0] - ball_radius < 0 or ball_pos[0] + ball_radius > 800:
        ball_speed[0] = -ball_speed[0]
    if ball_pos[1] - ball_radius < 0 or ball_pos[1] + ball_radius > 600:
        ball_speed[1] = -ball_speed[1]

    # Snelheid verminderen (wrijving)
    ball_speed[0] *= 0.98
    ball_speed[1] *= 0.98

    # Controleer of de bal in de hole is
    if distance(ball_pos, hole_pos) < hole_radius - ball_radius:
        print("Gewonnen!")
        running = False

    # Update het scherm
    pygame.display.flip()
    clock.tick(60)

pygame.quit()