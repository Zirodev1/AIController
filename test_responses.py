"""
Test script for the emotional response system.
"""
import sys
import os
import json
from ai_core.emotions.emotion_engine import EmotionEngine
from ai_core.llm.llm_interface import LLMInterface
from ai_core.speech.speech_engine import SpeechEngine

def print_emotion_state(engine):
    """Print the current emotional state in a readable format."""
    state = engine.get_current_state()
    print("\nCurrent Emotional State:")
    print(f"Complex State: {state['complex_state']}")
    print(f"Overall Intensity: {state['overall_intensity']:.2f}")
    print("\nBasic Emotions:")
    for emotion, intensity in state['basic_emotions'].items():
        print(f"- {emotion}: {intensity:.2f}")

def main():
    # Initialize components
    engine = EmotionEngine()
    llm = LLMInterface()
    speech_engine = SpeechEngine()
    speech_enabled = True
    
    print("Emotional System Test Interface")
    print("Available commands:")
    print("  text <message> - Process text input")
    print("  user <emotion> - Simulate user emotion")
    print("  env <json> - Set environmental factors")
    print("  reset - Reset emotional state")
    print("  show - Show current emotional state")
    print("  personality <type> - Set personality type (high_empathy, analytical, creative, balanced)")
    print("  speak - Toggle speech output")
    print("  rate <value> - Set speech rate (default: 150)")
    print("  volume <value> - Set speech volume (0.0 to 1.0)")
    print("  stop - Stop current speech")
    print("  voices - List available voices")
    print("  setvoice <voice_id> - Set voice by ID")
    print("  quit - Exit program")
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'quit':
                break
                
            elif command == 'show':
                print_emotion_state(engine)
                
            elif command == 'reset':
                engine.reset_emotions()
                print("Emotional state reset successfully.")
                
            elif command == 'speak':
                speech_enabled = not speech_enabled
                print(f"Speech output {'enabled' if speech_enabled else 'disabled'}")
                
            elif command == 'stop':
                speech_engine.stop_speaking()
                print("Speech stopped.")
                
            elif command == 'voices':
                speech_engine.list_voices()
                
            elif command.startswith('setvoice '):
                try:
                    voice_id = command[8:].strip()
                    if not voice_id:
                        print("Error: Please provide a voice ID")
                        continue
                    speech_engine.set_voice(voice_id)
                    print(f"Voice set to: {voice_id}")
                except Exception as e:
                    print(f"Error setting voice: {str(e)}")
                
            elif command.startswith('rate '):
                try:
                    rate = int(command.split(' ')[1])
                    speech_engine.set_rate(rate)
                    print(f"Speech rate set to {rate}")
                except (ValueError, IndexError):
                    print("Error: Please provide a valid rate value (e.g., 'rate 150')")
                    
            elif command.startswith('volume '):
                try:
                    volume = float(command.split(' ')[1])
                    speech_engine.set_volume(volume)
                    print(f"Speech volume set to {volume}")
                except (ValueError, IndexError):
                    print("Error: Please provide a valid volume value between 0.0 and 1.0")
                    
            elif command.startswith('text '):
                text = command[5:].strip()
                if not text:
                    print("Error: Please provide text to process")
                    continue
                    
                # Process text and get response
                engine.process_text(text)
                state = engine.get_current_state()
                response = llm.generate_response(state, text)
                print(f"\nAI Response: {response}")
                
                if speech_enabled:
                    speech_engine.speak(response)
                    
            elif command.startswith('user '):
                try:
                    emotion = command[5:].strip()
                    if not emotion:
                        print("Error: Please provide an emotion")
                        continue
                        
                    # Simulate user emotion and get response
                    engine.simulate_user_emotion(emotion)
                    state = engine.get_current_state()
                    response = llm.generate_response(state, f"User is feeling {emotion}")
                    print(f"\nAI Response: {response}")
                    
                    if speech_enabled:
                        speech_engine.speak(response)
                        
                except Exception as e:
                    print(f"Error: {str(e)}")
                    
            elif command.startswith('env '):
                try:
                    env_data = command[4:].strip()
                    if not env_data:
                        print("Error: Please provide environmental data as JSON")
                        continue
                        
                    env_factors = json.loads(env_data)
                    engine.update_environment(env_factors)
                    state = engine.get_current_state()
                    response = llm.generate_response(state, context={"environment": env_factors})
                    print(f"\nAI Response: {response}")
                    
                    if speech_enabled:
                        speech_engine.speak(response)
                        
                except json.JSONDecodeError:
                    print("Error: Invalid JSON format")
                except Exception as e:
                    print(f"Error: {str(e)}")
                    
            elif command.startswith('personality '):
                try:
                    personality = command[11:].strip()
                    if not personality:
                        print("Error: Please provide a personality type")
                        continue
                        
                    engine.set_personality(personality)
                    print(f"Personality set to: {personality}")
                    
                except Exception as e:
                    print(f"Error: {str(e)}")
                    
            else:
                print("Error: Unknown command")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 