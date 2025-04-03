"""
Voice controls tab for the AI Companion application.
"""
import tkinter as tk
from tkinter import ttk
import logging
import time

class VoiceTab:
    """
    Tab containing voice controls and settings.
    """
    def __init__(self, parent_frame, main_window):
        self.parent = parent_frame
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Initialize variables
        self.is_listening = False
        self.is_push_to_talk = False
        self.wake_word_var = tk.StringVar(value="hey ai")
        
        self._create_widgets()
        
        # Ensure the widgets are packed correctly
        parent_frame.update()
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)
        
    def _create_widgets(self):
        """Create the voice control tab widgets."""
        # Voice settings
        voice_frame = ttk.LabelFrame(self.parent, text="Voice Settings", padding="5")
        voice_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Voice selection
        voice_select_frame = ttk.Frame(voice_frame)
        voice_select_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Voice name label
        self.voice_name_var = tk.StringVar(value=f"Current Voice: {self.main_window.current_voice_name}")
        voice_name_label = ttk.Label(voice_select_frame, textvariable=self.voice_name_var)
        voice_name_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # List voices button
        list_voices = ttk.Button(voice_frame, text="List Available Voices",
                              command=self.list_voices)
        list_voices.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Wake word settings
        wake_frame = ttk.LabelFrame(self.parent, text="Wake Word", padding="5")
        wake_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Wake word entry
        wake_entry = ttk.Entry(wake_frame, textvariable=self.wake_word_var)
        wake_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Update wake word button
        update_wake = ttk.Button(wake_frame, text="Update Wake Word",
                              command=self.update_wake_word)
        update_wake.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Voice controls
        control_frame = ttk.LabelFrame(self.parent, text="Voice Controls", padding="5")
        control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Push to Talk button
        self.ptt_button = ttk.Button(control_frame, text="Push to Talk")
        self.ptt_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Continuous listening toggle
        self.listen_var = tk.BooleanVar()
        self.listen_toggle = ttk.Checkbutton(control_frame, text="Continuous Listening",
                                          variable=self.listen_var,
                                          command=self.toggle_listening)
        self.listen_toggle.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Bind push-to-talk events
        self.ptt_button.bind('<ButtonPress-1>', self.start_ptt)
        self.ptt_button.bind('<ButtonRelease-1>', self.stop_ptt)
        
    def list_voices(self):
        """List available voices in the chat window."""
        try:
            # This gets the available voices from the speech engine
            voices = self.main_window.speech_engine.list_voices()
            
            if voices:
                self.main_window.add_message("System", "Available voices:", animate=False)
                for voice in voices:
                    self.main_window.add_message("System", f"- {voice}", animate=False)
            else:
                self.main_window.add_message("System", "No voices available.", animate=False)
                
        except Exception as e:
            self.logger.error(f"Error listing voices: {e}")
            self.main_window.add_message("System", f"Error listing voices: {str(e)}", animate=False)
            
    def update_wake_word(self):
        """Update the wake word for voice recognition."""
        new_wake_word = self.wake_word_var.get().strip().lower()
        
        if not new_wake_word:
            self.main_window.add_message("System", "Wake word cannot be empty!", animate=False)
            return
            
        self.main_window.add_message("System", f"Setting wake word to: '{new_wake_word}'", animate=False)
        
        # Reset voice input with new wake word
        try:
            self._reset_voice_input()
            self.main_window.status_var.set(f"Wake word updated to: {new_wake_word}")
        except Exception as e:
            self.logger.error(f"Error updating wake word: {e}")
            self.main_window.add_message("System", f"Error updating wake word: {str(e)}", animate=False)
            
    def set_voice(self, voice_name: str):
        """Set the voice for the speech engine."""
        try:
            self.main_window.speech_engine.set_voice(voice_name)
            self.main_window.current_voice_name = voice_name
            self.voice_name_var.set(f"Current Voice: {voice_name}")
            self.main_window.add_message("System", f"Voice set to: {voice_name}", animate=False)
        except Exception as e:
            self.logger.error(f"Error setting voice: {e}")
            self.main_window.add_message("System", f"Error setting voice: {str(e)}", animate=False)
            
    def _reset_voice_input(self):
        """Reset/reinitialize the voice input component."""
        # Call the main window's method
        self.main_window._initialize_voice_input()
        
    def start_listening(self, background=False):
        """Start continuous listening."""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.listen_var.set(True)
        
        # Ensure voice input is initialized
        if self.main_window.voice_input is None:
            self._reset_voice_input()
            
        try:
            self.main_window.voice_input.start_listening(background=background)
            self.main_window.add_message("System", "Listening started", animate=False)
            self.main_window.status_var.set("Listening...")
        except Exception as e:
            self.is_listening = False
            self.listen_var.set(False)
            self.logger.error(f"Error starting listening: {e}")
            self.main_window.add_message("System", f"Error starting listening: {str(e)}", animate=False)
            
    def stop_listening(self):
        """Stop continuous listening."""
        if not self.is_listening:
            return
            
        self.is_listening = False
        self.listen_var.set(False)
        
        if self.main_window.voice_input:
            try:
                self.main_window.voice_input.stop_listening()
                self.main_window.add_message("System", "Listening stopped", animate=False)
                self.main_window.status_var.set("Ready")
            except Exception as e:
                self.logger.error(f"Error stopping listening: {e}")
                self.main_window.add_message("System", f"Error stopping listening: {str(e)}", animate=False)
                
    def start_ptt(self, event):
        """Start push-to-talk listening."""
        self.is_push_to_talk = True
        self.ptt_button.configure(text="Listening...")
        
        # Ensure voice input is initialized
        if self.main_window.voice_input is None:
            self._reset_voice_input()
            
        try:
            self.main_window.voice_input.start_listening(background=False)
            self.main_window.status_var.set("Push-to-talk active...")
        except Exception as e:
            self.is_push_to_talk = False
            self.ptt_button.configure(text="Push to Talk")
            self.logger.error(f"Error starting push-to-talk: {e}")
            self.main_window.add_message("System", f"Error starting push-to-talk: {str(e)}", animate=False)
            
    def stop_ptt(self, event):
        """Stop push-to-talk listening."""
        if not self.is_push_to_talk:
            return
            
        self.is_push_to_talk = False
        self.ptt_button.configure(text="Push to Talk")
        
        if self.main_window.voice_input:
            try:
                self.main_window.voice_input.stop_listening()
                self.main_window.status_var.set("Ready")
            except Exception as e:
                self.logger.error(f"Error stopping push-to-talk: {e}")
                
    def toggle_listening(self):
        """Toggle continuous listening mode."""
        if self.listen_var.get():
            self.start_listening(background=True)
        else:
            self.stop_listening() 