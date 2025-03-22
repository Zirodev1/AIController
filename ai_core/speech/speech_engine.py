"""
Speech engine for text-to-speech capabilities using ElevenLabs.
"""
import os
import requests
import pygame
import tempfile
import time
from typing import Optional, Callable, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpeechEngine:
    def __init__(self):
        """Initialize the speech engine with ElevenLabs."""
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required. Please set ELEVENLABS_API_KEY in your .env file.")
            
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Default voice settings
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID')
        if not self.voice_id:
            print("Warning: No default voice ID set. Please set ELEVENLABS_VOICE_ID in your .env file.")
        
        self.model_id = "eleven_monolingual_v1"
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Create directories for saving audio files
        self.audio_dir = "generated_audio"
        self.training_dir = os.path.join(self.audio_dir, "training_data")
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.training_dir, exist_ok=True)
        
        # Enhanced emotional voice settings
        self.voice_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
        
        # Enhanced emotional speaking styles with more nuanced control
        self.emotion_styles = {
            "happy": {
                "style": 0.8,
                "stability": 0.7,
                "similarity_boost": 0.8,
                "description": "Upbeat and cheerful"
            },
            "sad": {
                "style": 0.3,
                "stability": 0.6,
                "similarity_boost": 0.7,
                "description": "Melancholic and subdued"
            },
            "angry": {
                "style": 0.9,
                "stability": 0.4,
                "similarity_boost": 0.9,
                "description": "Intense and forceful"
            },
            "excited": {
                "style": 0.9,
                "stability": 0.5,
                "similarity_boost": 0.8,
                "description": "High energy and enthusiastic"
            },
            "calm": {
                "style": 0.2,
                "stability": 0.8,
                "similarity_boost": 0.6,
                "description": "Peaceful and soothing"
            },
            "neutral": {
                "style": 0.5,
                "stability": 0.5,
                "similarity_boost": 0.7,
                "description": "Balanced and natural"
            },
            "confident": {
                "style": 0.7,
                "stability": 0.6,
                "similarity_boost": 0.8,
                "description": "Strong and assured"
            },
            "gentle": {
                "style": 0.3,
                "stability": 0.7,
                "similarity_boost": 0.6,
                "description": "Soft and caring"
            }
        }
        
        self.is_speaking = False
        self.current_temp_file = None
        
    def speak(self, text: str, emotion: Optional[str] = None, callback: Optional[Callable] = None, save_for_training: bool = True) -> str:
        """
        Speak the given text with emotional expression and optionally save for training.
        
        Args:
            text: Text to speak
            emotion: Emotional state to express (happy, sad, angry, etc.)
            callback: Optional callback function to execute after speaking
            save_for_training: Whether to save the audio file for training
            
        Returns:
            str: Path to the saved audio file if save_for_training is True, else empty string
        """
        print(f"Speaking with emotion '{emotion or 'neutral'}': {text[:50]}...")
        
        # Update voice settings based on emotion
        if emotion and emotion in self.emotion_styles:
            style_settings = self.emotion_styles[emotion]
            self.voice_settings.update({
                k: v for k, v in style_settings.items() 
                if k in ["style", "stability", "similarity_boost"]
            })
        
        # Stop any current playback
        self.stop_speaking()
        
        # Prepare the API request
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": self.voice_settings
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            # Create a new temporary file for playback
            temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(temp_fd)
            
            # Save the previous temp file path
            previous_temp_file = self.current_temp_file
            self.current_temp_file = temp_path
            
            # Save the audio content
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            # Save a copy for training if requested
            saved_path = ""
            if save_for_training:
                # Create a filename with timestamp and emotion
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                emotion_str = emotion if emotion else "neutral"
                filename = f"{timestamp}_{emotion_str}.mp3"
                
                # Save in training directory
                training_path = os.path.join(self.training_dir, filename)
                with open(training_path, "wb") as f:
                    f.write(response.content)
                    
                # Save metadata
                metadata_path = os.path.join(self.training_dir, f"{timestamp}_{emotion_str}.txt")
                with open(metadata_path, "w", encoding='utf-8') as f:
                    f.write(f"Text: {text}\n")
                    f.write(f"Emotion: {emotion_str}\n")
                    f.write(f"Voice Settings: {self.voice_settings}\n")
                    if emotion in self.emotion_styles:
                        f.write(f"Style Description: {self.emotion_styles[emotion]['description']}\n")
                
                saved_path = training_path
                print(f"Saved audio for training: {training_path}")
            
            # Play the audio
            print("Playing audio...")
            self.is_speaking = True
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            self.is_speaking = False
            
            # Clean up the previous temporary file
            if previous_temp_file and os.path.exists(previous_temp_file):
                try:
                    os.remove(previous_temp_file)
                except:
                    pass
                    
            if callback:
                callback()
                
            return saved_path
                
        except Exception as e:
            print(f"Error generating/playing speech: {e}")
            self.is_speaking = False
            return ""
            
    def stop_speaking(self) -> None:
        """Stop the current speech."""
        if self.is_speaking:
            print("Stopping speech...")
            pygame.mixer.music.stop()
            self.is_speaking = False
        
    def set_emotion(self, emotion: str) -> None:
        """Set the emotional style for speech."""
        if emotion in self.emotion_styles:
            style_settings = self.emotion_styles[emotion]
            self.voice_settings.update({
                k: v for k, v in style_settings.items() 
                if k in ["style", "stability", "similarity_boost"]
            })
            print(f"Emotional style set to: {emotion} ({style_settings['description']})")
        else:
            print(f"Unknown emotion: {emotion}")
            print("Available emotions:", ", ".join(self.emotion_styles.keys()))
            
    def set_voice(self, voice_id: str) -> None:
        """Set the voice to use."""
        self.voice_id = voice_id
        print(f"Voice set to: {voice_id}")
        
    def list_voices(self) -> None:
        """List all available voices."""
        try:
            response = requests.get(f"{self.base_url}/voices", headers=self.headers)
            response.raise_for_status()
            voices = response.json()["voices"]
            
            print("\nAvailable voices:")
            for voice in voices:
                print(f"\nVoice Name: {voice['name']}")
                print(f"ID: {voice['voice_id']}")
                print(f"Labels: {voice.get('labels', {})}")
                
        except Exception as e:
            print(f"Error listing voices: {e}")
            
    def set_voice_settings(self, settings: Dict[str, float]) -> None:
        """Set custom voice settings."""
        self.voice_settings.update(settings)
        print("Voice settings updated")
        
    def get_emotion_description(self, emotion: str) -> str:
        """Get the description of an emotional style."""
        if emotion in self.emotion_styles:
            return self.emotion_styles[emotion]['description']
        return "Unknown emotion"
        
    def __del__(self):
        """Cleanup when the object is destroyed."""
        try:
            pygame.mixer.quit()
            if self.current_temp_file and os.path.exists(self.current_temp_file):
                os.remove(self.current_temp_file)
        except:
            pass 