import warnings
warnings.filterwarnings("ignore")

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import pyaudio
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import numpy as np
from deep_translator import GoogleTranslator
import librosa
import time

# Configuration
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 804
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Real-time settings
REALTIME_CHUNK_DURATION = 3  # seconds
REALTIME_BUFFER_SIZE = RATE * REALTIME_CHUNK_DURATION

# Colors - Futuristic theme
BG_COLOR = '#0a0a0a'
FRAME_COLOR = '#1a1a1a'
ACCENT_COLOR = '#00ff88'
SECONDARY_COLOR = '#ff6600'
ERROR_COLOR = '#ff4757'
TEXT_COLOR = '#ffffff'
BUTTON_COLOR = '#2d2d2d'


class WindowPosition:
    """Window position constants"""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"
    TOP_CENTER = "top_center"
    BOTTOM_CENTER = "bottom_center"
    LEFT_CENTER = "left_center"
    RIGHT_CENTER = "right_center"


class WindowPositioner:
    """Utility class for smart window positioning across multiple monitors"""
    
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
            # Fallback values
            return 1920, 1080
    
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
    def set_tkinter_window_position(window, position, monitor_index=0, offset_x=0, offset_y=0):
        """Set tkinter window position"""
        # Use fixed dimensions instead of trying to detect them
        window_width = WINDOW_WIDTH
        window_height = WINDOW_HEIGHT
        
        pos_x, pos_y = WindowPositioner.calculate_position(
            position, window_width, window_height, monitor_index, offset_x, offset_y
        )
        
        window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
        print(f"VoiceBridge positioned at: {pos_x}, {pos_y} (monitor {monitor_index}, position: {position})")
        return pos_x, pos_y


