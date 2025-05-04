import logging
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

# Bot token
TOKEN = os.getenv("TOKEN")

# Improved function to filter the relevant question
def filter_relevant_text(ocr_text):
    # Look for the specific pattern of the fill-in-the-blank question
    pattern = r"Read each of the sentences.+?fill in the blank\(s\).+?She.+?weeks\."
    match = re.search(pattern, ocr_text, re.DOTALL | re.IGNORECASE)
    
    if match:
        # Extract just the question part
        question_text = match.group(0)
        
        # Further refine to get just the sentence with blanks
        sentence_pattern = r"She.+?weeks\."
        sentence_match = re.search(sentence_pattern, question_text, re.DOTALL)
        
        if sentence_match:
            return f"Read each of the sentences and fill in the blank(s) with the appropriate word(s):\n{sentence_match.group(0)}"
    
    # Fallback: try to find just the sentence if the full pattern isn't found
    sentence_pattern = r"She.+?\(.+?to study.+?\).+?weeks\."
    sentence_match = re.search(sentence_pattern, ocr_text, re.DOTALL)
    
    if sentence_match:
        return f"Read each of the sentences and fill in the blank(s) with the appropriate word(s):\n{sentence_match.group(0)}"
    
    return "❌ Could not find the relevant question in the image."

# Enhanced OCR Function with Preprocessing
def extract_text_from_image(image_path):
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Apply multiple preprocessing techniques
        # Convert to grayscale
        img = img.convert("L")
        
        # Apply thresholding to reduce watermark impact
        threshold = 150
        img = img.point(lambda p: p > threshold and 255)
        
        # Enhance contrast
        img = ImageEnhance.Contrast(img).enhance(2.5)
        
        # Apply slight blur to reduce noise
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Sharpen the image to make text clearer
        img = img.filter(ImageFilter.SHARPEN)
        
        # Save preprocessed image for debugging (optional)
        img.save("preprocessed_image.jpg")
        
        # Configure pytesseract for better text recognition
        custom_config = r'--oem 3 --psm 6 -l eng'
        
        # Perform OCR
        ocr_text = pytesseract.image_to_string(img, config=custom_config)
        
        # Log the raw OCR text for debugging
        logger.info(f"Raw OCR text: {ocr_text}")
        
        # Filter for the relevant question
        relevant_text = filter_relevant_text(ocr_text)
        
        return relevant_text
    except Exception as e:
        logger.error(f"Error in OCR processing: {str(e)}")
        return "❌ Error processing the image. Please try again."

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me an image, and I'll extract the relevant question from it.")

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
        await update.message.reply_text(f"📝 Extracted Question:\n\n{extracted_text}")
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
