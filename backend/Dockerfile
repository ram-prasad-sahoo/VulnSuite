# VulnSuite Backend — Python/Flask
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Ensure directories exist
RUN mkdir -p logs documents pages

# Entrypoint: seed the DB if it doesn't exist, then launch Flask
CMD ["sh", "-c", "python /seed/seed.py && python app.py"]

EXPOSE 9999
