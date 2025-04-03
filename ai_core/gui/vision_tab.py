"""
Vision controls tab for the AI Companion application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
import cv2
import numpy as np
from PIL import Image, ImageTk

class VisionTab:
    """
    Tab containing vision system controls and settings.
    """
    def __init__(self, parent_frame, main_window):
        self.parent = parent_frame
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Initialize variables
        self.camera_var = tk.StringVar(value="Default")
        self.resolution_var = tk.StringVar(value="640x480")
        self.face_detect_var = tk.BooleanVar(value=True)
        self.emotion_detect_var = tk.BooleanVar(value=True)
        self.gesture_detect_var = tk.BooleanVar(value=True)
        self.debug_var = tk.BooleanVar(value=False)
        
        self._create_widgets()
        
        # Ensure the widgets are packed correctly
        parent_frame.update()
        parent_frame.columnconfigure(0, weight=1)
        
    def _create_widgets(self):
        """Create the vision control tab widgets."""
        # Vision settings
        vision_frame = ttk.LabelFrame(self.parent, text="Vision Settings", padding="5")
        vision_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Camera selection
        camera_frame = ttk.Frame(vision_frame)
        camera_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(camera_frame, text="Camera:").grid(row=0, column=0, padx=5)
        camera_combo = ttk.Combobox(camera_frame, textvariable=self.camera_var)
        camera_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Resolution selection
        resolution_frame = ttk.Frame(vision_frame)
        resolution_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(resolution_frame, text="Resolution:").grid(row=0, column=0, padx=5)
        resolution_combo = ttk.Combobox(resolution_frame, textvariable=self.resolution_var,
                                      values=["320x240", "640x480", "800x600", "1280x720", "1920x1080"])
        resolution_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Vision features
        features_frame = ttk.LabelFrame(vision_frame, text="Features", padding="5")
        features_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Checkbutton(features_frame, text="Face Detection",
                       variable=self.face_detect_var,
                       command=self._update_vision_features).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Checkbutton(features_frame, text="Emotion Detection",
                       variable=self.emotion_detect_var,
                       command=self._update_vision_features).grid(row=1, column=0, sticky=tk.W)
        
        ttk.Checkbutton(features_frame, text="Gesture Detection",
                       variable=self.gesture_detect_var,
                       command=self._update_vision_features).grid(row=2, column=0, sticky=tk.W)
        
        # Debug mode
        ttk.Checkbutton(features_frame, text="Debug Mode",
                       variable=self.debug_var,
                       command=self._toggle_debug).grid(row=3, column=0, sticky=tk.W)
        
        # Camera control buttons
        camera_buttons = ttk.Frame(vision_frame)
        camera_buttons.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(camera_buttons, text="Start Camera",
                 command=self.toggle_vision).grid(row=0, column=0, padx=2)
        
        ttk.Button(camera_buttons, text="List Cameras",
                 command=self._list_cameras).grid(row=0, column=1, padx=2)
        
        ttk.Button(camera_buttons, text="Capture Image",
                 command=self._capture_image).grid(row=0, column=2, padx=2)
        
    def toggle_vision(self):
        """Toggle the vision system on/off."""
        if not self.main_window.use_vision:
            # Enable vision
            self.main_window.use_vision = True
            
            # Initialize vision system if needed
            if self.main_window.vision_system is None:
                self._initialize_vision_system()
            
            # Start the vision update loop
            self.main_window._start_vision_update()
            self.main_window.add_message("System", "Vision system enabled", animate=False)
            self.main_window.status_var.set("Vision system active")
        else:
            # Disable vision
            self.main_window.use_vision = False
            
            # Stop the vision system
            if self.main_window.vision_system:
                self.main_window.vision_system.stop()
                
            self.main_window.add_message("System", "Vision system disabled", animate=False)
            self.main_window.status_var.set("Vision system stopped")
            
    def _initialize_vision_system(self):
        """Initialize the vision system."""
        try:
            # Create the vision system
            self.main_window.vision_system = self.main_window.vision_system or self.main_window.VisionSystem()
            
            # Parse camera index
            camera_str = self.camera_var.get()
            if camera_str == "Default":
                camera_index = 0
            else:
                try:
                    # Try to extract index from string like "Camera 1"
                    camera_index = int(camera_str.split()[-1])
                except (ValueError, IndexError):
                    camera_index = 0
                    
            # Parse resolution
            resolution_str = self.resolution_var.get()
            try:
                width, height = map(int, resolution_str.split('x'))
            except ValueError:
                width, height = 640, 480
                
            # Set camera parameters
            self.main_window.vision_system.set_camera_index(camera_index)
            self.main_window.vision_system.set_resolution(width, height)
            
            # Set feature flags
            self.main_window.vision_system.enable_face_detection(self.face_detect_var.get())
            self.main_window.vision_system.enable_emotion_detection(self.emotion_detect_var.get())
            self.main_window.vision_system.enable_gesture_detection(self.gesture_detect_var.get())
            
            # Set debug mode
            self.main_window.vision_system.set_debug_mode(self.debug_var.get())
            
            # Initialize the camera
            self.main_window.vision_system.initialize()
            
            # Register callbacks
            self.main_window.vision_system.register_callbacks(
                on_frame=self._update_vision_canvas,
                on_error=self._handle_vision_error,
                on_info=self._update_vision_info
            )
            
            self.main_window.add_message("System", "Vision system initialized", animate=False)
            
        except Exception as e:
            self.logger.error(f"Error initializing vision system: {e}")
            self.main_window.add_message("System", f"Error initializing vision system: {str(e)}", animate=False)
            self.main_window.use_vision = False
            
    def _update_vision_canvas(self, frame):
        """Update the vision canvas with a new frame."""
        if frame is None:
            return
            
        try:
            # Convert the OpenCV frame to a PIL image
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Resize to fit canvas
            canvas_width = self.main_window.vision_canvas.winfo_width()
            canvas_height = self.main_window.vision_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                # Calculate aspect ratio
                img_width, img_height = pil_image.size
                aspect_ratio = img_width / img_height
                
                # Resize to fit canvas while maintaining aspect ratio
                if canvas_width / canvas_height > aspect_ratio:
                    # Canvas is wider than image
                    new_height = canvas_height
                    new_width = int(new_height * aspect_ratio)
                else:
                    # Canvas is taller than image
                    new_width = canvas_width
                    new_height = int(new_width / aspect_ratio)
                    
                pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                
            # Convert to PhotoImage
            photo_image = ImageTk.PhotoImage(pil_image)
            
            # Update canvas
            self.main_window.vision_canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                image=photo_image, anchor=tk.CENTER
            )
            
            # Keep a reference to prevent garbage collection
            self.main_window.vision_canvas.image = photo_image
            
        except Exception as e:
            self.logger.error(f"Error updating vision canvas: {e}")
            
    def _resize_vision_canvas(self, event):
        """Handle canvas resize event."""
        # Just force a redraw of the current frame if available
        if hasattr(self.main_window.vision_system, 'current_frame') and self.main_window.vision_system.current_frame is not None:
            self._update_vision_canvas(self.main_window.vision_system.current_frame)
            
    def _update_vision_info(self, info=None):
        """Update the vision info text box."""
        if info is None:
            return
            
        try:
            # Clear current info
            self.main_window.vision_info.delete(1.0, tk.END)
            
            # Add new info
            self.main_window.vision_info.insert(tk.END, info)
            
        except Exception as e:
            self.logger.error(f"Error updating vision info: {e}")
            
    def _handle_vision_error(self, error_msg):
        """Handle vision system errors."""
        self.logger.error(f"Vision error: {error_msg}")
        self.main_window.add_message("System", f"Vision error: {error_msg}", animate=False)
        
        # Attempt to recover if possible
        self.main_window._attempt_camera_recovery()
        
    def _list_cameras(self):
        """List available cameras."""
        self.main_window.add_message("System", "Scanning for cameras...", animate=False)
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=self._scan_cameras, daemon=True).start()
        
    def _scan_cameras(self):
        """Scan for available cameras in a background thread."""
        available_cameras = []
        
        try:
            # Scan up to 5 cameras (0-4 indices)
            for i in range(5):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        available_cameras.append(f"Camera {i}")
                    cap.release()
                    
        except Exception as e:
            self.logger.error(f"Error scanning cameras: {e}")
            
        # Update UI from main thread
        self.main_window.root.after(0, lambda: self._update_camera_list(available_cameras))
        
    def _update_camera_list(self, available_cameras):
        """Update the camera combobox with available cameras."""
        if not available_cameras:
            self.main_window.add_message("System", "No cameras found", animate=False)
            available_cameras = ["Default"]
            
        self.main_window.add_message("System", "Available cameras:", animate=False)
        for camera in available_cameras:
            self.main_window.add_message("System", f"- {camera}", animate=False)
            
        # Update combobox values
        camera_combo = ttk.Combobox(self.parent.winfo_children()[0].winfo_children()[0], 
                                  textvariable=self.camera_var,
                                  values=available_cameras)
        camera_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
    def _update_vision_features(self):
        """Update vision system features based on UI settings."""
        if self.main_window.vision_system:
            try:
                self.main_window.vision_system.enable_face_detection(self.face_detect_var.get())
                self.main_window.vision_system.enable_emotion_detection(self.emotion_detect_var.get())
                self.main_window.vision_system.enable_gesture_detection(self.gesture_detect_var.get())
                
                self.main_window.add_message("System", "Vision features updated", animate=False)
                
            except Exception as e:
                self.logger.error(f"Error updating vision features: {e}")
                self.main_window.add_message("System", f"Error updating vision features: {str(e)}", animate=False)
                
    def _toggle_debug(self):
        """Toggle debug mode for vision system."""
        if self.main_window.vision_system:
            try:
                self.main_window.vision_system.set_debug_mode(self.debug_var.get())
                debug_state = "enabled" if self.debug_var.get() else "disabled"
                self.main_window.add_message("System", f"Vision debug mode {debug_state}", animate=False)
                
            except Exception as e:
                self.logger.error(f"Error toggling debug mode: {e}")
                
    def _capture_image(self):
        """Capture current camera frame."""
        if not self.main_window.vision_system or not self.main_window.use_vision:
            messagebox.showinfo("Capture Image", "Vision system must be active to capture an image.")
            return
            
        try:
            frame = self.main_window.vision_system.get_current_frame()
            
            if frame is not None:
                # Convert to PIL format and save
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captured_image_{timestamp}.png"
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                
                # Save image
                pil_image.save(filename)
                self.main_window.add_message("System", f"Image captured and saved as '{filename}'", animate=False)
                
                # Also show in chat
                chat_image = pil_image.copy()
                self.main_window._display_image_in_chat(chat_image)
                
            else:
                self.main_window.add_message("System", "Failed to capture image - no frame available", animate=False)
                
        except Exception as e:
            self.logger.error(f"Error capturing image: {e}")
            self.main_window.add_message("System", f"Error capturing image: {str(e)}", animate=False)
            
    def test_vision(self):
        """Run vision system tests."""
        # Create a test dialog window
        test_window = tk.Toplevel(self.main_window.root)
        test_window.title("Vision Test")
        test_window.geometry("800x600")
        
        # Test canvas for displaying frames
        test_canvas = tk.Canvas(test_window, bg='black')
        test_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Test controls
        controls_frame = ttk.Frame(test_window, padding="5")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status variable
        status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(controls_frame, textvariable=status_var)
        status_label.pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        start_button = ttk.Button(controls_frame, text="Start Test", 
                               command=lambda: toggle_test())
        start_button.pack(side=tk.LEFT, padx=5)
        
        capture_button = ttk.Button(controls_frame, text="Capture Frame", 
                                 command=lambda: capture())
        capture_button.pack(side=tk.LEFT, padx=5)
        
        close_button = ttk.Button(controls_frame, text="Close", 
                               command=lambda: on_test_close())
        close_button.pack(side=tk.RIGHT, padx=5)
        
        # Flags for test state
        test_active = False
        stop_event = threading.Event()
        test_thread = None
        
        # Function to toggle test
        def toggle_test():
            nonlocal test_active, test_thread
            
            if not test_active:
                # Start test
                start_button.configure(text="Stop Test")
                status_var.set("Test running...")
                
                # Reset stop event
                stop_event.clear()
                
                # Start test in a separate thread
                test_thread = threading.Thread(target=run_test, daemon=True)
                test_thread.start()
                
                test_active = True
            else:
                # Stop test
                stop_event.set()
                start_button.configure(text="Start Test")
                status_var.set("Test stopped")
                test_active = False
                
        # Function to capture a single frame
        def capture():
            if self.main_window.vision_system is None:
                status_var.set("Vision system not initialized")
                return
                
            try:
                status_var.set("Capturing frame...")
                frame = self.main_window.vision_system.get_current_frame()
                
                if frame is not None:
                    # Process frame for face detection
                    result_frame = self.main_window.vision_system.process_frame_for_test(frame)
                    
                    # Display on test canvas
                    update_test_canvas(result_frame)
                    status_var.set("Frame captured and processed")
                else:
                    status_var.set("Failed to capture frame")
                    
            except Exception as e:
                status_var.set(f"Error capturing frame: {str(e)}")
                
        # Function to run the test
        def run_test():
            try:
                # Initialize vision system if needed
                if self.main_window.vision_system is None:
                    self._initialize_vision_system()
                    
                if not self.main_window.vision_system.is_initialized():
                    self.main_window.vision_system.initialize()
                    
                status_var.set("Vision system initialized, starting capture...")
                
                # Run capture loop until stopped
                while not stop_event.is_set():
                    try:
                        frame = self.main_window.vision_system.get_current_frame()
                        
                        if frame is not None:
                            # Process frame for face detection
                            result_frame = self.main_window.vision_system.process_frame_for_test(frame)
                            
                            # Update test canvas from main thread
                            test_window.after(0, lambda f=result_frame: update_test_canvas(f))
                            
                        # Small delay to not overwhelm the UI
                        stop_event.wait(0.03)  # ~30 FPS
                        
                    except Exception as e:
                        status_var.set(f"Error during test: {str(e)}")
                        stop_event.wait(1.0)  # Pause before retry
                        
            except Exception as e:
                status_var.set(f"Test error: {str(e)}")
                
            finally:
                test_window.after(0, lambda: start_button.configure(text="Start Test"))
                test_window.after(0, lambda: status_var.set("Test finished"))
                
        # Function to update the test canvas
        def update_test_canvas(frame):
            try:
                # Convert the OpenCV frame to a PIL image
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                
                # Resize to fit canvas
                canvas_width = test_canvas.winfo_width()
                canvas_height = test_canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    # Calculate aspect ratio
                    img_width, img_height = pil_image.size
                    aspect_ratio = img_width / img_height
                    
                    # Resize to fit canvas while maintaining aspect ratio
                    if canvas_width / canvas_height > aspect_ratio:
                        # Canvas is wider than image
                        new_height = canvas_height
                        new_width = int(new_height * aspect_ratio)
                    else:
                        # Canvas is taller than image
                        new_width = canvas_width
                        new_height = int(new_width / aspect_ratio)
                        
                    pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                    
                # Convert to PhotoImage
                photo_image = ImageTk.PhotoImage(pil_image)
                
                # Clear canvas and update
                test_canvas.delete("all")
                test_canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=photo_image, anchor=tk.CENTER
                )
                
                # Keep a reference to prevent garbage collection
                test_canvas.image = photo_image
                
            except Exception as e:
                status_var.set(f"Error updating test canvas: {str(e)}")
                
        # Function to close the test window
        def on_test_close():
            stop_event.set()
            test_window.destroy()
            
        # Prepare canvas
        def on_canvas_configure(event):
            # Force update if we have a current frame
            if self.main_window.vision_system and self.main_window.vision_system.current_frame is not None:
                update_test_canvas(self.main_window.vision_system.current_frame)
                
        # Bind canvas resize event
        test_canvas.bind('<Configure>', on_canvas_configure) 