#!/bin/bash

# Script to build and deploy Lambda function using Docker

set -e  # Exit on error

echo "🚀 Building Lambda Docker image..."

# Build the Docker image
docker build -f Dockerfile.lambda -t cortex-lambda:latest .

# Test locally (optional)
echo "📦 Testing locally..."
docker run -p 9000:8080 \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
  cortex-lambda:latest &

# Wait for container to start
sleep 5

# Test with curl
echo "🧪 Testing Lambda function..."
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{
    "db_url": "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres",
    "test_name": "docker_test",
    "run_tests": [1]
  }'

# Kill the test container
docker stop $(docker ps -q --filter ancestor=cortex-lambda:latest)

echo "✅ Local test complete!"

# Push to ECR (if you have ECR repository)
read -p "Push to ECR? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Configure these variables
    AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
    AWS_REGION="us-east-1"
    ECR_REPO_NAME="cortex-lambda"
    
    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION | \
      docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Tag the image
    docker tag cortex-lambda:latest \
      $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
    
    # Push to ECR
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
    
    echo "✅ Pushed to ECR!"
    echo "📝 Update your Lambda function to use this image:"
    echo "   $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest"
fi