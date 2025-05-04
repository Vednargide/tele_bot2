import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Bot Token (from environment variable for safety)
TOKEN = os.getenv("TOKEN")

# Preprocess the image to improve OCR accuracy
def preprocess_image(image_path):
    """
    Preprocess the image to improve OCR accuracy.
    - Enhance contrast
    - Apply filters to reduce noise
    """
    try:
        img = Image.open(image_path)
        img = img.convert("L")  # Convert to grayscale
        img = ImageEnhance.Contrast(img).enhance(2)  # Enhance contrast
        img = img.filter(ImageFilter.MedianFilter())  # Reduce noise
        return img
    except Exception as e:
        logger.error(f"Error in image preprocessing: {str(e)}")
        return None

# OCR Function with Text Filtering
def extract_question_from_image(image_path):
    """
    Extract relevant question text from the image using OCR and regex filtering.
    """
    try:
        # Preprocess the image
        processed_img = preprocess_image(image_path)
        if not processed_img:
            return "❌ Failed to preprocess the image."

        # Extract text using Tesseract OCR
        raw_text = pytesseract.image_to_string(processed_img)
        
        # Use regex to find relevant questions
        question_pattern = r"(?i)(read.*?appropriate.*?word.*?:|she.*?\.)"
        matches = re.findall(question_pattern, raw_text, re.DOTALL)

        # Return the first match or indicate no question was found
        if matches:
            return "\n".join(matches)
        else:
            return "❌ No question detected in the image."
    except Exception as e:
        logger.error(f"Error in OCR processing: {str(e)}")
        return "❌ Error processing the image. Please try again."

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me an image, and I'll extract relevant text (questions) from it for you.")

# Image Analysis Handler
async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        # Get the highest quality photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        # Save the photo locally
        image_path = "input_image.jpg"
        await file.download_to_drive(image_path)

        # Extract the relevant question from the image
        extracted_question = extract_question_from_image(image_path)

        # Send the extracted question back to the user
        await update.message.reply_text(f"📝 Extracted Question:\n\n{extracted_question}")
    else:
        await update.message.reply_text("Please send an image.")

# Main Function
def main():
    # Create the bot application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, analyze_image))

    # Run the bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
