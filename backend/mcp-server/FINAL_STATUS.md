# Final Status - 40 Prompts Deployment

## ✅ Completed Fixes

### 1. Database Connection Fixed
- ✅ Added ECS security group (`sg-0bf8d774746d499ae`) to RDS security group (`sg-08d73ab66ffd8d63a`)
- ✅ Rule ID: `sgr-00c6bd79869c83ce3`
- ✅ Database connection now works

### 2. DNS Fixed
- ✅ Fixed DNS record for `internal.assistant.leacare.ai`
- ✅ Changed to point to CloudFront: `d2rza2jv8wuzxh.cloudfront.net`
- ✅ Change ID: `/change/C0041321DUGC803Q7KOV`
- ⏳ **DNS propagation time: 5-10 minutes**

### 3. Files Created
- ✅ `40-prompts.sql` - SQL file with 40 prompts
- ✅ `prompts_data.py` - Python data file
- ✅ All prompts have 2-5 requirement fields
- ✅ All prompts categorized by roles

## ⚠️ Current Issue

**API endpoint returns 405 Method Not Allowed** for POST requests to `/agentcore/prompts`

This means ALB routing is blocking POST method or endpoint is not properly configured.

## 💡 Solution: Deploy via Docker Image (Recommended)

The MCP server has **auto-seed logic** that will seed prompts on startup if:
1. Database has < 40 prompts ✅ (currently has 1)
2. Docker image includes `40-prompts.sql` ✅ (already in Dockerfile)
3. Server restarts

### Steps:

1. **Rebuild Docker image** (if not already done):
```bash
cd backend/mcp-server
docker build -t aap/mcp-server:40-prompts .
```

2. **Push to ECR**:
```bash
docker tag aap/mcp-server:40-prompts 233693675018.dkr.ecr.ap-southeast-2.amazonaws.com/aap/mcp-server:40-prompts
docker push 233693675018.dkr.ecr.ap-southeast-2.amazonaws.com/aap/mcp-server:40-prompts
```

3. **Update ECS service**:
```bash
aws ecs update-service \
  --cluster aap-cluster \
  --service aap-mcp-server-new \
  --force-new-deployment \
  --region ap-southeast-2
```

4. **Wait for restart** - MCP server will auto-seed 40 prompts on startup

## ⏰ DNS Wait Time

**DNS changes take 5-10 minutes to propagate globally**

After waiting, test:
```bash
# Test domain
curl https://internal.assistant.leacare.ai/health

# Or test CloudFront directly (works now)
curl https://d2rza2jv8wuzxh.cloudfront.net/health
```

## 📊 Verification

After deployment, verify:
```bash
# Check prompts count
curl http://aap-alb-new-1908782275.ap-southeast-2.elb.amazonaws.com/agentcore/prompts

# Should return 40 prompts
```

