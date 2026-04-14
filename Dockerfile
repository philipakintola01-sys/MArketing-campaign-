# Use a Python image that includes all Playwright dependencies
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the chromium browser
RUN playwright install chromium

# Copy the rest of the code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port Render uses
EXPOSE 10000

# Start the application
CMD ["python", "main.py"]
