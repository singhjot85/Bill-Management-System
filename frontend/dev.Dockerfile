FROM node:lts-alpine

WORKDIR /frontend

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port
EXPOSE 5173

# just to be double sure
RUN chmod +x scripts/npm-start.sh

# Start the Vite server
CMD ["sh", "scripts/npm-start.sh"]
