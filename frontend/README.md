# AAP Enduser - Enterprise Frontend Application

A production-ready enterprise web application featuring **Role-Based Access Control (RBAC)**, **comprehensive admin panel**, **dual authentication system** (AWS Cognito SSO + Devv.ai Email OTP), native GitHub/Jira/Drive integrations, modern chat interface with **smart prompt templates**, and **AWS ECS deployment ready**.

## 🚀 Features

### **Core Features**
- **🔐 Dual Authentication System**: AWS Cognito SSO (primary) + Devv.ai Email OTP (fallback)
- **👥 Role-Based Access Control (RBAC)**: Admin vs User roles with granular permissions
- **🎛️ Comprehensive Admin Panel**: Prompts, users, testing, and settings management
- **💬 Smart Prompt Template System**: Dynamic variables with GitHub auto-fill integration
- **🔗 Native Integrations**: GitHub, Jira, and Google Drive with managed OAuth
- **📱 Responsive Design**: Optimized for desktop and mobile devices
- **🐳 AWS ECS Ready**: Complete Docker + ECS deployment configuration

### **Admin Panel Features**
- **Prompts Management**: Create, edit, delete prompts with dynamic variable detection
- **Test Panel**: AI-powered prompt testing with multiple models
- **Users Management**: Role assignment and permissions overview
- **Settings Panel**: System configuration and backend integration

### **Chat Interface**
- **Smart Prompt Templates**: Full list with search and category filtering
- **Dynamic Variables**: Auto-parsed from prompt content with validation
- **GitHub Integration**: Auto-fill repository URLs from connected account
- **Real-time Backend**: Integration with AgentCore API and graceful fallback

## 🛠 Tech Stack

### **Frontend**
- **Framework**: React 18 + TypeScript + Vite
- **UI**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand with persistence
- **Routing**: React Router v6
- **Icons**: Lucide React

### **Backend Integration**
- **Authentication**: AWS Cognito OAuth2 (SSO) + Devv.ai Email OTP
- **API**: AgentCore backend integration with health monitoring
- **Integrations**: GitHub, Jira, Google Drive APIs

### **Deployment**
- **Container**: Docker (Multi-stage build with Nginx)
- **Orchestration**: AWS ECS Fargate
- **Load Balancer**: Application Load Balancer (ALB)
- **Monitoring**: CloudWatch Logs and Metrics

## 🏁 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- AWS Cognito User Pool configured with:
  - App Client (Public client, no client secret)
  - Hosted UI enabled
  - OAuth 2.0 flows: Authorization code grant
  - OAuth 2.0 scopes: openid, email, profile
  - Callback URLs configured

### Installation

1. **Clone and install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local` with your configuration (production values already configured):
   ```env
   # Production Configuration (Already Set)
   VITE_COGNITO_DOMAIN=aap-project.auth.ap-southeast-2.amazoncognito.com
   VITE_COGNITO_CLIENT_ID=20bsno0fmojtchqem9vacrlivt
   VITE_COGNITO_USER_POOL_ID=ap-southeast-2_TFmPkO0Lc
   VITE_COGNITO_REGION=ap-southeast-2
   VITE_COGNITO_REDIRECT_URI=https://preview-f0vxnvirb4sg.devv.app/callback
   VITE_API_BASE_URL=http://aap-alb-ALB-BD6uDqhT1dNT-61728180.ap-southeast-2.elb.amazonaws.com
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

## 🔧 Configuration

### AWS Cognito Setup

1. Create a Cognito User Pool
2. Configure an App Client:
   - Type: Public client
   - Authentication flows: Allow all
   - OAuth 2.0 grant types: Authorization code grant
   - OAuth 2.0 scopes: openid, email, profile
   - Callback URLs: Add your redirect URI
3. Enable Hosted UI
4. Note your domain and client ID for environment variables

### AgentCore Integration

The app supports two modes:

**Demo Mode** (default): 
- No VITE_AGENTCORE_URL configured
- Returns mock responses for testing
- Environment badge shows "Demo"

**Production Mode**:
- VITE_AGENTCORE_URL configured
- Calls actual AgentCore API with Bearer token
- Environment badge shows "Live"

#### AgentCore API Contract

