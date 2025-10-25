# Multi-stage build for Python + Next.js
FROM python:3.13-slim as backend

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy web dependencies and build
COPY web/package*.json ./web/
WORKDIR /app/web
RUN npm install

# Copy all files
WORKDIR /app
COPY . .

# Build Next.js
WORKDIR /app/web
RUN npm run build

# Back to root
WORKDIR /app

# Create storage directory
RUN mkdir -p storage

# Railway default web port
ENV PORT=8080
EXPOSE 8080

# Start Next.js (not Python!)
WORKDIR /app/web
CMD ["npm", "start"]

