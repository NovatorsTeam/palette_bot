from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import asyncio
import os
from handlers import send_instruction, show_instruction_button, reject_invalid_message, handle_valid_message


# Main function to run the bot
async def main():
    # Your bot token here
    TOKEN = os.getenv('BOT_TOKEN')

    # Create an Application object
    application = Application.builder().token(TOKEN).build()

    # Handler for the /start command to show the instruction button and send the greeting message
    application.add_handler(CommandHandler("start", show_instruction_button))

    application.add_handler(MessageHandler(
        filters.Regex('^Инструкция$'), send_instruction))

    # Handler for valid images (3 or 5 images with no text)
    application.add_handler(MessageHandler(
        filters.PHOTO & ~filters.TEXT, handle_valid_message))

    # Reject messages that don't match the criteria (invalid format)
    application.add_handler(MessageHandler(
        filters.ALL & ~filters.PHOTO, reject_invalid_message))

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
