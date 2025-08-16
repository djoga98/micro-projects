import random
import time
import os
import sys

# Configuration constants
MATRIX_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
GREEN_SHADES = ['\033[32m', '\033[92m', '\033[36m']  # dark green, bright green, cyan
RESET_COLOR = '\033[0m'
CLEAR_SCREEN = '\033[2J\033[H'
DROP_SPEED = 0.05
MIN_TRAIL_LENGTH = 5
MAX_TRAIL_LENGTH = 25
SPAWN_PROBABILITY = 0.5
MAX_DROPS = 150

class MatrixDrop:
    def __init__(self, x, y, length):
        self.x = x
        self.y = y
        self.length = length
        self.chars = [random.choice(MATRIX_CHARS) for _ in range(length)]
        self.speed = random.uniform(0.8, 1.5)
        self.char_change_counter = 0  # Dodano za kontrolu
    
    def update(self):
        self.y += self.speed
        
        # ORIGINALNA LOGIKA - samo optimizovano
        self.char_change_counter += 1
        if self.char_change_counter > 5 and random.random() < 0.1:  # Manje CPU load
            idx = random.randint(0, self.length - 1)
            self.chars[idx] = random.choice(MATRIX_CHARS)
            self.char_change_counter = 0

def get_terminal_size():
    try:
        columns, rows = os.get_terminal_size()
        return columns, rows
    except:
        return 80, 24  # fallback dimensions

def hide_cursor():
    print('\033[?25l', end='')

def show_cursor():
    print('\033[?25h', end='')

def draw_matrix(drops, width, height):
    # ORIGINALNA LOGIKA - samo optimizovana
    screen = [[' ' for _ in range(width)] for _ in range(height)]
    colors = [[0 for _ in range(width)] for _ in range(height)]
    
    # render each drop
    for drop in drops:
        for i, char in enumerate(drop.chars):
            y_pos = int(drop.y) - i
            if 0 <= y_pos < height and 0 <= drop.x < width:
                screen[y_pos][drop.x] = char
                # ORIGINALNA FORMULA ZA BRIGHTNESS
                intensity = max(0, 2 - (i / (drop.length / 3)))
                colors[y_pos][drop.x] = min(2, int(intensity))
    
    # OPTIMIZOVAN OUTPUT - jedan print umesto clear + loop
    output_lines = []
    for row_idx, row in enumerate(screen):
        line_parts = []
        current_color = None
        
        for col_idx, char in enumerate(row):
            color_code = GREEN_SHADES[colors[row_idx][col_idx]]
            if color_code != current_color:
                if current_color is not None:
                    line_parts.append(RESET_COLOR)
                line_parts.append(color_code)
                current_color = color_code
            line_parts.append(char)
        
        if current_color is not None:
            line_parts.append(RESET_COLOR)
        
        output_lines.append(''.join(line_parts))
    
    # JEDAN PRINT UMESTO MNOGO - smanjuje treperenje
    print(CLEAR_SCREEN + '\n'.join(output_lines), end='')
    sys.stdout.flush()

def main():
    width, height = get_terminal_size()
    drops = []
    
    # Setup terminal
    hide_cursor()
    
    print("Starting Matrix simulation... Press Ctrl+C to exit")
    time.sleep(2)
    
    try:
        while True:
            # ORIGINALNA SPAWN LOGIKA - samo dodato ograničenje
            if len(drops) < MAX_DROPS and random.random() < SPAWN_PROBABILITY:
                x = random.randint(0, width - 1)
                length = random.randint(MIN_TRAIL_LENGTH, MAX_TRAIL_LENGTH)
                drops.append(MatrixDrop(x, 0, length))
            
            # ORIGINALNA UPDATE LOGIKA
            for drop in drops[:]:
                drop.update()
                # remove drops that have fallen off screen
                if drop.y - drop.length > height:
                    drops.remove(drop)
            
            draw_matrix(drops, width, height)
            time.sleep(DROP_SPEED)
            
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        print(CLEAR_SCREEN)
        print("Matrix simulation terminated.")

if __name__ == "__main__":
    main()