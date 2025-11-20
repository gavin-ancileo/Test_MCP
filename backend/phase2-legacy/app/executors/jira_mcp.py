# app/executors/jira_mcp.py
import os
from jira import JIRA
from typing import Dict, Any, List

class JiraMCP:
    def __init__(self):
        self.server = os.getenv("JIRA_SERVER", "https://ancileo.atlassian.net/")
        self.email = os.getenv("JIRA_EMAIL")
        self.token = os.getenv("JIRA_API_TOKEN")
        self.jira = JIRA(server=self.server, basic_auth=(self.email, self.token))
    
    def get_my_issues(self, status: str = None) -> List[Dict[str, Any]]:
        """Get issues assigned to me"""
        jql = f'assignee = currentUser()'
        if status:
            jql += f' AND status = "{status}"'
        
        issues = self.jira.search_issues(jql, maxResults=20)
        
        return [{
            "key": issue.key,
            "summary": issue.fields.summary,
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else "None",
            "type": issue.fields.issuetype.name,
            "url": f"{self.server}/browse/{issue.key}"
        } for issue in issues]
    
    def get_sprint_issues(self) -> List[Dict[str, Any]]:
        """Get current sprint issues"""
        jql = 'sprint in openSprints() ORDER BY priority DESC'
        issues = self.jira.search_issues(jql, maxResults=50)
        
        return [{
            "key": issue.key,
            "summary": issue.fields.summary,
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
            "status": issue.fields.status.name,
            "story_points": getattr(issue.fields, 'customfield_10016', None)
        } for issue in issues]
    
    def create_issue(self, summary: str, description: str, 
                    issue_type: str = "Task", project: str = None) -> Dict[str, Any]:
        """Create new JIRA issue"""
        if not project:
            project = os.getenv("JIRA_DEFAULT_PROJECT", "PROJ")
        
        issue_dict = {
            'project': {'key': project},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type}
        }
        
        new_issue = self.jira.create_issue(fields=issue_dict)
        
        return {
            "key": new_issue.key,
            "url": f"{self.server}/browse/{new_issue.key}",
            "status": "created"
        }
    
    def update_issue_status(self, issue_key: str, status: str) -> Dict[str, Any]:
        """Move issue to different status"""
        issue = self.jira.issue(issue_key)
        transitions = self.jira.transitions(issue)
        
        # Find the transition ID for the desired status
        transition_id = None
        for t in transitions:
            if t['name'].lower() == status.lower():
                transition_id = t['id']
                break
        
        if transition_id:
            self.jira.transition_issue(issue, transition_id)
            return {
                "status": "updated",
                "issue": issue_key,
                "new_status": status
            }
        else:
            return {
                "status": "error",
                "message": f"Cannot transition to status: {status}"
            }

def run_jira_operations(args: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for JIRA operations"""
    jira = JiraMCP()
    action = args.get("action", "list_my_issues")
    
    if action == "list_my_issues":
        return {"issues": jira.get_my_issues(args.get("status"))}
    
    elif action == "sprint_overview":
        return {"sprint_issues": jira.get_sprint_issues()}
    
    elif action == "create_issue":
        return jira.create_issue(
            args.get("summary"),
            args.get("description"),
            args.get("type", "Task"),
            args.get("project")
        )
    
    elif action == "update_status":
        return jira.update_issue_status(
            args.get("issue_key"),
            args.get("new_status")
        )
    
    return {"error": "Unknown action"}