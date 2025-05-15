"""Test script to verify environment variables are loaded correctly."""

import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    """Test environment variable loading."""
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if api_key:
        # Mask the API key for security
        masked_key = api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]
        logging.info(f"API Key found: {masked_key}")
    else:
        logging.error("No API key found in .env file")
        
    # Test other environment variables
    output_dir = os.getenv('OUTPUT_DIRECTORY', 'results')
    logging.info(f"Output directory: {output_dir}")
    
    # Check if output directory exists
    if not os.path.exists(output_dir):
        logging.warning(f"Output directory '{output_dir}' does not exist")
        os.makedirs(output_dir)
        logging.info(f"Created output directory '{output_dir}'")

if __name__ == "__main__":
    main() 