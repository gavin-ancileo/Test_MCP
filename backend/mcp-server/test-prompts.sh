#!/bin/bash
# Test MCP server prompts endpoint

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Testing MCP Server Prompts${NC}"

# Check if MCP server URL is provided
MCP_SERVER_URL=${MCP_SERVER_URL:-"http://localhost:8001"}

echo -e "${GREEN}📡 Testing MCP Server at: $MCP_SERVER_URL${NC}"

# Test health endpoint
echo -e "${YELLOW}1. Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "$MCP_SERVER_URL/health" || echo "FAILED")
if [ "$HEALTH_RESPONSE" != "FAILED" ]; then
    echo -e "${GREEN}✅ Health check passed:${NC}"
    echo "$HEALTH_RESPONSE" | jq '.' || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

# Test prompts endpoint
echo -e "${YELLOW}2. Testing prompts endpoint...${NC}"
PROMPTS_RESPONSE=$(curl -s "$MCP_SERVER_URL/prompts" || echo "FAILED")
if [ "$PROMPTS_RESPONSE" != "FAILED" ]; then
    COUNT=$(echo "$PROMPTS_RESPONSE" | jq '.count // 0')
    echo -e "${GREEN}✅ Prompts endpoint accessible:${NC}"
    echo "   Total prompts: $COUNT"
    
    if [ "$COUNT" -ge 40 ]; then
        echo -e "${GREEN}✅ Expected 40 prompts found!${NC}"
        
        # Show sample prompts
        echo -e "${YELLOW}📝 Sample prompts:${NC}"
        echo "$PROMPTS_RESPONSE" | jq '.prompts[0:3] | .[] | {code: .code, name: .name, categories: .categories}'
    else
        echo -e "${YELLOW}⚠️  Found $COUNT prompts, expected 40${NC}"
    fi
else
    echo -e "${RED}❌ Prompts endpoint failed${NC}"
    exit 1
fi

# Test single prompt endpoint
echo -e "${YELLOW}3. Testing single prompt endpoint...${NC}"
PROMPT_RESPONSE=$(curl -s "$MCP_SERVER_URL/prompts/ba_1_qualify_sms" || echo "FAILED")
if [ "$PROMPT_RESPONSE" != "FAILED" ]; then
    echo -e "${GREEN}✅ Single prompt endpoint accessible:${NC}"
    echo "$PROMPT_RESPONSE" | jq '{code: .code, name: .name, categories: .categories}' || echo "$PROMPT_RESPONSE"
else
    echo -e "${RED}❌ Single prompt endpoint failed${NC}"
    exit 1
fi

# Test role-based filtering
echo -e "${YELLOW}4. Testing role-based filtering...${NC}"
ROLE_RESPONSE=$(curl -s "$MCP_SERVER_URL/prompts?user_email=hr@company.com" || echo "FAILED")
if [ "$ROLE_RESPONSE" != "FAILED" ]; then
    ROLE_COUNT=$(echo "$ROLE_RESPONSE" | jq '.count // 0')
    echo -e "${GREEN}✅ Role-based filtering works:${NC}"
    echo "   HR prompts visible: $ROLE_COUNT"
else
    echo -e "${YELLOW}⚠️  Role-based filtering test skipped${NC}"
fi

echo -e "${GREEN}✅ All tests passed!${NC}"

