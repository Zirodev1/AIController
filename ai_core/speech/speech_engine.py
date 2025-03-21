"""
Speech engine for text-to-speech capabilities.
"""
import pyttsx3
import threading
from typing import Optional, Callable
import queue
import time

class SpeechEngine:
    def __init__(self):
        """Initialize the speech engine."""
        # Initialize the text-to-speech engine
        self.engine = pyttsx3.init()
        
        # Set default properties
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Get available voices and set Zira as default
        voices = self.engine.getProperty('voices')
        zira_voice_found = False
        
        # Try to find Zira voice
        for voice in voices:
            if 'zira' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                zira_voice_found = True
                print(f"Selected default voice: {voice.name}")
                break
        
        if not zira_voice_found:
            print("Warning: Zira voice not found. Using default voice.")
            print("Available voices:")
            for voice in voices:
                gender_info = f" (gender: {voice.gender})" if hasattr(voice, 'gender') else ""
                print(f"- {voice.name}{gender_info}")
                
        # Speech queue for handling multiple speech requests
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        
        # Start the speech processing thread
        self.speech_thread = threading.Thread(target=self._process_speech_queue, daemon=True)
        self.speech_thread.start()
        
    def speak(self, text: str, callback: Optional[Callable] = None) -> None:
        """
        Add text to the speech queue.
        
        Args:
            text: Text to speak
            callback: Optional callback function to execute after speaking
        """
        self.speech_queue.put((text, callback))
        
    def stop_speaking(self) -> None:
        """Stop the current speech and clear the queue."""
        self.engine.stop()
        self.is_speaking = False
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
                
    def set_rate(self, rate: int) -> None:
        """Set the speech rate."""
        self.engine.setProperty('rate', rate)
        
    def set_volume(self, volume: float) -> None:
        """Set the speech volume (0.0 to 1.0)."""
        self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
        
    def set_voice(self, voice_id: str) -> None:
        """Set the voice to use."""
        # Get all available voices
        voices = self.engine.getProperty('voices')
        
        # Find the voice with matching ID (case-insensitive)
        for voice in voices:
            if voice.id.lower() == voice_id.lower():
                self.engine.setProperty('voice', voice.id)  # Use original case from voice.id
                print(f"Successfully set voice to: {voice.name}")
                return
                
        print(f"Warning: Voice ID '{voice_id}' not found")
        
    def list_voices(self) -> None:
        """List all available voices with their properties."""
        voices = self.engine.getProperty('voices')
        print("\nAvailable voices:")
        for i, voice in enumerate(voices, 1):
            gender_info = f" (gender: {voice.gender})" if hasattr(voice, 'gender') else ""
            languages = f" (languages: {voice.languages})" if hasattr(voice, 'languages') and voice.languages else ""
            age = f" (age: {voice.age})" if hasattr(voice, 'age') and voice.age else ""
            print(f"\n{i}. Voice Name: {voice.name}{gender_info}{languages}{age}")
            print(f"   ID: {voice.id}")
            print(f"   Current: {'✓' if voice.id == self.engine.getProperty('voice') else ' '}")
        
    def _process_speech_queue(self) -> None:
        """Process speech requests from the queue."""
        while True:
            try:
                if not self.speech_queue.empty():
                    text, callback = self.speech_queue.get()
                    self.is_speaking = True
                    self.engine.say(text)
                    self.engine.runAndWait()
                    self.is_speaking = False
                    
                    if callback:
                        callback()
                        
            except Exception as e:
                print(f"Error in speech processing: {e}")
                self.is_speaking = False
                
            time.sleep(0.1)  # Small delay to prevent CPU overuse 