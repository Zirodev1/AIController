"""
Speech engine for text-to-speech capabilities using ElevenLabs with enhanced roleplay support.
"""
import os
import requests
import pygame
import tempfile
import time
import re
from typing import Optional, List, Tuple, Dict, Any
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
        
        # Action patterns for roleplay
        self.action_patterns = [
            (r'\*(.*?)\*', 'action'),           # *action*
            (r'\((.*?)\)', 'emotion'),          # (emotion)
            (r'\[([^\]]*?)\]', 'description'),  # [description]
        ]
        
        # Enhanced voice settings for different content types
        self.voice_settings = {
            'text': {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            'action': {
                "stability": 0.7,
                "similarity_boost": 0.8,
                "style": 0.3,
                "use_speaker_boost": True
            },
            'emotion': {
                "stability": 0.4,
                "similarity_boost": 0.9,
                "style": 0.8,
                "use_speaker_boost": True
            },
            'description': {
                "stability": 0.6,
                "similarity_boost": 0.7,
                "style": 0.4,
                "use_speaker_boost": True
            }
        }
        
        # Emotional speaking styles
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
            "seductive": {
                "style": 0.6,
                "stability": 0.8,
                "similarity_boost": 0.9,
                "description": "Intimate and alluring"
            },
            "whisper": {
                "style": 0.2,
                "stability": 0.9,
                "similarity_boost": 0.6,
                "description": "Soft and quiet"
            }
        }
        
        self.is_speaking = False
        self.current_temp_file = None

    def speak(self, text: str) -> None:
        """Speak the given text with appropriate style changes for actions and emotions."""
        if not text:
            return
            
        # Parse text into segments
        segments = self._parse_text(text)
        
        for segment_type, content in segments:
            # Determine voice settings based on segment type
            settings = self.voice_settings[segment_type if segment_type in self.voice_settings else 'text']
            
            # Adjust settings for emotional content
            if segment_type == 'emotion':
                emotion = content.lower()
                for emotion_type, emotion_settings in self.emotion_styles.items():
                    if emotion_type in emotion:
                        settings.update(emotion_settings)
                        break
            
            # Generate and play speech
            self._generate_and_play_speech(content, settings)
            
            # Removed pause between segments

    def _parse_text(self, text: str) -> List[Tuple[str, str]]:
        """Parse text into segments of regular text and special content."""
        segments = []
        last_end = 0
        
        # Sort all matches from all patterns
        matches = []
        for pattern, seg_type in self.action_patterns:
            for match in re.finditer(pattern, text):
                matches.append((match.start(), match.end(), match.group(1), seg_type))
        matches.sort()
        
        # Process matches in order
        for start, end, content, seg_type in matches:
            # Add text before this match
            if start > last_end:
                segments.append(('text', text[last_end:start].strip()))
            # Add the special content
            segments.append((seg_type, content.strip()))
            last_end = end
        
        # Add remaining text
        if last_end < len(text):
            segments.append(('text', text[last_end:].strip()))
        
        return [seg for seg in segments if seg[1]]

    def _generate_and_play_speech(self, text: str, settings: Dict[str, Any]) -> None:
        """Generate and play speech with given settings."""
        # Stop any current playback
        self.stop_speaking()
        
        # Prepare the API request
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": settings
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
            
            # Play the audio
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
                    
        except Exception as e:
            print(f"Error generating/playing speech: {e}")
            self.is_speaking = False

    def stop_speaking(self) -> None:
        """Stop the current speech."""
        if self.is_speaking:
            pygame.mixer.music.stop()
            self.is_speaking = False

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

    def __del__(self):
        """Cleanup when the object is destroyed."""
        try:
            pygame.mixer.quit()
            if self.current_temp_file and os.path.exists(self.current_temp_file):
                os.remove(self.current_temp_file)
        except:
            pass 