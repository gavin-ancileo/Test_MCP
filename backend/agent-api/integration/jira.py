import httpx

JIRA_BASE_URL = "https://your-company.atlassian.net"

async def get_my_issues(access_token: str):
    """Get user's assigned issues"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{JIRA_BASE_URL}/rest/api/3/search?jql=assignee=currentUser()",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json()