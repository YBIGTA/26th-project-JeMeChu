# Use Python as base image
FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Copy only necessary files (excluding .env)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app files (excluding .env)
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI, automatically loading environment variables
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]