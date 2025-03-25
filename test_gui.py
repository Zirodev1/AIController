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
    PRIMARY_DARK = "#1976D2"  # Darker blue for pressed state
    PRIMARY_LIGHT = "#64B5F6"  # Lighter blue for hover
    SECONDARY = "#FF4081"  # Pink
    BACKGROUND = "#FFFFFF"  # White
    SURFACE = "#F5F5F5"  # Light Gray
    TEXT = "#212121"  # Dark Gray
    TEXT_SECONDARY = "#757575"  # Medium Gray
    TEXT_ON_PRIMARY = "#000000"  # Black text on primary color
    ERROR = "#F44336"  # Red for errors
    SUCCESS = "#4CAF50"  # Green for success
    
    # Styles
    BUTTON_STYLE = {
        'background': PRIMARY,
        'foreground': TEXT_ON_PRIMARY,
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
        
        # Initialize basic components only
        self.voice_input = None
        self.speech_engine = SpeechEngine()
        self.emotion_engine = EmotionEngine()
        self.llm = LLMInterface()
        self.text_processor = TextProcessor()
        
        # Defer vision system initialization
        self.vision_system = None
        
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
        self.use_vision = False  # Start with vision disabled
        
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

        # Log successful initialization
        self.logger.info("GUI initialized successfully")

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
                       foreground=ModernTheme.TEXT_ON_PRIMARY,
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
        """Update the vision canvas with a new frame using a simplified approach."""
        if frame is None or not self.use_vision:
            return
            
        try:
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

    def _update_vision_info(self, info=None):
        """Update the vision information display."""
        if self.use_vision and self.vision_system:
            try:
                # Get info from the vision system if not provided
                if info is None:
                    info = self.vision_system.get_info()
                
                # Clear the info display
                self.vision_info.delete(1.0, tk.END)
                
                # Add basic camera info
                self.vision_info.insert(tk.END, f"Camera Status: {info.camera_status}\n")
                self.vision_info.insert(tk.END, f"FPS: {info.fps:.1f}\n")
                
                # Add face detection info directly from VisionSystem
                self.vision_info.insert(tk.END, f"Face Detected: {info.face_detected}\n")
                if info.face_detected and info.face_location is not None:
                    x, y, w, h = info.face_location
                    self.vision_info.insert(tk.END, f"Face Location: ({x}, {y}, {w}, {h})\n")
                
                # Update status bar with current status
                self.vision_status_var.set(f"Status: {info.camera_status}")
                self.fps_var.set(f"FPS: {info.fps:.1f}")
                
            except Exception as e:
                self.logger.error(f"Error updating vision info: {e}")
                self.vision_info.insert(tk.END, f"Error getting vision info: {str(e)}\n")

    def _toggle_vision(self):
        """Toggle the vision system with improved error handling."""
        if self.use_vision:
            # Stopping the vision system
            if self.vision_system:
                self.vision_system.stop()
            self.vision_button.configure(text="Start Vision")
            self.vision_status_var.set("Stopped")
            self.use_vision = False
        else:
            # First ensure vision system is initialized
            if not self._initialize_vision_system():
                tk.messagebox.showerror("Vision System Error", 
                                      "Failed to initialize vision system")
                return
                
            try:
                # Update status to show initialization
                self.vision_status_var.set("Initializing camera...")
                self.root.update()  # Force GUI update
                
                # Get camera settings - we'll apply these directly to the vision system
                width, height = map(int, self.resolution_var.get().split('x'))
                camera_index = 0  # Default to first camera
                if self.camera_var.get() != "Default":
                    try:
                        camera_index = int(self.camera_var.get().split()[-1])
                    except ValueError:
                        self.logger.warning("Invalid camera selection, using default")
                
                # Set vision system properties before starting
                if hasattr(self.vision_system, "set_camera_index"):
                    self.vision_system.set_camera_index(camera_index)
                    
                if hasattr(self.vision_system, "set_resolution"):
                    self.vision_system.set_resolution(width, height)
                
                # Initialize camera in a separate thread
                def init_camera():
                    try:
                        # Start vision system without arguments
                        success = self.vision_system.start()
                        
                        if success:
                            self.root.after(0, self._on_camera_ready)
                        else:
                            error_msg = "Failed to initialize camera"
                            self.root.after(0, lambda: self._on_camera_error(error_msg))
                            
                    except Exception as exc:
                        error_msg = str(exc)
                        self.root.after(0, lambda: self._on_camera_error(error_msg))
                
                # Start initialization thread
                threading.Thread(target=init_camera, daemon=True).start()
                
            except Exception as e:
                self._on_camera_error(str(e))
                
    def _on_camera_ready(self):
        """Called when camera is successfully initialized."""
        self.vision_button.configure(text="Stop Vision")
        self.vision_status_var.set("Running")
        # Add a visual indicator of success
        self.status_var.set("Camera initialized successfully")
        self.use_vision = True
        
        # Switch to Vision tab in the output notebook to show camera feed
        for notebook in self.root.winfo_children():
            if isinstance(notebook, ttk.Notebook):
                for idx, tab_id in enumerate(notebook.tabs()):
                    tab_name = notebook.tab(tab_id, "text")
                    if tab_name == "Vision":
                        notebook.select(idx)
                        break
        
        # Start the vision update thread
        self._start_vision_update()
        
        # Display a message in the vision info panel
        self.vision_info.delete(1.0, tk.END)
        self.vision_info.insert(tk.END, "Camera is now active!\n")
        self.vision_info.insert(tk.END, "If you don't see an image, try the following:\n")
        self.vision_info.insert(tk.END, "1. Wait a moment for the camera to stabilize\n")
        self.vision_info.insert(tk.END, "2. Make sure your camera is properly connected\n")
        self.vision_info.insert(tk.END, "3. Try selecting a different camera from the dropdown\n")
        self.vision_info.insert(tk.END, "4. Try a different resolution\n")

    def _on_camera_error(self, error_msg):
        """Called when camera initialization fails."""
        self.vision_status_var.set(f"Error: {error_msg}")
        self.logger.error(f"Error starting vision system: {error_msg}")
        self.use_vision = False
        self.vision_button.configure(text="Start Vision")
        # Show error in status bar
        self.status_var.set(f"Camera error: {error_msg}")

    def _start_vision_update(self):
        """Start the vision update thread with enhanced error recovery."""
        def update_vision():
            failure_count = 0
            max_failures = 15  # Allow more failures before giving up
            recovery_attempts = 0
            max_recovery_attempts = 3
            
            # Set initial times
            last_frame_time = 0
            last_info_update_time = 0
            last_recovery_time = 0
            
            # Timing controls
            min_frame_interval = 0.033  # About 30fps max for frame capture
            info_update_interval = 0.2  # Update info display every 0.2 seconds
            
            # Initial dummy frame for displaying error messages
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, "Waiting for camera...", (100, 240),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # First show waiting message
            self.root.after(0, lambda f=error_frame: self._update_vision_canvas(f))
            
            while self.use_vision:
                try:
                    # Make sure the vision system is still running
                    if not hasattr(self.vision_system, 'is_running') or not self.vision_system.is_running:
                        self.logger.warning("Vision system not running. Stopping update thread.")
                        break
                    
                    # Control capture timing
                    current_time = time.time()
                    if current_time - last_frame_time < min_frame_interval:
                        time.sleep(0.001)  # Small sleep to avoid CPU spinning
                        continue
                        
                    # Update frame time
                    last_frame_time = current_time
                    
                    # Get frame from vision system (it will handle face detection internally)
                    frame = self.vision_system.capture_image()
                    
                    # If we got a valid frame
                    if frame is not None and frame.size > 0:
                        # Check if this is a black/empty frame (sometimes returned as fallback)
                        # Sum up pixel values - if very low, likely a black/dummy frame
                        frame_brightness = np.sum(frame)
                        if frame_brightness < 1000:  # Very dark frame threshold
                            # This is likely a dummy/error frame
                            failure_count += 1
                            self.logger.warning(f"Received likely dummy frame ({failure_count}/{max_failures})")
                            
                            # Create a message frame
                            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                            cv2.putText(error_frame, f"Camera recovering... ({failure_count}/{max_failures})", 
                                      (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            
                            # Update display with error message
                            self.root.after(0, lambda f=error_frame: self._update_vision_canvas(f))
                            
                            # Try to recover if needed
                            if failure_count % 5 == 0 and recovery_attempts < max_recovery_attempts:
                                self._attempt_camera_recovery()
                                recovery_attempts += 1
                                last_recovery_time = current_time
                            
                            # Check if we've had too many failures
                            if failure_count >= max_failures:
                                raise Exception("Too many consecutive frame capture failures")
                            
                            # Add delay between attempts
                            time.sleep(0.5)
                            continue
                        
                        # Get vision info (including face detection results)
                        info = self.vision_system.get_info()
                        
                        # Reset failure counters on success
                        failure_count = 0
                        # Reset recovery attempts if it's been a while since last recovery
                        if current_time - last_recovery_time > 30:
                            recovery_attempts = 0
                        
                        # Store original frame
                        self.current_frame = frame.copy()
                        
                        # Create a copy for drawing face detection results
                        display_frame = frame.copy()
                        
                        # Draw face detection results from the VisionSystem
                        if info.face_detected and info.face_location:
                            # Draw rectangle around face
                            x, y, w, h = info.face_location
                            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            
                            # Add face detection text
                            cv2.putText(display_frame, "Face Detected", (10, 30),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Update the display with the frame containing face detection
                        self.root.after(0, lambda f=display_frame: self._update_vision_canvas(f))
                        
                        # Update information display periodically
                        if current_time - last_info_update_time >= info_update_interval:
                            self.root.after(0, lambda: self._update_vision_info(info))
                            last_info_update_time = current_time
                    else:
                        # Frame capture failed
                        failure_count += 1
                        self.logger.warning(f"Failed to capture frame ({failure_count}/{max_failures})")
                        
                        # Create a message frame
                        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                        cv2.putText(error_frame, f"No camera feed ({failure_count}/{max_failures})", 
                                  (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        # Update display with error message
                        self.root.after(0, lambda f=error_frame: self._update_vision_canvas(f))
                        
                        # Try to recover if needed
                        if failure_count % 5 == 0 and recovery_attempts < max_recovery_attempts:
                            self._attempt_camera_recovery()
                            recovery_attempts += 1
                            last_recovery_time = current_time
                        
                        if failure_count >= max_failures:
                            raise Exception("Too many consecutive frame capture failures")
                        
                        # Add delay on failure to allow camera to recover
                        time.sleep(0.5)
                    
                except cv2.error as e:
                    error_msg = str(e)
                    self.logger.error(f"OpenCV error: {error_msg}")
                    
                    # For matrix assertion errors, add a longer delay
                    if "error: (-215:Assertion failed) _step >= minstep" in error_msg:
                        self.logger.warning("Matrix assertion error - waiting for camera to stabilize")
                        # Display error message
                        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                        cv2.putText(error_frame, "Camera stabilizing...", (50, 240),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        self.root.after(0, lambda f=error_frame: self._update_vision_canvas(f))
                        time.sleep(1.0)
                    else:
                        # Other OpenCV errors may be more serious
                        self.root.after(0, lambda msg=error_msg: self._handle_vision_error(msg))
                        break
                
                except Exception as e:
                    error_msg = str(e)
                    self.logger.error(f"Error in vision update: {error_msg}")
                    self.root.after(0, lambda msg=error_msg: self._handle_vision_error(msg))
                    break
                
                # Small delay between frames to prevent CPU overuse
                time.sleep(0.01)
        
        # Start the thread
        self.vision_update_thread = threading.Thread(target=update_vision, daemon=True)
        self.vision_update_thread.start()
    
    def _attempt_camera_recovery(self):
        """Attempt to recover a failing camera connection."""
        self.logger.info("Attempting camera recovery...")
        
        try:
            # Only proceed if vision system is initialized
            if not hasattr(self, 'vision_system') or self.vision_system is None:
                return False
                
            # Check if camera exists
            if hasattr(self.vision_system, 'camera') and self.vision_system.camera is not None:
                # Get current camera index
                camera_index = self.vision_system.camera_index
                
                # Release the current camera
                self.vision_system.camera.release()
                time.sleep(1.0)  # Give it time to fully release
                
                # Try to reinitialize with different backends
                for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, 0] if hasattr(cv2, 'CAP_DSHOW') else [0]:
                    try:
                        # Try to open with this backend
                        self.vision_system.camera = cv2.VideoCapture(camera_index + backend)
                        
                        if self.vision_system.camera.isOpened():
                            # Successfully reopened
                            # Set camera properties
                            width = 640
                            height = 480
                            if hasattr(self.vision_system, 'camera_width'):
                                width = self.vision_system.camera_width
                            if hasattr(self.vision_system, 'camera_height'):
                                height = self.vision_system.camera_height
                                
                            self.vision_system.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                            self.vision_system.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                            
                            # Try reading a test frame
                            ret, frame = self.vision_system.camera.read()
                            if ret and frame is not None and frame.size > 0:
                                self.logger.info(f"Camera recovery successful using backend {backend}")
                                return True
                    except Exception as e:
                        self.logger.error(f"Error during camera recovery with backend {backend}: {e}")
                
                self.logger.warning("Camera recovery failed with all backends")
                return False
            else:
                self.logger.warning("No camera to recover")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in camera recovery: {e}")
            return False

    def _handle_vision_error(self, error_msg):
        """Handle vision system errors on the main thread."""
        self.use_vision = False
        self.vision_button.configure(text="Start Vision")
        self.vision_status_var.set(f"Error: {error_msg}")
        
        # Only show error dialog for serious errors
        if "Too many consecutive frame capture failures" in error_msg:
            tk.messagebox.showerror("Vision System Error", 
                                  f"The vision system encountered an error:\n{error_msg}")
                                  
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
        """List available cameras with improved error handling."""
        # First ensure vision system is initialized
        if not self._initialize_vision_system():
            self.vision_info.delete(1.0, tk.END)
            self.vision_info.insert(tk.END, "Error: Failed to initialize vision system\n")
            return
            
        self.vision_info.delete(1.0, tk.END)
        self.vision_info.insert(tk.END, "Checking available cameras...\n")
        
        def scan_cameras():
            try:
                available_cameras = []
                
                # Try both DirectShow (700) and MSMF (1400) backends on Windows
                backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF] if hasattr(cv2, 'CAP_DSHOW') else [0]
                
                for i in range(5):  # Check first 5 indices
                    self.vision_info.insert(tk.END, f"\nTesting camera {i}...\n")
                    self.root.update()  # Force update to show progress
                    
                    for backend in backends:
                        try:
                            backend_name = "DirectShow" if backend == cv2.CAP_DSHOW else "MSMF" if backend == cv2.CAP_MSMF else "Default"
                            self.vision_info.insert(tk.END, f"  Testing with {backend_name} backend...\n")
                            self.root.update()
                            
                            # Try to open camera with specific backend
                            cap = cv2.VideoCapture(i + backend)
                            if not cap.isOpened():
                                self.vision_info.insert(tk.END, f"  Could not open with {backend_name} backend\n")
                                continue
                                
                            # Try to get camera properties
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            
                            # Try to read a test frame to confirm it's working
                            ret, frame = cap.read()
                            if ret and frame is not None and frame.size > 0:
                                camera_name = f"Camera {i} ({backend_name})"
                                available_cameras.append(camera_name)
                                # Update UI with success
                                msg = f"  SUCCESS: Camera {i} working with {backend_name} backend ({width}x{height} @ {fps:.1f}fps)\n"
                                self.vision_info.insert(tk.END, msg)
                                break  # Found a working backend for this camera
                            else:
                                self.vision_info.insert(tk.END, f"  Camera opened but failed to provide a valid frame\n")
                            
                            # Always release the camera
                            cap.release()
                        except Exception as e:
                            self.logger.warning(f"Error checking camera {i} with backend {backend_name}: {e}")
                            self.vision_info.insert(tk.END, f"  Error: {str(e)}\n")
                
                # Update camera dropdown
                if available_cameras:
                    cameras_copy = available_cameras.copy()  # Make a copy for the closure
                    self.root.after(0, lambda: self._update_camera_list(cameras_copy))
                    summary = "\nFound working cameras: " + ", ".join(available_cameras) + "\n"
                    self.vision_info.insert(tk.END, summary)
                else:
                    self.root.after(0, lambda: self.vision_info.insert(tk.END, "\nNo working cameras found!\n"))
                    self.vision_info.insert(tk.END, "\nTroubleshooting tips:\n")
                    self.vision_info.insert(tk.END, "1. Check if camera is connected and powered on\n")
                    self.vision_info.insert(tk.END, "2. Make sure no other application is using the camera\n")
                    self.vision_info.insert(tk.END, "3. Try updating your camera drivers\n")
                    self.vision_info.insert(tk.END, "4. Some cameras may need specific settings or drivers\n")
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.vision_info.insert(tk.END, f"Error: {error_msg}\n"))
                
        # Run camera scan in background thread
        threading.Thread(target=scan_cameras, daemon=True).start()
        
    def _update_camera_list(self, available_cameras):
        """Update the camera dropdown with available cameras."""
        if not available_cameras:
            self.camera_var.set("Default")
            camera_combo = self.camera_var.master
            camera_combo['values'] = ["Default"]
            return
            
        self.camera_var.set(available_cameras[0])  # Select first working camera
        camera_combo = self.camera_var.master
        camera_combo['values'] = available_cameras

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
                        self.chat_text.insert(tk.END, message)
                        self.chat_text.see(tk.END)
            except queue.Empty:
                pass
        
        # Schedule next update
        self.root.after(100, self.process_messages)

    def _animate_typing(self, message, index):
        """Animate typing effect for a message."""
        if index < len(message):
            # Add next character
            self.chat_text.insert(tk.END, message[index])
            self.chat_text.see(tk.END)
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
            # First ensure vision system is initialized
            if not self._initialize_vision_system():
                tk.messagebox.showerror("Vision System Error", 
                                     "Failed to initialize vision system")
                return
            
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
                    # Make sure vision system is running
                    if not self.vision_system.is_running:
                        info_text.insert(tk.END, "Starting vision system...\n")
                        self.vision_system.start()
                        time.sleep(0.5)  # Give camera time to initialize
                    
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
                if self.vision_system.is_running:
                    self.vision_system.stop()
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

    def _initialize_vision_system(self):
        """Initialize the vision system on demand with improved error handling."""
        if self.vision_system is not None:
            # Already initialized
            return True
        
        try:
            self.vision_status_var.set("Initializing vision system...")
            self.root.update()  # Force GUI update
            
            # Create vision system
            self.vision_system = VisionSystem()
            
            # Add fallback methods if they don't exist
            if not hasattr(self.vision_system, "set_camera_index"):
                def set_camera_index(index):
                    self.logger.info(f"Setting camera index to {index} (fallback method)")
                    self.vision_system.camera_index = index
                self.vision_system.set_camera_index = set_camera_index
                
            if not hasattr(self.vision_system, "set_resolution"):
                def set_resolution(width, height):
                    self.logger.info(f"Setting resolution to {width}x{height} (fallback method)")
                    self.vision_system.camera_width = width
                    self.vision_system.camera_height = height
                self.vision_system.set_resolution = set_resolution
                
            # Override the capture_image method to be more resilient
            original_capture = self.vision_system.capture_image
            def resilient_capture():
                """More resilient frame capture that handles common issues"""
                try:
                    # Directly try to capture from camera if available
                    if hasattr(self.vision_system, 'camera') and self.vision_system.camera is not None:
                        # Try a direct camera read first
                        ret, frame = self.vision_system.camera.read()
                        if ret and frame is not None and frame.size > 0:
                            # Update the last frame time for FPS calculation
                            self.vision_system.last_frame_time = time.time()
                            return frame
                        
                        # If direct read failed, try releasing and re-opening the camera
                        self.logger.warning("Direct camera read failed, attempting to recover...")
                        self.vision_system.camera.release()
                        time.sleep(0.5)
                        
                        # Try using DirectShow backend first on Windows
                        if hasattr(cv2, 'CAP_DSHOW'):
                            self.vision_system.camera = cv2.VideoCapture(
                                self.vision_system.camera_index + cv2.CAP_DSHOW
                            )
                        else:
                            self.vision_system.camera = cv2.VideoCapture(
                                self.vision_system.camera_index
                            )
                            
                        # Check if camera opened
                        if self.vision_system.camera.isOpened():
                            # Try to read a frame
                            ret, frame = self.vision_system.camera.read()
                            if ret and frame is not None and frame.size > 0:
                                # Update the last frame time for FPS calculation
                                self.vision_system.last_frame_time = time.time()
                                return frame
                    
                    # If we reach here, fall back to the original method
                    return original_capture()
                    
                except Exception as e:
                    self.logger.error(f"Error in resilient capture: {e}")
                    # Return an empty frame to avoid returning None
                    return np.zeros((480, 640, 3), dtype=np.uint8)
                    
            # Replace the method
            self.vision_system.capture_image = resilient_capture
            
            # Patch the vision system's start method for better compatibility
            original_start = self.vision_system.start
            def patched_start():
                """Patched version of the start method with better error handling"""
                try:
                    # Try using DirectShow backend first on Windows
                    if hasattr(cv2, 'CAP_DSHOW'):
                        self.vision_system.camera = cv2.VideoCapture(
                            self.vision_system.camera_index + cv2.CAP_DSHOW
                        )
                    else:
                        self.vision_system.camera = cv2.VideoCapture(
                            self.vision_system.camera_index
                        )
                        
                    if not self.vision_system.camera.isOpened():
                        # Try MSMF backend if DirectShow failed
                        if hasattr(cv2, 'CAP_MSMF'):
                            self.vision_system.camera = cv2.VideoCapture(
                                self.vision_system.camera_index + cv2.CAP_MSMF
                            )
                            
                    if not self.vision_system.camera.isOpened():
                        # Try default backend as last resort
                        self.vision_system.camera = cv2.VideoCapture(
                            self.vision_system.camera_index
                        )
                        
                    if not self.vision_system.camera.isOpened():
                        raise RuntimeError(f"Failed to open camera at index {self.vision_system.camera_index}")
                    
                    # Give the camera time to initialize
                    time.sleep(0.5)
                    
                    # Set camera properties
                    self.vision_system.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.vision_system.camera_width)
                    self.vision_system.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.vision_system.camera_height)
                    
                    # Read test frame - some cameras need multiple attempts
                    max_attempts = 10
                    for attempt in range(max_attempts):
                        ret, frame = self.vision_system.camera.read()
                        if ret and frame is not None and frame.size > 0:
                            # Successfully read a frame
                            self.logger.info(f"Successfully read camera frame after {attempt+1} attempts")
                            break
                        else:
                            # Failed to read a frame, try again after a short delay
                            self.logger.warning(f"Failed to read frame on attempt {attempt+1}/{max_attempts}")
                            time.sleep(0.5)
                    
                    # Even if we didn't get a valid frame, proceed anyway
                    # Some cameras may need more time to stabilize
                    
                    # Set status and start threads
                    self.vision_system.is_running = True
                    self.vision_system.last_frame_time = time.time()
                    
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Error in patched start method: {e}")
                    if hasattr(self.vision_system, 'camera') and self.vision_system.camera is not None:
                        self.vision_system.camera.release()
                        self.vision_system.camera = None
                    self.vision_system.is_running = False
                    return False
                    
            # Replace the start method with our patched version
            self.vision_system.start = patched_start
            
            self.logger.info("Vision system created and patched")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing vision system: {e}")
            self.vision_status_var.set(f"Error: {str(e)}")
            return False

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = AIGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 