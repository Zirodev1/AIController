"""
Vision system for handling camera input and processing.
"""
import cv2
import numpy as np
import threading
import time
from dataclasses import dataclass
import logging

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
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            if self.face_cascade.empty():
                raise RuntimeError("Failed to load face detection model")
        except Exception as e:
            self.logger.error(f"Error loading face detection model: {e}")
            raise
        
        self.logger.info("Vision system initialized successfully")

    def start(self):
        """Start the vision system."""
        if self.is_running:
            return
            
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                raise RuntimeError(f"Failed to open camera at index {self.camera_index}")
            
            # Test camera read
            ret, frame = self.camera.read()
            if not ret:
                raise RuntimeError("Failed to read from camera")
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.camera_fps)
            
            # Verify camera properties
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            self.logger.info(f"Camera initialized with resolution: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            # Start threads
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.processing_thread = threading.Thread(target=self._processing_loop)
            
            self.capture_thread.start()
            self.processing_thread.start()
            
            self.vision_info.camera_status = "running"
            self.logger.info("Vision system started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting vision system: {e}")
            self.vision_info.camera_status = f"error: {str(e)}"
            self.stop()
            raise

    def stop(self):
        """Stop the vision system."""
        self.is_running = False
        
        if self.capture_thread:
            self.capture_thread.join()
        if self.processing_thread:
            self.processing_thread.join()
            
        if self.camera:
            self.camera.release()
            self.camera = None
            
        self.vision_info.camera_status = "stopped"
        self.logger.info("Vision system stopped")

    def _capture_loop(self):
        """Main capture loop."""
        while self.is_running:
            try:
                ret, frame = self.camera.read()
                if ret:
                    with self.frame_lock:
                        self.current_frame = frame
                        self.frame_count += 1
                        
                        # Calculate FPS
                        current_time = time.time()
                        if current_time - self.last_frame_time >= 1.0:
                            self.vision_info.fps = self.frame_count
                            self.frame_count = 0
                            self.last_frame_time = current_time
                else:
                    self.logger.warning("Failed to capture frame")
                    time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in capture loop: {e}")
                time.sleep(0.1)

    def _processing_loop(self):
        """Main processing loop."""
        while self.is_running:
            try:
                with self.frame_lock:
                    if self.current_frame is not None:
                        # Convert to grayscale for face detection
                        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
                        
                        # Detect faces
                        faces = self.face_cascade.detectMultiScale(
                            gray,
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(30, 30)
                        )
                        
                        # Update vision info
                        self.vision_info.face_detected = len(faces) > 0
                        if self.vision_info.face_detected:
                            # Use the first detected face
                            x, y, w, h = faces[0]
                            self.vision_info.face_location = (x, y, w, h)
                        else:
                            self.vision_info.face_location = None
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(0.1)
                        
            time.sleep(0.01)  # Small delay to prevent CPU overuse

    def capture_image(self):
        """Capture the current frame."""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None

    def get_info(self):
        """Get current vision information."""
        return self.vision_info

    def set_camera(self, index: int):
        """Set the camera index."""
        if self.is_running:
            self.stop()
        self.camera_index = index
        if self.is_running:
            self.start()

    def set_resolution(self, width: int, height: int):
        """Set the camera resolution."""
        if self.is_running:
            self.stop()
        self.camera_width = width
        self.camera_height = height
        if self.is_running:
            self.start() 