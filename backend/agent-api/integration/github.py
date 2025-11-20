import httpx
from typing import Dict, List

GITHUB_CLIENT_ID = ""  # From secrets
GITHUB_CLIENT_SECRET = ""

async def get_user_repos(access_token: str) -> List[Dict]:
    """Get user's repositories"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user/repos",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json()