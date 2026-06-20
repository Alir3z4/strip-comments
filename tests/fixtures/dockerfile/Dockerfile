# Base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt  # install deps

# Copy source
COPY . .

# Run
CMD ["python", "-m", "strip_comments.cli"]
