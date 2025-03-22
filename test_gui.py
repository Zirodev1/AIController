"""
GUI testing interface for the AI system.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import time
from datetime import datetime
from ai_core.speech.voice_input import VoiceInput
from ai_core.speech.speech_engine import SpeechEngine
from ai_core.emotions.emotion_engine import EmotionEngine
from ai_core.llm.llm_interface import LLMInterface
from ai_core.nlp.text_processor import TextProcessor

class AIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Testing Interface")
        self.root.geometry("800x600")
        
        # Initialize AI components
        self.voice_input = None  # Will initialize when needed
        self.speech_engine = SpeechEngine()
        self.emotion_engine = EmotionEngine()
        self.llm = LLMInterface()
        self.text_processor = TextProcessor()
        
        # GUI state variables
        self.is_listening = False
        self.is_push_to_talk = False
        self.message_queue = queue.Queue()
        self.typing_speed = 50  # milliseconds per character
        self.is_typing = False
        self.current_voice_name = "Zira"  # Default voice name
        
        # Interaction mode flags
        self.use_voice_input = True
        self.use_voice_output = True
        
        self._create_gui()
        
        # Start message processing
        self.process_messages()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_gui(self):
        """Create the GUI elements."""
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left panel - Controls
        left_panel = ttk.LabelFrame(main_container, text="Controls", padding="5")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Interaction mode frame
        mode_frame = ttk.LabelFrame(left_panel, text="Interaction Mode", padding="5")
        mode_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # User input mode
        self.user_mode_var = tk.BooleanVar(value=True)
        user_mode = ttk.Checkbutton(mode_frame, text="Voice Input",
                                  variable=self.user_mode_var,
                                  command=self._toggle_input_mode)
        user_mode.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # AI output mode
        self.ai_mode_var = tk.BooleanVar(value=True)
        ai_mode = ttk.Checkbutton(mode_frame, text="Voice Output",
                               variable=self.ai_mode_var,
                               command=self._toggle_output_mode)
        ai_mode.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Text input frame
        text_frame = ttk.Frame(mode_frame)
        text_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Text input field
        self.text_input = ttk.Entry(text_frame)
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2)
        
        # Send button
        send_button = ttk.Button(text_frame, text="Send",
                               command=self._handle_text_input)
        send_button.grid(row=0, column=1, padx=2)
        
        # Bind Enter key to send
        self.text_input.bind('<Return>', lambda e: self._handle_text_input())
        
        # Listening mode frame
        listen_frame = ttk.LabelFrame(left_panel, text="Voice Controls", padding="5")
        listen_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Push to Talk button
        self.ptt_button = ttk.Button(listen_frame, text="Push to Talk")
        self.ptt_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Bind push-to-talk events
        self.ptt_button.bind('<ButtonPress-1>', self.start_ptt)
        self.ptt_button.bind('<ButtonRelease-1>', self.stop_ptt)
        
        # Continuous listening toggle
        self.listen_var = tk.BooleanVar()
        self.listen_toggle = ttk.Checkbutton(listen_frame, text="Continuous Listening",
                                           variable=self.listen_var,
                                           command=self.toggle_listening)
        self.listen_toggle.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Wake word frame
        wake_frame = ttk.LabelFrame(left_panel, text="Wake Word", padding="5")
        wake_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Wake word entry
        self.wake_word_var = tk.StringVar(value="hey ai")
        wake_entry = ttk.Entry(wake_frame, textvariable=self.wake_word_var)
        wake_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Update wake word button
        update_wake = ttk.Button(wake_frame, text="Update Wake Word",
                               command=self.update_wake_word)
        update_wake.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Voice settings frame
        voice_frame = ttk.LabelFrame(left_panel, text="Voice Settings", padding="5")
        voice_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Voice selection
        voice_select_frame = ttk.Frame(voice_frame)
        voice_select_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Voice name label
        self.voice_name_var = tk.StringVar(value=f"Current Voice: {self.current_voice_name}")
        voice_name_label = ttk.Label(voice_select_frame, textvariable=self.voice_name_var)
        voice_name_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # List voices button
        list_voices = ttk.Button(voice_frame, text="List Available Voices",
                               command=self.list_voices)
        list_voices.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Debug controls
        debug_frame = ttk.LabelFrame(left_panel, text="Debug", padding="5")
        debug_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Reset button
        reset_button = ttk.Button(debug_frame, text="Reset Voice Input",
                                command=self._reset_voice_input)
        reset_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Right panel - Output
        right_panel = ttk.Frame(main_container)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Conversation display
        conv_frame = ttk.LabelFrame(right_panel, text="Conversation", padding="5")
        conv_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Conversation text area
        self.conv_text = scrolledtext.ScrolledText(conv_frame, wrap=tk.WORD,
                                                 width=50, height=20)
        self.conv_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_container, textvariable=self.status_var,
                             relief=tk.SUNKEN, padding="2")
        status_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        
        # Update UI state
        self._update_ui_state()

    def _toggle_input_mode(self):
        """Toggle between voice and text input."""
        self.use_voice_input = self.user_mode_var.get()
        self._update_ui_state()
        
        # Stop listening if switching to text mode
        if not self.use_voice_input and self.is_listening:
            self.stop_listening()

    def _toggle_output_mode(self):
        """Toggle between voice and text output."""
        self.use_voice_output = self.ai_mode_var.get()

    def _update_ui_state(self):
        """Update UI elements based on current mode."""
        # Enable/disable voice controls
        for widget in [self.ptt_button, self.listen_toggle]:
            widget.configure(state='normal' if self.use_voice_input else 'disabled')
        
        # Enable/disable text input
        self.text_input.configure(state='normal' if not self.use_voice_input else 'disabled')
        
        # Update status message
        mode = "voice" if self.use_voice_input else "text"
        self.status_var.set(f"Using {mode} input")

    def _handle_text_input(self):
        """Process text input from the entry field."""
        text = self.text_input.get().strip()
        if text:
            self.text_input.delete(0, tk.END)
            self._process_input(text)

    def _process_input(self, text: str):
        """Process input regardless of source (voice or text)."""
        self.add_message("You", text, animate=False)
        self.status_var.set("Processing input...")
        
        try:
            # Process input
            nlp_analysis = self.text_processor.process_text(text)
            self.emotion_engine.process_text(text)
            emotional_state = self.emotion_engine.get_emotional_state()
            
            # Generate response
            response = self.llm.generate_response(emotional_state, text)
            
            # Handle response output
            if self.use_voice_output:
                # If using voice, show text immediately and speak
                self.add_message(self.current_voice_name, response, animate=False)
                self.speech_engine.speak(response)
            else:
                # If text only, animate the response
                self.add_message(self.current_voice_name, response, animate=True)
            
        finally:
            self.status_var.set("Ready")

    def _initialize_voice_input(self):
        """Initialize or reinitialize the voice input component."""
        if self.voice_input:
            self.voice_input.stop_listening()  # Ensure old instance is stopped
            
        self.voice_input = VoiceInput(wake_word=self.wake_word_var.get())
        self.voice_input.set_callbacks(
            on_wake_word=self._handle_wake_word,
            on_command_received=self._handle_command
        )
        self.add_message("System", "Voice input system initialized")
        self.status_var.set("Ready")

    def _reset_voice_input(self):
        """Reset the voice input system."""
        self.status_var.set("Resetting voice input...")
        if self.is_listening:
            self.stop_listening()
        self._initialize_voice_input()
        self.add_message("System", "Voice input system reset complete")

    def start_listening(self, background=False):
        """Start listening with proper state management."""
        if not self.voice_input:
            self._initialize_voice_input()
        
        if not self.is_listening:
            self.is_listening = True
            self.voice_input.start_listening(background=background)
            self.status_var.set("Listening..." if not background else "Listening for wake word...")
            self.add_message("System", "Started listening" if not background else "Listening for wake word")

    def stop_listening(self):
        """Stop listening with proper state management."""
        if self.is_listening and self.voice_input:
            self.is_listening = False
            self.voice_input.stop_listening()
            self.status_var.set("Ready")
            self.add_message("System", "Stopped listening")

    def start_ptt(self, event):
        """Handle push-to-talk button press."""
        if not self.is_listening:
            self.start_listening(background=False)

    def stop_ptt(self, event):
        """Handle push-to-talk button release."""
        if self.is_listening:
            self.stop_listening()

    def toggle_listening(self):
        """Toggle continuous listening mode."""
        if self.listen_var.get():
            self.start_listening(background=True)
        else:
            self.stop_listening()

    def update_wake_word(self):
        """Update the wake word."""
        new_wake_word = self.wake_word_var.get().strip()
        if new_wake_word:
            self._reset_voice_input()  # Reinitialize with new wake word

    def set_voice(self, voice_name: str):
        """Set the current voice and update the display."""
        self.current_voice_name = voice_name
        self.voice_name_var.set(f"Current Voice: {voice_name}")
        self.add_message("System", f"Switched to voice: {voice_name}", animate=False)

    def list_voices(self):
        """List available voices and allow selection."""
        voices = self.speech_engine.list_voices()
        if voices:
            self.add_message("System", "Available voices:", animate=False)
            for voice in voices:
                self.add_message("System", f"- {voice}", animate=False)
            
            # If we have the current voice in the list, update the display
            current = self.speech_engine.get_current_voice()
            if current:
                self.set_voice(current)

    def _handle_wake_word(self):
        """Handle wake word detection."""
        self.status_var.set("Wake word detected!")
        self.add_message("System", "Wake word detected!", animate=False)
        
        # Set speaking state and respond
        self.voice_input.set_speaking_state(True)
        response = "*perking up* Yes? I'm listening!"
        
        if self.use_voice_output:
            self.add_message(self.current_voice_name, response, animate=False)
            self.speech_engine.speak(response)
        else:
            self.add_message(self.current_voice_name, response, animate=True)
        
        # Reset speaking state
        time.sleep(0.5)
        self.voice_input.set_speaking_state(False)

    def _handle_command(self, text: str):
        """Handle received command."""
        self._process_input(text)

    def add_message(self, sender: str, message: str, animate=False):
        """Add a message to the queue for display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}] {sender}: "
        
        if not animate:
            # Add message immediately to queue
            self.message_queue.put((prefix + message + "\n", False))
        else:
            # Add prefix without animation
            self.message_queue.put((prefix, False))
            # Add message with animation
            self.message_queue.put((message + "\n", True))

    def process_messages(self):
        """Process and display queued messages."""
        if not self.is_typing:
            try:
                while True:
                    message, should_animate = self.message_queue.get_nowait()
                    if should_animate:
                        # Start typing animation for this message
                        self.is_typing = True
                        self._animate_typing(message, 0)
                    else:
                        # Display message immediately
                        self.conv_text.insert(tk.END, message)
                        self.conv_text.see(tk.END)
            except queue.Empty:
                pass
        
        # Schedule next update
        self.root.after(100, self.process_messages)

    def _animate_typing(self, message, index):
        """Animate typing effect for a message."""
        if index < len(message):
            # Add next character
            self.conv_text.insert(tk.END, message[index])
            self.conv_text.see(tk.END)
            # Schedule next character
            self.root.after(self.typing_speed, 
                          lambda: self._animate_typing(message, index + 1))
        else:
            # Animation complete
            self.is_typing = False

    def _on_closing(self):
        """Handle window closing event."""
        if self.voice_input:
            self.voice_input.stop_listening()
        self.root.destroy()

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = AIGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 