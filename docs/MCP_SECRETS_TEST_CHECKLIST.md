# MCP Secrets Manager Integration - Test Checklist

## ✅ Code Changes Summary

### Files Modified:
1. **`backend/agent-api/tools/mcp_client.py`**
   - ✅ Import `CONFIG` from `config.py` (Secrets Manager)
   - ✅ All secrets use pattern: `CONFIG.get('KEY') or os.getenv('KEY')`
   - ✅ GitHub, Jira, Drive tokens/configs load from Secrets Manager

2. **`backend/agent-api/config.py`**
   - ✅ `MCP_URL` và `N8N_URL` load từ `CONFIG` (Secrets Manager)
   - ✅ Fallback về environment variables

3. **`backend/agent-api/tools/jira_mcp_wrapper.py`**
   - ✅ Fixed syntax errors (missing brackets)

### Documentation Created:
- ✅ `docs/MCP_SECRETS_MANAGEMENT.md` - Secrets management guide

---

## 🧪 Testing Checklist

### Pre-Deployment Checks

#### 1. Local Development Test
- [ ] **Verify Secrets Manager fallback works**
  ```bash
  # Test without Secrets Manager access (local)
  # Should fallback to environment variables
  cd backend/agent-api
  python -c "from config import CONFIG; print('Config loaded:', len(CONFIG))"
  ```

- [ ] **Test MCP client imports**
  ```bash
  python -c "from tools.mcp_client import MCP_AVAILABLE, CONFIG; print('MCP available:', MCP_AVAILABLE)"
  ```

#### 2. Secrets Manager Verification
- [ ] **Check secrets exist in AWS Secrets Manager**
  ```bash
  aws secretsmanager get-secret-value \
    --secret-id AAP/uat/agentcore \
    --query SecretString --output text | jq .
  ```

- [ ] **Verify required keys are present:**
  - [ ] `GITHUB_CLIENT_ID`
  - [ ] `GITHUB_CLIENT_SECRET`
  - [ ] `JIRA_CLIENT_ID`
  - [ ] `JIRA_CLIENT_SECRET`
  - [ ] `GOOGLE_CLIENT_ID`
  - [ ] `GOOGLE_CLIENT_SECRET`
  - [ ] `MCP_URL`
  - [ ] `GITHUB_REDIRECT_URI`
  - [ ] `JIRA_REDIRECT_URI`
  - [ ] `GOOGLE_REDIRECT_URI`

### Deployment Steps

#### 3. Deploy to UAT
- [ ] **Push code to repository**
  ```bash
  git add .
  git commit -m "feat: Use Secrets Manager for all MCP integration secrets"
  git push origin main
  ```

- [ ] **Verify ECS Task Definition includes secrets**
  - Check `infra/ecs-task-definitions/` or CloudFormation
  - Ensure `AAP/uat/agentcore` secret is referenced

- [ ] **Deploy Agent API service**
  - Trigger CI/CD pipeline or manual deployment
  - Monitor deployment logs

#### 4. Post-Deployment Verification

- [ ] **Check service logs for config loading**
  ```bash
  # Should see:
  # [Config] Loading configuration from Secrets Manager: AAP/uat/agentcore
  # [Config] Successfully loaded from Secrets Manager
  # OK: Loaded X config values from Secrets Manager
  ```

- [ ] **Verify MCP client initialization**
  - Check logs for: `[MCP Client]` messages
  - No errors about missing CONFIG

### Functional Testing

#### 5. Test GitHub Integration
- [ ] **Test GitHub OAuth token retrieval**
  - Connect GitHub account via UI
  - Verify token stored in Company MCP Server DB
  - Test GitHub tool calls (list repos, search code, read file)

- [ ] **Test fallback to Secrets Manager token**
  - If user hasn't connected, should use `GITHUB_PERSONAL_ACCESS_TOKEN` from SM
  - (Optional: Add this key to Secrets Manager if needed)

#### 6. Test Jira Integration
- [ ] **Test Jira OAuth token retrieval**
  - Connect Jira account via UI
  - Verify token stored in Company MCP Server DB
  - Test Jira tool calls (list projects, search issues, get issue)

- [ ] **Test Jira instance URL resolution**
  - Should get from Company MCP Server metadata first
  - Fallback to `JIRA_INSTANCE_URL` from Secrets Manager
  - Fallback to default if not found

#### 7. Test Google Drive Integration
- [ ] **Test Drive OAuth token retrieval**
  - Connect Google Drive account via UI
  - Verify token stored in Company MCP Server DB
  - Test Drive tool calls (list files, search files, read file)

- [ ] **Test Google OAuth credentials**
  - Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` loaded from SM
  - Used for token refresh if needed

### Error Handling Tests

#### 8. Test Fallback Mechanisms
- [ ] **Test when Secrets Manager unavailable**
  - Should fallback to environment variables
  - Service should still start (with warnings)

- [ ] **Test when user token not found**
  - Should show clear error message
  - Should suggest connecting account in Settings

- [ ] **Test when OAuth credentials missing**
  - Should show clear error about missing credentials in SM

### Performance & Monitoring

#### 9. Monitor Performance
- [ ] **Check Secrets Manager API calls**
  - Should only load once at startup (cached in `CONFIG`)
  - No repeated calls during tool execution

- [ ] **Monitor error rates**
  - Check CloudWatch logs for any Secrets Manager errors
  - Verify fallback mechanisms work correctly

---

## 🚨 Rollback Plan

If issues occur:

1. **Immediate Rollback:**
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

2. **Verify old behavior:**
   - Code will fallback to environment variables
   - Service should continue working

3. **Investigate:**
   - Check Secrets Manager permissions
   - Verify secret keys exist
   - Check ECS Task Definition secret references

---

## 📝 Notes

- **Priority Order:**
  1. User OAuth Token (from DB) - Highest
  2. Secrets Manager (`CONFIG`) - Production
  3. Environment Variables - Local dev fallback

- **No Breaking Changes:**
  - All changes maintain backward compatibility
  - Fallback to env vars ensures local dev still works
  - Production uses Secrets Manager automatically

- **Optional Keys:**
  - `GITHUB_PERSONAL_ACCESS_TOKEN` - Only needed if users don't connect accounts
  - `JIRA_INSTANCE_URL` - Only needed if not in user metadata
  - `GITHUB_MCP_USE_DOCKER`, `DRIVE_MCP_USE_DOCKER` - Config flags

