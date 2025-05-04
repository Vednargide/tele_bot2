import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import pytesseract

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "5887342504:AAFYB4XchWo5EkT_kQsmfB6z4eb9MTgEQns"

# Resize Image for Faster Processing
def preprocess_image(image_path, max_width=800, max_height=800):
    """
    Resize the image to reduce processing time.
    """
    try:
        with Image.open(image_path) as img:
            img.thumbnail((max_width, max_height))
            resized_path = "resized_image.jpg"
            img.save(resized_path)
        return resized_path
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return image_path  # Fallback to original image

# Extract Text Using Tesseract
def extract_text_from_image(image_path):
    """
    Extract text from the given image using Tesseract OCR.
    """
    try:
        # Preprocess the image
        processed_image = preprocess_image(image_path)

        # Extract text
        extracted_text = pytesseract.image_to_string(Image.open(processed_image))
        return extracted_text if extracted_text.strip() else "❌ No text detected in the image."
    except Exception as e:
        logger.error(f"Error in OCR processing: {e}")
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

        # Extract text from the image
        extracted_text = extract_text_from_image(image_path)

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
