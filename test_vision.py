"""
Test script for the vision system.
"""
import cv2
import numpy as np
from ai_core.vision.vision_system import VisionSystem
import time
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_camera_info(vision):
    """Print detailed camera information."""
    info = vision.get_info()
    print("\nCamera Information:")
    print(f"Status: {info.camera_status}")
    print(f"FPS: {info.fps:.1f}")
    print(f"Face detected: {info.face_detected}")
    if info.face_detected:
        print(f"Face location: {info.face_location}")

def main():
    # Initialize vision system
    vision = VisionSystem()
    
    # Create display window
    cv2.namedWindow('Vision Test', cv2.WINDOW_NORMAL)
    
    try:
        # Start vision system
        vision.start()
        logger.info("Vision system started")
        
        print("\nVision System Test Interface")
        print("Commands:")
        print("  q - Quit")
        print("  c - Capture image")
        print("  i - Show vision info")
        print("  r - Reset camera")
        print("  s - Save current frame")
        print("  l - List available cameras")
        
        while True:
            # Get current frame
            frame = vision.capture_image()
            if frame is not None:
                # Draw face detection results
                info = vision.get_info()
                if info.face_detected and info.face_location:
                    x, y, w, h = info.face_location
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Draw FPS and status
                cv2.putText(frame, f"FPS: {info.fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Status: {info.camera_status}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Show frame
                cv2.imshow('Vision Test', frame)
            else:
                # If no frame, show error message
                error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(error_frame, "No camera feed available", (50, 240),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('Vision Test', error_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('c'):
                frame = vision.capture_image()
                if frame is not None:
                    cv2.imshow('Captured Image', frame)
                else:
                    print("Failed to capture image")
            elif key == ord('i'):
                print_camera_info(vision)
            elif key == ord('r'):
                print("Resetting camera...")
                vision.stop()
                time.sleep(0.5)
                vision.start()
                print("Camera reset complete")
            elif key == ord('s'):
                frame = vision.capture_image()
                if frame is not None:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"captured_frame_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"Frame saved as {filename}")
                else:
                    print("Failed to save frame")
            elif key == ord('l'):
                # List available cameras
                print("\nChecking available cameras...")
                for i in range(10):  # Check first 10 indices
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        ret, _ = cap.read()
                        if ret:
                            print(f"Camera {i} is available")
                        cap.release()
    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        print(f"\nError: {e}")
    finally:
        # Cleanup
        vision.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 