"""
Test script for demonstrating NLP capabilities integrated with emotional and speech systems.
"""
from ai_core.nlp.text_processor import TextProcessor
from ai_core.emotions.emotion_engine import EmotionEngine
from ai_core.speech.speech_engine import SpeechEngine
from ai_core.llm.llm_interface import LLMInterface
import json

class AITester:
    def __init__(self):
        """Initialize all AI components."""
        print("Initializing AI systems...")
        self.text_processor = TextProcessor()
        self.emotion_engine = EmotionEngine()
        self.speech_engine = SpeechEngine()
        self.llm = LLMInterface()
        
        # Set default mode
        self.content_mode = 'family'
        self.speech_enabled = True
        print("All systems initialized successfully!")

    def process_input(self, text: str) -> None:
        """Process user input through all AI systems."""
        print("\n=== Processing Input ===")
        print(f"Input text: {text}")
        
        # NLP Analysis
        nlp_analysis = self.text_processor.process_text(text, self.content_mode)
        
        # Print NLP insights
        print("\n=== NLP Analysis ===")
        print(f"Sentiment: {nlp_analysis['sentiment']['category']} "
              f"(polarity: {nlp_analysis['sentiment']['polarity']:.2f})")
        print(f"Detected intents: {json.dumps(nlp_analysis['intent'], indent=2)}")
        print(f"Key phrases: {', '.join(nlp_analysis['key_phrases'])}")
        
        # Update emotional state based on NLP analysis
        self.emotion_engine.process_text(text)
        emotional_state = self.emotion_engine.get_emotional_state()
        print("\n=== Emotional State ===")
        print(json.dumps(emotional_state, indent=2))
        
        # Generate response using LLM
        response = self.llm.generate_response(emotional_state, text)
        print("\n=== AI Response ===")
        print(response)
        
        # Speak response if enabled
        if self.speech_enabled:
            self.speech_engine.speak(response)

    def handle_command(self, command: str) -> bool:
        """Handle system commands."""
        parts = command.lower().split()
        if not parts:
            return True

        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "quit":
            return False
        elif cmd == "mode":
            if args and args[0] in ['family', 'mature', 'adult']:
                self.content_mode = args[0]
                self.llm.set_content_mode(args[0], True)  # Assuming age verified
                print(f"Switched to {args[0]} mode")
            else:
                print("Available modes: family, mature, adult")
        elif cmd == "speech":
            if args and args[0] in ['on', 'off']:
                self.speech_enabled = args[0] == 'on'
                print(f"Speech {'enabled' if self.speech_enabled else 'disabled'}")
            else:
                print("Usage: speech [on|off]")
        elif cmd == "voice":
            if args:
                self.speech_engine.set_voice(args[0])
            else:
                print("Available voices:")
                self.speech_engine.list_voices()
        elif cmd == "summary":
            summary = self.text_processor.get_conversation_summary()
            print("\n=== Conversation Summary ===")
            print(json.dumps(summary, indent=2))
        elif cmd == "help":
            self._print_help()
        else:
            self.process_input(command)
        
        return True

    def _print_help(self):
        """Print available commands."""
        print("\nAvailable Commands:")
        print("  mode [family|mature|adult] - Set content mode")
        print("  speech [on|off] - Enable/disable speech")
        print("  voice [id] - Set voice by ID")
        print("  summary - Show conversation summary")
        print("  help - Show this help message")
        print("  quit - Exit the program")
        print("\nAny other input will be processed as a conversation with the AI")

def main():
    """Main function to run the AI tester."""
    tester = AITester()
    print("\nAI Tester initialized. Type 'help' for available commands.")
    
    while True:
        try:
            user_input = input("\nEnter command or message: ").strip()
            if not tester.handle_command(user_input):
                break
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 