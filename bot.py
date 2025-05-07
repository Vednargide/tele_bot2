import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import subprocess

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get bot token from environment variables
TOKEN = os.getenv("TOKEN")

# Function to convert .docx to .tex using pandoc
def convert_docx_to_latex(input_path, output_path):
    try:
        # Run pandoc command
        subprocess.run(["pandoc", input_path, "-o", output_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc conversion failed: {str(e)}")
        return False

# Handler for document analysis and conversion
async def analyze_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        # Get the document file
        document = update.message.document
        file = await context.bot.get_file(document.file_id)

        # Save the file locally
        input_path = document.file_name
        await file.download_to_drive(input_path)

        # Set output LaTeX file path
        output_path = "converted_report.tex"

        # Convert the document to LaTeX using pandoc
        conversion_success = convert_docx_to_latex(input_path, output_path)

        if conversion_success:
            # Send the converted LaTeX file back to the user
            await update.message.reply_document(document=open(output_path, "rb"))
            # Clean up files
            os.remove(input_path)
            os.remove(output_path)
        else:
            await update.message.reply_text("❌ Conversion failed. Ensure the file is a valid .docx document.")
    else:
        await update.message.reply_text("Please send a .docx document.")

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a DOCX file, and I'll convert it to LaTeX using pandoc.")

# Main function
def main():
    # Create the bot application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, analyze_document))

    # Run the bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
