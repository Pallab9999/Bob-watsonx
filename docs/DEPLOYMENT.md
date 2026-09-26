# MCP Server Deployment Guide

## Overview

This guide provides instructions for deploying the MCP Server for watsonx Orchestrate in various environments.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)
- Git (for version control)

## Local Development Setup

### 1. Clone or Download the Project

```bash
cd mcp-watsonx-project
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
python src/mcp_server/main.py
```

The server will start on `http://localhost:8000`

### 5. Verify Server is Running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1234567890.123
}
```

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Tests with Coverage

```bash
pytest tests/ -v --cov=src/mcp_server --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_tools.py -v
```

### Run Specific Test

```bash
pytest tests/test_tools.py::TestGetWeatherTool::test_tool_initialization -v
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_DEBUG=false
MCP_LOG_LEVEL=INFO

# API Keys (optional)
WEATHER_API_KEY=your_weather_api_key
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
```

### Load Environment Variables

```bash
# Windows (PowerShell)
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}

# Linux/Mac
export $(cat .env | xargs)
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "src/mcp_server/main.py"]
```

### 2. Build Docker Image

```bash
docker build -t mcp-watsonx-server:1.0.0 .
```

### 3. Run Docker Container

```bash
docker run -p 8000:8000 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  -e MCP_LOG_LEVEL=INFO \
  mcp-watsonx-server:1.0.0
```

### 4. Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
      - MCP_LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

Run with Docker Compose:

```bash
docker-compose up -d
```

## Cloud Deployment

### IBM Cloud (Cloud Foundry)

#### 1. Create manifest.yml

```yaml
applications:
  - name: mcp-watsonx-server
    runtime: python_311
    memory: 512M
    instances: 1
    env:
      MCP_HOST: 0.0.0.0
      MCP_PORT: 8000
      MCP_LOG_LEVEL: INFO
```

#### 2. Deploy to IBM Cloud

```bash
ibmcloud cf push
```

### AWS (Elastic Beanstalk)

#### 1. Create .ebextensions/python.config

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: src/mcp_server/main:app
```

#### 2. Deploy

```bash
eb create mcp-watsonx-server
eb deploy
```

### Kubernetes

#### 1. Create Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-watsonx-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-watsonx-server
  template:
    metadata:
      labels:
        app: mcp-watsonx-server
    spec:
      containers:
      - name: mcp-server
        image: mcp-watsonx-server:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: MCP_HOST
          value: "0.0.0.0"
        - name: MCP_PORT
          value: "8000"
        - name: MCP_LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-watsonx-server
spec:
  selector:
    app: mcp-watsonx-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### 2. Deploy to Kubernetes

```bash
kubectl apply -f deployment.yaml
```

## Production Considerations

### 1. Security

- Enable HTTPS/TLS
- Implement authentication (API keys, OAuth2)
- Restrict CORS to specific domains
- Implement rate limiting
- Use environment variables for sensitive data
- Implement input validation and sanitization

### 2. Performance

- Use a production ASGI server (Gunicorn, Uvicorn with multiple workers)
- Implement caching for frequently accessed data
- Use a reverse proxy (Nginx, Apache)
- Monitor server performance and resource usage

### 3. Monitoring and Logging

- Implement centralized logging (ELK stack, Splunk)
- Set up monitoring and alerting (Prometheus, Grafana)
- Track API usage and performance metrics
- Implement health checks and uptime monitoring

### 4. Backup and Recovery

- Implement automated backups
- Test disaster recovery procedures
- Maintain multiple instances for high availability
- Use load balancing for distribution

## Production Deployment Example (Gunicorn + Nginx)

### 1. Install Gunicorn

```bash
pip install gunicorn
```

### 2. Create Gunicorn Configuration

Create `gunicorn_config.py`:

```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5
```

### 3. Run with Gunicorn

```bash
gunicorn -c gunicorn_config.py src.mcp_server.main:app
```

### 4. Nginx Configuration

Create `nginx.conf`:

```nginx
upstream mcp_server {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://mcp_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Server Won't Start

1. Check Python version: `python --version`
2. Verify dependencies: `pip list`
3. Check port availability: `netstat -an | grep 8000`
4. Review logs for error messages

### Tests Failing

1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python path: `echo $PYTHONPATH`
3. Run tests with verbose output: `pytest tests/ -vv`

### Performance Issues

1. Monitor CPU and memory usage
2. Check database query performance
3. Review application logs
4. Implement caching where appropriate
5. Scale horizontally with load balancing

## Maintenance

### Regular Tasks

- Monitor server health and performance
- Review and update dependencies
- Apply security patches
- Backup data and configurations
- Review logs for errors and warnings

### Updating the Server

```bash
# Pull latest changes
git pull origin main

# Install updated dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Restart server
# (method depends on deployment platform)
```

## Support and Documentation

- API Documentation: See `docs/API.md`
- Project README: See `README.md`
- Issue Tracking: Use GitHub Issues
- Contact: support@example.com