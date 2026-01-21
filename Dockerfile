# Use official Python image with Node.js
FROM python:3.11-slim

# Install Node.js 20.x
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* .npmrc ./

# Install Node.js dependencies
RUN npm install

# Copy all source files
COPY . .

# Build frontend
RUN npm run build

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Koyeb will override this)
EXPOSE 8000

# Start the application
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
