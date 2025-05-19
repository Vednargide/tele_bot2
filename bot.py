from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
from aspose.pdf import Document

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hi! Send me a PDF, and I'll convert it to DOCX while keeping the formatting.")

async def handle_document(update: Update, context: CallbackContext):
    file = update.message.document
    if file.mime_type == 'application/pdf':
        await update.message.reply_text("Received your PDF. Converting to DOCX while preserving formatting...")

        # Download the file
        file_path = file.file_id + ".pdf"
        new_file = await context.bot.get_file(file.file_id)
        await new_file.download_to_drive(file_path)

        try:
            # Convert PDF to DOCX using Aspose
            docx_path = file.file_id + ".docx"
            pdf_document = Document(file_path)
            pdf_document.save(docx_path, "docx")

            # Send the DOCX back to the user
            with open(docx_path, 'rb') as docx_file:
                await update.message.reply_document(docx_file, filename="converted.docx")
            
        except Exception as e:
            await update.message.reply_text(f"Failed to convert PDF: {e}")
        
        # Cleanup
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(docx_path):
                os.remove(docx_path)
    else:
        await update.message.reply_text("Please send a valid PDF file.")

def main():
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Get token from environment variable
    app = Application.builder().token(telegram_bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    app.run_polling()

if __name__ == "__main__":
    main()
