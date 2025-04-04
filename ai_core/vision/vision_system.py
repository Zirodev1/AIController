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
    recovery_attempts: int = 0
    last_error: str = None

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
        
        # Feature flags
        self.enable_face_detection_flag = True
        self.enable_emotion_detection_flag = False
        self.enable_gesture_detection_flag = False
        self.debug_mode = False
        
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
        
        # Callback functions
        self.on_frame_callback = None
        self.on_error_callback = None
        self.on_info_callback = None
        
        self.logger.info("Vision system initialized successfully")

    def enable_debug(self, enable=True):
        """Enable or disable debug logging."""
        if enable:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug("Debug logging enabled")
        else:
            self.logger.setLevel(logging.INFO)
            
    def set_debug_mode(self, debug_mode):
        """Set debug mode for the vision system."""
        self.debug_mode = debug_mode
        self.logger.info(f"Debug mode set to {debug_mode}")
        
    def enable_face_detection(self, enable=True):
        """Enable or disable face detection."""
        self.enable_face_detection_flag = enable
        self.logger.info(f"Face detection {'enabled' if enable else 'disabled'}")
        
    def enable_emotion_detection(self, enable=True):
        """Enable or disable emotion detection."""
        self.enable_emotion_detection_flag = enable
        self.logger.info(f"Emotion detection {'enabled' if enable else 'disabled'}")
        
    def enable_gesture_detection(self, enable=True):
        """Enable or disable gesture detection."""
        self.enable_gesture_detection_flag = enable
        self.logger.info(f"Gesture detection {'enabled' if enable else 'disabled'}")
        
    def register_callbacks(self, on_frame=None, on_error=None, on_info=None):
        """Register callback functions."""
        self.on_frame_callback = on_frame
        self.on_error_callback = on_error
        self.on_info_callback = on_info

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
            self.vision_info.recovery_attempts = 0
            self.vision_info.last_error = None
            
            # Start capture and processing threads
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            
            self.capture_thread.start()
            self.processing_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting vision system: {e}")
            self.vision_info.camera_status = "error"
            self.vision_info.last_error = str(e)
            
            if self.on_error_callback:
                self.on_error_callback(str(e))
                
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

    def get_current_frame(self):
        """Get the current frame."""
        return self.capture_image()

    def get_vision_info(self):
        """Get the current vision system information as a formatted string."""
        info = self.vision_info
        
        lines = [
            f"Camera status: {info.camera_status}",
            f"Frame rate: {info.fps:.1f} FPS",
            f"Face detected: {'Yes' if info.face_detected else 'No'}"
        ]
        
        if info.face_detected and info.face_location:
            x, y, w, h = info.face_location
            lines.append(f"Face position: ({x}, {y}), size: {w}x{h}")
            
        if info.emotion and info.emotion != "neutral":
            lines.append(f"Detected emotion: {info.emotion}")
            
        if info.gesture:
            lines.append(f"Detected gesture: {info.gesture}")
            
        if self.debug_mode:
            lines.append(f"Recovery attempts: {info.recovery_attempts}")
            if info.last_error:
                lines.append(f"Last error: {info.last_error}")
                
        return "\n".join(lines)
    
    def get_info(self):
        """Get the current vision system information object."""
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
        
    def initialize(self):
        """Initialize the vision system."""
        return self.start()
        
    def is_initialized(self):
        """Check if the vision system is initialized."""
        return self.is_running and self.camera is not None
        
    def reset_camera(self):
        """Reset the camera."""
        self.logger.info("Resetting camera...")
        
        # Stop the camera
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            
        # Wait a moment for resources to be released
        time.sleep(0.5)
        
        # Attempt to restart
        self.camera = cv2.VideoCapture(self.camera_index)
        
        if self.camera.isOpened():
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.camera_fps)
            
            self.logger.info("Camera reset successful")
            self.vision_info.camera_status = "running"
            self.vision_info.last_error = None
            return True
        else:
            self.logger.error("Failed to reset camera")
            self.vision_info.camera_status = "error"
            self.vision_info.last_error = "Failed to reset camera"
            return False
            
    def attempt_camera_recovery(self):
        """Attempt to recover the camera if it fails."""
        self.logger.info("Attempting camera recovery...")
        success = False
        
        try:
            # Update recovery attempt count
            self.vision_info.recovery_attempts += 1
            self.vision_info.camera_status = "recovering"
            
            # Release current camera
            if self.camera:
                self.camera.release()
                self.camera = None
                
            # Give system time to fully release camera resources
            time.sleep(1.0)
            
            # Try different backend options
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, 0]  # Different backends for Windows
            
            for backend in backends:
                try:
                    self.logger.info(f"Trying camera with backend {backend}")
                    
                    # Create camera with specific backend
                    camera_with_backend = self.camera_index + backend
                    self.camera = cv2.VideoCapture(camera_with_backend)
                    
                    if self.camera.isOpened():
                        # Set camera properties
                        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
                        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
                        self.camera.set(cv2.CAP_PROP_FPS, self.camera_fps)
                        
                        # Verify with a test read
                        ret, frame = self.camera.read()
                        if ret and frame is not None:
                            self.logger.info(f"Camera recovery successful with backend {backend}")
                            self.vision_info.camera_status = "running"
                            success = True
                            break
                        else:
                            self.camera.release()
                            self.camera = None
                            
                except Exception as e:
                    self.logger.error(f"Recovery attempt with backend {backend} failed: {e}")
                    if self.camera:
                        self.camera.release()
                        self.camera = None
            
            # If all backends failed, try one last attempt with default settings
            if not success:
                self.logger.info("Trying last-resort recovery...")
                time.sleep(2.0)  # Extended wait
                
                try:
                    self.camera = cv2.VideoCapture(self.camera_index)
                    if self.camera.isOpened():
                        ret, frame = self.camera.read()
                        if ret and frame is not None:
                            self.logger.info("Last-resort camera recovery successful")
                            self.vision_info.camera_status = "running"
                            success = True
                        else:
                            self.camera.release()
                            self.camera = None
                except Exception as e:
                    self.logger.error(f"Last-resort recovery failed: {e}")
                    if self.camera:
                        self.camera.release()
                        self.camera = None
            
            # Update status based on recovery result
            if success:
                self.vision_info.last_error = None
                return True
            else:
                self.vision_info.camera_status = "error"
                self.vision_info.last_error = "Camera recovery failed after multiple attempts"
                return False
                
        except Exception as e:
            self.logger.error(f"Error during camera recovery: {e}")
            self.vision_info.camera_status = "error"
            self.vision_info.last_error = str(e)
            return False

    def _capture_loop(self):
        """Continuously capture frames from the camera."""
        self.logger.info("Starting capture loop")
        frame_failure_count = 0
        max_frame_failures = 5
        
        try:
            while self.is_running:
                if self.camera is None:
                    time.sleep(0.1)
                    continue
                    
                # Attempt to read a frame
                ret, frame = self.camera.read()
                
                if not ret or frame is None:
                    frame_failure_count += 1
                    self.logger.warning(f"Failed to read frame from camera (attempt {frame_failure_count}/{max_frame_failures})")
                    
                    # If we've had multiple failures, try recovery
                    if frame_failure_count >= max_frame_failures:
                        self.logger.error("Multiple frame capture failures, attempting recovery")
                        
                        # Update vision info
                        self.vision_info.camera_status = "error"
                        self.vision_info.last_error = "Multiple frame capture failures"
                        
                        # Trigger error callback
                        if self.on_error_callback:
                            self.on_error_callback("Camera failure - attempting recovery")
                            
                        # Attempt recovery
                        if self.attempt_camera_recovery():
                            frame_failure_count = 0
                            self.logger.info("Camera recovery successful")
                        else:
                            self.logger.error("Camera recovery failed")
                            time.sleep(2.0)  # Wait longer before next attempt
                            
                    time.sleep(0.1)
                    continue
                    
                # Reset failure counter on successful frame
                frame_failure_count = 0
                    
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
                    
                # Call frame callback if registered
                if self.on_frame_callback:
                    processed_frame = self.process_frame(frame.copy())
                    self.on_frame_callback(processed_frame)
                    
                # Update vision info if required
                if self.on_info_callback:
                    self.on_info_callback(self.get_vision_info())
                    
                # Limit capture rate to avoid excessive CPU usage
                time.sleep(0.01)
                
        except Exception as e:
            self.logger.error(f"Error in capture loop: {e}")
            self.vision_info.camera_status = "error"
            self.vision_info.last_error = str(e)
            
            # Trigger error callback
            if self.on_error_callback:
                self.on_error_callback(str(e))
                
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
                    
                # Process the frame (without sending to callback, that's done in capture loop)
                self._process_frame(frame)
                
                # Limit processing rate
                time.sleep(0.03)  # ~30 FPS max
                
        except Exception as e:
            self.logger.error(f"Error in processing loop: {e}")
            self.vision_info.camera_status = "error"
            self.vision_info.last_error = str(e)
            
            # Trigger error callback
            if self.on_error_callback:
                self.on_error_callback(str(e))

    def _process_frame(self, frame):
        """Process a single frame without GUI updates."""
        if frame is None:
            return
            
        # Detect faces if enabled
        if self.enable_face_detection_flag:
            self._detect_faces(frame)
            
        # Add other processing as needed
        if self.enable_emotion_detection_flag:
            # Emotion detection (placeholder)
            pass
            
        if self.enable_gesture_detection_flag:
            # Gesture detection (placeholder)
            pass
            
    def process_frame(self, frame):
        """Process a frame and return it with annotations."""
        if frame is None:
            return None
            
        # Make a copy for drawing
        result_frame = frame.copy()
        
        # Draw face rectangle if face detected
        if self.vision_info.face_detected and self.vision_info.face_location:
            x, y, w, h = self.vision_info.face_location
            cv2.rectangle(result_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Add emotion if detected
            if self.vision_info.emotion and self.vision_info.emotion != "neutral":
                cv2.putText(result_frame, self.vision_info.emotion, (x, y-10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
        # Add debug info if enabled
        if self.debug_mode:
            # Add FPS counter
            cv2.putText(result_frame, f"FPS: {self.vision_info.fps:.1f}", (10, 30), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                      
            # Add camera status
            cv2.putText(result_frame, f"Status: {self.vision_info.camera_status}", (10, 60), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                      
            # Add recovery attempts if any
            if self.vision_info.recovery_attempts > 0:
                cv2.putText(result_frame, f"Recovery: {self.vision_info.recovery_attempts}", (10, 90), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                          
        return result_frame
        
    def process_frame_for_test(self, frame):
        """Process a frame for test purposes with additional visualizations."""
        return self.process_frame(frame)
        
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
                else:
                    self.vision_info.face_location = None
            except Exception as e:
                self.logger.error(f"Error in face detection: {e}")
                self.vision_info.face_detected = False
                self.vision_info.face_location = None
        else:
            self.logger.warning("Face cascade not available, skipping face detection")
            self.vision_info.face_detected = False 