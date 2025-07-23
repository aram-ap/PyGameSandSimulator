import curses
import random
import math
import colorsys
import time

# Constants
DEFAULT_GRAVITY = 1.01
DEFAULT_TERMINAL_VELOCITY = 10
FAST_MOVE_STEP = 5

class SandParticle:
    def __init__(self, color):
        self.color = color
        self.velocity = 0
        self.x_offset = 0

current_color = (194, 178, 128)  # Default sand color
sand_size = 1
use_new_physics = True
gravity = DEFAULT_GRAVITY
terminal_velocity = DEFAULT_TERMINAL_VELOCITY
drawing_mode = False

# Predefined colors for selection (optional in advanced UI)
PREDEFINED_COLORS = {
    '1': (255, 0, 0),    # Red
    '2': (0, 255, 0),    # Green
    '3': (0, 0, 255),    # Blue
    '4': (255, 255, 0),  # Yellow
    '5': (255, 0, 255),  # Magenta
    '6': (0, 255, 255),  # Cyan
    '7': (255, 165, 0),  # Orange
    '8': (128, 0, 128),  # Purple
    '9': (194, 178, 128),# Sand
    '0': (255, 255, 255),# White
    'r': (0, 0, 0)       # Random (placeholder, will generate random)
}

def update_sand_new_physics(sand, COLS, ROWS):
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

def update_sand_old_physics(sand, COLS, ROWS):
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

def add_sand(sand, x, y, color, size, COLS, ROWS):
    for dx in range(-size // 2, size // 2 + 1):
        for dy in range(-size // 2, size // 2 + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and not sand[nx][ny]:
                sand[nx][ny] = SandParticle(color)

def clear_sand(sand, ROWS, COLS):
    sand[:] = [[None for _ in range(ROWS)] for _ in range(COLS)]

def random_color():
    h = random.random()
    s = random.uniform(0.5, 1.0)
    v = 1.0
    return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))

