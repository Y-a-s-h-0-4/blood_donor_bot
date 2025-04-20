import logging
import signal
import sys
import os
from pyrogram import Client
from pyrogram import filters
from dotenv import load_dotenv
from handlers import (
    start_command, 
    help_command, 
    find_command, 
    register_command, 
    callback_query_handler,
    handle_registration
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global app instance
app = None

# Load environment variables
load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

if not (api_id and api_hash and bot_token):
    raise ValueError("Missing one or more environment variables.")

API_ID = int(api_id)
API_HASH = api_hash
BOT_TOKEN = bot_token

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info("Received shutdown signal. Cleaning up...")
    if app:
        app.stop()
    sys.exit(0)

def main():
    global app
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize the bot
        app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
        
        # Register handlers
        app.on_message(filters.command("start"))(start_command)
        app.on_message(filters.command("help"))(help_command)
        app.on_message(filters.command("find"))(find_command)
        app.on_message(filters.command("register"))(register_command)
        app.on_callback_query()(callback_query_handler)
        # Add handler for text messages during registration
        app.on_message(filters.text & filters.create(lambda _, __, ___: True))(handle_registration)
        
        # Start the bot
        logger.info("Starting bot...")
        app.run()
        
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        if app:
            app.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()