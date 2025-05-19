FROM python:3.10-slim

# Install LibreOffice
RUN apt-get update && apt-get install -y libreoffice

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy bot script
COPY bot.py .

# Run bot
CMD ["python", "bot.py"]
