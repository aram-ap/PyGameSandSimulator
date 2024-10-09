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
DEFAULT_GRAVITY = 0.5
DEFAULT_TERMINAL_VELOCITY = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sand Simulation")

class SandParticle:
    def __init__(self, color):
        self.color = color
        self.velocity = 0
        self.x_offset = 0

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

# Physics toggle button
physics_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - 220, 320), (200, 30)),
    text="New Physics: ON",
    manager=manager
)

# Gravity slider
gravity_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((WIDTH - 220, 360), (200, 20)),
    start_value=DEFAULT_GRAVITY,
    value_range=(0, 2),
    manager=manager
)

# Gravity label
gravity_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((WIDTH - 220, 390), (200, 20)),
    text=f"Gravity: {DEFAULT_GRAVITY:.2f}",
    manager=manager
)

# Terminal velocity slider
terminal_velocity_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((WIDTH - 220, 420), (200, 20)),
    start_value=DEFAULT_TERMINAL_VELOCITY,
    value_range=(1, 20),
    manager=manager
)

# Terminal velocity label
terminal_velocity_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((WIDTH - 220, 450), (200, 20)),
    text=f"Terminal Velocity: {DEFAULT_TERMINAL_VELOCITY:.2f}",
    manager=manager
)

current_color = (194, 178, 128)  # Default sand color
sand_size = 1
use_new_physics = True
gravity = DEFAULT_GRAVITY
terminal_velocity = DEFAULT_TERMINAL_VELOCITY

def update_sand_new_physics():
    for x in range(COLS):
        for y in range(ROWS - 1, -1, -1):
            if sand[x][y]:
                particle = sand[x][y]

                # Apply acceleration
                particle.velocity = min(particle.velocity + gravity, terminal_velocity)

                # Calculate new position
                new_y = y + particle.velocity

                # Handle sub-pixel movement
                particle.x_offset += random.uniform(-0.5, 0.5)
                new_x = x + int(particle.x_offset)
                particle.x_offset -= int(particle.x_offset)

                # Keep particles within bounds
                new_x = max(0, min(new_x, COLS - 1))
                new_y = min(new_y, ROWS - 1)

                if new_y == y:
                    continue  # Particle hasn't moved to a new cell

                # Check if space below is empty
                if not sand[new_x][int(new_y)]:
                    sand[x][y] = None
                    sand[new_x][int(new_y)] = particle
                else:
                    # Try to move diagonally
                    left = new_x > 0 and not sand[new_x - 1][int(new_y)]
                    right = new_x < COLS - 1 and not sand[new_x + 1][int(new_y)]
                    if left and right:
                        direction = random.choice([-1, 1])
                        sand[x][y] = None
                        sand[new_x + direction][int(new_y)] = particle
                    elif left:
                        sand[x][y] = None
                        sand[new_x - 1][int(new_y)] = particle
                    elif right:
                        sand[x][y] = None
                        sand[new_x + 1][int(new_y)] = particle
                    else:
                        # Particle can't move, reset velocity
                        particle.velocity = 0

def update_sand_old_physics():
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
                pygame.draw.rect(screen, sand[x][y].color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def add_sand(x, y, color, size):
    for dx in range(-size // 2, size // 2 + 1):
        for dy in range(-size // 2, size // 2 + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and not sand[nx][ny]:
                sand[nx][ny] = SandParticle(color)

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
            elif event.ui_element == gravity_slider:
                gravity = event.value
                gravity_label.set_text(f"Gravity: {gravity:.2f}")
            elif event.ui_element == terminal_velocity_slider:
                terminal_velocity = event.value
                terminal_velocity_label.set_text(f"Terminal Velocity: {terminal_velocity:.2f}")

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == clear_button:
                clear_sand()
            elif event.ui_element == physics_button:
                use_new_physics = not use_new_physics
                physics_button.set_text(f"New Physics: {'ON' if use_new_physics else 'OFF'}")

        manager.process_events(event)

    # Continuously add sand while left mouse button is pressed
    if pygame.mouse.get_pressed()[0]:  # Left mouse button
        x, y = pygame.mouse.get_pos()
        if x < WIDTH - 220:  # Check if not clicking on UI
            grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
            add_sand(grid_x, grid_y, current_color, sand_size)

    manager.update(time_delta)

    if use_new_physics:
        update_sand_new_physics()
    else:
        update_sand_old_physics()

    screen.fill(BLACK)
    draw_sand()
    manager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()

