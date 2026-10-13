# Base image: Official lightweight Python 3.11 slim
FROM python:3.11-slim

# Set container working directory
WORKDIR /app

# Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy dependency specifications and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application codebase
COPY . .

# Ensure data directory exists for SQLite database storage & Docker Volume mounting
RUN mkdir -p /app/data

# Expose default Flask service port
EXPOSE 5000

# Execute Flask application on 0.0.0.0:5000
CMD ["python", "app.py"]
