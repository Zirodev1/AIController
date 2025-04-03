"""
Utility functions for the AI Companion GUI.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import logging
import threading
from PIL import Image, ImageTk
import datetime

# Setup logger
logger = logging.getLogger(__name__)

def load_json_file(file_path):
    """Load data from a JSON file."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading JSON file '{file_path}': {e}")
        return {}

def save_json_file(file_path, data):
    """Save data to a JSON file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file '{file_path}': {e}")
        return False

def ask_save_file(title="Save File", filetypes=(("All Files", "*.*"),), 
                 defaultextension="", initialdir=None):
    """Show a save file dialog and return the selected path."""
    return filedialog.asksaveasfilename(
        title=title,
        filetypes=filetypes,
        defaultextension=defaultextension,
        initialdir=initialdir
    )

def ask_open_file(title="Open File", filetypes=(("All Files", "*.*"),), 
                 initialdir=None):
    """Show an open file dialog and return the selected path."""
    return filedialog.askopenfilename(
        title=title,
        filetypes=filetypes,
        initialdir=initialdir
    )

def create_tool_tip(widget, text):
    """Create a tooltip for a widget."""
    
    def enter(event):
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Create a toplevel window
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(tooltip, text=text, justify=tk.LEFT,
                        background="#FFFFDD", relief=tk.SOLID, borderwidth=1,
                        padding=(5, 2))
        label.pack()
        
        widget.tooltip = tooltip
        
    def leave(event):
        if hasattr(widget, "tooltip"):
            widget.tooltip.destroy()
            
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

def run_in_thread(func, *args, **kwargs):
    """Run a function in a separate thread."""
    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread

def generate_timestamp():
    """Generate a formatted timestamp string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_filename_timestamp():
    """Generate a timestamp suitable for filenames."""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def resize_image(image, max_width=None, max_height=None):
    """Resize an image while maintaining aspect ratio."""
    if not isinstance(image, Image.Image):
        logger.error("Invalid image type for resize_image")
        return None
        
    img_width, img_height = image.size
    
    if max_width is None and max_height is None:
        return image  # No resize needed
        
    if max_width is None:
        # Only constrain height
        scale = max_height / img_height
        new_width = int(img_width * scale)
        new_height = max_height
    elif max_height is None:
        # Only constrain width
        scale = max_width / img_width
        new_width = max_width
        new_height = int(img_height * scale)
    else:
        # Constrain both dimensions, maintain aspect ratio
        width_scale = max_width / img_width
        height_scale = max_height / img_height
        scale = min(width_scale, height_scale)  # Use the more restrictive scale
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
    return image.resize((new_width, new_height), Image.LANCZOS)

def image_to_photoimage(pil_image):
    """Convert a PIL image to a Tkinter PhotoImage."""
    try:
        return ImageTk.PhotoImage(pil_image)
    except Exception as e:
        logger.error(f"Error converting image to PhotoImage: {e}")
        return None

def show_error(title, message):
    """Show an error message dialog."""
    messagebox.showerror(title, message)

def show_info(title, message):
    """Show an information message dialog."""
    messagebox.showinfo(title, message)

def show_warning(title, message):
    """Show a warning message dialog."""
    messagebox.showwarning(title, message)

def ask_yes_no(title, message):
    """Show a yes/no question dialog."""
    return messagebox.askyesno(title, message)

def ask_ok_cancel(title, message):
    """Show an OK/Cancel question dialog."""
    return messagebox.askokcancel(title, message)

def create_button_with_icon(parent, text, command, icon_path=None, **kwargs):
    """Create a button with an optional icon."""
    button = ttk.Button(parent, text=text, command=command, **kwargs)
    
    if icon_path and os.path.exists(icon_path):
        try:
            icon = Image.open(icon_path)
            icon = resize_image(icon, max_width=16, max_height=16)
            photo = ImageTk.PhotoImage(icon)
            button.image = photo  # Keep a reference
            button.configure(image=photo, compound=tk.LEFT)
        except Exception as e:
            logger.error(f"Error loading icon for button: {e}")
            
    return button 