import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re,os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = os.getenv("TOKEN")

# Improved function to extract and format questions
def extract_questions(ocr_text):
    # Try to identify different question patterns
    
    # Pattern 1: Fill in the blanks questions
    fill_blank_pattern = r"(Read each of the sentences.+?fill in the blank.+?(?:She|He|They|It).+?\.)"
    fill_blank_match = re.search(fill_blank_pattern, ocr_text, re.DOTALL | re.IGNORECASE)
    
    # Pattern 2: Multiple choice questions
    mcq_pattern = r"((?:Choose|Select|Pick).+?(?:option|answer|alternative).+?(?:A|B|C|D|1|2|3|4).+?(?:A|B|C|D|1|2|3|4).+?\.)"
    mcq_match = re.search(mcq_pattern, ocr_text, re.DOTALL | re.IGNORECASE)
    
    # Pattern 3: General questions with question marks
    general_pattern = r"([A-Z][^.!?]*\?)"
    general_matches = re.findall(general_pattern, ocr_text)
    
    # Collect all found questions
    questions = []
    
    if fill_blank_match:
        questions.append(fill_blank_match.group(1).strip())
    
    if mcq_match:
        questions.append(mcq_match.group(1).strip())
    
    if general_matches:
        for match in general_matches[:3]:  # Limit to first 3 questions to avoid noise
            questions.append(match.strip())
    
    # If no structured questions found, return the most relevant text
    if not questions:
        # Try to extract any text that looks like instructions or questions
        instruction_pattern = r"([A-Z][^.!?]{10,}[.!?])"
        instruction_matches = re.findall(instruction_pattern, ocr_text)
        
        if instruction_matches:
            for match in instruction_matches[:3]:
                questions.append(match.strip())
        else:
            # Last resort: return the first few sentences that seem meaningful
            sentences = re.findall(r"[A-Z][^.!?]{5,}[.!?]", ocr_text)
            meaningful_sentences = [s for s in sentences if len(s) > 15]
            
            if meaningful_sentences:
                questions = meaningful_sentences[:3]
            else:
                return "❌ Could not identify any questions in the image."
    
    return "📝 Extracted Question(s):\n\n" + "\n\n".join(questions)

# Enhanced OCR Function with Preprocessing
def extract_text_from_image(image_path):
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Apply multiple preprocessing techniques
        # Convert to grayscale
        img = img.convert("L")
        
        # Create multiple processed versions with different techniques
        processed_images = []
        
        # Version 1: Standard threshold
        threshold = 150
        img1 = img.point(lambda p: p > threshold and 255)
        img1 = ImageEnhance.Contrast(img1).enhance(2.5)
        img1 = img1.filter(ImageFilter.GaussianBlur(radius=0.5))
        img1 = img1.filter(ImageFilter.SHARPEN)
        processed_images.append(img1)
        
        # Version 2: Higher threshold for stronger watermark removal
        threshold2 = 180
        img2 = img.point(lambda p: p > threshold2 and 255)
        img2 = ImageEnhance.Contrast(img2).enhance(2.0)
        img2 = img2.filter(ImageFilter.GaussianBlur(radius=0.7))
        img2 = img2.filter(ImageFilter.SHARPEN)
        processed_images.append(img2)
        
        # Version 3: Morphological operations to remove thin watermark lines
        img3 = img.copy()
        img3 = img3.filter(ImageFilter.MinFilter(3))  # Erosion-like effect
        img3 = img3.filter(ImageFilter.MaxFilter(3))  # Dilation-like effect
        img3 = img3.point(lambda p: p > 160 and 255)
        img3 = ImageEnhance.Contrast(img3).enhance(2.2)
        processed_images.append(img3)
        
        # Save preprocessed images for debugging (optional)
        for i, processed_img in enumerate(processed_images):
            processed_img.save(f"preprocessed_image{i+1}.jpg")
        
        # Configure pytesseract for better text recognition
        custom_config = r'--oem 3 --psm 6 -l eng'
        
        # Perform OCR on all preprocessed images
        ocr_results = []
        for i, processed_img in enumerate(processed_images):
            ocr_text = pytesseract.image_to_string(processed_img, config=custom_config)
            ocr_results.append(ocr_text)
            logger.info(f"OCR result {i+1} length: {len(ocr_text)}")
        
        # Choose the OCR result with the most text
        ocr_text = max(ocr_results, key=len)
        
        # Log the raw OCR text for debugging
        logger.info(f"Selected raw OCR text: {ocr_text}")
        
        # Extract questions from the OCR text
        extracted_questions = extract_questions(ocr_text)
        
        return extracted_questions
    except Exception as e:
        logger.error(f"Error in OCR processing: {str(e)}")
        return "❌ Error processing the image. Please try again."

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me an image containing questions, and I'll extract them for you.")

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
        await update.message.reply_text(extracted_text)
    else:
        await update.message.reply_text("Please send an image containing questions.")

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
