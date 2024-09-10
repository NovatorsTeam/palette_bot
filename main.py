from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, Update
import asyncio

# Function to display the keyboard by default


async def default_keyboard(update: Update, context: CallbackContext) -> None:
    # Define the reply keyboard layout
    keyboard = [
        ["Option 1 🚀", "Option 2"],  # Row 1
        ["Option 3"]  # Row 2
    ]

    # Create the ReplyKeyboardMarkup object
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=False, resize_keyboard=True)

    # Send the message with the reply keyboard (this will be sent every time the user sends a message)
    await update.message.reply_text('Choose an option:', reply_markup=reply_markup)

# Callback function to handle button presses


async def button_handler(update: Update, context: CallbackContext) -> None:
    # Echo back the text the user selected
    await update.message.reply_text(f"You selected: {update.message.text}")

# Main function to run the bot


async def main():
    # Your bot token here
    TOKEN = '7537225129:AAEzwy4Y7W_M8RcU7r8jeLx5YZTDScq2QtQ'

    # Create an Application object
    application = Application.builder().token(TOKEN).build()

    # Add a handler that triggers the default keyboard on any message (except commands)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, default_keyboard))

    # Add a handler for button presses (from the default keyboard)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, button_handler))

    await application.initialize()

    # Start polling manually without trying to close the loop
    await application.start()

    # Keep the bot running and handle updates indefinitely
    await application.updater.start_polling()

    # This will keep the bot alive
    await asyncio.Event().wait()

# Check if the event loop is running and handle it
if __name__ == '__main__':
    try:
        # If there's an event loop already running, use it
        loop = asyncio.get_event_loop()
        # Run the bot using the existing event loop
        loop.run_until_complete(main())
    except RuntimeError:
        # If no event loop is running, start a new one
        asyncio.run(main())
