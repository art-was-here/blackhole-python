import os
import time
import math
import random

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_size():
    try:
        size = os.get_terminal_size()
        height = size.lines - 5
        width = size.columns - 2
        if width > 2 * height:
            width = 2 * height
        elif width < 2 * height:
            height = width // 2
        width = max(width, 20)
        height = max(height, 10)
        return width, height
    except OSError:
        return 20, 10

def create_background_grid(width, height):
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    background_chars = ['.', ',', '*']
    for y in range(height):
        for x in range(width):
            if random.random() < 0.1:
                grid[y][x] = random.choice(background_chars)
    return grid

def create_grid(width, height, background_grid, shift_offset, shining_stars, frame_count):
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            src_x = (x - shift_offset) % width
            char = background_grid[y][src_x]
            if char != ' ':
                if (y, x) in shining_stars:
                    grid[y][x] = f'\033[38;5;251m{char}\033[0m'
                else:
                    grid[y][x] = f'\033[38;5;237m{char}\033[0m'
    num_new_shines = random.randint(1, 2)
    for _ in range(num_new_shines):
        for _ in range(10):
            y = random.randint(0, height - 1)
            x = random.randint(0, width - 1)
            src_x = (x - shift_offset) % width
            if background_grid[y][src_x] != ' ' and (y, x) not in shining_stars:
                shining_stars[(y, x)] = 3
                break
    expired = []
    for pos in shining_stars:
        shining_stars[pos] -= 1
        if shining_stars[pos] <= 0:
            expired.append(pos)
    for pos in expired:
        del shining_stars[pos]
    return grid

def place_black_hole(grid, center_x, center_y, width):
    if width < 65:
        if (center_y >= 0 and center_y < len(grid) and
            center_x - 1 >= 0 and center_x + 1 < len(grid[0])):
            grid[center_y][center_x - 1] = '\033[0m('
            grid[center_y][center_x] = '\033[0mX'
            grid[center_y][center_x + 1] = '\033[0m)'
    elif width > 95:
        if (center_y - 3 >= 0 and center_y + 2 < len(grid) and
            center_x - 10 >= 0 and center_x + 10 < len(grid[0])):
            for i in range(-3, 3):
                grid[center_y - 3][center_x + i] = '\033[0m+'
            for i in [-4, -3, -2, 2, 3, 4]:
                grid[center_y - 2][center_x + i] = '\033[0m+'
            for i in [-5, -4, -3, 3, 4, 5]:
                grid[center_y - 1][center_x + i] = '\033[0m+'
            grid[center_y][center_x - 10] = '\033[0m/'
            for i in [-9, -8, -7, -6, -2, -1, 0, 1, 2, 6, 7, 8, 9]:
                grid[center_y][center_x + i] = '\033[0m-'
            for i in [-5, -4, -3, 3, 4, 5]:
                grid[center_y][center_x + i] = '\033[0m+'
            grid[center_y][center_x + 10] = '\033[0m/'
            for i in [-5, -4, -3, 3, 4, 5]:
                grid[center_y + 1][center_x + i] = '\033[0m+'
            for i in range(-3, 3):
                grid[center_y + 2][center_x + i] = '\033[0m+'
    else:
        if (center_y - 1 >= 0 and center_y + 1 < len(grid) and
            center_x - 4 >= 0 and center_x + 4 < len(grid[0])):
            grid[center_y - 1][center_x - 1] = '\033[0m@'
            grid[center_y - 1][center_x] = '\033[0m@'
            grid[center_y - 1][center_x + 1] = '\033[0m@'
            grid[center_y][center_x - 4] = '\033[0m-'
            grid[center_y][center_x - 3] = '\033[0m-'
            grid[center_y][center_x - 2] = '\033[0m@'
            grid[center_y][center_x - 1] = '\033[0m-'
            grid[center_y][center_x] = '\033[0mx'
            grid[center_y][center_x + 1] = '\033[0m-'
            grid[center_y][center_x + 2] = '\033[0m@'
            grid[center_y][center_x + 3] = '\033[0m-'
            grid[center_y][center_x + 4] = '\033[0m-'
            grid[center_y + 1][center_x - 1] = '\033[0m@'
            grid[center_y + 1][center_x] = '\033[0m@'
            grid[center_y + 1][center_x + 1] = '\033[0m@'

def place_star(grid, x, y, width):
    x, y = int(x), int(y)
    if width > 85:
        if (y >= 0 and y < len(grid) and
            x - 1 >= 0 and x + 1 < len(grid[0])):
            grid[y][x - 1] = '\033[0m('
            grid[y][x] = '\033[0m@'
            grid[y][x + 1] = '\033[0m)'
    else:
        if (y >= 0 and y < len(grid) and
            x >= 0 and x < len(grid[0])):
            grid[y][x] = '\033[0m@'

def calculate_acceleration(r, mass=5e6, G=0.02):
    return G * mass / (r ** 2 + 0.5)

