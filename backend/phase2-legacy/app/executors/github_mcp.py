# app/executors/github_mcp.py
import os
import json
import requests
from typing import Dict, Any, List
from github import Github
from github.PullRequest import PullRequest

class GitHubMCP:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.org = os.getenv("GITHUB_ORG", "your-org")
        self.github = Github(self.token)
    
    def get_pr_details(self, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """Get PR details including diff, comments, checks"""
        repo = self.github.get_repo(f"{self.org}/{repo_name}")
        pr = repo.get_pull(pr_number)
        
        # Get files changed
        files = []
        for file in pr.get_files():
            files.append({
                "filename": file.filename,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch if file.patch else ""
            })
        
        # Get review comments
        comments = []
        for comment in pr.get_review_comments():
            comments.append({
                "user": comment.user.login,
                "body": comment.body,
                "path": comment.path,
                "line": comment.line
            })
        
        # Get status checks
        checks = []
        for check in pr.head.repo.get_commit(pr.head.sha).get_check_runs():
            checks.append({
                "name": check.name,
                "status": check.status,
                "conclusion": check.conclusion
            })
        
        return {
            "number": pr.number,
            "title": pr.title,
            "description": pr.body,
            "author": pr.user.login,
            "state": pr.state,
            "mergeable": pr.mergeable,
            "files_changed": len(files),
            "additions": pr.additions,
            "deletions": pr.deletions,
            "files": files,
            "comments": comments,
            "checks": checks,
            "url": pr.html_url
        }
    
    def analyze_pr_code(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code quality, security issues, best practices"""
        analysis = {
            "security_issues": [],
            "code_quality": [],
            "suggestions": [],
            "approval_recommendation": "pending"
        }
        
        # Analyze each file
        for file in pr_data["files"]:
            patch = file.get("patch", "")
            
            # Security checks
            if "password" in patch.lower() or "secret" in patch.lower():
                analysis["security_issues"].append({
                    "file": file["filename"],
                    "issue": "Potential hardcoded credentials detected"
                })
            
            # Code quality checks
            if file["changes"] > 500:
                analysis["code_quality"].append({
                    "file": file["filename"],
                    "issue": "Large file change - consider breaking into smaller PRs"
                })
            
            # Check for common issues
            if ".env" in file["filename"]:
                analysis["security_issues"].append({
                    "file": file["filename"],
                    "issue": "Environment file should not be committed"
                })
        
        # Make recommendation
        if len(analysis["security_issues"]) > 0:
            analysis["approval_recommendation"] = "changes_requested"
        elif len(analysis["code_quality"]) > 2:
            analysis["approval_recommendation"] = "review_suggested"
        else:
            analysis["approval_recommendation"] = "approved"
        
        return analysis
    
    def approve_pr(self, repo_name: str, pr_number: int, comment: str = "") -> Dict[str, Any]:
        """Approve PR with optional comment"""
        repo = self.github.get_repo(f"{self.org}/{repo_name}")
        pr = repo.get_pull(pr_number)
        
        # Create approval review
        review = pr.create_review(
            body=comment or "LGTM! Approved via MCP automation.",
            event="APPROVE"
        )
        
        return {
            "status": "approved",
            "review_id": review.id,
            "pr_number": pr_number,
            "message": f"PR #{pr_number} has been approved"
        }
    
    def request_changes(self, repo_name: str, pr_number: int, 
                       comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Request changes with specific comments"""
        repo = self.github.get_repo(f"{self.org}/{repo_name}")
        pr = repo.get_pull(pr_number)
        
        # Build review body
        body = "## Changes Requested\n\n"
        for comment in comments:
            body += f"### {comment['file']}\n"
            body += f"{comment['issue']}\n\n"
            if comment.get('suggestion'):
                body += f"**Suggestion:** {comment['suggestion']}\n\n"
        
        review = pr.create_review(
            body=body,
            event="REQUEST_CHANGES"
        )
        
        return {
            "status": "changes_requested",
            "review_id": review.id,
            "pr_number": pr_number
        }

# Function to be called from main.py
def run_github_pr_review(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for PR review
    args: {
        "action": "review|approve|request_changes",
        "repo": "repo-name",
        "pr_number": 123,
        "auto_approve": false
    }
    """
    github = GitHubMCP()
    action = args.get("action", "review")
    repo = args.get("repo")
    pr_number = args.get("pr_number")
    
    if not repo or not pr_number:
        return {
            "status": "error",
            "message": "Missing required parameters: repo and pr_number"
        }
    
    # Get PR details
    pr_data = github.get_pr_details(repo, int(pr_number))
    
    # Analyze the PR
    analysis = github.analyze_pr_code(pr_data)
    
    result = {
        "pr": pr_data,
        "analysis": analysis
    }
    
    # Auto-approve if requested and safe
    if args.get("auto_approve") and analysis["approval_recommendation"] == "approved":
        approval = github.approve_pr(repo, int(pr_number))
        result["action_taken"] = approval
    elif action == "approve":
        approval = github.approve_pr(repo, int(pr_number), args.get("comment", ""))
        result["action_taken"] = approval
    elif action == "request_changes":
        changes = github.request_changes(repo, int(pr_number), analysis["security_issues"] + analysis["code_quality"])
        result["action_taken"] = changes
    
    return result