from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
from aspose.pdf import Document

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! Send me a PDF, and I'll convert it to DOCX while keeping the formatting.")

def handle_document(update: Update, context: CallbackContext):
    file = update.message.document
    if file.mime_type == 'application/pdf':
        update.message.reply_text("Received your PDF. Converting to DOCX while preserving formatting...")

        # Download the file
        file_path = file.file_id + ".pdf"
        new_file = context.bot.get_file(file.file_id)
        new_file.download(file_path)

        try:
            # Convert PDF to DOCX using Aspose
            docx_path = file.file_id + ".docx"
            pdf_document = Document(file_path)
            pdf_document.save(docx_path, "docx")

            # Send the DOCX back to the user
            with open(docx_path, 'rb') as docx_file:
                update.message.reply_document(docx_file, filename="converted.docx")
            
        except Exception as e:
            update.message.reply_text(f"Failed to convert PDF: {e}")
        
        # Cleanup
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(docx_path):
                os.remove(docx_path)
    else:
        update.message.reply_text("Please send a valid PDF file.")

def main():
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Get token from environment variable
    updater = Updater(telegram_bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_document))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
