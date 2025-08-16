import pygame
import random
import sys

# Configuration constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
BACKGROUND_COLOR = (0, 0, 0)
MATRIX_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
GREEN_COLORS = [(0, 100, 0), (0, 150, 0), (0, 255, 0), (150, 255, 150)]
FONT_SIZE = 18
DROP_SPEED_MIN = 2
DROP_SPEED_MAX = 6
SPAWN_RATE = 0.5
TRAIL_LENGTH_MIN = 8
TRAIL_LENGTH_MAX = 25
FPS = 60

class MatrixDrop:
    def __init__(self, x, speed):
        self.x = x
        self.y = random.randint(-500, -300)
        self.speed = speed
        self.trail_length = random.randint(TRAIL_LENGTH_MIN, TRAIL_LENGTH_MAX)
        self.chars = [random.choice(MATRIX_CHARS) for _ in range(self.trail_length)]
        self.char_timer = 0
        self.char_change_rate = random.randint(5, 15)
    
    def update(self):
        self.y += self.speed
        
        # randomly change characters for glitch effect
        self.char_timer += 1
        if self.char_timer >= self.char_change_rate:
            self.char_timer = 0
            if random.random() < 0.3:
                idx = random.randint(0, self.trail_length - 1)
                self.chars[idx] = random.choice(MATRIX_CHARS)
    
    def draw(self, screen, font):
        for i, char in enumerate(self.chars):
            char_y = self.y + (i * FONT_SIZE)
            if char_y > WINDOW_HEIGHT + FONT_SIZE:
                continue
            if char_y < -FONT_SIZE:
                continue
                
            # calculate brightness based on position in trail
            brightness_factor = max(0, 1 - (i / self.trail_length))
            
            if i == 0:  # head of the trail - brightest
                color = GREEN_COLORS[3]
            elif i < 3:  # near head - bright
                color = GREEN_COLORS[2]
            elif brightness_factor > 0.5:  # middle - medium
                color = GREEN_COLORS[1]
            else:  # tail - dark
                color = GREEN_COLORS[0]
            
            # apply additional dimming for older characters
            if brightness_factor < 0.3:
                color = tuple(int(c * brightness_factor * 3) for c in color)
            
            text_surface = font.render(char, True, color)
            screen.blit(text_surface, (self.x, char_y))
    
    def is_off_screen(self):
        return self.y > WINDOW_HEIGHT + (self.trail_length * FONT_SIZE)

class MatrixSimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Matrix Digital Rain")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.drops = []
        
        # calculate column positions
        self.column_width = FONT_SIZE - 2
        self.num_columns = WINDOW_WIDTH // self.column_width
        
        # initialize some drops
        for _ in range(50):
            x = random.randint(0, self.num_columns - 1) * self.column_width
            speed = random.uniform(DROP_SPEED_MIN, DROP_SPEED_MAX)
            self.drops.append(MatrixDrop(x, speed))
    
    def spawn_drops(self):
        if random.random() < SPAWN_RATE:
            x = random.randint(0, self.num_columns - 1) * self.column_width
            speed = random.uniform(DROP_SPEED_MIN, DROP_SPEED_MAX)
            self.drops.append(MatrixDrop(x, speed))
    
    def update(self):
        # update existing drops
        for drop in self.drops[:]:
            drop.update()
            if drop.is_off_screen():
                self.drops.remove(drop)
        
        # spawn new drops
        self.spawn_drops()
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        for drop in self.drops:
            drop.draw(self.screen, self.font)
        
        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    try:
        simulation = MatrixSimulation()
        simulation.run()
    except pygame.error as e:
        print(f"Pygame error: {e}")
        print("Make sure pygame is installed: pip install pygame")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()