"""
Chat interface tab for the AI Companion application.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import logging

from ai_core.gui.command_processor import CommandProcessor

class ChatTab:
    """
    Tab containing the chat interface for interacting with the AI.
    """
    def __init__(self, parent_frame, main_window):
        self.parent = parent_frame
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Initialize command processor
        self.command_processor = CommandProcessor(main_window)
        
        self._create_widgets()
        
        # Ensure the widgets are packed correctly
        parent_frame.update()
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)
        
    def _create_widgets(self):
        """Create the chat interface widgets."""
        # Chat display
        self.chat_text = scrolledtext.ScrolledText(self.parent, wrap=tk.WORD)
        self.chat_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Make the chat text accessible from main window
        self.main_window.chat_text = self.chat_text
        
        # Input frame
        input_frame = ttk.Frame(self.parent)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Text input
        self.text_input = ttk.Entry(input_frame)
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        # Make the text input accessible from main window
        self.main_window.text_input = self.text_input
        
        # Send button
        send_button = ttk.Button(input_frame, text="Send",
                              command=self._handle_text_input)
        send_button.grid(row=0, column=1, padx=5)
        
        # Add a command button
        command_button = ttk.Button(input_frame, text="/",
                                 command=self._show_command_help,
                                 width=2)
        command_button.grid(row=0, column=2, padx=(0, 5))
        
        # Bind Enter key
        self.text_input.bind('<Return>', lambda e: self._handle_text_input())
        
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)
        
    def _handle_text_input(self):
        """Process text input from the entry field."""
        text = self.text_input.get().strip()
        if text:
            self.text_input.delete(0, tk.END)
            
            # Check if it's a command
            if text.startswith('/') and self.command_processor.process_text(text):
                return
                
            # Not a command, process as normal input
            self.main_window._process_input(text)
    
    def _show_command_help(self):
        """Show command help when the command button is clicked."""
        # First, insert '/' into the text input
        self.text_input.insert(tk.END, '/')
        self.text_input.focus_set()
        
        # Show command help
        self.command_processor._show_help("Available commands:")
        
    def clear_chat(self):
        """Clear the chat display."""
        self.chat_text.delete(1.0, tk.END)
        self.main_window.add_message("System", "Chat cleared", animate=False)
        
    def save_chat(self, filename=None):
        """Save the chat content to a file."""
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_log_{timestamp}.txt"
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.chat_text.get(1.0, tk.END))
                
            self.main_window.add_message("System", f"Chat saved to '{filename}'", animate=False)
            
        except Exception as e:
            self.logger.error(f"Error saving chat: {e}")
            self.main_window.add_message("System", f"Error saving chat: {str(e)}", animate=False) 