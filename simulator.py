import pygame
import pygame_gui
import random
import math
import colorsys

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 1000
HEIGHT = 600
CELL_SIZE = 4
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sand Simulation")

# Create a 2D array to represent the sand
sand = [[None for _ in range(ROWS)] for _ in range(COLS)]

# UI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Create a surface for the color wheel
wheel_size = 200
wheel_surface = pygame.Surface((wheel_size, wheel_size), pygame.SRCALPHA)

# Draw the color wheel
for x in range(wheel_size):
    for y in range(wheel_size):
        dx, dy = x - wheel_size // 2, y - wheel_size // 2
        distance = math.sqrt(dx**2 + dy**2)
        if distance <= wheel_size // 2:
            angle = math.atan2(dy, dx)
            hue = (angle + math.pi) / (2 * math.pi)
            saturation = min(distance / (wheel_size // 2), 1.0)
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, saturation, 1.0)]
            wheel_surface.set_at((x, y), (r, g, b))

# Color wheel
color_wheel = pygame_gui.elements.UIImage(
    relative_rect=pygame.Rect((WIDTH - 220, 10), (200, 200)),
    image_surface=wheel_surface,
    manager=manager
)

# Sand size slider
sand_size_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((WIDTH - 220, 220), (200, 20)),
    start_value=1,
    value_range=(1, 10),
    manager=manager
)

# Sand size label
sand_size_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((WIDTH - 220, 250), (200, 20)),
    text="Sand Size: 1",
    manager=manager
)

# Clear sand button
clear_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - 220, 280), (200, 30)),
    text="Clear Sand",
    manager=manager
)

current_color = (194, 178, 128)  # Default sand color
sand_size = 1

def update_sand():
    for x in range(COLS):
        for y in range(ROWS - 1, -1, -1):
            if sand[x][y]:
                if y < ROWS - 1 and not sand[x][y + 1]:
                    # Fall down
                    sand[x][y + 1] = sand[x][y]
                    sand[x][y] = None
                elif y < ROWS - 1:
                    # Try to fall diagonally
                    left = x > 0 and not sand[x - 1][y + 1]
                    right = x < COLS - 1 and not sand[x + 1][y + 1]
                    if left and right:
                        # Choose randomly between left and right
                        direction = random.choice([-1, 1])
                        sand[x + direction][y + 1] = sand[x][y]
                        sand[x][y] = None
                    elif left:
                        sand[x - 1][y + 1] = sand[x][y]
                        sand[x][y] = None
                    elif right:
                        sand[x + 1][y + 1] = sand[x][y]
                        sand[x][y] = None

def draw_sand():
    for x in range(COLS):
        for y in range(ROWS):
            if sand[x][y]:
                pygame.draw.rect(screen, sand[x][y], (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def add_sand(x, y, color, size):
    for dx in range(-size // 2, size // 2 + 1):
        for dy in range(-size // 2, size // 2 + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and not sand[nx][ny]:
                sand[nx][ny] = color

def get_color_from_wheel(pos):
    wheel_pos = pos[0] - (WIDTH - 220), pos[1] - 10
    if 0 <= wheel_pos[0] < wheel_size and 0 <= wheel_pos[1] < wheel_size:
        return wheel_surface.get_at(wheel_pos)
    return None

def clear_sand():
    global sand
    sand = [[None for _ in range(ROWS)] for _ in range(COLS)]

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                color = get_color_from_wheel(event.pos)
                if color:
                    current_color = color

        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == sand_size_slider:
                sand_size = int(event.value)
                sand_size_label.set_text(f"Sand Size: {sand_size}")

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == clear_button:
                clear_sand()

        manager.process_events(event)

    # Continuously add sand while left mouse button is pressed
    if pygame.mouse.get_pressed()[0]:  # Left mouse button
        x, y = pygame.mouse.get_pos()
        if x < WIDTH - 220:  # Check if not clicking on UI
            grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
            add_sand(grid_x, grid_y, current_color, sand_size)

    manager.update(time_delta)

    update_sand()

    screen.fill(BLACK)
    draw_sand()
    manager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()

