"""
Test script for the emotional system.
"""
import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_core.emotions.emotion_engine import EmotionEngine
import json

def print_emotion_state(engine):
    """Print the current emotional state in a readable format."""
    state = engine.get_current_emotion()
    print("\nCurrent Emotional State:")
    print("-" * 50)
    print(f"Complex State: {state['complex_state']} (confidence: {state['complex_confidence']:.2f})")
    print(f"Overall Intensity: {state['intensity']:.2f}")
    print("\nBasic Emotions:")
    for emotion, intensity in state['basic_emotions'].items():
        print(f"  {emotion:12}: {intensity:.2f}")
    print("-" * 50)

def main():
    # Initialize the emotion engine
    engine = EmotionEngine()
    
    print("Emotional System Test Interface")
    print("=" * 50)
    print("Commands:")
    print("  text <message>  - Process text input")
    print("  user <emotion>  - Simulate user emotion")
    print("  env <factor>    - Set environmental factor")
    print("  reset          - Reset emotional state")
    print("  show           - Show current emotional state")
    print("  quit           - Exit the program")
    print("=" * 50)
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'quit':
                break
            elif command == 'reset':
                engine.reset_state()
                print("Emotional state reset to neutral.")
            elif command == 'show':
                print_emotion_state(engine)
            elif command.startswith('text '):
                text = command[5:].strip()
                engine.update_state({
                    'text': {'text': text},
                    'context': {'context_type': 'text_input'}
                })
                print(f"Processed text: '{text}'")
                print_emotion_state(engine)
            elif command.startswith('user '):
                emotion = command[5:].strip()
                engine.update_state({
                    'user_emotion': {emotion: 0.8},
                    'context': {'context_type': 'user_emotion'}
                })
                print(f"Processed user emotion: {emotion}")
                print_emotion_state(engine)
            elif command.startswith('env '):
                factor = command[4:].strip()
                try:
                    factor_dict = json.loads(factor)
                    engine.update_state({
                        'environment': factor_dict,
                        'context': {'context_type': 'environment'}
                    })
                    print(f"Updated environment: {factor_dict}")
                    print_emotion_state(engine)
                except json.JSONDecodeError:
                    print("Invalid environment factor format. Use JSON format, e.g.:")
                    print('env {"brightness": 0.8, "noise_level": 0.3}')
            else:
                print("Unknown command. Available commands:")
                print("  text <message>  - Process text input")
                print("  user <emotion>  - Simulate user emotion")
                print("  env <factor>    - Set environmental factor")
                print("  reset          - Reset emotional state")
                print("  show           - Show current emotional state")
                print("  quit           - Exit the program")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 