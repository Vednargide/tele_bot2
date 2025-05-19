import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pdf2docx import Converter
from docx import Document

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Get bot token from environment variables
TOKEN = os.getenv("TOKEN")

# Function to convert PDF to DOCX
def convert_pdf_to_docx(input_path, output_path):
    try:
        cv = Converter(input_path)
        cv.convert(output_path)
        cv.close()
        return True
    except Exception as e:
        logger.error(f"Error in PDF to DOCX conversion: {e}")
        return False

# Function to standardize fonts in a DOCX file
def standardize_fonts(docx_path, font_name="Arial", font_size=12):
    try:
        doc = Document(docx_path)
        for paragraph in doc.paragraphs:
            for run in paragraph.runs:
                run.font.name = font_name
                run.font.size = font_size
        doc.save(docx_path)
        logger.info("Fonts standardized.")
    except Exception as e:
        logger.error(f"Error standardizing fonts: {e}")

# Telegram command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a PDF file, and I'll convert it to DOCX with standardized fonts for you.")

# Telegram handler: File upload
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        document = update.message.document
        file_name = document.file_name
        file_extension = file_name.split(".")[-1].lower()

        if file_extension != "pdf":
            await update.message.reply_text("❌ Unsupported file type. Please upload a PDF file.")
            return

        # Download the file
        file = await context.bot.get_file(document.file_id)
        input_path = f"input_{file_name}"
        output_path = f"converted_{file_name.replace('.pdf', '.docx')}"
        await file.download_to_drive(input_path)

        # Convert the PDF to DOCX
        conversion_success = convert_pdf_to_docx(input_path, output_path)

        if conversion_success:
            # Standardize fonts
            standardize_fonts(output_path)
            await update.message.reply_document(document=open(output_path, "rb"))
            os.remove(input_path)
            os.remove(output_path)
        else:
            await update.message.reply_text("❌ Conversion failed. Please try again later.")

# Main function to run the bot
def main():
    # Initialize the bot application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Run the bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
