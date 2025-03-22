"""
Test script for the emotional response system with speech capabilities.
"""
import os
import json
from dotenv import load_dotenv
from ai_core.emotions.emotion_engine import EmotionEngine
from ai_core.llm.llm_interface import LLMInterface
from ai_core.speech.speech_engine import SpeechEngine

# Load environment variables
load_dotenv()

def print_emotional_state(engine: EmotionEngine) -> None:
    """Print the current emotional state."""
    state = engine.get_current_state()
    print("\nCurrent Emotional State:")
    for key, value in state.items():
        if isinstance(value, (float, str)):
            print(f"{key}: {value}")
        elif isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        elif isinstance(value, list):
            print(f"{key}: {', '.join(map(str, value))}")

def test_emotional_scenarios(emotion_engine: EmotionEngine, llm_interface: LLMInterface, speech_engine: SpeechEngine):
    """Run through different emotional scenarios."""
    scenarios = [
        {
            "name": "Happy Greeting",
            "text": "I'm so excited to see you! It's been such a wonderful day!",
            "expected_emotion": "happy"
        },
        {
            "name": "Sad News",
            "text": "I just heard some disappointing news about the project...",
            "expected_emotion": "sad"
        },
        {
            "name": "Angry Frustration",
            "text": "I can't believe they changed the deadline without telling us!",
            "expected_emotion": "angry"
        },
        {
            "name": "Excited Announcement",
            "text": "We just won the innovation award! This is amazing!",
            "expected_emotion": "excited"
        },
        {
            "name": "Calm Reflection",
            "text": "Let's take a moment to think about our progress...",
            "expected_emotion": "calm"
        },
        {
            "name": "Confident Presentation",
            "text": "I'm ready to present our findings with absolute certainty.",
            "expected_emotion": "confident"
        },
        {
            "name": "Gentle Encouragement",
            "text": "Don't worry, we'll work through this together at your pace.",
            "expected_emotion": "gentle"
        }
    ]
    
    print("\nStarting Emotional Scenario Tests")
    print("=================================")
    
    for scenario in scenarios:
        print(f"\nTesting: {scenario['name']}")
        print("-" * (len(scenario['name']) + 9))
        print(f"Input: {scenario['text']}")
        
        # Process the text
        response = emotion_engine.process_text(scenario['text'])
        if not response:
            state = emotion_engine.get_current_state()
            response = llm_interface.generate_response(state, scenario['text'])
        
        print(f"Response: {response}")
        
        # Get and display emotional state
        state = emotion_engine.get_current_state()
        print("\nEmotional State:")
        for emotion, value in state['emotions'].items():
            print(f"  {emotion}: {value:.2f}")
            
        # Speak with appropriate emotion
        saved_path = speech_engine.speak(response, emotion=scenario['expected_emotion'])
        print(f"Audio saved to: {saved_path}")
        
        input("\nPress Enter to continue to next scenario...")

def main():
    # Initialize components
    emotion_engine = EmotionEngine()
    llm_interface = LLMInterface()
    speech_engine = SpeechEngine()
    
    print("\nEmotional Response System Test Interface")
    print("=======================================")
    print("\nAvailable commands:")
    print("  test - Run emotional scenario tests")
    print("  text <message> - Process text input")
    print("  user <emotion> - Simulate user emotion")
    print("  env <json> - Update environment factors")
    print("  reset - Reset emotional state")
    print("  show - Show current emotional state")
    print("  personality <type> - Set personality type")
    print("  voices - List available voices")
    print("  voice <id> - Set voice by ID")
    print("  mode <family|mature|adult> - Set content mode")
    print("  relationship <friend|romantic|companion> - Set relationship type")
    print("  verify <age> - Verify age for adult content")
    print("  quit - Exit the program")
    
    # Age verification status
    age_verified = False
    
    while True:
        try:
            # Get user input
            command = input("\nEnter command: ").strip()
            
            if command.lower() == 'quit':
                break
                
            # Parse command
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None
            
            # Process command
            if cmd == 'mode' and arg:
                # Set content mode
                success = llm_interface.set_content_mode(arg, age_verified)
                if success:
                    print(f"Content mode set to: {arg}")
                else:
                    print("Failed to set content mode. Check requirements.")
                    
            elif cmd == 'relationship' and arg:
                # Set relationship type
                success = llm_interface.set_relationship_type(arg)
                if success:
                    print(f"Relationship type set to: {arg}")
                else:
                    print("Failed to set relationship type.")
                    
            elif cmd == 'verify' and arg:
                try:
                    age = int(arg)
                    if age >= 18:
                        age_verified = True
                        print("Age verification successful.")
                        # Update content mode if it was previously set to adult
                        if llm_interface.content_level == 'adult':
                            llm_interface.set_content_mode('adult', True)
                    else:
                        age_verified = False
                        print("Must be 18 or older for adult content.")
                except ValueError:
                    print("Please enter a valid age number.")
                    
            elif cmd == 'test':
                test_emotional_scenarios(emotion_engine, llm_interface, speech_engine)
                
            elif cmd == 'text' and arg:
                # Process text and get emotional response
                response = emotion_engine.process_text(arg)
                if not response:
                    state = emotion_engine.get_current_state()
                    response = llm_interface.generate_response(state, arg)
                
                print(f"\nAI Response: {response}")
                
                # Get current emotional state for speech
                state = emotion_engine.get_current_state()
                emotions = state.get('emotions', {})
                if emotions:
                    dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                else:
                    dominant_emotion = 'neutral'
                
                # Speak the response with the dominant emotion
                saved_path = speech_engine.speak(response, emotion=dominant_emotion)
                if saved_path:
                    print(f"Audio saved to: {saved_path}")
                    
            elif cmd == 'user' and arg:
                # Simulate user emotion
                emotion_engine.simulate_user_emotion(arg)
                state = emotion_engine.get_current_state()
                response = llm_interface.generate_response(state, f"User is feeling {arg}")
                print(f"\nAI Response: {response}")
                saved_path = speech_engine.speak(response, emotion=state.get('primary_emotion', 'neutral'))
                if saved_path:
                    print(f"Audio saved to: {saved_path}")
                
            elif cmd == 'env' and arg:
                try:
                    env_data = json.loads(arg)
                    emotion_engine.update_environment(env_data)
                    state = emotion_engine.get_current_state()
                    response = llm_interface.generate_response(state, "Environmental update")
                    print(f"\nAI Response: {response}")
                    saved_path = speech_engine.speak(response, emotion=state.get('primary_emotion', 'neutral'))
                    if saved_path:
                        print(f"Audio saved to: {saved_path}")
                except json.JSONDecodeError:
                    print("Error: Invalid JSON format")
                except Exception as e:
                    print(f"Error updating environment: {e}")
                    
            elif cmd == 'reset':
                emotion_engine.reset_emotions()
                print("Emotional state reset")
                speech_engine.speak("Emotional state has been reset", emotion='neutral')
                
            elif cmd == 'show':
                print_emotional_state(emotion_engine)
                
            elif cmd == 'personality' and arg:
                emotion_engine.set_personality(arg)
                print(f"Personality set to: {arg}")
                speech_engine.speak(f"Personality has been set to {arg}", emotion='neutral')
                
            elif cmd == 'voices':
                speech_engine.list_voices()
                
            elif cmd == 'voice' and arg:
                speech_engine.set_voice(arg)
                speech_engine.speak("Voice has been updated", emotion='neutral')
                
            else:
                print("Invalid command or missing argument")
                
        except Exception as e:
            print(f"Error: {e}")
            
    print("\nExiting test interface...")

if __name__ == "__main__":
    main() 