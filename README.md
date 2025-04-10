# AI Companion System

A sophisticated AI system designed to control and animate 3D avatars with realistic personalities, emotions, and behaviors. This system can be integrated with any 3D engine through a simple API interface.

## Core Features

### Personality System
- Customizable personality traits
- Dynamic emotional responses
- Relationship development
- Memory and learning capabilities
- Adaptive behavior based on user interaction
- Deep learning-based personality modeling

### Communication System
- Multiple communication modes:
  - Voice interaction
  - Text-based chat
  - Gesture recognition
  - Facial expressions
  - Body language
- User-configurable communication preferences
- Natural language understanding
- Contextual responses
- Low-latency processing

### Behavior System
- Natural movement and animations
- Complex environment interaction
- Realistic emotional expressions
- Adaptive decision making
- Context-aware responses
- Memory-based behavior patterns

### Vision System
- Facial recognition
- Gesture recognition
- User tracking
- Environment perception
- Object recognition
- Emotion detection

### Social Media Integration
- Natural posting based on emotional state and experiences
- Scheduled content updates and announcements
- Command-based posting system
- Multi-platform support (Twitter, OnlyFans, etc.)
- Platform-specific content validation
- Automated engagement and responses
- Content scheduling and management

### Character Image Generation System
- Stable Diffusion integration for high-quality character images
- Character selfies and portraits on demand
- Various emotional expressions (happy, sad, surprised)
- Different clothing styles (casual, elegant)
- Various environments (bedroom, garden, cafe)
- Different activities (reading, cooking, working)
- Auto-completion of character-appropriate prompts
- Robust fallback to placeholder images

## Project Structure

```
AIController/
├── ai_core/          # Core AI logic
│   ├── personality/  # Personality system
│   ├── emotions/     # Emotional processing
│   ├── memory/       # Memory system
│   ├── behavior/     # Behavior control
│   ├── image/        # Image generation
│   └── social/       # Social media integration
├── vision/           # Computer vision
│   ├── face/        # Facial recognition
│   ├── gesture/     # Gesture recognition
│   └── tracking/    # User tracking
├── nlp/              # Natural language processing
│   ├── voice/       # Voice processing
│   ├── text/        # Text processing
│   └── context/     # Context understanding
├── api/              # Engine integration API
│   ├── bindings/    # Language bindings
│   └── protocols/   # Communication protocols
├── social/           # Social media features
│   ├── platforms/   # Platform integrations
│   ├── scheduler/   # Content scheduling
│   └── validator/   # Content validation
├── generated_images/ # Generated image storage
└── utils/           # Shared utilities
```

## Technical Requirements

### Core Requirements
- Python 3.8+
- PyTorch for deep learning
- Transformers for NLP
- OpenCV for computer vision
- Stable Diffusion for image generation
- Additional dependencies in requirements.txt

### API Requirements
- FastAPI for REST API
- WebSocket for real-time communication
- Protocol Buffers for data serialization
- ZeroMQ for high-performance messaging
- Social media platform APIs (Twitter, OnlyFans)

## Development Status

Current focus:
- Core personality system implementation
- Basic emotional modeling
- Initial memory system
- Basic behavior control
- Engine integration API
- Social media integration
- Character image generation with Stable Diffusion
- Conversation memory integration

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
# Copy .env.example to .env and add your API keys

# Run the companion
python ai_companion.py
```

## Character Image Generation

The AI Companion includes character image generation capabilities using Stable Diffusion:

1. **Simple image requests**:
   ```
   Send me a picture of yourself
   ```

2. **Specific emotional expressions**:
   ```
   Show me a picture of you looking happy
   Send me a picture of you when you're sad
   ```

3. **Environment requests**:
   ```
   Show me a picture of you in a garden
   Send me a selfie of you at the beach
   ```

4. **Activity requests**:
   ```
   Send me a picture of you reading a book
   Show me a picture of you cooking
   ```

5. **Configuration**:
   - The system will automatically search for Stable Diffusion models in common locations
   - For customization, set the `SD_MODEL_PATH` in your `.env` file
   - No external setup needed, the system handles everything internally

6. **Technical note**:
   - Uses the diffusers library to load models directly
   - Includes optimizations for different hardware configurations
   - Falls back to placeholder images if Stable Diffusion is unavailable

## API Usage

```python
from ai_companion import AICompanion

# Initialize the AI companion
companion = AICompanion(
    personality_traits={
        'openness': 0.8,
        'extraversion': 0.7,
        'agreeableness': 0.9
    }
)

# Start interaction
companion.start_interaction()

# Send user input
companion.process_input("Hello!")

# Get AI response
response = companion.get_response()

# Request character images
companion.process_command("Show me a picture of you smiling")
companion.process_command("Send me a selfie of you at the beach")

# Schedule a post
companion.social_media.schedule_post(
    "Good morning everyone! *stretches*",
    time="09:00",
    frequency="daily"
)
```

## License

[To be determined] 