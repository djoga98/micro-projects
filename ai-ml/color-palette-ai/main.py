# Configuration constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
DEFAULT_COLORS = 5
MAX_COLORS = 8
MIN_COLORS = 3

# Color scheme
BG_COLOR = '#0a0a0a'
FRAME_COLOR = '#1a1a1a' 
PANEL_COLOR = '#2a2a2a'
ACCENT_COLOR = '#00ff88'
SECONDARY_COLOR = '#ff6600'
TEXT_COLOR = '#ffffff'
MUTED_COLOR = '#888888'

# UI settings
FONT_MAIN = ('Consolas', 18, 'bold')
FONT_BUTTON = ('Consolas', 12, 'bold')
FONT_LABEL = ('Consolas', 10, 'bold')
FONT_SMALL = ('Consolas', 8)

# Layout and sizing constants
HEADER_HEIGHT = 60
HEADER_PADDING_X = 20
HEADER_PADDING_Y = 10
HEADER_TITLE_PADDING_Y = 15

MAIN_FRAME_PADDING_X = 20
MAIN_FRAME_PADDING_Y = 10
MAIN_FRAME_BORDER = 2

CONTROLS_PADDING_X = 20
CONTROLS_PADDING_Y = 10
CONTROLS_SPINBOX_WIDTH = 5
CONTROLS_LABEL_PADDING_RIGHT = 10
CONTROLS_SPINBOX_PADDING_RIGHT = 20

IMAGE_FRAME_HEIGHT = 250
IMAGE_FRAME_PADDING_Y_BOTTOM = 20
IMAGE_THUMBNAIL_WIDTH = 400
IMAGE_THUMBNAIL_HEIGHT = 220

BUTTON_FRAME_PADDING_Y = 15
BUTTON_WIDTH_LOAD = 15
BUTTON_WIDTH_EXTRACT = 18
BUTTON_HEIGHT = 2
BUTTON_PADDING_X = 10
BUTTON_BORDER = 2

PALETTE_FRAME_HEIGHT = 200
PALETTE_FRAME_PADDING_X = 20
PALETTE_FRAME_PADDING_Y_TOP = 15
PALETTE_FRAME_PADDING_Y_BOTTOM = 20
PALETTE_CONTAINER_MARGIN = 120
PALETTE_CONTAINER_PADDING_X = 10
PALETTE_CONTAINER_PADDING_Y = 20
PALETTE_COLOR_MARGIN = 2
COLOR_CANVAS_HEIGHT = 100
COLOR_CANVAS_BORDER = 2
HEX_LABEL_PADDING_Y = 2

STATUS_BAR_HEIGHT = 30
STATUS_LABEL_PADDING_Y = 5

# Image processing constants
IMAGE_RESIZE_WIDTH = 150
IMAGE_RESIZE_HEIGHT = 150
KMEANS_RANDOM_STATE = 42
KMEANS_N_INIT = 10

# Animation constants
ANIMATION_DELAY_MULTIPLIER = 150
ANIMATION_STEPS = range(0, 101, 10)
ANIMATION_STEP_DELAY = 2
ANIMATION_ALPHA_THRESHOLD = 50

# Status messages
STATUS_READY = "READY"
STATUS_IMAGE_LOADED = "IMAGE LOADED - READY TO EXTRACT"
STATUS_ANALYZING = "ANALYZING IMAGE..."
STATUS_EXTRACTION_COMPLETE = "EXTRACTION COMPLETE"
STATUS_COPIED_PREFIX = "COPIED: "
STATUS_ERROR_PREFIX = "ERROR: "

# Timing constants
STATUS_RESET_DELAY = 2000

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time

