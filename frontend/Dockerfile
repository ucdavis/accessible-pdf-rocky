FROM node:22-alpine

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Default command (overridden in docker-compose)
CMD ["npm", "run", "dev"]
