# Stage 1: Build Drive MCP Server (TypeScript)
# Note: Build from backend/ directory with: docker build -f agent-api/Dockerfile -t agent-api .
FROM node:20-slim AS drive-mcp-builder
WORKDIR /drive-mcp-server

# Copy package files and install dependencies
COPY drive-mcp-server/package*.json ./
RUN npm ci

# Copy source and build
COPY drive-mcp-server/tsconfig.json ./
COPY drive-mcp-server/src ./src
RUN npm run build

# Stage 2: Python application with Node.js runtime
FROM python:3.11-slim
WORKDIR /app

# Install Node.js (includes npm/npx) for MCP servers (GitHub + Drive)
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy built Drive MCP Server from builder stage
COPY --from=drive-mcp-builder /drive-mcp-server/dist /app/drive-mcp-server/dist
COPY --from=drive-mcp-builder /drive-mcp-server/node_modules /app/drive-mcp-server/node_modules
COPY --from=drive-mcp-builder /drive-mcp-server/package.json /app/drive-mcp-server/

# Install Python dependencies
COPY agent-api/requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy Python application
COPY agent-api/ .

EXPOSE 8080

# Use app.py with service discovery for MCP Server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]