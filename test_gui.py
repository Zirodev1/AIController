"""
Professional GUI interface for the AI system.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import time
from datetime import datetime
from PIL import Image, ImageTk
import cv2
import numpy as np
from ai_core.speech.voice_input import VoiceInput
from ai_core.speech.speech_engine import SpeechEngine
from ai_core.emotions.emotion_engine import EmotionEngine
from ai_core.llm.llm_interface import LLMInterface
from ai_core.nlp.text_processor import TextProcessor
from ai_core.vision.vision_system import VisionSystem
# TODO: Re-enable social media integration once the API key issue is resolved
# from ai_core.social.social_ai import SocialAI
# from ai_core.platforms.platform_manager import Platform
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernTheme:
    """Modern color scheme and styling."""
    # Colors
    PRIMARY = "#2196F3"  # Blue
    SECONDARY = "#FF4081"  # Pink
    BACKGROUND = "#FFFFFF"  # White
    SURFACE = "#F5F5F5"  # Light Gray
    TEXT = "#212121"  # Dark Gray
    TEXT_SECONDARY = "#757575"  # Medium Gray
    
    # Styles
    BUTTON_STYLE = {
        'background': PRIMARY,
        'foreground': 'white',
        'padding': (10, 5)
    }
    
    FRAME_STYLE = {
        'background': SURFACE,
        'padding': 10
    }
    
    LABEL_STYLE = {
        'background': SURFACE,
        'foreground': TEXT
    }

class AIGUI:
    def __init__(self, root):
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        self.root = root
        self.root.title("AI Companion")
        self.root.geometry("1200x800")
        
        # Initialize AI components
        self.voice_input = None
        self.speech_engine = SpeechEngine()
        self.emotion_engine = EmotionEngine()
        self.llm = LLMInterface()
        self.text_processor = TextProcessor()
        self.vision_system = VisionSystem()
        # TODO: Re-enable social media integration once the API key issue is resolved
        # self.social_ai = SocialAI(api_key="your-api-key")  # Replace with actual API key
        
        # GUI state variables
        self.is_listening = False
        self.is_push_to_talk = False
        self.message_queue = queue.Queue()
        self.typing_speed = 50
        self.is_typing = False
        self.current_voice_name = "Zira"
        
        # Interaction mode flags
        self.use_voice_input = True
        self.use_voice_output = True
        self.use_vision = True
        
        # Create main menu
        self._create_menu()
        
        # Create main interface
        self._create_gui()
        
        # Start message processing
        self.process_messages()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Apply modern theme
        self._apply_theme()

    def _create_menu(self):
        """Create the main menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Voice Input", variable=tk.BooleanVar(value=self.use_voice_input),
                                command=self._toggle_input_mode)
        view_menu.add_checkbutton(label="Voice Output", variable=tk.BooleanVar(value=self.use_voice_output),
                                command=self._toggle_output_mode)
        view_menu.add_checkbutton(label="Vision System", variable=tk.BooleanVar(value=self.use_vision),
                                command=self._toggle_vision)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Test Vision", command=self._test_vision)
        tools_menu.add_command(label="Test Emotions", command=self._test_emotions)
        # TODO: Re-enable social media testing once the API key issue is resolved
        # tools_menu.add_command(label="Test Social", command=self._test_social)

    def _create_gui(self):
        """Create the main GUI elements."""
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left panel - Controls
        left_panel = ttk.LabelFrame(main_container, text="Controls", padding="5")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(left_panel)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Voice tab
        voice_frame = ttk.Frame(notebook)
        notebook.add(voice_frame, text="Voice")
        self._create_voice_tab(voice_frame)
        
        # Vision tab
        vision_frame = ttk.Frame(notebook)
        notebook.add(vision_frame, text="Vision")
        self._create_vision_tab(vision_frame)
        
        # TODO: Re-enable social tab once the API key issue is resolved
        # Social tab
        # social_frame = ttk.Frame(notebook)
        # notebook.add(social_frame, text="Social")
        # self._create_social_tab(social_frame)
        
        # Right panel - Output
        right_panel = ttk.Frame(main_container)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Create notebook for output tabs
        output_notebook = ttk.Notebook(right_panel)
        output_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Chat tab
        chat_frame = ttk.Frame(output_notebook)
        output_notebook.add(chat_frame, text="Chat")
        self._create_chat_tab(chat_frame)
        
        # Vision output tab
        vision_output_frame = ttk.Frame(output_notebook)
        output_notebook.add(vision_output_frame, text="Vision")
        self._create_vision_output_tab(vision_output_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(main_container, textvariable=self.status_var,
                             relief=tk.SUNKEN, padding="2")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

    def _apply_theme(self):
        """Apply the modern theme to the GUI elements."""
        # Configure ttk styles
        style = ttk.Style()
        
        # Configure common styles with explicit colors
        style.configure("TFrame", background=ModernTheme.SURFACE)
        style.configure("TLabel", background=ModernTheme.SURFACE, foreground=ModernTheme.TEXT)
        
        # Create custom button style with black text
        style.configure("Custom.TButton",
                       background=ModernTheme.PRIMARY,
                       foreground='black',
                       padding=(10, 5))
        style.map("Custom.TButton",
                 foreground=[('pressed', 'black'), ('active', 'black')],
                 background=[('pressed', ModernTheme.SECONDARY), ('active', ModernTheme.PRIMARY)])
        
        style.configure("TEntry", 
                       fieldbackground=ModernTheme.BACKGROUND,
                       foreground=ModernTheme.TEXT)
        style.configure("TCombobox", 
                       fieldbackground=ModernTheme.BACKGROUND,
                       foreground=ModernTheme.TEXT)
        style.configure("TNotebook", 
                       background=ModernTheme.SURFACE)
        style.configure("TNotebook.Tab", 
                       background=ModernTheme.SURFACE,
                       foreground=ModernTheme.TEXT)
        style.configure("TLabelframe", 
                       background=ModernTheme.SURFACE)
        style.configure("TLabelframe.Label", 
                       background=ModernTheme.SURFACE,
                       foreground=ModernTheme.TEXT)
        
        # Configure root window
        self.root.configure(background=ModernTheme.BACKGROUND)
        
        # Configure text widgets
        text_config = {
            'background': ModernTheme.BACKGROUND,
            'foreground': ModernTheme.TEXT,
            'insertbackground': ModernTheme.TEXT,
            'selectbackground': ModernTheme.PRIMARY,
            'selectforeground': 'white'
        }
        
        if hasattr(self, 'chat_text'):
            self.chat_text.configure(**text_config)
        if hasattr(self, 'vision_info'):
            self.vision_info.configure(**text_config)
            
        # Configure canvas
        if hasattr(self, 'vision_canvas'):
            self.vision_canvas.configure(background='black')
            
        # Configure status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.configure(background=ModernTheme.SURFACE, foreground=ModernTheme.TEXT)
            
        # Configure all buttons to ensure text visibility
        for widget in self.root.winfo_children():
            self._configure_child_widgets(widget)

    def _configure_child_widgets(self, widget):
        """Recursively configure all child widgets."""
        for child in widget.winfo_children():
            if isinstance(child, ttk.Button):
                child.configure(style="Custom.TButton")
            self._configure_child_widgets(child)

    def _create_voice_tab(self, parent):
        """Create the voice control tab."""
        # Voice settings
        voice_frame = ttk.LabelFrame(parent, text="Voice Settings", padding="5")
        voice_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Voice selection
        voice_select_frame = ttk.Frame(voice_frame)
        voice_select_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Voice name label
        self.voice_name_var = tk.StringVar(value=f"Current Voice: {self.current_voice_name}")
        voice_name_label = ttk.Label(voice_select_frame, textvariable=self.voice_name_var)
        voice_name_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # List voices button
        list_voices = ttk.Button(voice_frame, text="List Available Voices",
                               command=self.list_voices)
        list_voices.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Wake word settings
        wake_frame = ttk.LabelFrame(parent, text="Wake Word", padding="5")
        wake_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Wake word entry
        self.wake_word_var = tk.StringVar(value="hey ai")
        wake_entry = ttk.Entry(wake_frame, textvariable=self.wake_word_var)
        wake_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Update wake word button
        update_wake = ttk.Button(wake_frame, text="Update Wake Word",
                               command=self.update_wake_word)
        update_wake.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Voice controls
        control_frame = ttk.LabelFrame(parent, text="Voice Controls", padding="5")
        control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Push to Talk button
        self.ptt_button = ttk.Button(control_frame, text="Push to Talk")
        self.ptt_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Continuous listening toggle
        self.listen_var = tk.BooleanVar()
        self.listen_toggle = ttk.Checkbutton(control_frame, text="Continuous Listening",
                                           variable=self.listen_var,
                                           command=self.toggle_listening)
        self.listen_toggle.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Bind push-to-talk events
        self.ptt_button.bind('<ButtonPress-1>', self.start_ptt)
        self.ptt_button.bind('<ButtonRelease-1>', self.stop_ptt)

    def _create_vision_tab(self, parent):
        """Create the vision control tab."""
        # Vision settings
        vision_frame = ttk.LabelFrame(parent, text="Vision Settings", padding="5")
        vision_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Camera selection
        camera_frame = ttk.Frame(vision_frame)
        camera_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(camera_frame, text="Camera:").grid(row=0, column=0, padx=5)
        self.camera_var = tk.StringVar(value="Default")
        camera_combo = ttk.Combobox(camera_frame, textvariable=self.camera_var)
        camera_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Resolution selection
        resolution_frame = ttk.Frame(vision_frame)
        resolution_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(resolution_frame, text="Resolution:").grid(row=0, column=0, padx=5)
        self.resolution_var = tk.StringVar(value="640x480")
        resolution_combo = ttk.Combobox(resolution_frame, textvariable=self.resolution_var,
                                      values=["640x480", "1280x720", "1920x1080"])
        resolution_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Vision features
        features_frame = ttk.LabelFrame(vision_frame, text="Features", padding="5")
        features_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.face_detect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(features_frame, text="Face Detection",
                       variable=self.face_detect_var,
                       command=self._update_vision_features).grid(row=0, column=0, sticky=tk.W)
        
        self.emotion_detect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(features_frame, text="Emotion Detection",
                       variable=self.emotion_detect_var,
                       command=self._update_vision_features).grid(row=1, column=0, sticky=tk.W)
        
        self.gesture_detect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(features_frame, text="Gesture Detection",
                       variable=self.gesture_detect_var,
                       command=self._update_vision_features).grid(row=2, column=0, sticky=tk.W)
        
        # Vision controls
        control_frame = ttk.LabelFrame(parent, text="Vision Controls", padding="5")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Start/Stop vision button
        self.vision_button = ttk.Button(control_frame, text="Start Vision",
                                      command=self._toggle_vision)
        self.vision_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Capture button
        self.capture_button = ttk.Button(control_frame, text="Capture Image",
                                       command=self._capture_image)
        self.capture_button.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # List cameras button
        self.list_cameras_button = ttk.Button(control_frame, text="List Cameras",
                                            command=self._list_cameras)
        self.list_cameras_button.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Vision status
        status_frame = ttk.LabelFrame(parent, text="Status", padding="5")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.vision_status_var = tk.StringVar(value="Not running")
        ttk.Label(status_frame, textvariable=self.vision_status_var).grid(row=0, column=0, sticky=tk.W)
        
        self.fps_var = tk.StringVar(value="FPS: 0")
        ttk.Label(status_frame, textvariable=self.fps_var).grid(row=1, column=0, sticky=tk.W)

    def _create_chat_tab(self, parent):
        """Create the chat interface tab."""
        # Chat display
        self.chat_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD)
        self.chat_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input frame
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Text input
        self.text_input = ttk.Entry(input_frame)
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        # Send button
        send_button = ttk.Button(input_frame, text="Send",
                               command=self._handle_text_input)
        send_button.grid(row=0, column=1, padx=5)
        
        # Bind Enter key
        self.text_input.bind('<Return>', lambda e: self._handle_text_input())
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

    def _create_vision_output_tab(self, parent):
        """Create the vision output tab."""
        # Vision display
        self.vision_canvas = tk.Canvas(parent, bg='black')
        self.vision_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Vision info
        info_frame = ttk.LabelFrame(parent, text="Vision Information", padding="5")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.vision_info = scrolledtext.ScrolledText(info_frame, height=5)
        self.vision_info.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Bind resize event
        self.vision_canvas.bind('<Configure>', self._resize_vision_canvas)

    def _resize_vision_canvas(self, event):
        """Handle vision canvas resize."""
        if hasattr(self, 'current_photo'):
            self._update_vision_canvas(self.current_frame)

    def _update_vision_canvas(self, frame):
        """Update the vision canvas with a new frame."""
        if frame is None or not self.use_vision:
            return
            
        try:
            # Store the current frame
            self.current_frame = frame
            
            # Get canvas dimensions
            canvas_width = self.vision_canvas.winfo_width()
            canvas_height = self.vision_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return  # Canvas not properly initialized yet
            
            # Calculate scaling to fit frame in canvas while maintaining aspect ratio
            frame_height, frame_width = frame.shape[:2]
            scale = min(canvas_width/frame_width, canvas_height/frame_height)
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            # Resize frame
            resized = cv2.resize(frame, (new_width, new_height))
            
            # Convert to PhotoImage
            image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            self.current_photo = ImageTk.PhotoImage(image=image)
            
            # Update canvas
            self.vision_canvas.delete("all")
            self.vision_canvas.create_image(
                canvas_width//2, canvas_height//2,
                image=self.current_photo,
                anchor=tk.CENTER
            )
        except Exception as e:
            self.logger.error(f"Error updating vision canvas: {e}")

    def _update_vision_info(self):
        """Update the vision information display."""
        if self.use_vision:
            info = self.vision_system.get_info()
            self.vision_info.delete(1.0, tk.END)
            self.vision_info.insert(tk.END, f"Camera Status: {info.camera_status}\n")
            self.vision_info.insert(tk.END, f"FPS: {info.fps:.1f}\n")
            self.vision_info.insert(tk.END, f"Face Detected: {info.face_detected}\n")
            if info.face_detected:
                self.vision_info.insert(tk.END, f"Face Location: {info.face_location}\n")
            
            # Update status bar
            self.vision_status_var.set(f"Status: {info.camera_status}")
            self.fps_var.set(f"FPS: {info.fps:.1f}")

    def _toggle_vision(self):
        """Toggle the vision system."""
        if self.use_vision:
            self.vision_system.stop()
            self.vision_button.configure(text="Start Vision")
            self.vision_status_var.set("Stopped")
            self.use_vision = False
        else:
            try:
                # Update status to show initialization
                self.vision_status_var.set("Initializing camera...")
                self.root.update()  # Force GUI update
                
                # Get camera settings
                width, height = map(int, self.resolution_var.get().split('x'))
                camera_index = 0  # Default to first camera
                if self.camera_var.get() != "Default":
                    try:
                        camera_index = int(self.camera_var.get().split()[-1])
                    except ValueError:
                        self.logger.warning("Invalid camera selection, using default")
                
                # Initialize camera in a separate thread
                def init_camera():
                    try:
                        # Start vision system with settings
                        success = self.vision_system.start(
                            camera_index=camera_index,
                            width=width,
                            height=height
                        )
                        
                        if success:
                            self.root.after(0, lambda: self._on_camera_ready())
                        else:
                            self.root.after(0, lambda: self._on_camera_error("Failed to initialize camera"))
                            
                    except Exception as e:
                        self.root.after(0, lambda: self._on_camera_error(str(e)))
                
                # Start initialization thread
                threading.Thread(target=init_camera, daemon=True).start()
                
            except Exception as e:
                self._on_camera_error(str(e))

    def _on_camera_ready(self):
        """Called when camera is successfully initialized."""
        self.vision_button.configure(text="Stop Vision")
        self.vision_status_var.set("Running")
        self.use_vision = True
        self._start_vision_update()

    def _on_camera_error(self, error_msg):
        """Called when camera initialization fails."""
        self.vision_status_var.set(f"Error: {error_msg}")
        self.logger.error(f"Error starting vision system: {error_msg}")
        self.use_vision = False
        self.vision_button.configure(text="Start Vision")

    def _start_vision_update(self):
        """Start the vision update thread."""
        def update_vision():
            while self.use_vision:
                try:
                    frame = self.vision_system.capture_image()
                    if frame is not None and frame.size > 0:  # Check if frame is valid
                        self._update_vision_canvas(frame)
                        self._update_vision_info()
                    else:
                        self.logger.warning("Received invalid frame from camera")
                except Exception as e:
                    self.logger.error(f"Error updating vision: {e}")
                    # Stop vision system on error
                    self.use_vision = False
                    self.vision_button.configure(text="Start Vision")
                    self.vision_status_var.set("Error: Camera disconnected")
                    break
                time.sleep(0.01)  # Small delay to prevent CPU overuse
        
        self.vision_update_thread = threading.Thread(target=update_vision)
        self.vision_update_thread.daemon = True
        self.vision_update_thread.start()

    def _capture_image(self):
        """Capture an image from the vision system."""
        if self.use_vision:
            frame = self.vision_system.capture_image()
            if frame is not None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"captured_image_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                self.vision_info.insert(tk.END, f"\nImage saved as {filename}\n")
            else:
                self.vision_info.insert(tk.END, "\nFailed to capture image\n")

    def _list_cameras(self):
        """List available cameras."""
        self.vision_info.delete(1.0, tk.END)
        self.vision_info.insert(tk.END, "Checking available cameras...\n")
        
        available_cameras = []
        for i in range(10):  # Check first 10 indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(f"Camera {i}")
                    self.vision_info.insert(tk.END, f"Camera {i} is available\n")
                cap.release()
        
        # Update camera combo box
        self.camera_var.set("Default")
        camera_combo = self.camera_var.master
        camera_combo['values'] = ["Default"] + available_cameras

    def _update_vision_features(self):
        """Update vision features based on checkboxes."""
        # This will be implemented when we add feature toggling
        pass

    def _toggle_input_mode(self):
        """Toggle between voice and text input."""
        self.use_voice_input = self.user_mode_var.get()
        self._update_ui_state()
        
        # Stop listening if switching to text mode
        if not self.use_voice_input and self.is_listening:
            self.stop_listening()

    def _toggle_output_mode(self):
        """Toggle between voice and text output."""
        self.use_voice_output = self.ai_mode_var.get()

    def _update_ui_state(self):
        """Update UI elements based on current mode."""
        # Enable/disable voice controls
        for widget in [self.ptt_button, self.listen_toggle]:
            widget.configure(state='normal' if self.use_voice_input else 'disabled')
        
        # Enable/disable text input
        self.text_input.configure(state='normal' if not self.use_voice_input else 'disabled')
        
        # Update status message
        mode = "voice" if self.use_voice_input else "text"
        self.status_var.set(f"Using {mode} input")

    def _handle_text_input(self):
        """Process text input from the entry field."""
        text = self.text_input.get().strip()
        if text:
            self.text_input.delete(0, tk.END)
            self._process_input(text)

    def _process_input(self, text: str):
        """Process input regardless of source (voice or text)."""
        self.add_message("You", text, animate=False)
        self.status_var.set("Processing input...")
        
        try:
            # Process input
            nlp_analysis = self.text_processor.process_text(text)
            self.emotion_engine.process_text(text)
            emotional_state = self.emotion_engine.get_emotional_state()
            
            # Generate response
            response = self.llm.generate_response(emotional_state, text)
            
            # Handle response output
            if self.use_voice_output:
                # If using voice, show text immediately and speak
                self.add_message(self.current_voice_name, response, animate=False)
                self.speech_engine.speak(response)
            else:
                # If text only, animate the response
                self.add_message(self.current_voice_name, response, animate=True)
            
        finally:
            self.status_var.set("Ready")

    def _initialize_voice_input(self):
        """Initialize or reinitialize the voice input component."""
        if self.voice_input:
            self.voice_input.stop_listening()  # Ensure old instance is stopped
            
        self.voice_input = VoiceInput(wake_word=self.wake_word_var.get())
        self.voice_input.set_callbacks(
            on_wake_word=self._handle_wake_word,
            on_command_received=self._handle_command
        )
        self.add_message("System", "Voice input system initialized")
        self.status_var.set("Ready")

    def _reset_voice_input(self):
        """Reset the voice input system."""
        self.status_var.set("Resetting voice input...")
        if self.is_listening:
            self.stop_listening()
        self._initialize_voice_input()
        self.add_message("System", "Voice input system reset complete")

    def start_listening(self, background=False):
        """Start listening with proper state management."""
        if not self.voice_input:
            self._initialize_voice_input()
        
        if not self.is_listening:
            self.is_listening = True
            self.voice_input.start_listening(background=background)
            self.status_var.set("Listening..." if not background else "Listening for wake word...")
            self.add_message("System", "Started listening" if not background else "Listening for wake word")

    def stop_listening(self):
        """Stop listening with proper state management."""
        if self.is_listening and self.voice_input:
            self.is_listening = False
            self.voice_input.stop_listening()
            self.status_var.set("Ready")
            self.add_message("System", "Stopped listening")

    def start_ptt(self, event):
        """Handle push-to-talk button press."""
        if not self.is_listening:
            self.start_listening(background=False)

    def stop_ptt(self, event):
        """Handle push-to-talk button release."""
        if self.is_listening:
            self.stop_listening()

    def toggle_listening(self):
        """Toggle continuous listening mode."""
        if self.listen_var.get():
            self.start_listening(background=True)
        else:
            self.stop_listening()

    def update_wake_word(self):
        """Update the wake word."""
        new_wake_word = self.wake_word_var.get().strip()
        if new_wake_word:
            self._reset_voice_input()  # Reinitialize with new wake word

    def set_voice(self, voice_name: str):
        """Set the current voice and update the display."""
        self.current_voice_name = voice_name
        self.voice_name_var.set(f"Current Voice: {voice_name}")
        self.add_message("System", f"Switched to voice: {voice_name}", animate=False)

    def list_voices(self):
        """List available voices and allow selection."""
        voices = self.speech_engine.list_voices()
        if voices:
            self.add_message("System", "Available voices:", animate=False)
            for voice in voices:
                self.add_message("System", f"- {voice}", animate=False)
            
            # If we have the current voice in the list, update the display
            current = self.speech_engine.get_current_voice()
            if current:
                self.set_voice(current)

    def _handle_wake_word(self):
        """Handle wake word detection."""
        self.status_var.set("Wake word detected!")
        self.add_message("System", "Wake word detected!", animate=False)
        
        # Set speaking state and respond
        self.voice_input.set_speaking_state(True)
        response = "*perking up* Yes? I'm listening!"
        
        if self.use_voice_output:
            self.add_message(self.current_voice_name, response, animate=False)
            self.speech_engine.speak(response)
        else:
            self.add_message(self.current_voice_name, response, animate=True)
        
        # Reset speaking state
        time.sleep(0.5)
        self.voice_input.set_speaking_state(False)

    def _handle_command(self, text: str):
        """Handle received command."""
        self._process_input(text)

    def add_message(self, sender: str, message: str, animate=False):
        """Add a message to the queue for display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}] {sender}: "
        
        if not animate:
            # Add message immediately to queue
            self.message_queue.put((prefix + message + "\n", False))
        else:
            # Add prefix without animation
            self.message_queue.put((prefix, False))
            # Add message with animation
            self.message_queue.put((message + "\n", True))

    def process_messages(self):
        """Process and display queued messages."""
        if not self.is_typing:
            try:
                while True:
                    message, should_animate = self.message_queue.get_nowait()
                    if should_animate:
                        # Start typing animation for this message
                        self.is_typing = True
                        self._animate_typing(message, 0)
                    else:
                        # Display message immediately
                        self.conv_text.insert(tk.END, message)
                        self.conv_text.see(tk.END)
            except queue.Empty:
                pass
        
        # Schedule next update
        self.root.after(100, self.process_messages)

    def _animate_typing(self, message, index):
        """Animate typing effect for a message."""
        if index < len(message):
            # Add next character
            self.conv_text.insert(tk.END, message[index])
            self.conv_text.see(tk.END)
            # Schedule next character
            self.root.after(self.typing_speed, 
                          lambda: self._animate_typing(message, index + 1))
        else:
            # Animation complete
            self.is_typing = False

    def _on_closing(self):
        """Handle window closing event."""
        if self.use_vision:
            self.vision_system.stop()
        if self.voice_input:
            self.voice_input.stop_listening()
        self.root.destroy()

    def _test_vision(self):
        """Run vision system tests."""
        try:
            # Create test window
            test_window = tk.Toplevel(self.root)
            test_window.title("Vision Test")
            test_window.geometry("800x600")
            
            # Create vision display
            vision_canvas = tk.Canvas(test_window, bg='black')
            vision_canvas.pack(fill=tk.BOTH, expand=True)
            
            # Create info display
            info_text = scrolledtext.ScrolledText(test_window, height=5)
            info_text.pack(fill=tk.X, padx=5, pady=5)
            
            # Test controls
            control_frame = ttk.Frame(test_window)
            control_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Start/Stop button
            is_running = False
            def toggle_test():
                nonlocal is_running
                if is_running:
                    is_running = False
                    toggle_button.configure(text="Start Test")
                    info_text.insert(tk.END, "Test stopped\n")
                else:
                    is_running = True
                    toggle_button.configure(text="Stop Test")
                    info_text.insert(tk.END, "Test started\n")
                    run_test()
            
            toggle_button = ttk.Button(control_frame, text="Start Test",
                                    command=toggle_test)
            toggle_button.pack(side=tk.LEFT, padx=5)
            
            # Capture button
            def capture():
                if self.vision_system.is_running:
                    frame = self.vision_system.capture_image()
                    if frame is not None:
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"test_capture_{timestamp}.jpg"
                        cv2.imwrite(filename, frame)
                        info_text.insert(tk.END, f"Image saved as {filename}\n")
                    else:
                        info_text.insert(tk.END, "Failed to capture image\n")
                else:
                    info_text.insert(tk.END, "Vision system not running\n")
            
            capture_button = ttk.Button(control_frame, text="Capture",
                                     command=capture)
            capture_button.pack(side=tk.LEFT, padx=5)
            
            # Test function
            def run_test():
                if not is_running:
                    return
                
                try:
                    frame = self.vision_system.capture_image()
                    if frame is not None:
                        # Update canvas
                        canvas_width = vision_canvas.winfo_width()
                        canvas_height = vision_canvas.winfo_height()
                        
                        # Calculate scaling
                        frame_height, frame_width = frame.shape[:2]
                        scale = min(canvas_width/frame_width, canvas_height/frame_height)
                        new_width = int(frame_width * scale)
                        new_height = int(frame_height * scale)
                        
                        # Resize and display
                        resized = cv2.resize(frame, (new_width, new_height))
                        image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                        image = Image.fromarray(image)
                        photo = ImageTk.PhotoImage(image=image)
                        
                        vision_canvas.delete("all")
                        vision_canvas.create_image(
                            canvas_width//2, canvas_height//2,
                            image=photo,
                            anchor=tk.CENTER
                        )
                        vision_canvas.image = photo  # Keep reference
                        
                        # Update info
                        info = self.vision_system.get_info()
                        info_text.delete(1.0, tk.END)
                        info_text.insert(tk.END, f"Camera Status: {info.camera_status}\n")
                        info_text.insert(tk.END, f"FPS: {info.fps:.1f}\n")
                        info_text.insert(tk.END, f"Face Detected: {info.face_detected}\n")
                        if info.face_detected:
                            info_text.insert(tk.END, f"Face Location: {info.face_location}\n")
                    
                except Exception as e:
                    info_text.insert(tk.END, f"Error: {str(e)}\n")
                
                # Schedule next update
                if is_running:
                    test_window.after(10, run_test)
            
            # Handle window closing
            def on_test_close():
                nonlocal is_running
                is_running = False
                test_window.destroy()
            
            test_window.protocol("WM_DELETE_WINDOW", on_test_close)
            
        except Exception as e:
            self.logger.error(f"Error in vision test: {e}")
            tk.messagebox.showerror("Error", f"Failed to start vision test: {str(e)}")

    def _test_emotions(self):
        """Run emotion system tests."""
        try:
            # Create test window
            test_window = tk.Toplevel(self.root)
            test_window.title("Emotion Test")
            test_window.geometry("600x400")
            
            # Create emotion display
            emotion_frame = ttk.LabelFrame(test_window, text="Emotional State", padding="5")
            emotion_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            emotion_text = scrolledtext.ScrolledText(emotion_frame)
            emotion_text.pack(fill=tk.BOTH, expand=True)
            
            # Test controls
            control_frame = ttk.Frame(test_window)
            control_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Input frame
            input_frame = ttk.Frame(control_frame)
            input_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(input_frame, text="Test Text:").pack(side=tk.LEFT, padx=5)
            test_input = ttk.Entry(input_frame)
            test_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            def process_input():
                text = test_input.get().strip()
                if text:
                    # Process text through emotion engine
                    self.emotion_engine.process_text(text)
                    state = self.emotion_engine.get_emotional_state()
                    
                    # Display results
                    emotion_text.delete(1.0, tk.END)
                    emotion_text.insert(tk.END, f"Input: {text}\n\n")
                    emotion_text.insert(tk.END, "Emotional State:\n")
                    emotion_text.insert(tk.END, f"Complex State: {state['complex_state']}\n")
                    emotion_text.insert(tk.END, f"Intensity: {state['intensity']:.2f}\n\n")
                    emotion_text.insert(tk.END, "Basic Emotions:\n")
                    for emotion, value in state['basic_emotions'].items():
                        emotion_text.insert(tk.END, f"{emotion}: {value:.2f}\n")
                    
                    test_input.delete(0, tk.END)
            
            ttk.Button(input_frame, text="Process", command=process_input).pack(side=tk.LEFT, padx=5)
            
            # Reset button
            def reset_emotions():
                self.emotion_engine.reset_state()
                emotion_text.delete(1.0, tk.END)
                emotion_text.insert(tk.END, "Emotional state reset to neutral\n")
            
            ttk.Button(control_frame, text="Reset Emotions", command=reset_emotions).pack(pady=5)
            
            # Initial state
            reset_emotions()
            
        except Exception as e:
            self.logger.error(f"Error in emotion test: {e}")
            tk.messagebox.showerror("Error", f"Failed to start emotion test: {str(e)}")

    def _show_settings(self):
        """Show the settings dialog."""
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        
        # Create notebook for settings tabs
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # General settings tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        # Voice settings tab
        voice_frame = ttk.Frame(notebook)
        notebook.add(voice_frame, text="Voice")
        
        # Vision settings tab
        vision_frame = ttk.Frame(notebook)
        notebook.add(vision_frame, text="Vision")
        
        # Add settings to general tab
        general_settings = ttk.LabelFrame(general_frame, text="General Settings", padding="5")
        general_settings.pack(fill=tk.X, padx=5, pady=5)
        
        # Theme selection
        theme_frame = ttk.Frame(general_settings)
        theme_frame.pack(fill=tk.X, pady=2)
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        theme_var = tk.StringVar(value="Modern")
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var,
                                 values=["Modern", "Classic", "Dark"])
        theme_combo.pack(side=tk.LEFT, padx=5)
        
        # Add settings to voice tab
        voice_settings = ttk.LabelFrame(voice_frame, text="Voice Settings", padding="5")
        voice_settings.pack(fill=tk.X, padx=5, pady=5)
        
        # Voice selection
        voice_select_frame = ttk.Frame(voice_settings)
        voice_select_frame.pack(fill=tk.X, pady=2)
        ttk.Label(voice_select_frame, text="Voice:").pack(side=tk.LEFT)
        voice_var = tk.StringVar(value=self.current_voice_name)
        voice_combo = ttk.Combobox(voice_select_frame, textvariable=voice_var)
        voice_combo.pack(side=tk.LEFT, padx=5)
        
        # Add settings to vision tab
        vision_settings = ttk.LabelFrame(vision_frame, text="Vision Settings", padding="5")
        vision_settings.pack(fill=tk.X, padx=5, pady=5)
        
        # Resolution selection
        resolution_frame = ttk.Frame(vision_settings)
        resolution_frame.pack(fill=tk.X, pady=2)
        ttk.Label(resolution_frame, text="Resolution:").pack(side=tk.LEFT)
        resolution_var = tk.StringVar(value=self.resolution_var.get())
        resolution_combo = ttk.Combobox(resolution_frame, textvariable=resolution_var,
                                      values=["640x480", "1280x720", "1920x1080"])
        resolution_combo.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def apply_settings():
            """Apply the selected settings."""
            # Update voice
            if voice_var.get() != self.current_voice_name:
                self.set_voice(voice_var.get())
            
            # Update resolution
            if resolution_var.get() != self.resolution_var.get():
                self.resolution_var.set(resolution_var.get())
                if self.use_vision:
                    width, height = map(int, resolution_var.get().split('x'))
                    self.vision_system.set_resolution(width, height)
            
            # Update theme
            if theme_var.get() != "Modern":  # Currently only Modern theme is implemented
                self.logger.warning(f"Theme '{theme_var.get()}' not yet implemented")
            
            settings_window.destroy()
        
        ttk.Button(button_frame, text="Apply", command=apply_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT)

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = AIGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 