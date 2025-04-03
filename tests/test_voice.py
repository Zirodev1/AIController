"""
Test script for voice interaction with the AI.
"""
from ai_core.speech.voice_input import VoiceInput
from ai_core.speech.speech_engine import SpeechEngine
from ai_core.emotions.emotion_engine import EmotionEngine
from ai_core.llm.llm_interface import LLMInterface
from ai_core.nlp.text_processor import TextProcessor
import time

class VoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant with all components."""
        print("Initializing AI systems...")
        self.voice_input = VoiceInput(wake_word="hey ai")
        self.speech_engine = SpeechEngine()
        self.emotion_engine = EmotionEngine()
        self.llm = LLMInterface()
        self.text_processor = TextProcessor()
        
        # Set up voice input callbacks
        self.voice_input.set_callbacks(
            on_wake_word=self._handle_wake_word,
            on_command_received=self._handle_command
        )
        
        print("All systems initialized!")
        
    def start(self):
        """Start the voice assistant."""
        print("\nStarting voice assistant...")
        print("Say 'Hey AI' to get my attention!")
        self.voice_input.start_listening(background=True)
        
        try:
            while True:
                # Keep the main thread alive
                input()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.voice_input.stop_listening()
            
    def _handle_wake_word(self):
        """Handle wake word detection."""
        # Set speaking state before response
        self.voice_input.set_speaking_state(True)
        
        response = "*perking up* Yes? I'm listening!"
        print("\nWake word detected!")
        self.speech_engine.speak(response)
        
        # Small delay to ensure speech is finished
        time.sleep(0.5)
        
        # Reset speaking state after response
        self.voice_input.set_speaking_state(False)
        
    def _handle_command(self, text: str):
        """Process voice command and generate response."""
        print(f"\nProcessing command: {text}")
        
        # Set speaking state before processing
        self.voice_input.set_speaking_state(True)
        
        try:
            # Process text through NLP
            nlp_analysis = self.text_processor.process_text(text)
            
            # Update emotional state
            self.emotion_engine.process_text(text)
            emotional_state = self.emotion_engine.get_emotional_state()
            
            # Generate response using LLM
            response = self.llm.generate_response(emotional_state, text)
            
            # Speak the response
            print(f"AI: {response}")
            self.speech_engine.speak(response)
            
            # Small delay to ensure speech is finished
            time.sleep(0.5)
            
        finally:
            # Always reset speaking state after processing
            self.voice_input.set_speaking_state(False)

def main():
    """Main function to run the voice assistant."""
    assistant = VoiceAssistant()
    assistant.start()

if __name__ == "__main__":
    main() 