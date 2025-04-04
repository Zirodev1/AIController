"""
Main application window for the AI Companion system.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from datetime import datetime
from PIL import Image, ImageTk
import cv2
import numpy as np
import logging
import re

# Core AI components
from ai_core.speech.voice_input import VoiceInput
from ai_core.speech.speech_engine import SpeechEngine
from ai_core.emotions.emotion_engine import EmotionEngine
from ai_core.llm.llm_interface import LLMInterface
from ai_core.nlp.text_processor import TextProcessor
from ai_core.vision.vision_system import VisionSystem
from ai_core.image.image_generator import ImageGenerator

# GUI components
from ai_core.gui.theme import ModernTheme
from ai_core.gui.personality_tab import PersonalityTab
from ai_core.gui.voice_tab import VoiceTab
from ai_core.gui.vision_tab import VisionTab
from ai_core.gui.chat_tab import ChatTab
from ai_core.gui.memory_manager import MemoryManager

class MainWindow:
    """Main application window containing all UI components and logic."""
    
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
        self.image_generator = ImageGenerator()
        self.vision_system = None  # Initialized on demand
        
        # Get the actual voice name from SpeechEngine
        try:
            self.current_voice_name = self.speech_engine.get_current_voice_name()
        except AttributeError:
            self.logger.warning("SpeechEngine missing get_current_voice_name method. Using fallback name.")
            self.current_voice_name = "AI Voice" # Fallback
        except Exception as e:
             self.logger.error(f"Error getting voice name from SpeechEngine: {e}")
             self.current_voice_name = "AI Voice" # Fallback
        
        # Initialize memory system
        self.memory_manager = MemoryManager(self)
        
        # GUI state variables
        self.is_listening = False
        self.is_push_to_talk = False
        self.message_queue = queue.Queue()
        self.typing_speed = 50
        self.is_typing = False
        self.image_references = []
        self.face_detect_var = tk.BooleanVar(value=True)
        
        # Personality Settings Store
        self.personality_settings = {}
        # We will store tk variables here to easily access/save settings
        self._personality_vars = {}
        
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
        
        # Load initial personality (optional)
        # self._load_personality_settings()
        
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
        
        # Ensure the left panel expands properly
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)
        
        print("Creating Personality Tab...")
        # Personality Tab
        personality_frame = ttk.Frame(notebook)
        notebook.add(personality_frame, text="Personality")
        self.personality_tab = PersonalityTab(personality_frame, self)
        self.personality_tab.pack(fill=tk.BOTH, expand=True)
        
        print("Creating Voice Tab...")
        # Voice tab
        voice_frame = ttk.Frame(notebook)
        notebook.add(voice_frame, text="Voice")
        self.voice_tab = VoiceTab(voice_frame, self)
        
        print("Creating Vision Tab...")
        # Vision tab
        vision_frame = ttk.Frame(notebook)
        notebook.add(vision_frame, text="Vision")
        self.vision_tab = VisionTab(vision_frame, self)
        
        # Right panel - Output
        right_panel = ttk.Frame(main_container)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Create notebook for output tabs
        output_notebook = ttk.Notebook(right_panel)
        output_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Chat tab
        chat_frame = ttk.Frame(output_notebook)
        output_notebook.add(chat_frame, text="Chat")
        self.chat_tab = ChatTab(chat_frame, self)
        
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
        
        # Configure root grid to expand with window
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

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
        self.vision_canvas.bind('<Configure>', self.vision_tab._resize_vision_canvas)

    def _process_input(self, text: str):
        """Process input regardless of source (voice or text)."""
        self.add_message("You", text, animate=False)
        self.status_var.set("Processing input...")
        
        # Check for image generation command
        image_request_match = re.search(
            r"(generate|create|make|send)\s+(?:me\s+)?(?:(?:a|an)\s+)?(pic|picture|image|photo)\s*(.*)", 
            text, 
            re.IGNORECASE
        )
        
        if image_request_match:
            # Extract raw potential prompt from group 3
            raw_prompt = image_request_match.group(3).strip()
            
            # Clean up common leading words from the prompt
            cleaned_prompt = re.sub(r"^(of|like|showing|about)\\s+", "", raw_prompt, flags=re.IGNORECASE).strip()
            cleaned_prompt = re.sub(r"^(you|yourself)\\s*", "", cleaned_prompt, flags=re.IGNORECASE).strip()

            # Use default prompt if cleaning results in an empty string
            final_prompt = cleaned_prompt if cleaned_prompt else "yourself" 
            
            self.add_message("System", f"Generating image with prompt: '{final_prompt}'...", animate=False)
            # Generate image in a separate thread to avoid blocking GUI
            # Pass the original text as well for context in the response
            threading.Thread(target=self._handle_image_generation, args=(final_prompt, text), daemon=True).start()
            self.status_var.set("Generating image...")
        else:
            # Normal text processing
            try:
                # Process input
                nlp_analysis = self.text_processor.process_text(text)
                self.emotion_engine.process_text(text)
                emotional_state = self.emotion_engine.get_emotional_state()
                
                # Get conversation context from memory
                context = self.memory_manager.get_recent_context()
                
                # Generate response
                response = self.llm.generate_response(emotional_state, text, context)
                
                # Store the exchange in memory
                self.memory_manager.add_interaction(text, response)
                
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

    def _handle_image_generation(self, prompt: str, original_text: str):
        """Handle image generation and generate a text response in a background thread."""
        image_success = False
        
        try:
            # Parse the image request
            params = self.image_generator.parse_image_request(original_text)
            
            # Check if we need to use the provided prompt
            if "prompt" not in params and prompt:
                params["prompt"] = prompt
                
            self.logger.info(f"Generating character image with params: {params}")
            
            # Generate the image with character parameters
            generated_image = self.image_generator.generate_image(**params)
            
            if generated_image:
                # Image generation successful - queue image for display
                self.message_queue.put(("image", generated_image))
                
                # Save the image
                saved_path = self.image_generator.save_image(generated_image, f"character_{int(time.time())}")
                if saved_path:
                    self.logger.info(f"Image saved to {saved_path}")
                    
                image_success = True
            else:
                # Image generation failed
                self.message_queue.put(("System: Sorry, I couldn't generate the image.\n", False))
        except Exception as e:
            self.logger.error(f"Error during image generation: {e}")
            self.message_queue.put(("System: An error occurred during image generation.\n", False))

        # Now, generate a text response based on the outcome and original request
        try:
            emotional_state = self.emotion_engine.get_emotional_state()
            
            # Create a context-aware prompt for the LLM
            if image_success:
                llm_prompt = f"User asked: \"{original_text}\". You successfully sent an image of yourself as requested. Respond naturally as if you're a character who just shared a selfie/picture of yourself."
            else:
                llm_prompt = f"User asked: \"{original_text}\". You tried to send an image of yourself but couldn't. Apologize and explain you couldn't create the image right now."
            
            # Get conversation context
            context = self.memory_manager.get_recent_context() if hasattr(self, 'memory_manager') else None
            
            # Generate the text response
            response = self.llm.generate_response(emotional_state, llm_prompt, context)
            
            # Store in memory if available
            if hasattr(self, 'memory_manager'):
                self.memory_manager.add_interaction(original_text, response)
            
            # Add the text response to the queue
            if self.use_voice_output:
                self.message_queue.put((f"{self.current_voice_name}: {response}\n", False)) # Text first
                self.speech_engine.speak(response) # Then speak
            else:
                self.message_queue.put((f"{self.current_voice_name}: ", False)) # Prefix
                self.message_queue.put((response + "\n", True)) # Animate the response
                
        except Exception as e:
            self.logger.error(f"Error generating text response after image generation: {e}")
            self.message_queue.put(("System: Sorry, I had trouble formulating a response after the image request.\n", False))
            
        finally:
            # Ensure status is updated after generation attempt
            self.root.after(0, lambda: self.status_var.set("Ready"))

    def _parse_image_parameters(self, text: str) -> dict:
        """Parse image generation parameters from the text."""
        params = {}
        
        # Parse size
        size_match = re.search(r"size\s+(\d+)x(\d+)", text, re.IGNORECASE)
        if size_match:
            try:
                width = min(int(size_match.group(1)), 1024)  # Cap at 1024 for safety
                height = min(int(size_match.group(2)), 1024)
                params['size'] = (width, height)
            except ValueError:
                pass
                
        # Parse style
        style_patterns = [
            r"style\s+([a-zA-Z0-9 ]+)", 
            r"in\s+([a-zA-Z0-9]+)\s+style",
            r"([a-zA-Z0-9]+)\s+style"
        ]
        
        for pattern in style_patterns:
            style_match = re.search(pattern, text, re.IGNORECASE)
            if style_match:
                style = style_match.group(1).strip()
                if style:
                    params['style'] = style
                break
                
        # Parse negative prompt
        negative_patterns = [
            r"negative\s+(.+?)(,|$|\.|;)",
            r"no\s+(.+?)(,|$|\.|;)",
            r"without\s+(.+?)(,|$|\.|;)",
        ]
        
        negative_prompts = []
        for pattern in negative_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                if match.group(1).strip():
                    negative_prompts.append(match.group(1).strip())
                    
        if negative_prompts:
            params['negative_prompt'] = ", ".join(negative_prompts)
            
        return params

    def process_messages(self):
        """Process and display queued messages."""
        if not self.is_typing:
            try:
                while True:
                    message_data = self.message_queue.get_nowait()
                    
                    if isinstance(message_data, tuple) and len(message_data) == 2:
                        message_type, content = message_data
                        
                        if message_type == "image":
                            # Handle image display
                            self._display_image_in_chat(content)
                        else:
                            # Handle text message
                            message, should_animate = message_type, content 
                            if should_animate:
                                # Start typing animation
                                self.is_typing = True
                                self._animate_typing(message, 0)
                            else:
                                # Display message immediately
                                self.chat_text.insert(tk.END, message)
                                self.chat_text.see(tk.END)
                    else:
                        # Handle legacy message format
                        self.logger.warning(f"Received unexpected message format: {type(message_data)}")
                        try:
                            message = str(message_data)
                            self.chat_text.insert(tk.END, message)
                            self.chat_text.see(tk.END)
                        except Exception as fmt_e:
                             self.logger.error(f"Could not handle legacy message format: {fmt_e}")
                        
            except queue.Empty:
                pass
            except Exception as e:
                self.logger.error(f"Error processing message queue: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
        
        # Schedule next update
        self.root.after(100, self.process_messages)

    def _display_image_in_chat(self, pil_image: Image.Image):
        """Displays a PIL image directly in the chat text widget."""
        try:
            # Resize image to fit chat width
            max_width = 300
            img_width, img_height = pil_image.size
            if img_width > max_width:
                scale = max_width / img_width
                new_height = int(img_height * scale)
                pil_image = pil_image.resize((max_width, new_height), Image.LANCZOS)
            
            # Convert PIL image to PhotoImage
            photo_image = ImageTk.PhotoImage(pil_image)
            
            # Keep a reference to prevent garbage collection
            self.image_references.append(photo_image)
            if len(self.image_references) > 20:
                self.image_references.pop(0)
            
            # Insert image into chat
            self.chat_text.image_create(tk.END, image=photo_image)
            self.chat_text.insert(tk.END, '\n')
            self.chat_text.see(tk.END)
            
        except Exception as e:
            self.logger.error(f"Error displaying image in chat: {e}")
            self.add_message("System", "[Error displaying image]", animate=False)

    def _animate_typing(self, message, index):
        """Animate typing effect for a message."""
        if index < len(message):
            self.chat_text.insert(tk.END, message[index])
            self.chat_text.see(tk.END)
            self.root.after(self.typing_speed, 
                          lambda: self._animate_typing(message, index + 1))
        else:
            self.is_typing = False

    def add_message(self, sender: str, message: str, animate=False):
        """Add a message to the queue for display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}] {sender}: "
        
        if not animate:
            # Add message immediately
            self.message_queue.put((prefix + message + "\n", False))
        else:
            # Add prefix without animation
            self.message_queue.put((prefix, False))
            # Add message with animation
            self.message_queue.put((message + "\n", True))

    def _initialize_voice_input(self):
        """Initialize or reinitialize the voice input component."""
        if self.voice_input:
            self.voice_input.stop_listening()
            
        self.voice_input = VoiceInput(wake_word=self.voice_tab.wake_word_var.get())
        self.voice_input.set_callbacks(
            on_wake_word=self._handle_wake_word,
            on_command_received=self._handle_command
        )
        self.add_message("System", "Voice input system initialized")
        self.status_var.set("Ready")

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

    def _toggle_input_mode(self):
        """Toggle between voice and text input."""
        self.use_voice_input = not self.use_voice_input
        
        # Update UI based on mode
        if not self.use_voice_input and hasattr(self, 'is_listening') and self.is_listening:
            self.voice_tab.stop_listening()
            
        self.status_var.set(f"Using {'voice' if self.use_voice_input else 'text'} input")

    def _toggle_output_mode(self):
        """Toggle between voice and text output."""
        self.use_voice_output = not self.use_voice_output
        self.status_var.set(f"Using {'voice' if self.use_voice_output else 'text'} output")

    def _show_settings(self):
        """Show the settings dialog."""
        # To be implemented
        pass

    def _on_closing(self):
        """Handle window closing event."""
        if self.use_vision:
            self.vision_system.stop()
        if self.voice_input:
            self.voice_input.stop_listening()
        self.root.destroy()

    def _toggle_vision(self):
        """Toggle the vision system."""
        # Forward to vision tab handler
        self.vision_tab.toggle_vision()

    def _test_vision(self):
        """Run vision system tests."""
        # Forward to vision tab handler
        self.vision_tab.test_vision()

    def _test_emotions(self):
        """Run emotion system tests."""
        # To be implemented 
        pass
        
    def _start_vision_update(self):
        """Start the vision update loop."""
        if not self.use_vision or not self.vision_system:
            return
            
        # Load face cascade for direct detection if needed
        if self.face_detect_var.get() and not hasattr(self, 'face_cascade'):
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                self.logger.info("Loaded face cascade for direct detection")
            except Exception as e:
                self.logger.error(f"Error loading face cascade: {e}")
                self.face_cascade = None
                
        # Function to update frames
        def update_vision():
            try:
                while self.use_vision:
                    try:
                        # Get frame from vision system
                        frame = self.vision_system.get_current_frame()
                        
                        if frame is not None:
                            # Process frame with face detection, etc.
                            processed_frame = self.vision_system.process_frame(frame)
                            
                            # Direct face detection in GUI for stability if needed
                            if hasattr(self, 'face_cascade') and self.face_cascade and self.face_detect_var.get():
                                self._apply_direct_face_detection(processed_frame)
                            
                            # Update UI with processed frame
                            self.vision_tab._update_vision_canvas(processed_frame)
                            
                            # Get and display vision info
                            vision_info = self.vision_system.get_vision_info()
                            if vision_info:
                                self.vision_tab._update_vision_info(vision_info)
                                
                        # Delay to control frame rate
                        time.sleep(0.03)  # ~30 FPS
                        
                    except Exception as e:
                        self.logger.error(f"Error in vision update loop: {e}")
                        self.vision_tab._handle_vision_error(str(e))
                        time.sleep(1.0)  # Wait a bit before retrying
                        
            except Exception as e:
                self.logger.error(f"Vision update thread error: {e}")
                self.status_var.set("Vision system error")
                
        # Start update thread
        vision_thread = threading.Thread(target=update_vision, daemon=True)
        vision_thread.start()
        
    def _apply_direct_face_detection(self, frame):
        """Apply direct face detection to reduce flickering"""
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply face detection
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.2, 
                minNeighbors=4, 
                minSize=(30, 30)
            )
            
            # Draw face rectangles for stability
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                
            # If any faces were detected, update the status bar
            if len(faces) > 0 and not self.vision_system.get_info().face_detected:
                # This adds an extra indication of face presence
                self.status_var.set(f"Face detected ({len(faces)})")
                
        except Exception as e:
            # Silently fail on errors since this is just a stabilization feature
            self.logger.debug(f"Direct face detection error: {e}")
            pass

    def _attempt_camera_recovery(self):
        """Attempt to recover from camera failure."""
        self.add_message("System", "Attempting to recover camera...", animate=False)
        
        try:
            if self.vision_system:
                # Use the new robust recovery mechanism
                if self.vision_system.attempt_camera_recovery():
                    self.add_message("System", "Camera recovery successful", animate=False)
                    self.status_var.set("Camera recovered")
                else:
                    self.add_message("System", "Camera recovery failed - please check your camera connection", animate=False)
                    self.status_var.set("Camera recovery failed")
                
        except Exception as e:
            self.logger.error(f"Camera recovery failed: {e}")
            self.add_message("System", f"Camera recovery failed: {str(e)}", animate=False) 