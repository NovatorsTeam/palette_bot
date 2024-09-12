from telegram import Update
from telegram import ReplyKeyboardMarkup, Update, InputMediaPhoto
from messages import inavlid_input_message, instruction_message, greeting_message, processing_message
import os
import time
import asyncio
from telegram.ext import CallbackContext
from io import BytesIO
from processor import ImageProcessor

# Function to send instructions with images from the assets folder
ASSETS_PATH = "./assets/"

image_processor = ImageProcessor(model_name="resnet")


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


# Initialize ImageProcessor with the model name (e.g., 'resnet')
image_processor = ImageProcessor(model_name="resnet")

# Function to handle valid messages with exactly 3 or 5 images


async def handle_valid_message(update: Update, context: CallbackContext) -> None:
    # Check if the message is part of a media group
    if update.message.media_group_id:
        media_group_id = update.message.media_group_id

        # Initialize the media group if it doesn't exist in the chat data
        if media_group_id not in context.chat_data:
            context.chat_data[media_group_id] = {
                "photos": [],
                "last_update_time": time.time()  # Track when the last image was received
            }

        # Append the current image to the media group and update the last update timestamp
        context.chat_data[media_group_id]["photos"].append(
            update.message.photo[-1].file_id)
        context.chat_data[media_group_id]["last_update_time"] = time.time()

        # Check every 0.5 seconds to see if more images arrive
        while time.time() - context.chat_data[media_group_id]["last_update_time"] < 2:
            await asyncio.sleep(0.5)

        # Proceed only when no new images arrive for 2 seconds
        if len(context.chat_data[media_group_id]["photos"]) == 3 or len(context.chat_data[media_group_id]["photos"]) == 5:
            await update.message.reply_text("⌛ Processing your images...")

            # Download and process the images
            images = []
            for file_id in context.chat_data[media_group_id]["photos"]:
                file = await context.bot.get_file(file_id)
                file_bytearray = await file.download_as_bytearray()
                images.append(file_bytearray)

            # Send the images for further processing
            result = await image_processor.process(images)

            # Send the result back to the user
            await update.message.reply_text(f"🎉 Processing complete! Result: {result}")

            # Clear the media group after processing
            context.chat_data.pop(media_group_id)
        elif len(context.chat_data[media_group_id]["photos"]) > 5:
            # Reject if more than 5 images are received
            await update.message.reply_text("🐍 Invalid input! Please send exactly 3 or 5 images.")
            context.chat_data.pop(media_group_id)
    else:
        # Handle single image case or non-media group case
        await update.message.reply_text("🐍 Invalid input! Please send exactly 3 or 5 images.")


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