class VoiceBridgeAI:
    def __init__(self, window_position=WindowPosition.TOP_RIGHT, monitor_index=0, offset_x=50, offset_y=50):
        self.window_position = window_position
        self.monitor_index = monitor_index
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        self.root = tk.Tk()
        self.setup_window()

        # Audio recording
        self.audio = pyaudio.PyAudio()
        self.recording = False
        self.frames = []
        self.recording_start_time = 0

        # Real-time processing
        self.realtime_buffer = []
        self.realtime_thread = None
        self.realtime_active = False

        # AI Models
        self.whisper_pipe = None

        # Model loading
        self.model_loaded = False
        self.load_model_thread()

    def setup_window(self):
        self.root.title("VoiceBridge AI - Voice Translator")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Header
        header_frame = tk.Frame(self.root, bg=BG_COLOR, height=100)
        header_frame.pack(fill='x', padx=20, pady=15)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="VoiceBridge AI",
            font=('Consolas', 24, 'bold'),
            fg=ACCENT_COLOR,
            bg=BG_COLOR
        )
        title_label.pack(pady=2)

        subtitle_label = tk.Label(
            header_frame,
            text="Powered by Whisper Large V3 Turbo",
            font=('Consolas', 12),
            fg=SECONDARY_COLOR,
            bg=BG_COLOR
        )
        subtitle_label.pack()

        # Device indicator
        device_text = "GPU Ready" if torch.cuda.is_available() else "CPU Mode"
        device_label = tk.Label(
            header_frame,
            text=device_text,
            font=('Consolas', 10),
            fg=ACCENT_COLOR if torch.cuda.is_available() else TEXT_COLOR,
            bg=BG_COLOR
        )
        device_label.pack()

        # Position indicator for TikTok demos
        # position_text = f"Monitor {self.monitor_index} | {self.window_position.replace('_', ' ').title()}"
        # position_label = tk.Label(
        #     header_frame,
        #     text=position_text,
        #     font=('Consolas', 8),
        #     fg='#666666',
        #     bg=BG_COLOR
        # )
        # position_label.pack()

        # Main container
        main_frame = tk.Frame(self.root, bg=FRAME_COLOR, relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Controls section
        controls_frame = tk.Frame(main_frame, bg=FRAME_COLOR)
        controls_frame.pack(fill='x', padx=20, pady=15)

        # Language selection
        lang_frame = tk.Frame(controls_frame, bg=FRAME_COLOR)
        lang_frame.pack(fill='x', pady=10)

        tk.Label(lang_frame, text="Translate to:",
                 font=('Consolas', 14, 'bold'),
                 fg=TEXT_COLOR, bg=FRAME_COLOR).pack(side='left')

        self.target_lang = tk.StringVar(value='en')
        self.lang_names = GoogleTranslator().get_supported_languages(as_dict=True)

        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.target_lang,
            values=list(self.lang_names.keys()),
            state='readonly',
            width=8,
            font=('Consolas', 12)
        )
        lang_combo.pack(side='left', padx=15)

        # Real-time mode toggle
        self.realtime_var = tk.BooleanVar(value=False)
        realtime_check = tk.Checkbutton(
            lang_frame,
            text="Real-time mode",
            variable=self.realtime_var,
            font=('Consolas', 12),
            fg=ACCENT_COLOR,
            bg=FRAME_COLOR,
            selectcolor=BUTTON_COLOR,
            command=self.toggle_realtime_mode
        )
        realtime_check.pack(side='right', padx=10)

        # Recording timer
        self.timer_label = tk.Label(
            lang_frame,
            text="00:00",
            font=('Consolas', 12, 'bold'),
            fg=SECONDARY_COLOR,
            bg=FRAME_COLOR
        )
        self.timer_label.pack(side='right', padx=10)

        # Button + status section
        button_frame = tk.Frame(controls_frame, bg=FRAME_COLOR)
        button_frame.pack(fill='x', pady=15)

        self.record_btn = tk.Button(
            button_frame,
            text="START RECORDING",
            font=('Consolas', 14, 'bold'),
            fg='black',
            bg=ACCENT_COLOR,
            activebackground='#00cc6a',
            command=self.toggle_recording,
            height=2,
            relief='raised',
            bd=3
        )
        self.record_btn.grid(row=0, column=0, sticky="nsew", padx=5)

        self.clear_btn = tk.Button(
            button_frame,
            text="CLEAR",
            font=('Consolas', 14, 'bold'),
            fg=TEXT_COLOR,
            bg=BUTTON_COLOR,
            activebackground='#404040',
            command=self.clear_text,
            height=2,
            relief='raised',
            bd=3
        )
        self.clear_btn.grid(row=0, column=1, sticky="nsew", padx=5)

        # Make buttons expand
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Status label
        self.status_label = tk.Label(
            button_frame,
            text="Loading Whisper Turbo...",
            font=('Consolas', 12, 'bold'),
            fg=SECONDARY_COLOR,
            bg=FRAME_COLOR
        )
        self.status_label.grid(row=1, column=0, columnspan=3, pady=8)

        # Results area
        results_frame = tk.Frame(main_frame, bg=FRAME_COLOR)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Original speech
        original_label = tk.Label(
            results_frame,
            text="DETECTED SPEECH",
            font=('Consolas', 14, 'bold'),
            fg=ACCENT_COLOR,
            bg=FRAME_COLOR
        )
        original_label.pack(anchor='w', pady=(0, 5))

        self.original_text = scrolledtext.ScrolledText(
            results_frame,
            height=8,
            font=('Consolas', 12),
            bg='#2a2a2a',
            fg='white',
            insertbackground='white',
            relief='sunken',
            bd=2
        )
        self.original_text.pack(fill='both', expand=True, pady=(0, 15))

        # Translation
        translation_label = tk.Label(
            results_frame,
            text="TRANSLATION",
            font=('Consolas', 14, 'bold'),
            fg=SECONDARY_COLOR,
            bg=FRAME_COLOR
        )
        translation_label.pack(anchor='w', pady=(0, 5))

        self.translated_text = scrolledtext.ScrolledText(
            results_frame,
            height=8,
            font=('Consolas', 12),
            bg='#2a2a2a',
            fg=SECONDARY_COLOR,
            insertbackground='white',
            relief='sunken',
            bd=2
        )
        self.translated_text.pack(fill='both', expand=True)

        # Position window AFTER all widgets are created
        self.root.update_idletasks()  # Force geometry calculation
        self.root.after(100, self.position_window)  # Small delay for proper sizing

    def position_window(self):
        """Position window after it's fully created"""
        WindowPositioner.set_tkinter_window_position(
            self.root, 
            self.window_position, 
            self.monitor_index, 
            self.offset_x, 
            self.offset_y
        )

    def toggle_realtime_mode(self):
        """Toggle real-time processing mode"""
        if self.realtime_var.get():
            if not self.model_loaded:
                messagebox.showerror("Error", "Whisper model still loading!")
                self.realtime_var.set(False)
                return
            self.start_realtime_mode()
        else:
            self.stop_realtime_mode()

    def start_realtime_mode(self):
        """Start real-time continuous processing"""
        self.realtime_active = True
        self.realtime_buffer = []
        self.update_status("Real-time mode: Listening...")
        
        # Disable regular recording button in real-time mode
        self.record_btn.config(state='disabled', text="REAL-TIME ACTIVE")
        
        def realtime_capture():
            """Continuous audio capture for real-time processing"""
            try:
                stream = self.audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK
                )
                
                chunk_frames = []
                chunk_count = 0
                frames_per_chunk = REALTIME_BUFFER_SIZE // CHUNK
                
                while self.realtime_active:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    chunk_frames.append(data)
                    chunk_count += 1
                    
                    # Process every 3 seconds of audio
                    if chunk_count >= frames_per_chunk:
                        if self.realtime_active:  # Double check
                            audio_chunk = b''.join(chunk_frames)
                            threading.Thread(
                                target=self.process_realtime_chunk, 
                                args=(audio_chunk,), 
                                daemon=True
                            ).start()
                        
                        # Reset for next chunk
                        chunk_frames = []
                        chunk_count = 0
                        
                stream.stop_stream()
                stream.close()
                
            except Exception as e:
                self.update_status(f"Real-time capture error: {str(e)}")
                
        self.realtime_thread = threading.Thread(target=realtime_capture, daemon=True)
        self.realtime_thread.start()

    def stop_realtime_mode(self):
        """Stop real-time processing"""
        self.realtime_active = False
        self.record_btn.config(state='normal', text="START RECORDING")
        self.update_status("Real-time mode stopped")

    def process_realtime_chunk(self, audio_chunk):
        """Process a single chunk of audio in real-time"""
        try:
            # Convert audio chunk
            audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Skip if audio is too quiet (basic voice activity detection)
            if np.max(np.abs(audio_float)) < 0.01:  # Threshold for silence
                return
            
            # Resample if needed
            if RATE != 16000:
                audio_float = librosa.resample(audio_float, orig_sr=RATE, target_sr=16000)
            
            # Process with Whisper
            result = self.whisper_pipe(audio_float)
            text = result["text"].strip()
            
            if text and len(text) > 2:  # Only process meaningful text
                # Update original text (append new text)
                self.root.after(0, lambda: self.append_text(self.original_text, text + "\n"))
                
                # Translate
                target = self.target_lang.get()
                if target and target != 'en':
                    try:
                        translated = GoogleTranslator(source='auto', target=target).translate(text)
                        # Update translation (append)
                        self.root.after(0, lambda: self.append_text(self.translated_text, translated + "\n"))
                    except Exception:
                        pass  # Skip translation errors in real-time
                else:
                    self.root.after(0, lambda: self.append_text(self.translated_text, text + "\n"))
                
        except Exception as e:
            # Don't show errors in real-time mode to avoid spam
            pass

    def append_text(self, text_widget, text):
        """Append text to widget and auto-scroll"""
        text_widget.insert(tk.END, text)
        text_widget.see(tk.END)

    def load_model_thread(self):
        """Load Whisper Large V3 Turbo model"""
        def load_model():
            try:
                self.update_status("Loading Whisper Large V3 Turbo...")

                device = "cuda:0" if torch.cuda.is_available() else "cpu"
                torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

                model_id = "openai/whisper-large-v3-turbo"
                model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    model_id,
                    torch_dtype=torch_dtype,
                    low_cpu_mem_usage=True,
                    use_safetensors=True
                )
                model.to(device)

                processor = AutoProcessor.from_pretrained(model_id)

                self.whisper_pipe = pipeline(
                    "automatic-speech-recognition",
                    model=model,
                    tokenizer=processor.tokenizer,
                    feature_extractor=processor.feature_extractor,
                    torch_dtype=torch_dtype,
                    device=device,
                    return_timestamps=True,
                    generate_kwargs={"task": "transcribe"}
                )

                self.model_loaded = True
                device_name = "GPU" if torch.cuda.is_available() else "CPU"
                self.update_status(f"Turbo Ready! Running on {device_name}")

            except Exception as e:
                self.update_status(f"Model Error: {str(e)}")

        threading.Thread(target=load_model, daemon=True).start()

    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))

    def update_timer(self):
        """Update recording timer"""
        if self.recording:
            elapsed = time.time() - self.recording_start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.root.after(100, self.update_timer)

    def toggle_recording(self):
        if not self.model_loaded:
            messagebox.showerror("Error", "Whisper model still loading! Please wait...")
            return

        # Don't allow regular recording if real-time is active
        if self.realtime_active:
            messagebox.showinfo("Info", "Real-time mode is active. Disable it first.")
            return

        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        self.frames = []
        self.recording_start_time = time.time()

        self.record_btn.config(
            text="STOP RECORDING",
            bg=ERROR_COLOR,
            activebackground='#ff3838'
        )
        self.update_status("Recording... Speak clearly!")
        self.update_timer()

        def record():
            try:
                stream = self.audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK
                )

                while self.recording:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    self.frames.append(data)

                stream.stop_stream()
                stream.close()

            except Exception as e:
                self.update_status(f"Recording error: {str(e)}")

        threading.Thread(target=record, daemon=True).start()

    def stop_recording(self):
        self.recording = False
        self.record_btn.config(
            text="START RECORDING",
            bg=ACCENT_COLOR,
            activebackground='#00cc6a'
        )
        self.timer_label.config(text="00:00")
        self.update_status("Processing with Whisper Turbo...")

        threading.Thread(target=self.process_audio, daemon=True).start()

    def process_audio(self):
        try:
            if not self.frames:
                self.update_status("No audio recorded!")
                return

            # Process audio
            processing_start = time.time()
            
            audio_data = np.frombuffer(b''.join(self.frames), dtype=np.int16)
            audio_float = audio_data.astype(np.float32) / 32768.0

            if RATE != 16000:
                audio_float = librosa.resample(audio_float, orig_sr=RATE, target_sr=16000)

            # Whisper transcription
            result = self.whisper_pipe(audio_float)
            original_text = result["text"].strip()

            if not original_text:
                self.update_status("No speech detected!")
                return

            # Update original text
            self.root.after(0, lambda: self.original_text.delete('1.0', tk.END))
            self.root.after(0, lambda: self.original_text.insert('1.0', original_text))

            # Translation
            target = self.target_lang.get()
            try:
                if target and target != 'en':
                    translated = GoogleTranslator(source='auto', target=target).translate(original_text)
                    translated_text = translated
                else:
                    translated_text = original_text
            except Exception as e:
                translated_text = f"Translation error: {str(e)}"

            # Update translation
            self.root.after(0, lambda: self.translated_text.delete('1.0', tk.END))
            self.root.after(0, lambda: self.translated_text.insert('1.0', translated_text))

            # Performance stats
            processing_time = time.time() - processing_start
            lang_name = self.lang_names.get(target, target.upper())
            self.update_status(f"Complete! {lang_name} ({processing_time:.1f}s)")

        except Exception as e:
            self.update_status(f"Processing error: {str(e)}")

    def clear_text(self):
        self.original_text.delete('1.0', tk.END)
        self.translated_text.delete('1.0', tk.END)
        self.timer_label.config(text="00:00")
        self.update_status("Ready for next recording!")

    def run(self):
        try:
            self.root.mainloop()
        finally:
            # Clean shutdown
            self.realtime_active = False
            if hasattr(self, 'audio'):
                self.audio.terminate()


def main():
    # TikTok demo configurations
    demo_configs = {
        "main_screen": (WindowPosition.CENTER, 0, 0, 0),
        "side_monitor": (WindowPosition.LEFT_CENTER, 1, 100, -150),
        "corner_demo": (WindowPosition.TOP_RIGHT, 0, -50, 50),
        "presentation": (WindowPosition.BOTTOM_CENTER, 0, 0, -100)
    }
    
    # Choose configuration
    config = demo_configs["side_monitor"]  # Change this for different setups
    position, monitor, offset_x, offset_y = config
    
    print(f"Starting VoiceBridge AI at position: {position} on monitor {monitor}")
    app = VoiceBridgeAI(
        window_position=position,
        monitor_index=monitor,
        offset_x=offset_x,
        offset_y=offset_y
    )
    
    app.run()


if __name__ == "__main__":
    print("Starting VoiceBridge AI with Whisper Large V3 Turbo...")
    main()