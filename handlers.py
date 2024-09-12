from telegram import ReplyKeyboardMarkup, Update, InputMediaPhoto
from messages import inavlid_input_message, instruction_message, greeting_message, processing_message
import os
from telegram.ext import CallbackContext

# Function to send instructions with images from the assets folder
ASSETS_PATH = "./assets/"


async def send_instruction(update: Update, context: CallbackContext) -> None:
    # Load images from the assets folder
    # Update with actual image file names in 'assets'
    image_files = ['image1.jpg', 'image2.jpg', 'image3.jpg']
    images = [InputMediaPhoto(
        open(os.path.join(ASSETS_PATH, img), 'rb')) for img in image_files]

    # Send the message with the images
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=images)

    # Send the instruction message
    await update.message.reply_text(instruction_message)


# Function to handle valid messages with exactly 3 or 5 images
async def handle_valid_message(update: Update, context: CallbackContext) -> None:
    # Check if media_group_id exists (multiple images in a group)
    if update.message.media_group_id:
        media_group_id = update.message.media_group_id

        # Initialize or update the list of images in the group
        if media_group_id not in context.chat_data:
            context.chat_data[media_group_id] = []

        context.chat_data[media_group_id].append(update.message)

        # Check if the group has exactly 3 or 5 images
        if len(context.chat_data[media_group_id]) == 3 or len(context.chat_data[media_group_id]) == 5:
            await update.message.reply_text(processing_message)
            # Remove the media group from the context after processing
            context.chat_data.pop(media_group_id)
        elif len(context.chat_data[media_group_id]) > 5:
            await update.message.reply_text(inavlid_input_message)
            # Remove the media group after rejecting
            context.chat_data.pop(media_group_id)

    # Handle individual images or cases where media_group_id does not exist
    else:
        # Single image, or group of images not in a media group
        num_images = len(update.message.photo)
        if num_images != 3 and num_images != 5:  # Invalid if it's not exactly 3 or 5 images
            await update.message.reply_text(inavlid_input_message)
        else:
            await update.message.reply_text(processing_message)


# Function to reject invalid messages
async def reject_invalid_message(update: Update, context: CallbackContext) -> None:
    # Only send the rejection if the message is not part of a media group
    if not update.message.media_group_id:
        await update.message.reply_text(inavlid_input_message)


# Function to show the instruction button and send the greeting message
async def show_instruction_button(update: Update, context: CallbackContext) -> None:
    # Define the reply keyboard layout with a single button
    # Make sure the button label is exactly "Инструкция"
    keyboard = [["Инструкция"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=False, resize_keyboard=True
    )

    # Send the greeting message
    await update.message.reply_text(greeting_message)
