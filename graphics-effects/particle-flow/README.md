# 🌊 Particle Flow Effect

> _Transform any image into a mesmerizing particle flow visualization with AI-powered brightness analysis_

A sophisticated particle system that analyzes image brightness and creates flowing particle effects with multi-monitor support, 3D anaglyph effects, and real-time image processing.

![Particle Flow Demo](demo.gif)

## ✨ Features

### 🎨 **Visual Effects**

- **Smart Particle Flow** - Particles move based on image brightness analysis
- **6-Step Visualization Process** - See how the effect is built step by step
- **3D Anaglyph Mode** - Red-blue stereoscopic effect for depth perception
- **Dynamic Trails** - Persistent particle trails with smooth fade effects
- **Real-time Processing** - Live brightness grid analysis and particle updates

### 🖥️ **Multi-Monitor Support**

- **Intelligent Window Positioning** - 9 different position presets
- **Multi-Monitor Detection** - Automatic detection of monitor setup
- **Cross-Monitor Placement** - Position windows on any available monitor
- **Smart Resizing** - Automatic window sizing based on image dimensions

### 🖼️ **Image Processing**

- **Universal Format Support** - JPG, PNG, BMP, TIFF, GIF, WebP
- **Smart Resize** - Maintains aspect ratio while fitting screen
- **Brightness Analysis** - Converts images to brightness grids for particle behavior
- **Default Pattern** - Built-in spiral pattern when no image is loaded

### ⚡ **Performance Optimized**

- **Efficient Rendering** - Optimized particle drawing and trail management
- **Memory Management** - Automatic cleanup of off-screen particles
- **Configurable Quality** - Adjustable particle count and update frequency
- **Smooth Animation** - 60 FPS target with adaptive performance

## 🚀 Quick Start

### Prerequisites

```bash
pip install pygame pillow numpy
```

### Installation

```bash
git clone https://github.com/djoga98/micro-projects.git
cd micro-projects/graphics-effects/particle-flow
python main.py
```

### Quick Run

```bash
python main.py
```

## 🎮 Controls

| Key     | Action                                  |
| ------- | --------------------------------------- |
| `SPACE` | Cycle through visualization steps (1-6) |
| `L`     | Load image from file dialog             |
| `R`     | Reset particles and clear trails        |
| `3`     | Toggle 3D anaglyph effect               |
| `C`     | Clear trails manually                   |
| `ESC`   | Exit application                        |

## 📊 Visualization Steps

| Step  | Description     | What You See                                       |
| ----- | --------------- | -------------------------------------------------- |
| **1** | Original + Grid | Source image with brightness analysis grid overlay |
| **2** | Brightness Map  | Grayscale representation of brightness values      |
| **3** | Few Particles   | Small particle sample to see individual behavior   |
| **4** | All Particles   | Complete particle system (3000 particles)          |
| **5** | Alpha Blending  | Particles with transparency based on brightness    |
| **6** | Particle Trails | Full effect with persistent trailing               |

## 🖥️ Multi-Monitor Configuration

### Window Positioning Options

```python
# Available positions
WindowPosition.TOP_LEFT
WindowPosition.TOP_RIGHT
WindowPosition.BOTTOM_LEFT
WindowPosition.BOTTOM_RIGHT
WindowPosition.CENTER
WindowPosition.TOP_CENTER
WindowPosition.BOTTOM_CENTER
WindowPosition.LEFT_CENTER
WindowPosition.RIGHT_CENTER
```

### Configuration Example

```python
def main():
    # Multi-monitor setup
    window_position = WindowPosition.TOP_RIGHT
    monitor_index = 1  # 0 = primary, 1 = secondary
    offset_x = 100     # Additional X offset
    offset_y = 50      # Additional Y offset

    effect = ParticleFlowEffect(
        window_position=window_position,
        monitor_index=monitor_index,
        offset_x=offset_x,
        offset_y=offset_y
    )
    effect.run()
```

### Monitor Detection Test

```python
# Test multi-monitor positioning
def test_multi_monitor():
    WindowPositioner.detect_monitors()
    # ... test various positions
```

## ⚙️ Configuration

### Basic Settings

```python
# Window and display
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 804
FPS = 60

# Particle system
PARTICLE_COUNT = 3000
PARTICLE_SIZE = 2
MAX_SPEED = 4
TRAIL_FADE = 0.09

# Image processing
DETAIL = 16  # Brightness grid resolution
```

### Advanced Settings

```python
# 3D Effect
DEPTH_OFFSET = 3
RED_CHANNEL = (255, 0, 0)
BLUE_CHANNEL = (0, 100, 255)
ENABLE_3D = False

# Performance
UPDATE_FREQUENCY = 1
MAX_TRAIL_LENGTH = 20
```

## 🛠️ Technical Details

### Particle System Architecture

