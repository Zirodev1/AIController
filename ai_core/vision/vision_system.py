"""
Vision system for handling camera input and processing.
"""
import cv2
import numpy as np
import threading
import time
from dataclasses import dataclass
import logging
import os

@dataclass
class VisionInfo:
    """Information about the current vision state."""
    face_detected: bool = False
    face_location: tuple = None
    emotion: str = "neutral"
    gesture: str = None
    frame_count: int = 0
    fps: float = 0.0
    camera_status: str = "initialized"

class VisionSystem:
    def __init__(self):
        """Initialize the vision system."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing vision system...")
        
        # Camera settings
        self.camera_index = 0
        self.camera_width = 640
        self.camera_height = 480
        self.camera_fps = 30
        
        # Vision state
        self.is_running = False
        self.camera = None
        self.current_frame = None
        self.vision_info = VisionInfo()
        self.last_frame_time = 0
        self.frame_count = 0
        
        # Threading
        self.capture_thread = None
        self.processing_thread = None
        self.frame_lock = threading.Lock()
        
        # Load face detection model
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.logger.info(f"Loading cascade classifier from: {cascade_path}")
            
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            if self.face_cascade.empty():
                self.logger.error(f"Failed to load face detection model from {cascade_path}")
                raise RuntimeError(f"Failed to load face detection model from {cascade_path}")
            else:
                self.logger.info("Successfully loaded face cascade classifier")
                
        except Exception as e:
            self.logger.error(f"Error loading face detection model: {e}")
            # Create placeholder to prevent errors
            self.face_cascade = None
        
        self.logger.info("Vision system initialized successfully")

    def enable_debug(self, enable=True):
        """Enable or disable debug logging."""
        if enable:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug("Debug logging enabled")
        else:
            self.logger.setLevel(logging.INFO)

    def start(self):
        """Start the vision system."""
        if self.is_running:
            return True
            
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                raise RuntimeError(f"Failed to open camera at index {self.camera_index}")
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.camera_fps)
            # Set additional camera parameters
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)  # Adjust brightness
            self.camera.set(cv2.CAP_PROP_CONTRAST, 0.5)  # Adjust contrast
            
            # Test camera read
            ret, frame = self.camera.read()
            if not ret:
                raise RuntimeError("Failed to read from camera")
            
            # Verify camera properties
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            self.logger.info(f"Camera initialized with resolution: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            # Start processing threads
            self.is_running = True
            self.frame_count = 0
            self.vision_info.camera_status = "running"
            
            # Start capture and processing threads
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            
            self.capture_thread.start()
            self.processing_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting vision system: {e}")
            return False

    def stop(self):
        """Stop the vision system."""
        self.is_running = False
        
        # Release camera
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            
        # Wait for threads to terminate
        if self.capture_thread is not None and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
            
        if self.processing_thread is not None and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)
            
        self.vision_info.camera_status = "stopped"
        self.logger.info("Vision system stopped")

    def capture_image(self):
        """Capture current image from the camera."""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        
        # If no frame available, try direct capture
        if self.camera is not None and self.is_running:
            ret, frame = self.camera.read()
            if ret and frame is not None:
                return frame
                
        return None

    def get_info(self):
        """Get the current vision system information."""
        return self.vision_info

    def set_camera_index(self, index):
        """Set the camera index."""
        if self.is_running:
            self.logger.warning("Cannot change camera while vision system is running")
            return False
            
        self.camera_index = index
        return True
        
    def set_resolution(self, width, height):
        """Set the camera resolution."""
        if self.is_running:
            self.logger.warning("Cannot change resolution while vision system is running")
            return False
            
        self.camera_width = width
        self.camera_height = height
        return True

    def _capture_loop(self):
        """Continuously capture frames from the camera."""
        self.logger.info("Starting capture loop")
        
        try:
            while self.is_running:
                if self.camera is None:
                    time.sleep(0.1)
                    continue
                    
                ret, frame = self.camera.read()
                if not ret:
                    self.logger.warning("Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
                    
                # Store the captured frame
                with self.frame_lock:
                    self.current_frame = frame.copy()
                    
                # Update frame count and FPS
                current_time = time.time()
                if current_time - self.last_frame_time >= 1.0:
                    self.vision_info.fps = self.frame_count / (current_time - self.last_frame_time)
                    self.last_frame_time = current_time
                    self.frame_count = 0
                else:
                    self.frame_count += 1
                    
                # Limit capture rate to avoid excessive CPU usage
                time.sleep(0.01)
                
        except Exception as e:
            self.logger.error(f"Error in capture loop: {e}")
            self.vision_info.camera_status = "error"
            self.is_running = False

    def _processing_loop(self):
        """Process captured frames."""
        self.logger.info("Starting processing loop")
        
        try:
            while self.is_running:
                # Get the current frame
                with self.frame_lock:
                    if self.current_frame is None:
                        time.sleep(0.1)
                        continue
                    frame = self.current_frame.copy()
                    
                # Process the frame
                self._process_frame(frame)
                
                # Limit processing rate
                time.sleep(0.03)  # ~30 FPS max
                
        except Exception as e:
            self.logger.error(f"Error in processing loop: {e}")
            self.vision_info.camera_status = "error"

    def _process_frame(self, frame):
        """Process a single frame."""
        # Detect faces
        self._detect_faces(frame)
        
        # Further processing can be added here
        
    def _detect_faces(self, frame):
        """Detect faces in the given frame."""
        if self.face_cascade is not None:
            try:
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces with improved parameters
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,  # Smaller value for better detection
                    minNeighbors=5,   # Minimum number of neighbors required
                    minSize=(30, 30), # Minimum size of face to detect
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                self.logger.debug(f"Face detection found {len(faces)} faces")
                
                # Update vision info
                self.vision_info.face_detected = len(faces) > 0
                if self.vision_info.face_detected:
                    # Use the first detected face
                    x, y, w, h = faces[0]
                    self.vision_info.face_location = (x, y, w, h)
                    
                    # Draw the face rectangle for debugging (without modifying the frame)
                    debug_frame = frame.copy()
                    cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(debug_frame, "Face", (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    self.vision_info.face_location = None
            except Exception as e:
                self.logger.error(f"Error in face detection: {e}")
                self.vision_info.face_detected = False
                self.vision_info.face_location = None
        else:
            self.logger.warning("Face cascade not available, skipping face detection")
            self.vision_info.face_detected = False 