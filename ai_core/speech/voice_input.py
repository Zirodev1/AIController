"""
Voice input processing using speech recognition with wake word detection and emotion analysis.
"""
import speech_recognition as sr
import numpy as np
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any

class VoiceInput:
    def __init__(self, wake_word: str = "hey ai"):
        """Initialize voice input system."""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.wake_word = wake_word.lower()
        
        # Queues for processing
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        
        # Processing flags
        self.is_listening = False
        self.is_processing = False
        self.background_listening = False
        self.ai_is_speaking = False  # New flag to track AI speech
        
        # Energy threshold for speech detection
        self.energy_threshold = 300  # Default value
        self.dynamic_energy_ratio = 1.5  # Multiplier for dynamic energy threshold
        
        # Callbacks
        self.on_wake_word: Optional[Callable] = None
        self.on_speech_detected: Optional[Callable] = None
        self.on_command_received: Optional[Callable] = None
        
        # Adjust for ambient noise
        print("Calibrating microphone for ambient noise... Please stay quiet.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            # Set energy threshold higher than ambient noise
            self.energy_threshold = self.recognizer.energy_threshold * self.dynamic_energy_ratio
            self.recognizer.energy_threshold = self.energy_threshold
        print(f"Microphone calibrated! Energy threshold: {self.energy_threshold}")

    def set_speaking_state(self, is_speaking: bool):
        """Set whether the AI is currently speaking."""
        self.ai_is_speaking = is_speaking
        if is_speaking:
            # Temporarily increase energy threshold while AI is speaking
            self.recognizer.energy_threshold = self.energy_threshold * 2
        else:
            # Reset to normal threshold
            self.recognizer.energy_threshold = self.energy_threshold

    def start_listening(self, background: bool = True) -> None:
        """Start listening for voice input."""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.background_listening = background
        
        if background:
            # Start background listening thread
            self.listen_thread = threading.Thread(target=self._background_listening)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            
            # Start processing thread
            self.process_thread = threading.Thread(target=self._process_audio)
            self.process_thread.daemon = True
            self.process_thread.start()
        else:
            # Single foreground listening session
            self._listen_once()

    def stop_listening(self) -> None:
        """Stop listening for voice input."""
        self.is_listening = False
        self.background_listening = False

    def _background_listening(self) -> None:
        """Continuously listen for audio in background."""
        while self.background_listening:
            try:
                with self.microphone as source:
                    print("Listening..." if not self.ai_is_speaking else "AI speaking...")
                    
                    # Skip audio processing if AI is speaking
                    if self.ai_is_speaking:
                        time.sleep(0.1)
                        continue
                        
                    audio = self.recognizer.listen(
                        source,
                        timeout=None,
                        phrase_time_limit=10,
                    )
                    self.audio_queue.put(audio)
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Error in background listening: {e}")
                time.sleep(1)

    def _process_audio(self) -> None:
        """Process audio from queue."""
        while self.is_listening:
            try:
                # Skip processing if AI is speaking
                if self.ai_is_speaking:
                    time.sleep(0.1)
                    continue
                    
                audio = self.audio_queue.get(timeout=1)
                text = self._recognize_speech(audio)
                
                if text:
                    text = text.lower()
                    print(f"Recognized: {text}")
                    
                    # Check for wake word if not already processing
                    if not self.is_processing and self.wake_word in text:
                        self.is_processing = True
                        if self.on_wake_word:
                            self.on_wake_word()
                    # Process command if wake word was detected
                    elif self.is_processing:
                        if self.on_command_received:
                            self.on_command_received(text)
                        self.is_processing = False
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
                self.is_processing = False

    def _listen_once(self) -> None:
        """Listen for a single voice input."""
        try:
            with self.microphone as source:
                print("Listening for command...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self._recognize_speech(audio)
                
                if text and self.on_command_received:
                    self.on_command_received(text)
                    
        except sr.WaitTimeoutError:
            print("No speech detected")
        except Exception as e:
            print(f"Error in single listening: {e}")

    def _recognize_speech(self, audio: sr.AudioData) -> Optional[str]:
        """Convert audio to text using speech recognition."""
        try:
            # Try using Google's speech recognition
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Error in speech recognition: {e}")
        return None

    def set_wake_word(self, wake_word: str) -> None:
        """Set the wake word for voice activation."""
        self.wake_word = wake_word.lower()

    def set_callbacks(self, 
                     on_wake_word: Optional[Callable] = None,
                     on_speech_detected: Optional[Callable] = None,
                     on_command_received: Optional[Callable] = None) -> None:
        """Set callback functions for various events."""
        self.on_wake_word = on_wake_word
        self.on_speech_detected = on_speech_detected
        self.on_command_received = on_command_received 