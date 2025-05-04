import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import easyocr
import cv2
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OCR reader
reader = easyocr.Reader(['en'])  # Load EasyOCR with English language

# Bot token
TOKEN = "5887342504:AAFYB4XchWo5EkT_kQsmfB6z4eb9MTgEQns"  # Replace with your Telegram bot token

# OCR Function with Preprocessing
def preprocess_and_extract_text(image_path):
    """
    Preprocess the image and extract text using EasyOCR.
    """
    try:
        # Load the image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        # Preprocess: Resize, Denoise, and Threshold
        image = cv2.resize(image, (800, 800), interpolation=cv2.INTER_AREA)
        image = cv2.fastNlMeansDenoising(image, h=30)
        _, processed_image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)

        # Save processed image for debugging (optional)
        cv2.imwrite("processed_image.jpg", processed_image)

        # Perform OCR
        results = reader.readtext(processed_image, detail=0)
        return "\n".join(results) if results else "❌ No text detected in the image."
    except Exception as e:
        logger.error(f"Error in OCR processing: {str(e)}")
        return "❌ Error processing the image. Please try again."

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me an image, and I'll extract text from it for you.")

# Image Analysis Handler
async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        # Get the highest quality photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        # Save the photo locally
        image_path = "input_image.jpg"
        await file.download_to_drive(image_path)

        # Preprocess and extract text from the image
        extracted_text = preprocess_and_extract_text(image_path)

        # Send the extracted text back to the user
        await update.message.reply_text(f"📝 Extracted Text:\n\n{extracted_text}")
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
