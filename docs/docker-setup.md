# Docker Setup

This document provides detailed information on setting up and running the Summarization Agent using Docker.

## Overview

The Summarization Agent is containerized using Docker to ensure consistent environment, simplified deployment, and improved scalability. Docker containers package the application and its dependencies, allowing it to run reliably across different computing environments.

## System Requirements

Before proceeding with the Docker setup, ensure your system meets the following requirements:

- **Docker**: Version 20.10.0 or later
- **Docker Compose**: Version 2.0.0 or later
- **Storage**: At least 2GB of free disk space
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **CPU**: Minimum 2 cores (4 cores recommended)
- **Network**: Internet connection for pulling images and accessing OpenAI API

## Container Components

The Docker setup consists of the following components:

1. **Application Container**: Runs the Summarization Agent application
2. **Database Container**: (Planned) Will host the Supabase database for persistent storage
3. **Redis Container**: (Planned) Will provide caching and message queue functionality

## Docker Compose Configuration

The application is defined in the `docker-compose.yml` file, which orchestrates the containers and their configurations:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - .:/app
      - ./tmp:/app/tmp
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=true
      - LOG_LEVEL=INFO
      - MAX_ATTACHMENT_SIZE=25000000
    command: uvicorn src.main:app --host 0.0.0.0 --reload
    restart: unless-stopped
```

## Dockerfile

The `Dockerfile` defines how the application container is built:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

## Setup Instructions

### 1. Environment Configuration

Create a `.env` file in the project root with the following variables:

OPENAI_API_KEY=your_openai_api_key
DEBUG=true
LOG_LEVEL=INFO
MAX_ATTACHMENT_SIZE=25000000

### 2. Building the Docker Image

To build the Docker image for the Summarization Agent:

```bash
docker-compose build
```

This command builds the Docker image based on the Dockerfile and configuration.

### 3. Starting the Containers

To start the Docker containers:

```bash
docker-compose up -d
```

The `-d` flag runs the containers in detached mode, allowing them to run in the background.

### 4. Verifying the Setup

To verify that the containers are running properly:

```bash
docker-compose ps
```

You should see the app container running with status "Up".

To check the application logs:

```bash
docker-compose logs -f app
```

The `-f` flag enables log following, displaying logs in real-time.

### 5. Accessing the Application

Once the containers are running, you can access the application at:

```bash
http://localhost:8000
```

Test the health check endpoint:

```bash
curl http://localhost:8000/health
```

You should receive a response with `{"status": "ok"}`.

## Volume Mapping

The Docker Compose configuration includes volume mapping to enable:

1. **Code Changes Without Rebuilding**: The `.:/app` mapping allows code changes to be reflected in the container without rebuilding.
2. **Persistent Storage**: The `./tmp:/app/tmp` mapping ensures that temporary files (like extracted images) are accessible from the host machine.

## Environment Variables

The following environment variables can be configured:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `OPENAI_API_KEY` | OpenAI API key for authentication | None (Required) |
| `DEBUG` | Enable debug mode | true |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `MAX_ATTACHMENT_SIZE` | Maximum attachment size in bytes | 25000000 (25MB) |

## Docker Commands Reference

### Basic Commands

```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# Restart containers
docker-compose restart

# View logs
docker-compose logs -f app

# Rebuild the image
docker-compose build

# Start with rebuild
docker-compose up -d --build
```

### Advanced Commands

```bash
# Execute a command in the running container
docker-compose exec app bash

# Check resource usage
docker stats

# Inspect container configuration
docker-compose config

# Force recreation of containers
docker-compose up -d --force-recreate

# View only the most recent logs
docker-compose logs -f --tail=100 app
```

## Troubleshooting

### Common Issues

1. **Container fails to start**:
   - Check logs with `docker-compose logs app`
   - Verify that the required environment variables are set
   - Ensure ports are not already in use by another application

2. **Application errors**:
   - Check application logs with `docker-compose logs -f app`
   - Verify that the OPENAI_API_KEY is valid
   - Check if the tmp directory has proper permissions

3. **Permission issues with mounted volumes**:
   - Run `chmod -R 777 ./tmp` to grant full permissions to the tmp directory
   - Verify ownership of mounted directories

4. **Network connectivity issues**:
   - Check if the container can access the internet with `docker-compose exec app ping openai.com`
   - Verify Docker network settings

5. **Changes not reflecting**:
   - Ensure you're editing the files on the host, not in the container
   - Check if automatic reload is working (`--reload` flag in command)
   - Try restarting the containers with `docker-compose restart`

### Debugging Steps

1. **Access the container shell**:
   ```bash
   docker-compose exec app bash
   ```

2. **Check dependencies**:
   ```bash
   pip list
   ```

3. **Verify file permissions**:
   ```bash
   ls -la /app/tmp
   ```

4. **Check environment variables**:
   ```bash
   env | grep OPENAI
   ```

5. **Test API connectivity**:
   ```bash
   curl -I https://api.openai.com
   ```

## Performance Tuning

### Container Resource Limits

To optimize performance, you can add resource limits to your `docker-compose.yml`:

```yaml
services:
  app:
    # ... existing configuration ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

### Volume Performance

For improved I/O performance, consider using Docker volumes instead of bind mounts:

```yaml
services:
  app:
    # ... existing configuration ...
    volumes:
      - .:/app
      - app_tmp:/app/tmp

volumes:
  app_tmp:
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **Container Privileges**: Avoid running containers with elevated privileges
3. **Image Security**: Regularly update base images and dependencies
4. **Network Security**: Limit exposed ports to only what's necessary
5. **Secrets Management**: Consider using Docker secrets for sensitive information

## Production Deployment

For production environments, consider the following adjustments:

1. **Disable Debug Mode**: Set `DEBUG=false` in production
2. **Remove Code Mounting**: Remove the `.:/app` volume mount
3. **Use Multi-stage Builds**: Optimize the Dockerfile with multi-stage builds
4. **Implement Health Checks**: Add health checks to the Docker Compose configuration
5. **Set Up Monitoring**: Configure monitoring and alerting
6. **Use Container Orchestration**: Consider using Kubernetes or Docker Swarm for advanced orchestration

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/)
- [Python Docker Best Practices](https://pythonspeed.com/docker/)

http://localhost:8000

