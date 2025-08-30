# AWS Console Guide for Lambda Deployment (Simple Version)

## Step 1: Build Docker Image Locally

```bash
# Build the Docker image on your computer
docker build -f Dockerfile.lambda -t cortex-lambda:latest .
```

## Step 2: Create ECR Repository (AWS Console)

1. **Go to Amazon ECR** in AWS Console
2. Click **"Create repository"**
3. Name: `cortex-lambda`
4. Keep other settings default
5. Click **"Create repository"**
6. Click on your new repository
7. Click **"View push commands"** - save these for later

## Step 3: Push Docker Image to ECR

Use the push commands from ECR (they look like this):

```bash
# 1. Get login token (replace with your region)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# 2. Tag your image (replace with your ECR URI)
docker tag cortex-lambda:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/cortex-lambda:latest

# 3. Push image
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/cortex-lambda:latest
```

## Step 4: Create Lambda Function (AWS Console)

1. **Go to AWS Lambda** in Console
2. Click **"Create function"**
3. Choose **"Container image"** (not "Author from scratch")
4. Function name: `cortex-pooler-test`
5. Container image URI: Click **"Browse images"**
   - Select your `cortex-lambda` repository
   - Select `latest` tag
6. Architecture: `x86_64`
7. Click **"Create function"**

## Step 5: Configure Lambda Function

After creation, in your Lambda function:

1. **Configuration → General configuration:**
   - Memory: `512 MB` (or more if needed)
   - Timeout: `1 minute`
   - Click "Save"

2. **Configuration → Environment variables:**
   Click "Edit" and add:
   ```
   DATABASE_URL = your_supabase_pooler_url
   OPENAI_API_KEY = sk-...
   GOOGLE_API_KEY = ...
   ```

3. **Configuration → Permissions:**
   - Make sure the execution role has basic Lambda permissions

## Step 6: Test Your Function

1. Click **"Test"** tab
2. Create new test event:
   ```json
   {
     "db_url": "postgresql://postgres.xxx:password@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres",
     "test_name": "console_test",
     "run_tests": [1, 2, 3]
   }
   ```
3. Click **"Test"**
4. Check the execution results

## Step 7: View Logs

1. Click **"Monitor"** tab
2. Click **"View CloudWatch logs"**
3. Click on latest log stream
4. See all your test outputs

## How It All Works

```
Your Computer                AWS
-------------                ---
                            
1. Build Docker     ───►    2. Push to ECR
   (includes all             (stores image)
    dependencies)                 │
                                 ▼
                            3. Lambda pulls
                               image from ECR
                                 │
                                 ▼
4. You trigger      ───►    5. Lambda runs
   test from                   your code
   Console                       │
                                ▼
6. View results    ◄───     Returns JSON
   in Console                  response
```

## What Each File Does

- **Dockerfile.lambda**: Builds container with all dependencies
- **requirements-lambda.txt**: Lists all Python packages needed
- **lambda_pooler_test.py**: Your actual test code that runs
- **cortex/**: Your Cortex package code

## Common Issues

### "Module not found" errors
**Why it happens**: ZIP deployment missing dependencies
**Docker fixes this**: All dependencies are in the container

### "Cannot import PostgresSaver"
**Why it happens**: LangGraph not installed properly
**Docker fixes this**: Installs everything correctly

### Lambda times out
**Solution**: Increase timeout in Configuration → General configuration

### Can't see logs
**Solution**: Check CloudWatch → Log groups → /aws/lambda/cortex-pooler-test

## Update Your Function

When you change code:

```bash
# 1. Rebuild image
docker build -f Dockerfile.lambda -t cortex-lambda:latest .

# 2. Push to ECR (same commands as before)
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/cortex-lambda:latest

# 3. In Lambda Console
- Go to your function
- Click "Deploy new image" 
- Select latest version
- Click "Save"
```

## That's It!

No Django needed, just:
1. Build Docker image
2. Push to ECR
3. Create Lambda from image
4. Test from Console

The Docker approach ensures everything works because it packages all dependencies together, unlike ZIP files which often miss system libraries.