"""
Sessions service
Handles chat session management
"""

import uuid
import time
from typing import Dict, List
from fastapi import HTTPException
from config import CONFIG

# DynamoDB for conversation history
try:
    import boto3
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    conversations_table = dynamodb.Table(CONFIG.get('DYNAMODB_TABLE', 'aap-conversations-prod'))
except Exception as e:
    print(f"WARNING: DynamoDB connection failed: {e}")
    conversations_table = None


async def create_session(title: str, user: Dict) -> Dict:
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        user_id = user.get('sub')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        
        if conversations_table:
            now = int(time.time() * 1000)
            conversations_table.put_item(Item={
                'conversationId': session_id,
                'userId': user_id,
                'userEmail': user.get('email', ''),
                'title': title,
                'createdAt': now,
                'updatedAt': now,
                'messageCount': 0,
                'messages': []
            })
            return {
                'session_id': session_id,
                'title': title,
                'created_at': now,
                'updated_at': now,
                'message_count': 0
            }
        
        # Fallback
        now = int(time.time() * 1000)
        return {
            'session_id': session_id,
            'title': title,
            'created_at': now,
            'updated_at': now,
            'message_count': 0
        }
    except Exception as e:
        print(f"ERROR: Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def list_sessions(user: Dict) -> Dict:
    """List all sessions for current user"""
    try:
        user_id = user.get('sub')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        
        if conversations_table:
            # Scan for user's conversations
            response = conversations_table.scan(
                FilterExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id},
                Limit=50
            )
            sessions = []
            for item in response.get('Items', []):
                sessions.append({
                    'session_id': item.get('conversationId'),
                    'title': item.get('title', 'New Chat'),
                    'created_at': item.get('createdAt', 0),
                    'updated_at': item.get('updatedAt', 0),
                    'message_count': item.get('messageCount', 0)
                })
            return {"sessions": sessions, "count": len(sessions)}
        
        return {"sessions": [], "count": 0}
    except Exception as e:
        print(f"ERROR: Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_session_messages(session_id: str, user: Dict) -> Dict:
    """Get messages for a session"""
    try:
        user_id = user.get('sub')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")

        if conversations_table:
            response = conversations_table.get_item(Key={'conversationId': session_id})
            if 'Item' in response:
                item = response['Item']
                if item.get('userId') != user_id:
                    raise HTTPException(status_code=403, detail="Access denied")

                messages = item.get('messages', [])
                return {
                    "session_id": session_id,
                    "messages": messages,
                    "count": len(messages)
                }

        return {"session_id": session_id, "messages": [], "count": 0}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error getting session messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def update_session_title(session_id: str, title: str, user: Dict) -> Dict:
    """Update session title"""
    try:
        user_id = user.get('sub')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")

        if conversations_table:
            # First verify user owns this session
            response = conversations_table.get_item(Key={'conversationId': session_id})
            if 'Item' not in response:
                raise HTTPException(status_code=404, detail="Session not found")

            item = response['Item']
            if item.get('userId') != user_id:
                raise HTTPException(status_code=403, detail="Access denied")

            # Update title
            now = int(time.time() * 1000)
            conversations_table.update_item(
                Key={'conversationId': session_id},
                UpdateExpression='SET title = :title, updatedAt = :updated',
                ExpressionAttributeValues={
                    ':title': title,
                    ':updated': now
                }
            )

            return {
                "session_id": session_id,
                "title": title,
                "updated_at": now
            }

        raise HTTPException(status_code=503, detail="Database not available")
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error updating session title: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def delete_session(session_id: str, user: Dict) -> Dict:
    """Delete a session"""
    try:
        user_id = user.get('sub')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")

        if conversations_table:
            # First verify user owns this session
            response = conversations_table.get_item(Key={'conversationId': session_id})
            if 'Item' not in response:
                raise HTTPException(status_code=404, detail="Session not found")

            item = response['Item']
            if item.get('userId') != user_id:
                raise HTTPException(status_code=403, detail="Access denied")

            # Delete session
            conversations_table.delete_item(Key={'conversationId': session_id})

            return {"session_id": session_id, "deleted": True}

        raise HTTPException(status_code=503, detail="Database not available")
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

