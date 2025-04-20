from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_donors, donors_collection, register_donor

# Dictionary to store user states during registration and search
user_states = {}
search_states = {}

# Start command
def start_command(client, message):
    welcome_text = "👋 Welcome to the Blood Donor Bot!\n\n"
    welcome_text += "🩸 This bot helps connect blood donors with those in need.\n\n"
    welcome_text += "📋 Available Commands:\n\n"
    welcome_text += "🔍 /find - Search for blood donors by blood group\n"
    welcome_text += "➕ /register - Register yourself as a blood donor\n"
    welcome_text += "❓ /help - Get detailed help about using the bot\n\n"
    welcome_text += "To get started, you can:\n"
    welcome_text += "1. Register as a donor using /register\n"
    welcome_text += "2. Search for donors using /find"
    
    message.reply(welcome_text)

# Help command
def help_command(client, message):
    help_text = "🩸 Blood Donor Bot Help Guide\n\n"
    help_text += "📋 Available Commands:\n\n"
    help_text += "🔍 /find\n"
    help_text += "   • Search for blood donors by blood group\n"
    help_text += "   • Select a blood group from the options\n"
    help_text += "   • Enter location to find nearby donors\n"
    help_text += "   • View contact details of available donors\n\n"
    help_text += "➕ /register\n"
    help_text += "   • Register yourself as a blood donor\n"
    help_text += "   • Provide your blood group and contact details\n"
    help_text += "   • Your information will be available to those in need\n\n"
    help_text += "❓ /help\n"
    help_text += "   • Show this help message\n"
    help_text += "   • Get detailed information about bot commands\n\n"
    help_text += "💡 Tips:\n"
    help_text += "• Keep your contact information up to date\n"
    help_text += "• Respond promptly to blood donation requests\n"
    help_text += "• Share this bot with others who might need it"
    
    message.reply(help_text)

# Users list command
def find_command(client, message):
    # Create inline keyboard with blood group options
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    keyboard = []
    row = []
    for i, group in enumerate(blood_groups):
        row.append(InlineKeyboardButton(text=group, callback_data=f"blood_{group}"))
        if len(row) == 2 or i == len(blood_groups) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message.reply("🩸 Select a blood group to see available donors:", reply_markup=reply_markup)

# Become a donor command
def register_command(client, message):
    user_id = message.from_user.id
    
    # Create inline keyboard with blood group options
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    keyboard = []
    row = []
    for i, group in enumerate(blood_groups):
        row.append(InlineKeyboardButton(text=group, callback_data=f"register_blood_{group}"))
        if len(row) == 2 or i == len(blood_groups) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message.reply("🩸 Please select your blood group:", reply_markup=reply_markup)

# Handle text messages for donor registration and search
def handle_registration(client, message):
    user_id = message.from_user.id
    
    if user_id in user_states:
        state = user_states[user_id]
        
        if state["step"] == "name":
            state["name"] = message.text
            state["step"] = "phone"
            message.reply("📱 Please enter your phone number:")
        
        elif state["step"] == "phone":
            state["phone"] = message.text
            state["step"] = "email"
            message.reply("📧 Please enter your email address:")
        
        elif state["step"] == "email":
            state["email"] = message.text
            state["step"] = "location"
            message.reply("📍 Please enter your location (city, state):")
        
        elif state["step"] == "location":
            # Save all donor information
            donor_data = {
                "name": state["name"],
                "phone": state["phone"],
                "email": state["email"],
                "location": message.text,
                "blood_group": state["blood_group"],
                "user_id": user_id
            }
            
            # Register donor in database
            register_donor(donor_data)
            
            # Clear user state
            del user_states[user_id]
            
            # Send confirmation message
            message.reply("✅ Thank you for registering as a blood donor! Your information has been saved.")
    
    elif user_id in search_states:
        state = search_states[user_id]
        
        if state["step"] == "location":
            # Search for donors in the database with matching blood group and location
            donors = donors_collection.find({
                "blood_group": state["blood_group"],
                "location": {"$regex": message.text, "$options": "i"}  # Case-insensitive search
            })
            
            donor_count = donors_collection.count_documents({
                "blood_group": state["blood_group"],
                "location": {"$regex": message.text, "$options": "i"}
            })
            
            if donor_count > 0:
                donor_list = f"📋 Available blood donors for {state['blood_group']} in {message.text}:\n\n"
                for donor in donors:
                    donor_list += f"👤 Name: {donor.get('name', 'N/A')}\n"
                    donor_list += f"📱 Phone: {donor.get('phone', 'N/A')}\n"
                    donor_list += f"📧 Email: {donor.get('email', 'N/A')}\n"
                    donor_list += f"📍 Location: {donor.get('location', 'N/A')}\n"
                    donor_list += "─────────────────\n"
                message.reply(donor_list)
            else:
                message.reply(f"❌ No blood donors found for {state['blood_group']} blood group in {message.text}.")
            
            # Clear search state
            del search_states[user_id]

# Callback query handler
def callback_query_handler(client, callback_query):
    data = callback_query.data
    
    if data.startswith("blood_"):
        # Handle blood group selection for users list
        user_id = callback_query.from_user.id
        blood_group = data.replace("blood_", "")
        
        # Initialize search state
        search_states[user_id] = {
            "blood_group": blood_group,
            "step": "location"
        }
        
        callback_query.answer()
        callback_query.message.reply("📍 Please enter the location where you need blood donors (city, state):")
    
    elif data.startswith("register_blood_"):
        # Handle blood group selection for registration
        user_id = callback_query.from_user.id
        blood_group = data.replace("register_blood_", "")
        
        # Initialize user state
        user_states[user_id] = {
            "blood_group": blood_group,
            "step": "name"
        }
        
        callback_query.answer()
        callback_query.message.reply("👤 Please enter your full name:")