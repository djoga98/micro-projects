import pygame
import numpy as np
from PIL import Image
import random
import math
import sys
import os
from tkinter import filedialog
import tkinter as tk

# Configuration constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 804
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 300
MAX_WINDOW_WIDTH = 1920
MAX_WINDOW_HEIGHT = 1080
BACKGROUND_COLOR = (0, 0, 0)
PARTICLE_COLOR = (255, 255, 255)
PARTICLE_SIZE = 2
DETAIL = 16
PARTICLE_COUNT = 3000
MAX_SPEED = 4
TRAIL_FADE = 0.09
FPS = 60

# 3D Effect constants
DEPTH_OFFSET = 3
RED_CHANNEL = (255, 0, 0)
BLUE_CHANNEL = (0, 0, 255)
ENABLE_3D = False

# Window positioning constants
class WindowPosition:
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"
    TOP_CENTER = "top_center"
    BOTTOM_CENTER = "bottom_center"
    LEFT_CENTER = "left_center"
    RIGHT_CENTER = "right_center"

class Particle:
    """Particle class with trail history"""
    __slots__ = ['x', 'y', 'prev_x', 'prev_y', 'speed', 'velocity_x', 'velocity_y', 
                 'alpha', 'depth', 'trail_history', 'max_trail_length', 'window_width', 'window_height']
    
    def __init__(self, x=None, y=None, window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT):
        self.window_width = window_width
        self.window_height = window_height
        self.x = x if x is not None else random.uniform(0, self.window_width)
        self.y = y if y is not None else random.uniform(0, self.window_height)
        self.prev_x = self.x
        self.prev_y = self.y
        self.speed = 0
        self.velocity_x = random.uniform(-0.5, 0.5)
        self.velocity_y = random.uniform(-0.5, 0.5)
        self.alpha = random.uniform(0.3, 1.0)
        self.depth = random.uniform(0.0, 1.0)
        self.trail_history = []
        self.max_trail_length = 20

    def update(self, brightness_grid, grid_width, grid_height):
        # Store previous position for trail with alpha info
        self.trail_history.append((self.x, self.y, self.alpha, self.depth))
        if len(self.trail_history) > self.max_trail_length:
            self.trail_history.pop(0)

        # Get brightness value from grid with bounds checking
        if brightness_grid is not None and grid_width > 0 and grid_height > 0:
            grid_x = max(0, min(int(self.x / DETAIL), grid_width - 1))
            grid_y = max(0, min(int(self.y / DETAIL), grid_height - 1))
            brightness = brightness_grid[grid_y][grid_x]
        else:
            brightness = 0.5

        # Calculate speed based on brightness
        self.speed = brightness * MAX_SPEED

        # Update position
        self.prev_x, self.prev_y = self.x, self.y
        self.x += (1 - brightness) * 2.5 + self.velocity_x
        self.y += self.velocity_y * 0.3

        # Wrap around screen
        if self.x > self.window_width:
            self.x = 0
            self.y = random.uniform(0, self.window_height)
            self.trail_history.clear()
        elif self.x < 0:
            self.x = self.window_width
            self.trail_history.clear()

        if self.y > self.window_height:
            self.y = 0
            self.trail_history.clear()
        elif self.y < 0:
            self.y = self.window_height
            self.trail_history.clear()

        # Update alpha and depth
        self.alpha = min(1.0, brightness * 0.9 + 0.1)
        self.depth = brightness

    def draw(self, screen, enable_3d=False):
        if enable_3d:
            self._draw_3d(screen)
        else:
            self._draw_normal(screen)

    def _draw_normal(self, screen):
        if self.alpha <= 0:
            return
        color = (*PARTICLE_COLOR, max(0, min(255, int(self.alpha * 255))))
        surf = pygame.Surface((PARTICLE_SIZE * 2, PARTICLE_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (PARTICLE_SIZE, PARTICLE_SIZE), PARTICLE_SIZE)
        screen.blit(surf, (int(self.x - PARTICLE_SIZE), int(self.y - PARTICLE_SIZE)))

    def _draw_3d(self, screen):
        if self.alpha <= 0:
            return
        offset = int(DEPTH_OFFSET * self.depth)
        
        # Red channel
        red_surf = pygame.Surface((PARTICLE_SIZE * 2, PARTICLE_SIZE * 2), pygame.SRCALPHA)
        red_color = (*RED_CHANNEL, max(0, min(255, int(self.alpha * 180))))
        pygame.draw.circle(red_surf, red_color, (PARTICLE_SIZE, PARTICLE_SIZE), PARTICLE_SIZE)
        screen.blit(red_surf, (int(self.x - PARTICLE_SIZE - offset), int(self.y - PARTICLE_SIZE)))
        
        # Blue channel
        blue_surf = pygame.Surface((PARTICLE_SIZE * 2, PARTICLE_SIZE * 2), pygame.SRCALPHA)
        blue_color = (*BLUE_CHANNEL, max(0, min(255, int(self.alpha * 180))))
        pygame.draw.circle(blue_surf, blue_color, (PARTICLE_SIZE, PARTICLE_SIZE), PARTICLE_SIZE)
        screen.blit(blue_surf, (int(self.x - PARTICLE_SIZE + offset), int(self.y - PARTICLE_SIZE)))

    def draw_trail(self, screen, enable_3d=False):
        """Draw trail with fade effect"""
        if len(self.trail_history) < 2:
            return
            
        for i, (old_x, old_y, old_alpha, old_depth) in enumerate(self.trail_history):
            trail_progress = (i + 1) / len(self.trail_history)
            trail_alpha = old_alpha * trail_progress * 0.6
            trail_size = max(1, int(PARTICLE_SIZE * (0.5 + trail_progress * 0.5)))
            
            if trail_alpha <= 0.01:
                continue
                
            if enable_3d:
                offset = int(DEPTH_OFFSET * old_depth * trail_progress)
                
                # Red trail
                red_surf = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                red_color = (*RED_CHANNEL, max(0, min(255, int(trail_alpha * 120))))
                pygame.draw.circle(red_surf, red_color, (trail_size, trail_size), trail_size)
                screen.blit(red_surf, (int(old_x - trail_size - offset), int(old_y - trail_size)))
                
                # Blue trail
                blue_surf = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                blue_color = (*BLUE_CHANNEL, max(0, min(255, int(trail_alpha * 120))))
                pygame.draw.circle(blue_surf, blue_color, (trail_size, trail_size), trail_size)
                screen.blit(blue_surf, (int(old_x - trail_size + offset), int(old_y - trail_size)))
            else:
                trail_surf = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                trail_color = (*PARTICLE_COLOR, max(0, min(255, int(trail_alpha * 255))))
                pygame.draw.circle(trail_surf, trail_color, (trail_size, trail_size), trail_size)
                screen.blit(trail_surf, (int(old_x - trail_size), int(old_y - trail_size)))


class WindowPositioner:
    """Utility class for smart window positioning"""
    
    @staticmethod
    def get_monitor_info():
        """Get monitor information - this gets PRIMARY monitor only"""
        info = pygame.display.Info()
        return info.current_w, info.current_h
    
    @staticmethod
    def get_total_desktop_size():
        """Get total desktop size across all monitors"""
        try:
            # Try to get from tkinter for multi-monitor support
            root = tk.Tk()
            root.withdraw()
            
            # Get virtual screen dimensions
            total_width = root.winfo_vrootwidth()
            total_height = root.winfo_vrootheight()
            
            root.destroy()
            return total_width, total_height
        except:
            # Fallback to pygame
            info = pygame.display.Info()
            return info.current_w, info.current_h
    
    @staticmethod
    def detect_monitors():
        """Detect number of monitors and their arrangement"""
        try:
            root = tk.Tk()
            root.withdraw()
            
            # Get primary monitor size
            primary_width = root.winfo_screenwidth()
            primary_height = root.winfo_screenheight()
            
            # Get total virtual screen size
            virtual_width = root.winfo_vrootwidth()
            virtual_height = root.winfo_vrootheight()
            
            root.destroy()
            
            # Estimate number of monitors (assumes horizontal arrangement)
            num_monitors = max(1, virtual_width // primary_width)
            
            print(f"Detected monitors: {num_monitors}")
            print(f"Primary monitor: {primary_width}x{primary_height}")
            print(f"Virtual desktop: {virtual_width}x{virtual_height}")
            
            return num_monitors, primary_width, primary_height, virtual_width, virtual_height
            
        except Exception as e:
            print(f"Monitor detection failed: {e}")
            return 1, 1920, 1080, 1920, 1080
    
    @staticmethod
    def calculate_position(position, window_width, window_height, monitor_index=0, offset_x=0, offset_y=0):
        """Calculate window position based on specified location"""
        # Detect monitor configuration
        num_monitors, primary_width, primary_height, virtual_width, virtual_height = WindowPositioner.detect_monitors()
        
        # Calculate monitor offset (assumes horizontal arrangement)
        monitor_offset_x = primary_width * monitor_index
        monitor_offset_y = 0
        
        # Use primary monitor dimensions for position calculation
        single_monitor_width = primary_width
        single_monitor_height = primary_height
        
        # Calculate base position within the target monitor
        positions = {
            WindowPosition.TOP_LEFT: (0, 0),
            WindowPosition.TOP_RIGHT: (single_monitor_width - window_width, 0),
            WindowPosition.BOTTOM_LEFT: (0, single_monitor_height - window_height),
            WindowPosition.BOTTOM_RIGHT: (single_monitor_width - window_width, 
                                        single_monitor_height - window_height),
            WindowPosition.CENTER: ((single_monitor_width - window_width) // 2,
                                   (single_monitor_height - window_height) // 2),
            WindowPosition.TOP_CENTER: ((single_monitor_width - window_width) // 2, 0),
            WindowPosition.BOTTOM_CENTER: ((single_monitor_width - window_width) // 2,
                                         single_monitor_height - window_height),
            WindowPosition.LEFT_CENTER: (0, (single_monitor_height - window_height) // 2),
            WindowPosition.RIGHT_CENTER: (single_monitor_width - window_width,
                                        (single_monitor_height - window_height) // 2)
        }
        
        base_x, base_y = positions.get(position, positions[WindowPosition.CENTER])
        
        # Add monitor offset and user offset
        final_x = base_x + monitor_offset_x + offset_x
        final_y = base_y + monitor_offset_y + offset_y
        
        # Ensure position is within valid bounds
        final_x = max(0, min(final_x, virtual_width - window_width))
        final_y = max(0, min(final_y, virtual_height - window_height))
        
        return final_x, final_y
    
    @staticmethod
    def set_window_position(position, window_width, window_height, monitor_index=0, offset_x=0, offset_y=0):
        """Set window position using SDL environment variable"""
        pos_x, pos_y = WindowPositioner.calculate_position(
            position, window_width, window_height, monitor_index, offset_x, offset_y
        )
        
        # Set SDL window position
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{pos_x},{pos_y}"
        print(f"Window positioned at: {pos_x}, {pos_y} (monitor {monitor_index}, position: {position})")
        return pos_x, pos_y


class ParticleFlowEffect:
    def __init__(self, window_position=WindowPosition.TOP_RIGHT, monitor_index=0, offset_x=50, offset_y=50):
        pygame.init()
        
        # Set window position before creating display
        WindowPositioner.set_window_position(
            window_position, WINDOW_WIDTH, WINDOW_HEIGHT, monitor_index, offset_x, offset_y
        )
        
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Particle Flow Effect")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)

        # Effect state
        self.current_step = 1
        self.max_steps = 6
        self.particles = []
        self.brightness_grid = []
        self.original_image = None
        
        # Trail surface
        self.trail_surface = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        self.persistent_trail_surface = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        self.enable_3d = ENABLE_3D

        # Performance
        self.frame_count = 0
        self.update_frequency = 1

        self.load_default_image()
        self.init_particles()

    def resize_window(self, new_width, new_height, window_position=None):
        """Resize window with optional repositioning"""
        new_width = max(MIN_WINDOW_WIDTH, min(MAX_WINDOW_WIDTH, new_width))
        new_height = max(MIN_WINDOW_HEIGHT, min(MAX_WINDOW_HEIGHT, new_height))
        
        if window_position:
            WindowPositioner.set_window_position(window_position, new_width, new_height)
        
        self.window_width = new_width
        self.window_height = new_height
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        
        # Recreate surfaces
        self.trail_surface = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        self.persistent_trail_surface = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        
        print(f"Window resized to: {self.window_width}x{self.window_height}")

    def load_default_image(self):
        """Generate default image pattern"""
        image_array = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)
        
        center_x, center_y = self.window_width // 2, self.window_height // 2
        
        for y in range(self.window_height):
            for x in range(self.window_width):
                # Spiral pattern
                dx, dy = x - center_x, y - center_y
                distance = math.sqrt(dx * dx + dy * dy)
                angle = math.atan2(dy, dx)
                
                # Create flowing pattern
                wave1 = math.sin(distance * 0.02 + angle * 3) * 0.5 + 0.5
                wave2 = math.sin(x * 0.01) * math.cos(y * 0.01) * 0.5 + 0.5
                
                brightness = int((wave1 * 0.7 + wave2 * 0.3) * 255)
                brightness = max(0, min(255, brightness))
                image_array[y, x] = [brightness, brightness, brightness]

        self.original_image = pygame.surfarray.make_surface(image_array.swapaxes(0, 1))
        self.process_image()

    def load_image(self, image_path):
        """Load image with smart resizing"""
        try:
            pil_image = Image.open(image_path)
            original_width, original_height = pil_image.size
            
            # Smart resizing logic
            aspect_ratio = original_width / original_height
            
            if original_width > MAX_WINDOW_WIDTH or original_height > MAX_WINDOW_HEIGHT:
                if aspect_ratio > 1:
                    new_width = MAX_WINDOW_WIDTH
                    new_height = int(MAX_WINDOW_WIDTH / aspect_ratio)
                else:
                    new_height = MAX_WINDOW_HEIGHT
                    new_width = int(MAX_WINDOW_HEIGHT * aspect_ratio)
            else:
                new_width = max(MIN_WINDOW_WIDTH, original_width)
                new_height = max(MIN_WINDOW_HEIGHT, original_height)
            
            self.resize_window(new_width, new_height)
            pil_image = pil_image.resize((self.window_width, self.window_height), Image.Resampling.LANCZOS)

            image_array = np.array(pil_image)
            if len(image_array.shape) == 2:
                image_array = np.stack([image_array] * 3, axis=-1)
            elif image_array.shape[2] == 4:
                image_array = image_array[:, :, :3]

            self.original_image = pygame.surfarray.make_surface(image_array.swapaxes(0, 1))
            self.process_image()
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False

    def load_image_dialog(self):
        """Image loading dialog"""
        try:
            pygame.display.iconify()
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)

            file_path = filedialog.askopenfilename(
                title="Select Image File",
                filetypes=[
                    ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.gif *.webp"),
                    ("All files", "*.*")
                ]
            )

            root.destroy()

            if file_path:
                success = self.load_image(file_path)
                if success:
                    print(f"Successfully loaded: {os.path.basename(file_path)}")
                    self.current_step = 1
                    self.init_particles()
                    
                    # Restore window
                    pygame.display.quit()
                    pygame.display.init()
                    self.screen = pygame.display.set_mode((self.window_width, self.window_height))
                    pygame.display.set_caption("Particle Flow Effect")
                    return True
                else:
                    print(f"Failed to load image: {file_path}")
                    return False
            else:
                print("No file selected")
                return False

        except Exception as e:
            print(f"Error in file dialog: {e}")
            return False

    def process_image(self):
        """Process image into brightness grid"""
        if not self.original_image:
            return

        image_array = pygame.surfarray.array3d(self.original_image)
        grid_width = self.window_width // DETAIL
        grid_height = self.window_height // DETAIL
        
        self.brightness_grid = np.zeros((grid_height, grid_width), dtype=np.float32)

        for y in range(grid_height):
            for x in range(grid_width):
                start_x = x * DETAIL
                start_y = y * DETAIL
                end_x = min(start_x + DETAIL, self.window_width)
                end_y = min(start_y + DETAIL, self.window_height)

                region = image_array[start_x:end_x, start_y:end_y]
                if region.size > 0:
                    self.brightness_grid[y, x] = np.mean(region) / 255.0
                else:
                    self.brightness_grid[y, x] = 0.5

    def init_particles(self):
        """Initialize particles"""
        self.particles = []
        for i in range(PARTICLE_COUNT):
            y = (i / PARTICLE_COUNT) * self.window_height
            self.particles.append(Particle(y=y, window_width=self.window_width, window_height=self.window_height))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.current_step = (self.current_step % self.max_steps) + 1
                elif event.key == pygame.K_r:
                    self.init_particles()
                    # Clear trails
                    self.trail_surface.fill((0, 0, 0, 0))
                    self.persistent_trail_surface.fill((0, 0, 0, 0))
                elif event.key == pygame.K_l:
                    self.load_image_dialog()
                elif event.key == pygame.K_3:
                    self.enable_3d = not self.enable_3d
                    print(f"3D Effect: {'ON' if self.enable_3d else 'OFF'}")
                elif event.key == pygame.K_c:
                    # Clear trails manually
                    self.trail_surface.fill((0, 0, 0, 0))
                    self.persistent_trail_surface.fill((0, 0, 0, 0))
                    print("Trails cleared")
        return True

    def update(self):
        """Update loop"""
        self.frame_count += 1
        
        if self.frame_count % self.update_frequency == 0 and isinstance(self.brightness_grid, np.ndarray) and self.brightness_grid.size > 0:
            grid_width = self.brightness_grid.shape[1] if len(self.brightness_grid.shape) > 1 else 0
            grid_height = self.brightness_grid.shape[0] if len(self.brightness_grid.shape) > 0 else 0
            
            for particle in self.particles:
                particle.update(self.brightness_grid, grid_width, grid_height)

    def draw_trails(self):
        """Draw trail system"""
        fade_surface = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, int(TRAIL_FADE * 255)))
        
        # Apply fade to persistent trail surface
        self.persistent_trail_surface.blit(fade_surface, (0, 0))
        
        # Draw new particle positions to persistent surface
        for particle in self.particles:
            if self.enable_3d:
                offset = int(DEPTH_OFFSET * particle.depth)
                
                # Red channel
                red_surf = pygame.Surface((PARTICLE_SIZE * 2, PARTICLE_SIZE * 2), pygame.SRCALPHA)
                red_color = (*RED_CHANNEL, max(0, min(255, int(particle.alpha * 100))))
                pygame.draw.circle(red_surf, red_color, (PARTICLE_SIZE, PARTICLE_SIZE), PARTICLE_SIZE)
                self.persistent_trail_surface.blit(red_surf, (int(particle.x - PARTICLE_SIZE - offset), int(particle.y - PARTICLE_SIZE)))
                
                # Blue channel
                blue_surf = pygame.Surface((PARTICLE_SIZE * 2, PARTICLE_SIZE * 2), pygame.SRCALPHA)
                blue_color = (*BLUE_CHANNEL, max(0, min(255, int(particle.alpha * 100))))
                pygame.draw.circle(blue_surf, blue_color, (PARTICLE_SIZE, PARTICLE_SIZE), PARTICLE_SIZE)
                self.persistent_trail_surface.blit(blue_surf, (int(particle.x - PARTICLE_SIZE + offset), int(particle.y - PARTICLE_SIZE)))
            else:
                color = (*PARTICLE_COLOR, max(0, min(255, int(particle.alpha * 120))))
                surf = pygame.Surface((PARTICLE_SIZE * 2, PARTICLE_SIZE * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (PARTICLE_SIZE, PARTICLE_SIZE), PARTICLE_SIZE)
                self.persistent_trail_surface.blit(surf, (int(particle.x - PARTICLE_SIZE), int(particle.y - PARTICLE_SIZE)))

        # Draw the persistent trail surface to screen
        self.screen.blit(self.persistent_trail_surface, (0, 0))

    def draw_step_1(self):
        self.screen.fill(BACKGROUND_COLOR)
        if self.original_image:
            self.screen.blit(self.original_image, (0, 0))
        # Grid overlay
        for x in range(0, self.window_width, DETAIL):
            pygame.draw.line(self.screen, (100, 100, 100), (x, 0), (x, self.window_height))
        for y in range(0, self.window_height, DETAIL):
            pygame.draw.line(self.screen, (100, 100, 100), (0, y), (self.window_width, y))

    def draw_step_2(self):
        self.screen.fill(BACKGROUND_COLOR)
        if isinstance(self.brightness_grid, np.ndarray) and self.brightness_grid.size > 0:
            for y in range(self.brightness_grid.shape[0]):
                for x in range(self.brightness_grid.shape[1]):
                    brightness = self.brightness_grid[y, x]
                    color_value = int(brightness * 255)
                    color = (color_value, color_value, color_value)
                    rect = pygame.Rect(x * DETAIL, y * DETAIL, DETAIL, DETAIL)
                    pygame.draw.rect(self.screen, color, rect)

    def draw_step_3(self):
        self.screen.fill(BACKGROUND_COLOR)
        for particle in self.particles[:20]:
            particle.draw(self.screen, self.enable_3d)

    def draw_step_4(self):
        self.screen.fill(BACKGROUND_COLOR)
        for particle in self.particles:
            particle.draw(self.screen, self.enable_3d)

    def draw_step_5(self):
        self.screen.fill(BACKGROUND_COLOR)
        for particle in self.particles:
            particle.draw(self.screen, self.enable_3d)

    def draw_step_6(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_trails()

    def draw(self):
        step_functions = {
            1: self.draw_step_1,
            2: self.draw_step_2,
            3: self.draw_step_3,
            4: self.draw_step_4,
            5: self.draw_step_5,
            6: self.draw_step_6
        }
        step_functions.get(self.current_step, self.draw_step_1)()

        # Status display
        step_descriptions = {
            1: "Original + Grid",
            2: "Brightness", 
            3: "Few Particles",
            4: "All Particles",
            5: "Alpha Blend",
            6: "Trails"
        }
        
        step_desc = step_descriptions.get(self.current_step, "Unknown")
        threed_status = " | 3D: ON" if self.enable_3d else ""
        
        # Adaptive text based on window width
        if self.window_width < 800:
            step_text = f"S{self.current_step}/{self.max_steps}: {step_desc}{threed_status}"
        else:
            step_text = f"Step {self.current_step}/{self.max_steps}: {step_desc}{threed_status} - SPACE/R/L/3/C/ESC"
        
        font_size = 24 if self.window_width < 800 else 28
        font = pygame.font.Font(None, font_size)
        
        text_surface = font.render(step_text, True, (0, 255, 136))
        text_rect = text_surface.get_rect()
        text_rect.bottomleft = (10, self.window_height - 5)
        
        # Background for text
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(self.screen, (0, 255, 136), bg_rect, 2)
        self.screen.blit(text_surface, text_rect)

        pygame.display.flip()

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
    """Main function with positioning options"""
    try:
        # MONITOR DETECTION TEST
        print("=== Monitor Detection ===")
        WindowPositioner.detect_monitors()
        
        # Configuration parameters
        window_position = WindowPosition.LEFT_CENTER
        monitor_index = 1
        offset_x = 150
        offset_y = -100
        
        print("\n=== Particle Flow Effect ===")
        print("Position options:", [attr for attr in dir(WindowPosition) if not attr.startswith('_')])
        print(f"Starting with position: {window_position} on monitor {monitor_index}")
        
        # Test window positioning
        test_x, test_y = WindowPositioner.calculate_position(
            window_position, WINDOW_WIDTH, WINDOW_HEIGHT, monitor_index, offset_x, offset_y
        )
        print(f"Calculated window position: {test_x}, {test_y}")
        
        print("Controls:")
        print("- SPACE: Change effect step (1-6)")
        print("- R: Reset particles and clear trails")
        print("- L: Load image")
        print("- 3: Toggle 3D red-blue effect")
        print("- C: Clear trails manually")
        print("- ESC: Exit")
        
        effect = ParticleFlowEffect(
            window_position=window_position,
            monitor_index=monitor_index,
            offset_x=offset_x,
            offset_y=offset_y
        )
        
        effect.run()
        
    except pygame.error as e:
        print(f"Pygame error: {e}")
        print("Make sure pygame is installed: pip install pygame pillow numpy")
    except Exception as e:
        print(f"Error: {e}")


def test_multi_monitor():
    """Test function to verify multi-monitor positioning"""
    print("=== Multi-Monitor Position Test ===")
    
    # Detect monitors
    WindowPositioner.detect_monitors()
    
    # Test various positions on different monitors
    test_configs = [
        (WindowPosition.TOP_LEFT, 0, 0, 0),
        (WindowPosition.TOP_RIGHT, 0, 0, 0),
        (WindowPosition.CENTER, 0, 0, 0),
        (WindowPosition.TOP_LEFT, 1, 0, 0),
        (WindowPosition.TOP_RIGHT, 1, 0, 0),
        (WindowPosition.CENTER, 1, 0, 0),
    ]
    
    for position, monitor, offset_x, offset_y in test_configs:
        x, y = WindowPositioner.calculate_position(
            position, WINDOW_WIDTH, WINDOW_HEIGHT, monitor, offset_x, offset_y
        )
        print(f"Position: {position}, Monitor: {monitor} -> ({x}, {y})")


if __name__ == "__main__":
    # Uncomment next line to run position test only
    # test_multi_monitor()
    main()