```typescript
// Request
POST {AGENTCORE_URL}/run
Authorization: Bearer <id_token>
Content-Type: application/json

{
  "message": "User message",
  "conversationId": "optional-conversation-id"
}

// Response
{
  "message": "Assistant response",
  "conversationId": "conversation-id",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🏗 Architecture

### Security Features

- **PKCE Flow**: Secure OAuth 2.0 implementation
- **Memory-Only Storage**: Tokens stored in memory, not localStorage
- **State Validation**: CSRF protection with state parameter
- **Token Validation**: JWT decoding and validation

### State Management

- **Auth Store**: User authentication state
- **Conversation Store**: Chat history with persistence
- **Zustand**: Lightweight state management

### Route Structure

- `/` - Landing page with SSO login
- `/callback` - OAuth callback handler
- `/chat` - Protected chat interface
- `*` - 404 error page

## 📱 User Experience

### Landing Page
- Hero section with company branding
- Single sign-on authentication
- Feature highlights
- Disabled "Start Chatting" until logged in

### Chat Interface
- Conversation sidebar with history
- Message area with user/assistant bubbles
- Input field with keyboard shortcuts
- Loading states and error handling

### Mobile Support
- Responsive sidebar (sheet on mobile)
- Touch-optimized interactions
- Proper viewport handling

## 🔒 Security Considerations

- Tokens stored in memory only (cleared on refresh)
- PKCE implementation for OAuth 2.0
- State parameter validation
- Secure redirect URI validation
- No sensitive data in localStorage

## 🚀 Deployment

### **Quick Start: AWS ECS Deployment**

**📋 Complete deployment guides available:**
- `EDIT-SUMMARY.md` - **START HERE** - Files to edit summary
- `AWS-ECS-DEPLOYMENT.md` - Complete ECS deployment guide
- `DEPLOYMENT-CHECKLIST.md` - Quick reference checklist
- `DEPLOYMENT.md` - Docker deployment options
- `DOCKER-QUICKSTART.md` - Fast local deployment

### **Files to Edit Before Deployment**

#### 1. Environment Configuration (`.env.production`)
```bash
# ⚠️ MUST CHANGE - Your Backend URL
VITE_AGENTCORE_URL=http://YOUR-BACKEND-ALB.elb.amazonaws.com/agentcore
VITE_API_BASE_URL=http://YOUR-BACKEND-ALB.elb.amazonaws.com/agentcore

# ⚠️ MUST CHANGE - Your Frontend Callback URL (after deployment)
VITE_COGNITO_REDIRECT_URI=https://YOUR-FRONTEND-ALB.elb.amazonaws.com/callback

# ✅ KEEP AS IS - Cognito Configuration
VITE_COGNITO_DOMAIN=https://aap-uat-20251014.auth.ap-southeast-2.amazoncognito.com
VITE_COGNITO_CLIENT_ID=20bsno0fmojtchqem9vacrlivt
VITE_COGNITO_USER_POOL_ID=ap-southeast-2_TFmPkO0Lc
VITE_COGNITO_REGION=ap-southeast-2
```

#### 2. ECS Task Definition (`ecs-task-definition.json`)
```json
// Update YOUR_ACCOUNT_ID with your AWS Account ID
"executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole"
"image": "YOUR_ACCOUNT_ID.dkr.ecr.ap-southeast-2.amazonaws.com/aap-enduser-frontend:latest"
```

#### 3. AWS Cognito Console (Manual)
- Add callback URL: `https://YOUR-FRONTEND-ALB.elb.amazonaws.com/callback`

### **Deployment Commands**

```bash
# 1. Build Docker image
export $(cat .env.production | xargs)
docker build \
  --build-arg VITE_COGNITO_DOMAIN=$VITE_COGNITO_DOMAIN \
  --build-arg VITE_COGNITO_CLIENT_ID=$VITE_COGNITO_CLIENT_ID \
  --build-arg VITE_COGNITO_REDIRECT_URI=$VITE_COGNITO_REDIRECT_URI \
  --build-arg VITE_AGENTCORE_URL=$VITE_AGENTCORE_URL \
  -t aap-enduser-frontend:latest .

# 2. Push to ECR
aws ecr get-login-password --region ap-southeast-2 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.ap-southeast-2.amazonaws.com
docker tag aap-enduser-frontend:latest YOUR_ACCOUNT_ID.dkr.ecr.ap-southeast-2.amazonaws.com/aap-enduser-frontend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.ap-southeast-2.amazonaws.com/aap-enduser-frontend:latest

# 3. Deploy to ECS
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json --region ap-southeast-2
aws ecs update-service --cluster aap-cluster --service aap-enduser-frontend-service --force-new-deployment --region ap-southeast-2
```

### **Local Testing with Docker**

```bash
# Quick local deployment
docker-compose up -d

# Access at http://localhost:8080
```

### **⚠️ Critical Notes**
- Environment variables are baked at **BUILD TIME** (Vite requirement)
- Cognito callback URL must match **EXACTLY**
- Two-phase deployment required (get ALB URL → update Cognito → rebuild)

## 🎨 Customization

### Brand Colors
Edit `src/index.css` to customize the color scheme:
```css
--primary: 214 100% 54%; /* #1B7FFF */
--secondary: 220 25% 20%; /* #111827 */
```

### Environment Badge
The header shows environment status based on AgentCore configuration:
- "Demo" - VITE_AGENTCORE_URL not set
- "Live" - VITE_AGENTCORE_URL configured

## 📄 License

This project is licensed under the MIT License.