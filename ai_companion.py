"""
AI Companion - Main application entry point.

This module initializes the application and launches the GUI.
"""
import tkinter as tk
import logging
import sys

# Import from our module structure
from ai_core.gui.main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Log to stdout for immediate feedback
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application."""
    try:
        print("Starting AI Companion application")
        logger.info("Starting AI Companion application")
        
        # Create the main window
        root = tk.Tk()
        print("Tkinter root window created")
        
        app = MainWindow(root)
        print("MainWindow initialized")
        
        # Run the application
        logger.info("Application initialized, starting main loop")
        print("Starting main UI loop")
        root.mainloop()
        
        logger.info("Application exited normally")
        
    except Exception as e:
        logger.error(f"Error during application execution: {e}")
        print(f"ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(traceback.format_exc())
    
if __name__ == "__main__":
    main() 