def color_edit_menu(stdscr, current_color, monochrome, color_map, pair_map, next_color_id, next_pair_id):
    r, g, b = current_color
    selected = 0  # 0: R, 1: G, 2: B
    preview_size = 3  # Small preview block

    while True:
        stdscr.clear()
        menu_text = [
            "Color Editor:",
            f"R: {r:3d}  {'<' if selected == 0 else ' '}",
            f"G: {g:3d}  {'<' if selected == 1 else ' '}",
            f"B: {b:3d}  {'<' if selected == 2 else ' '}",
            "Use up/down to select component",
            "+/- to adjust (hold Shift for 10)",
            "p: Pick predefined, r: Random",
            "Enter: Save, q: Cancel",
            "Preview:"
        ]
        for i, line in enumerate(menu_text):
            stdscr.addstr(i, 0, line)

        # Draw color preview
        if not monochrome:
            rgb = (r, g, b)
            if rgb not in pair_map:
                if next_color_id < curses.COLORS:
                    curses.init_color(next_color_id, r * 1000 // 255, g * 1000 // 255, b * 1000 // 255)
                    curses.init_pair(next_pair_id, next_color_id, next_color_id)  # Foreground and background same for solid block
                    color_map[rgb] = next_color_id
                    pair_map[rgb] = next_pair_id
                    next_color_id += 1
                    next_pair_id += 1
            pair = curses.color_pair(pair_map.get(rgb, 0))
            for py in range(preview_size):
                for px in range(preview_size * 2):  # Wider for better visibility
                    stdscr.addch(len(menu_text) + py, px, '█', pair)
        else:
            stdscr.addstr(len(menu_text), 0, "[Color Preview Not Available]")

        stdscr.refresh()

        key = stdscr.getch()
        if key == -1:
            continue
        if 0 <= key < 256:
            key_char = chr(key).lower()
            is_upper = chr(key).isupper()
        else:
            key_char = curses.keyname(key).decode('utf-8').lower()
            is_upper = False

        step = 10 if is_upper else 1

        if key == curses.KEY_UP or key_char == 'k':
            selected = (selected - 1) % 3
        elif key == curses.KEY_DOWN or key_char == 'j':
            selected = (selected + 1) % 3
        elif key_char == '+' or key == curses.KEY_PPAGE:
            if selected == 0:
                r = min(255, r + step)
            elif selected == 1:
                g = min(255, g + step)
            elif selected == 2:
                b = min(255, b + step)
        elif key_char == '-' or key == curses.KEY_NPAGE:
            if selected == 0:
                r = max(0, r - step)
            elif selected == 1:
                g = max(0, g - step)
            elif selected == 2:
                b = max(0, b - step)
        elif key_char == 'p':
            # Simple predefined selection
            stdscr.addstr(len(menu_text) + preview_size + 1, 0, "Enter number (1-0) or r for random:")
            stdscr.refresh()
            pkey = stdscr.getch()
            if 0 <= pkey < 256:
                pchar = chr(pkey).lower()
                if pchar in PREDEFINED_COLORS:
                    if pchar == 'r':
                        r, g, b = random_color()
                    else:
                        r, g, b = PREDEFINED_COLORS[pchar]
        elif key_char == 'r':
            r, g, b = random_color()
        elif key == ord('\n') or key_char == 'enter':
            return (r, g, b)
        elif key_char == 'q':
            return None

def main(stdscr):
    global current_color, sand_size, use_new_physics, gravity, terminal_velocity, drawing_mode

    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input

    if not curses.has_colors() or not curses.can_change_color():
        stdscr.addstr(0, 0, "Your terminal does not support colors. Using monochrome mode.")
        stdscr.refresh()
        time.sleep(2)
        monochrome = True
    else:
        monochrome = False
        curses.start_color()
        # Initialize maps for dynamic colors
        color_map = {}  # rgb_tuple: color_id
        pair_map = {}   # rgb_tuple: pair_id
        next_color_id = 8  # Start after standard 0-7
        next_pair_id = 1

    # Get terminal size
    max_y, max_x = stdscr.getmaxyx()
    if max_y < 10 or max_x < 40:
        stdscr.addstr(0, 0, "Terminal too small. Please resize to at least 40x10.")
        stdscr.refresh()
        time.sleep(5)
        return

    ROWS = max_y - 1  # Leave one line for info
    COLS = max_x

    # Create sand grid
    sand = [[None for _ in range(ROWS)] for _ in range(COLS)]

    # Cursor for adding sand
    cursor_x = COLS // 2
    cursor_y = ROWS // 2

    running = True
    space_pressed = False  # For hold detection

    while running:
        space_pressed = False  # Reset per frame

        # Handle input
        try:
            while True:
                key = stdscr.getch()
                if key == -1:
                    break
                if key == curses.KEY_RESIZE:
                    max_y, max_x = stdscr.getmaxyx()
                    if max_y < 10 or max_x < 40:
                        stdscr.clear()
                        stdscr.addstr(0, 0, "Terminal too small.")
                        stdscr.refresh()
                        continue
                    old_ROWS = ROWS
                    old_COLS = COLS
                    ROWS = max_y - 1
                    COLS = max_x
                    old_sand = sand
                    sand = [[None for _ in range(ROWS)] for _ in range(COLS)]
                    copy_rows = min(ROWS, old_ROWS)
                    copy_cols = min(COLS, old_COLS)
                    for x in range(copy_cols):
                        for y in range(copy_rows):
                            sand[x][y] = old_sand[x][y]
                    cursor_x = min(cursor_x, COLS - 1)
                    cursor_y = min(cursor_y, ROWS - 1)
                    stdscr.clear()
                    continue

                if 0 <= key < 256:
                    key_char = chr(key).lower()
                    is_upper = chr(key).isupper()
                else:
                    key_char = curses.keyname(key).decode('utf-8').lower()
                    is_upper = False

                if key_char == 'q':
                    running = False
                elif key_char == 'c':
                    clear_sand(sand, ROWS, COLS)
                elif key_char == 'p':
                    use_new_physics = not use_new_physics
                elif key_char == '+':
                    sand_size = min(sand_size + 1, 20)
                elif key_char == '-':
                    sand_size = max(sand_size - 1, 1)
                elif key_char == 'g':
                    if is_upper:
                        gravity = max(gravity - 0.1, 0.0)
                    else:
                        gravity = min(gravity + 0.1, 2.0)
                elif key_char == 't':
                    if is_upper:
                        terminal_velocity = max(terminal_velocity - 1, 1)
                    else:
                        terminal_velocity = min(terminal_velocity + 1, 20)
                elif key_char == 'r':
                    current_color = random_color()
                elif key_char == 's':
                    new_color = color_edit_menu(stdscr, current_color, monochrome, color_map, pair_map, next_color_id, next_pair_id)
                    if new_color:
                        current_color = new_color
                    # Redraw the main screen after menu
                    stdscr.clear()
                    stdscr.refresh()
                elif key == curses.KEY_LEFT or key_char == 'h':
                    step = FAST_MOVE_STEP if is_upper else 1
                    cursor_x = max(0, cursor_x - step)
                elif key == curses.KEY_RIGHT or key_char == 'l':
                    step = FAST_MOVE_STEP if is_upper else 1
                    cursor_x = min(COLS - 1, cursor_x + step)
                elif key == curses.KEY_UP or key_char == 'k':
                    step = FAST_MOVE_STEP if is_upper else 1
                    cursor_y = max(0, cursor_y - step)
                elif key == curses.KEY_DOWN or key_char == 'j':
                    step = FAST_MOVE_STEP if is_upper else 1
                    cursor_y = min(ROWS - 1, cursor_y + step)
                elif key == ord(' '):
                    space_pressed = True
        except Exception as e:
            # In case of any input error, continue
            pass

        # Add sand if space is pressed/held (adds every frame if held due to repeat)
        if space_pressed:
            add_sand(sand, cursor_x, cursor_y, current_color, sand_size, COLS, ROWS)

        # Update simulation
        if use_new_physics:
            update_sand_new_physics(sand, COLS, ROWS)
        else:
            update_sand_old_physics(sand, COLS, ROWS)

        # Draw grid with improved sand rendering (use '•' for particle look)
        stdscr.clear()
        for y in range(ROWS):
            for x in range(COLS):
                if x >= COLS or y >= ROWS:  # Safety check
                    continue
                if sand[x][y]:
                    ch = '•'  # Better looking particle (bullet point)
                    if monochrome:
                        stdscr.addch(y, x, ch)
                    else:
                        rgb = sand[x][y].color
                        if rgb not in pair_map:
                            if next_color_id >= curses.COLORS:
                                # Too many colors, fallback to default
                                stdscr.addch(y, x, ch)
                                continue
                            r, g, b = rgb
                            curses.init_color(next_color_id, r * 1000 // 255, g * 1000 // 255, b * 1000 // 255)
                            curses.init_pair(next_pair_id, next_color_id, 0)  # Pair with black background
                            color_map[rgb] = next_color_id
                            pair_map[rgb] = next_pair_id
                            next_color_id += 1
                            next_pair_id += 1
                        pair = curses.color_pair(pair_map[rgb])
                        stdscr.addch(y, x, ch, pair)

        # Draw brush cursor (highlight the area)
        half_size = sand_size // 2
        for dy in range(-half_size, half_size + 1):
            for dx in range(-half_size, half_size + 1):
                bx = cursor_x + dx
                by = cursor_y + dy
                if 0 <= bx < COLS and 0 <= by < ROWS:
                    # Get current char and attr
                    current_ch = stdscr.inch(by, bx) & 0xff
                    current_attr = stdscr.inch(by, bx) & curses.A_ATTRIBUTES
                    if current_ch == ord(' '):  # Empty space
                        stdscr.addch(by, bx, '.', curses.A_DIM | current_attr)  # Use dim dot for empty
                    else:
                        stdscr.addch(by, bx, current_ch, curses.A_REVERSE | current_attr)  # Reverse for occupied

        # Draw info
        info = f"Size: {sand_size} Physics: {'New' if use_new_physics else 'Old'} Grav: {gravity:.2f} TV: {terminal_velocity} | Keys: hjkl/arrows move (Shift for fast), hold space to draw, +/- size, g/G grav, t/T tv, p toggle phys, r random color, s edit color, c clear, q quit"
        if ROWS < max_y and 0 < COLS:  # Safety
            stdscr.addstr(ROWS, 0, info[:COLS-1])

        stdscr.refresh()

        time.sleep(1 / 120)  # Approximate original frame rate

if __name__ == "__main__":
    curses.wrapper(main)

