"""
Modern theme and styling for the AI Companion application.
"""

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
    
    @staticmethod
    def apply(widget, theme_style):
        """Apply a theme style to a widget."""
        for key, value in theme_style.items():
            try:
                widget[key] = value
            except Exception:
                # Some keys might not be valid for all widgets
                pass 