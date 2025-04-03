"""
Test script for the SocialAI system.
"""
from ai_core.social.social_ai import SocialAI
from ai_core.platforms.platform_manager import Platform
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize SocialAI with API key
    api_key = "your-api-key-here"  # Replace with actual API key
    social_ai = SocialAI(api_key)
    
    # Initialize platforms
    twitter_credentials = {
        "api_key": "your-twitter-api-key",
        "api_secret": "your-twitter-api-secret",
        "access_token": "your-twitter-access-token",
        "access_token_secret": "your-twitter-access-token-secret"
    }
    
    onlyfans_credentials = {
        "api_key": "your-onlyfans-api-key",
        "api_secret": "your-onlyfans-api-secret"
    }
    
    # Initialize Twitter
    twitter_user_id = social_ai.initialize_platform(
        Platform.TWITTER,
        twitter_credentials
    )
    logger.info(f"Initialized Twitter with user ID: {twitter_user_id}")
    
    # Initialize OnlyFans
    onlyfans_user_id = social_ai.initialize_platform(
        Platform.ONLYFANS,
        onlyfans_credentials
    )
    logger.info(f"Initialized OnlyFans with user ID: {onlyfans_user_id}")
    
    # Test Twitter interaction
    logger.info("\nTesting Twitter interaction:")
    twitter_response = social_ai.generate_response(
        Platform.TWITTER,
        twitter_user_id,
        "What's your favorite tech gadget?"
    )
    logger.info(f"Twitter Response: {twitter_response}")
    
    # Test OnlyFans interaction
    logger.info("\nTesting OnlyFans interaction:")
    onlyfans_response = social_ai.generate_response(
        Platform.ONLYFANS,
        onlyfans_user_id,
        "Tell me about your day"
    )
    logger.info(f"OnlyFans Response: {onlyfans_response}")
    
    # Test posting content
    logger.info("\nTesting content posting:")
    
    # Twitter post
    twitter_post = "Just discovered a new AI feature! 🤖✨ #AI #Technology"
    success = social_ai.post_content(Platform.TWITTER, twitter_post)
    logger.info(f"Twitter post {'successful' if success else 'failed'}")
    
    # OnlyFans post
    onlyfans_post = "New exclusive content coming soon! 😘✨"
    success = social_ai.post_content(Platform.ONLYFANS, onlyfans_post)
    logger.info(f"OnlyFans post {'successful' if success else 'failed'}")

if __name__ == "__main__":
    main() 