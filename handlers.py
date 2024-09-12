from telegram import ReplyKeyboardMarkup, Update, InputMediaPhoto
from messages import inavlid_input_message, instruction_message, greeting_message, processing_message
import os
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


async def handle_valid_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Download images from the message
    images = []
    for photo in update.message.photo:
        # Get the highest resolution of the photo
        file = await context.bot.get_file(photo.file_id)

        # Use download_as_bytearray to get the image as a bytearray
        file_bytearray = await file.download_as_bytearray()
        images.append(file_bytearray)

    # Process images using ImageProcessor
    if len(images) == 3 or len(images) == 5:
        await update.message.reply_text("⌛ Processing your images...")

        # Send the images for processing
        result = await image_processor.process(images)

        # Send the result back to the user
        await update.message.reply_text(f"🎉 Processing complete! Result: {result}")
    else:
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