class ColorPalette:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.current_colors = []
        self.n_colors = DEFAULT_COLORS
        
    def setup_window(self):
        # dark theme
        self.root.title("AI COLOR EXTRACTOR")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        # header with neon effect
        header_frame = tk.Frame(self.root, bg=BG_COLOR, height=HEADER_HEIGHT)
        header_frame.pack(fill='x', padx=HEADER_PADDING_X, pady=HEADER_PADDING_Y)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="COLOR PALETTE EXTRACTOR",
                              font=FONT_MAIN,
                              fg=ACCENT_COLOR,
                              bg=BG_COLOR)
        title_label.pack(pady=HEADER_TITLE_PADDING_Y)
        
        # main content area
        main_frame = tk.Frame(self.root, bg=FRAME_COLOR, relief='raised', bd=MAIN_FRAME_BORDER)
        main_frame.pack(fill='both', expand=True, padx=MAIN_FRAME_PADDING_X, pady=MAIN_FRAME_PADDING_Y)
        
        # controls frame
        controls_frame = tk.Frame(main_frame, bg=FRAME_COLOR)
        controls_frame.pack(fill='x', padx=CONTROLS_PADDING_X, pady=CONTROLS_PADDING_Y)
        
        # color count selector
        tk.Label(controls_frame, text="Colors:", font=FONT_LABEL, 
                fg=TEXT_COLOR, bg=FRAME_COLOR).pack(side='left', padx=(0, CONTROLS_LABEL_PADDING_RIGHT))
        
        self.color_var = tk.IntVar(value=DEFAULT_COLORS)
        self.color_spinbox = tk.Spinbox(controls_frame, from_=MIN_COLORS, to=MAX_COLORS,
                                       textvariable=self.color_var, width=CONTROLS_SPINBOX_WIDTH,
                                       font=FONT_LABEL, bg=PANEL_COLOR, fg=TEXT_COLOR,
                                       buttonbackground=ACCENT_COLOR)
        self.color_spinbox.pack(side='left', padx=(0, CONTROLS_SPINBOX_PADDING_RIGHT))
        
        # image preview area
        self.image_frame = tk.Frame(main_frame, bg=PANEL_COLOR, height=IMAGE_FRAME_HEIGHT)
        self.image_frame.pack(fill='x', padx=MAIN_FRAME_PADDING_X, pady=(0, IMAGE_FRAME_PADDING_Y_BOTTOM))
        self.image_frame.pack_propagate(False)
        
        self.image_label = tk.Label(self.image_frame,
                                   text="NO IMAGE LOADED",
                                   font=('Consolas', 14),
                                   fg='#555555',
                                   bg=PANEL_COLOR)
        self.image_label.pack(expand=True)
        
        # buttons with neon styling
        button_frame = tk.Frame(main_frame, bg=FRAME_COLOR)
        button_frame.pack(pady=BUTTON_FRAME_PADDING_Y)
        
        self.load_btn = tk.Button(button_frame,
                                 text="LOAD IMAGE",
                                 font=FONT_BUTTON,
                                 fg=ACCENT_COLOR,
                                 bg=BG_COLOR,
                                 activeforeground='#000000',
                                 activebackground=ACCENT_COLOR,
                                 bd=BUTTON_BORDER,
                                 relief='raised',
                                 command=self.load_image,
                                 width=BUTTON_WIDTH_LOAD,
                                 height=BUTTON_HEIGHT)
        self.load_btn.pack(side='left', padx=BUTTON_PADDING_X)
        
        self.extract_btn = tk.Button(button_frame,
                                    text="EXTRACT COLORS",
                                    font=FONT_BUTTON,
                                    fg=SECONDARY_COLOR,
                                    bg=BG_COLOR,
                                    activeforeground='#000000',
                                    activebackground=SECONDARY_COLOR,
                                    bd=BUTTON_BORDER,
                                    relief='raised',
                                    command=self.extract_colors,
                                    width=BUTTON_WIDTH_EXTRACT,
                                    height=BUTTON_HEIGHT,
                                    state='disabled')
        self.extract_btn.pack(side='left', padx=BUTTON_PADDING_X)
        
        # color palette display area - fixed height for consistent layout
        self.palette_frame = tk.Frame(main_frame, bg=PANEL_COLOR, height=PALETTE_FRAME_HEIGHT)
        self.palette_frame.pack(fill='x', padx=PALETTE_FRAME_PADDING_X, 
                               pady=(PALETTE_FRAME_PADDING_Y_TOP, PALETTE_FRAME_PADDING_Y_BOTTOM))
        self.palette_frame.pack_propagate(False)
        
        # status bar
        self.status_frame = tk.Frame(self.root, bg=BG_COLOR, height=STATUS_BAR_HEIGHT)
        self.status_frame.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(self.status_frame,
                                    text=STATUS_READY,
                                    font=('Consolas', 10),
                                    fg=ACCENT_COLOR,
                                    bg=BG_COLOR)
        self.status_label.pack(pady=STATUS_LABEL_PADDING_Y)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
            self.extract_btn.config(state='normal')
            self.update_status(STATUS_IMAGE_LOADED)
            
    def display_image(self, image_path):
        # load and resize image for display
        image = Image.open(image_path)
        image.thumbnail((IMAGE_THUMBNAIL_WIDTH, IMAGE_THUMBNAIL_HEIGHT), Image.Resampling.LANCZOS)
        
        # convert to tkinter format
        photo = ImageTk.PhotoImage(image)
        
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo
        
    def extract_colors(self):
        self.n_colors = self.color_var.get()
        self.update_status(STATUS_ANALYZING)
        self.extract_btn.config(state='disabled')
        
        # run extraction in separate thread to prevent UI freeze
        threading.Thread(target=self._extract_colors_thread, daemon=True).start()
        
    def _extract_colors_thread(self):
        try:
            # load and process image
            image = cv2.imread(self.image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (IMAGE_RESIZE_WIDTH, IMAGE_RESIZE_HEIGHT))
            
            # extract colors using kmeans
            data = image.reshape((-1, 3))
            kmeans = KMeans(n_clusters=self.n_colors, random_state=KMEANS_RANDOM_STATE, 
                           n_init=KMEANS_N_INIT)
            kmeans.fit(data)
            colors = kmeans.cluster_centers_.astype(int)
            
            self.current_colors = colors
            
            # update UI in main thread
            self.root.after(0, self.display_palette)
            
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"{STATUS_ERROR_PREFIX}{str(e)}"))
            self.root.after(0, lambda: self.extract_btn.config(state='normal'))
            
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.update_status(f"{STATUS_COPIED_PREFIX}{text}")
        # reset status after configured delay
        self.root.after(STATUS_RESET_DELAY, 
                       lambda: self.update_status(STATUS_EXTRACTION_COMPLETE))
    
    def display_palette(self):
        # clear previous palette
        for widget in self.palette_frame.winfo_children():
            widget.destroy()
            
        # calculate equal width for all colors to fit screen
        total_colors = len(self.current_colors)
        available_width = WINDOW_WIDTH - PALETTE_CONTAINER_MARGIN
        color_width = available_width // total_colors
        
        # create container for equal-width colors
        colors_container = tk.Frame(self.palette_frame, bg=PANEL_COLOR, width=available_width)
        colors_container.pack(fill='both', expand=True, 
                             padx=PALETTE_CONTAINER_PADDING_X, 
                             pady=PALETTE_CONTAINER_PADDING_Y)
        
        for i, color in enumerate(self.current_colors):
            # create color frame with fixed width
            color_frame = tk.Frame(colors_container, bg=PANEL_COLOR, width=color_width)
            color_frame.pack(side='left', fill='y', padx=PALETTE_COLOR_MARGIN)
            color_frame.pack_propagate(False)
            
            # color display
            hex_code = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            color_canvas = tk.Canvas(color_frame, height=COLOR_CANVAS_HEIGHT, bg=hex_code, 
                                   highlightthickness=COLOR_CANVAS_BORDER, 
                                   highlightcolor=TEXT_COLOR)
            color_canvas.pack(fill='x', pady=(0, 5))

            color_canvas.bind("<Button-1>", lambda e, hex_val=hex_code: self.copy_to_clipboard(hex_val))
            color_canvas.config(cursor="hand2")
            
            # hex code label
            hex_label = tk.Label(color_frame,
                               text=hex_code,
                               font=FONT_LABEL,
                               fg=TEXT_COLOR,
                               bg=BG_COLOR)
            hex_label.pack(pady=HEX_LABEL_PADDING_Y)
            
            # rgb values
            rgb_text = f"R:{color[0]} G:{color[1]} B:{color[2]}"
            rgb_label = tk.Label(color_frame,
                               text=rgb_text,
                               font=FONT_SMALL,
                               fg=MUTED_COLOR,
                               bg=PANEL_COLOR)
            rgb_label.pack()
            
            # animate color appearance
            self.animate_color_bar(color_canvas, i * ANIMATION_DELAY_MULTIPLIER)
        
        self.update_status(STATUS_EXTRACTION_COMPLETE)
        self.extract_btn.config(state='normal')
        
    def animate_color_bar(self, canvas, delay):
        def animate():
            time.sleep(delay / 1000)
            for alpha in ANIMATION_STEPS:
                self.root.after(alpha * ANIMATION_STEP_DELAY, 
                               lambda a=alpha: self.update_canvas_alpha(canvas, a))
                
        threading.Thread(target=animate, daemon=True).start()
        
    def update_canvas_alpha(self, canvas, alpha):
        # simulate fade-in effect by changing border
        if alpha > ANIMATION_ALPHA_THRESHOLD:
            canvas.config(highlightcolor=ACCENT_COLOR)
        else:
            canvas.config(highlightcolor='#333333')
            
    def update_status(self, message):
        self.status_label.config(text=message)
        
    def run(self):
        self.root.mainloop()

# run the palette generator
if __name__ == "__main__":
    app = ColorPalette()
    app.run()