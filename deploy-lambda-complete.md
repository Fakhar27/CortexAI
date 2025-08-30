# Complete Lambda Deployment Guide with Docker

## Why Docker for Lambda?

Docker solves the "module not found" errors by:
1. **Including all system dependencies** (PostgreSQL libs, compilation tools)
2. **Properly compiling binary packages** (psycopg2, cryptography)
3. **Ensuring compatibility** with Lambda runtime environment
4. **Bundling everything** in a single container image

## Step-by-Step Deployment

### 1. Prerequisites
```bash
# Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Install AWS CLI
pip install awscli
aws configure
```

### 2. Create ECR Repository
```bash
# Create repository for your Lambda image
aws ecr create-repository --repository-name cortex-lambda --region us-east-1

# Get repository URI
aws ecr describe-repositories --repository-names cortex-lambda --query 'repositories[0].repositoryUri' --output text
```

### 3. Build Docker Image
```bash
# Make build script executable
chmod +x build-lambda-docker.sh

# Build the image
docker build -f Dockerfile.lambda -t cortex-lambda:latest .

# For Django integration
docker build -f Dockerfile.lambda.django -t cortex-lambda-django:latest .
```

### 4. Test Locally
```bash
# Run container locally
docker run -p 9000:8080 \
  -e DATABASE_URL="your_pooler_url" \
  -e OPENAI_API_KEY="your_key" \
  -e GOOGLE_API_KEY="your_key" \
  cortex-lambda:latest

# Test with curl
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"db_url": "your_pooler_url", "test_name": "local_test"}'
```

### 5. Push to ECR
```bash
# Set variables
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-east-1"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag image
docker tag cortex-lambda:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/cortex-lambda:latest

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/cortex-lambda:latest
```

### 6. Create Lambda Function
```bash
# Create Lambda function from container image
aws lambda create-function \
  --function-name cortex-pooler-test \
  --package-type Image \
  --code ImageUri=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/cortex-lambda:latest \
  --role arn:aws:iam::$AWS_ACCOUNT_ID:role/lambda-execution-role \
  --timeout 60 \
  --memory-size 512 \
  --environment Variables="{DATABASE_URL=your_pooler_url,OPENAI_API_KEY=your_key}"
```

### 7. Update Existing Lambda
```bash
# Update function code
aws lambda update-function-code \
  --function-name cortex-pooler-test \
  --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/cortex-lambda:latest
```

## Common Issues and Solutions

### Issue: "No module named 'langgraph'"
**Solution:** Module not included in image. Add to `requirements-lambda.txt`:
```txt
langgraph==0.2.0
langgraph-checkpoint==2.0.0
langgraph-checkpoint-postgres==2.0.0
langgraph-checkpoint-sqlite==2.0.0
```

### Issue: "No module named 'psycopg2'"
**Solution:** Binary compilation issue. Docker handles this with:
```dockerfile
RUN yum install -y postgresql-devel libpq-devel
RUN pip install psycopg2-binary psycopg[binary]
```

### Issue: "Cannot import name 'PostgresSaver'"
**Solution:** Wrong import path. Ensure:
```python
from langgraph.checkpoint.postgres import PostgresSaver
```

### Issue: Lambda times out
**Solution:** Increase timeout and memory:
```bash
aws lambda update-function-configuration \
  --function-name cortex-pooler-test \
  --timeout 120 \
  --memory-size 1024
```

## Django Integration

For Django + Cortex in Lambda:

1. **Add Django dependencies** to `requirements-lambda.txt`:
```txt
Django>=4.2.0
mangum>=0.17.0  # ASGI adapter for Lambda
```

2. **Use the Django Dockerfile**:
```bash
docker build -f Dockerfile.lambda.django -t cortex-django:latest .
```

3. **Configure API Gateway**:
```bash
# Create REST API
aws apigatewayv2 create-api \
  --name cortex-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:function:cortex-pooler-test
```

## Testing Your Deployment

### Direct Lambda Test:
```bash
aws lambda invoke \
  --function-name cortex-pooler-test \
  --payload '{"db_url": "your_pooler_url", "test_name": "aws_test"}' \
  response.json

cat response.json
```

### API Gateway Test:
```bash
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/prod \
  -H "Content-Type: application/json" \
  -d '{"test_type": "cortex_pooler", "db_url": "your_pooler_url"}'
```

## Environment Variables

Set these in Lambda configuration:
```bash
DATABASE_URL=postgresql://user:pass@pooler.supabase.com:6543/postgres
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
COHERE_API_KEY=...
ANTHROPIC_API_KEY=...
```

## Monitoring

View logs:
```bash
aws logs tail /aws/lambda/cortex-pooler-test --follow
```

## Cost Optimization

1. **Use ARM architecture** (Graviton2):
```bash
FROM public.ecr.aws/lambda/python:3.11-arm64
```

2. **Enable Lambda SnapStart** for faster cold starts
3. **Use provisioned concurrency** for consistent performance
4. **Set up CloudWatch alarms** for errors and duration

## Complete Package Structure
```
cortex/
├── Dockerfile.lambda           # Basic Lambda Docker
├── Dockerfile.lambda.django    # Django + Lambda Docker
├── requirements-lambda.txt     # All Python dependencies
├── lambda_pooler_test.py      # Test handler
├── lambda_handler_django.py   # Django handler
├── build-lambda-docker.sh     # Build script
├── cortex/                    # Your cortex package
│   ├── __init__.py
│   ├── responses/
│   └── ...
└── deploy-lambda-complete.md  # This guide
```

This Docker approach ensures all dependencies are properly included and compiled for the Lambda environment, eliminating module not found errors.