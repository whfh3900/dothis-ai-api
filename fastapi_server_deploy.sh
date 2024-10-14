#!/bin/bash

# 1. Change directory to the project directory
# cd /home/ybw/ai-fastapi-api || { echo "Directory not found"; exit 1; }

# 2. Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
else
    echo ".env file not found"
    exit 1
fi

# 3. Update the Git repository and pull the latest changes from the main branch
# git remote update && git pull origin main || { echo "Git pull failed"; exit 1; }

# 4. Remove the existing Docker container if it exists
docker rm --force ai-fastapi-api-v-c || { echo "No container to remove or removal failed"; }

# 5. Remove the existing Docker image if it exists
docker rmi ai-fastapi-api-v-c:latest || { echo "No image to remove or removal failed"; }

# 6. Build the Docker image with the specified Dockerfile
docker build -t ai-fastapi-api-v-c:latest -f dockerfile . || { echo "Docker build failed"; exit 1; }

# 7. Run the Docker container with the specified environment variables
docker run -d -p 8003:8001 --gpus all --name ai-fastapi-api-v-c \
-e HASH_KEY=$HASH_KEY \
-e REDIS_SENTINEL_PASSWORD=$REDIS_SENTINEL_PASSWORD \
-e REDIS_SENTINEL_NODE1=$REDIS_SENTINEL_NODE1 \
-e REDIS_SENTINEL_NODE2=$REDIS_SENTINEL_NODE2 \
-e REDIS_SENTINEL_NODE3=$REDIS_SENTINEL_NODE3 \
-e USE_CUDA=$USE_CUDA \
ai-fastapi-api-v-c || { echo "Docker run failed"; exit 1; }

echo "Docker container started successfully"