```python
class Particle:
    def __init__(self, x, y, window_width, window_height):
        self.x, self.y = x, y
        self.velocity_x = random.uniform(-0.5, 0.5)
        self.velocity_y = random.uniform(-0.5, 0.5)
        self.alpha = random.uniform(0.3, 1.0)
        self.depth = random.uniform(0.0, 1.0)
        self.trail_history = []

    def update(self, brightness_grid, grid_width, grid_height):
        # Brightness-based movement
        brightness = self.get_brightness_at_position()
        self.speed = brightness * MAX_SPEED

        # Update position with flow
        self.x += (1 - brightness) * 2.5 + self.velocity_x
        self.y += self.velocity_y * 0.3
```

### Brightness Analysis

```python
def process_image(self):
    """Convert image to brightness grid for particle behavior"""
    image_array = pygame.surfarray.array3d(self.original_image)
    grid_width = self.window_width // DETAIL
    grid_height = self.window_height // DETAIL

    self.brightness_grid = np.zeros((grid_height, grid_width))

    for y in range(grid_height):
        for x in range(grid_width):
            region = image_array[x*DETAIL:(x+1)*DETAIL, y*DETAIL:(y+1)*DETAIL]
            self.brightness_grid[y, x] = np.mean(region) / 255.0
```

### Multi-Monitor Implementation

```python
class WindowPositioner:
    @staticmethod
    def detect_monitors():
        """Detect monitor configuration using tkinter"""
        root = tk.Tk()
        root.withdraw()

        primary_width = root.winfo_screenwidth()
        virtual_width = root.winfo_vrootwidth()

        num_monitors = max(1, virtual_width // primary_width)
        return num_monitors, primary_width, primary_height

    @staticmethod
    def calculate_position(position, window_width, window_height, monitor_index=0):
        """Calculate window position for specified monitor"""
        monitor_offset_x = primary_width * monitor_index
        # ... position calculation logic
```

## 🎨 Usage Examples

### Basic Usage

```python
# Simple center positioning
effect = ParticleFlowEffect()
effect.run()
```

### Advanced Multi-Monitor Setup

```python
# Position on second monitor, top-right corner
effect = ParticleFlowEffect(
    window_position=WindowPosition.TOP_RIGHT,
    monitor_index=1,
    offset_x=50,
    offset_y=50
)
effect.run()
```

### Custom Image Loading

```python
# Load specific image
effect = ParticleFlowEffect()
success = effect.load_image("path/to/your/image.jpg")
if success:
    effect.run()
```

### 3D Effect with Custom Positioning

```python
# 3D effect on secondary monitor
effect = ParticleFlowEffect(
    window_position=WindowPosition.CENTER,
    monitor_index=1
)
effect.enable_3d = True
effect.run()
```

## 📸 Screenshots

| Step                | Preview                             |
| ------------------- | ----------------------------------- |
| **Original Image**  | ![Step 1](screenshots/step1.png)    |
| **Brightness Grid** | ![Step 2](screenshots/step2.png)    |
| **Particle System** | ![Step 4](screenshots/step4.png)    |
| **Trails Effect**   | ![Step 6](screenshots/step6.png)    |
| **3D Anaglyph**     | ![3D Mode](screenshots/3d_mode.png) |

## 🐛 Troubleshooting

### Multi-Monitor Issues

**Problem**: Window doesn't appear on specified monitor

```python
# Test monitor detection
test_multi_monitor()

# Check SDL environment
import os
print(os.environ.get('SDL_VIDEO_WINDOW_POS', 'Not set'))
```

**Solution**: Try different monitor arrangement or manual positioning:

```python
# Force manual positioning
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{1920},{100}"  # Second monitor
```

### Performance Issues

**Problem**: Low FPS with many particles

```python
# Reduce particle count
PARTICLE_COUNT = 1500

# Lower update frequency
self.update_frequency = 2

# Reduce trail length
self.max_trail_length = 10
```

### Image Loading Problems

**Problem**: Image not loading or displaying incorrectly

```python
# Check supported formats
supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif", ".webp"]

# Verify image dimensions
pil_image = Image.open(image_path)
print(f"Image size: {pil_image.size}")
print(f"Image mode: {pil_image.mode}")
```

## 🔬 Development

### Project Structure

```
particle-flow-effect/
├── main.py                   # Main application
├── README.md                 # This documentation
├── requirements.txt          # Dependencies
```

### Adding New Features

```python
# Example: Add new particle behavior
class AdvancedParticle(Particle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rotation = random.uniform(0, 2 * math.pi)
        self.spin_speed = random.uniform(-0.1, 0.1)

    def update(self, brightness_grid, grid_width, grid_height):
        super().update(brightness_grid, grid_width, grid_height)
        self.rotation += self.spin_speed
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## 👨‍💻 Author

**Slavko Đogić**

- GitHub: [@djoga98](https://github.com/djoga98)
- LinkedIn: [@djogicslavko](https://linkedin.com/in/djogicslavko)
- TikTok: [@tensorix](https://tiktok.com/@tensorix)

## 🙏 Acknowledgments

- **Pygame Community** - Excellent graphics library and community support
- **NumPy Team** - Fast numerical operations for image processing
- **PIL/Pillow** - Comprehensive image handling capabilities
- **Scientific Visualization Community** - Inspiration for particle effects

## ⭐ Star this repo

If you found this project helpful, please consider giving it a star! It helps others discover the project.