def simulate_orbits(num_stars, steps, delay=0.033):
    width, height = get_terminal_size()
    background_grid = create_background_grid(width, height)
    center_x, center_y = width // 2, height // 2
    original_delay = 0.1
    base_dt = 0.01
    physics_dt = base_dt * (delay / original_delay)
    stars = []
    for _ in range(num_stars):
        radius = random.uniform(10, min(width, height) / 2.5) if width > 85 else random.uniform(7, min(width, height) / 3)
        angle = random.uniform(0, 2 * math.pi)
        v = math.sqrt(calculate_acceleration(radius) * radius) * random.uniform(0.8, 1.0)
        vx = -v * math.sin(angle)
        vy = v * math.cos(angle)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        stars.append({
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'mass': random.uniform(100, 1000),
            'active': True,
            'prev_x': x,
            'prev_y': y
        })
    frame_count = 0
    shift_counter = 0
    shift_offset = 0
    shining_stars = {}
    max_steps = steps if steps > 0 else float('inf')
    while frame_count < max_steps:
        new_width, new_height = get_terminal_size()
        if new_width != width or new_height != height:
            old_center_x, old_center_y = center_x, center_y
            width, height = new_width, new_height
            center_x, center_y = width // 2, height // 2
            background_grid = create_background_grid(width, height)
            shining_stars.clear()
            dx = center_x - old_center_x
            dy = center_y - old_center_y
            for star in stars:
                if star['active']:
                    star['x'] += dx
                    star['y'] += dy
                    star['prev_x'] += dx
                    star['prev_y'] += dy
        active_stars = [s for s in stars if s['active']]
        for i, star in enumerate(active_stars):
            if not star['active']:
                continue
            star['prev_x'] = star['x']
            star['prev_y'] = star['y']
            dx = star['x'] - center_x
            dy = star['y'] - center_y
            r = math.sqrt(dx**2 + dy**2)
            if r < 3 or star['x'] < -10 or star['x'] > width + 10 or star['y'] < -10 or star['y'] > height + 10:
                star['active'] = False
                continue
            if r > 0.5:
                acc = calculate_acceleration(r)
                ax = -acc * dx / r
                ay = -acc * dy / r
            else:
                ax, ay = 0, 0
            if num_stars > 50:
                sampled_stars = random.sample(active_stars, min(10, len(active_stars))) if len(active_stars) > 10 else active_stars
            else:
                sampled_stars = active_stars
            for j, other_star in enumerate(sampled_stars):
                if i != j and other_star['active']:
                    dx_star = star['x'] - other_star['x']
                    dy_star = star['y'] - other_star['y']
                    dist = math.sqrt(dx_star**2 + dy_star**2 + 0.5)
                    if dist > 0.5:
                        acc_star = 0.05 * other_star['mass'] / (dist ** 2)
                        ax -= acc_star * dx_star / dist
                        ay -= acc_star * dy_star / dist
                        rel_vx = star['vx'] - other_star['vx']
                        rel_vy = star['vy'] - other_star['vy']
                        tangent_ax = 0.01 * other_star['mass'] * rel_vy / (dist ** 2 + 0.5)
                        tangent_ay = -0.01 * other_star['mass'] * rel_vx / (dist ** 2 + 0.5)
                        ax += tangent_ax
                        ay += tangent_ay
            star['vx'] += ax * physics_dt
            star['vy'] += ay * physics_dt
            star['x'] += star['vx'] * physics_dt
            star['y'] += star['vy'] * physics_dt
            speed = math.sqrt(star['vx']**2 + star['vy']**2)
            escape_speed = math.sqrt(2 * calculate_acceleration(r) * r)
            if speed > escape_speed:
                star['active'] = False
        interpolation_factor = min(1.0, physics_dt / delay)
        grid = create_grid(width, height, background_grid, shift_offset, shining_stars, frame_count)
        place_black_hole(grid, center_x, center_y, width)
        if shift_counter >= 5:
            shift_offset = (shift_offset + 1) % width
            shift_counter = 0
            for y in range(height):
                background_grid[y][shift_offset] = random.choice(['.', ',', '*']) if random.random() < 0.1 else ' '
        shift_counter += 1
        for star in active_stars:
            if star['active']:
                render_x = star['prev_x'] + (star['x'] - star['prev_x']) * interpolation_factor
                render_y = star['prev_y'] + (star['y'] - star['prev_y']) * interpolation_factor
                place_star(grid, render_x, render_y, width)
        clear_screen()
        for row in grid:
            print(''.join(row), flush=False)
        print(f"\nStars: {len(active_stars)}/{num_stars} | Frame: {frame_count + 1}{'/' + str(steps) if steps > 0 else ''} | Press Ctrl+C to stop", flush=True)
        frame_count += 1
        time.sleep(delay)
        if len(active_stars) == 0 and steps == 0:
            print(f"\nAll stars gone! Total frames: {frame_count}")
            break
    return frame_count

def main():
    try:
        num_stars_input = input("Enter the number of stars to orbit the black hole (default 0): ").strip()
        num_stars = int(num_stars_input) if num_stars_input else 0
        steps_input = input("Enter the number of simulation steps (default 0 for indefinite): ").strip()
        steps = int(steps_input) if steps_input else 0
        if num_stars < 0 or steps < 0:
            print("Please enter non-negative numbers.")
            return
        frame_count = simulate_orbits(num_stars, steps)
        if steps > 0:
            print(f"\nSimulation completed. Total frames: {frame_count}")
    except ValueError:
        print("Please enter valid integers or leave blank for defaults.")
    except KeyboardInterrupt:
        print("\nSimulation stopped.")

if __name__ == "__main__":
    main()