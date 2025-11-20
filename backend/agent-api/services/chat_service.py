"""
Chat service
Handles chat orchestration and message saving
"""

import time
from typing import Dict
from datetime import datetime
from fastapi import HTTPException
from config import CONFIG
from services.openai_service import call_openai_with_tools

# DynamoDB for conversation history
try:
    import boto3
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    conversations_table = dynamodb.Table(CONFIG.get('DYNAMODB_TABLE', 'aap-conversations-prod'))
except Exception as e:
    print(f"WARNING: DynamoDB connection failed: {e}")
    conversations_table = None


async def process_chat(message: str, conversation_id: str, user: Dict) -> Dict:
    """Process chat message and return response"""
    try:
        print(f"[Mail] User: {user['email']} ({user['role']}) - user_id: {user.get('sub', 'unknown')}")
        print(f"[Msg] Message: {message}")
        print(f"[ID] Conversation: {conversation_id}")
        
        # Call OpenAI with tools
        response_result = await call_openai_with_tools(
            message, 
            conversation_id, 
            user
        )
        
        # Handle response result (can be string or dict with source/tools_used)
        if isinstance(response_result, dict):
            response_text = response_result.get('content', '')
            response_source = response_result.get('source', 'openai-tools')
            tools_used = response_result.get('tools_used', [])
            print(f"OK: OpenAI response received (source: {response_source}, tools: {tools_used})")
        else:
            response_text = response_result
            response_source = "openai-tools"
            tools_used = []
            print("OK: OpenAI response received (no tools used)")
        
        # Save to DynamoDB
        if conversations_table:
            try:
                response_data = conversations_table.get_item(
                    Key={'conversationId': conversation_id}
                )
                
                item = response_data.get('Item', {
                    'conversationId': conversation_id,
                    'userId': user['sub'],
                    'userEmail': user['email'],
                    'createdAt': int(time.time() * 1000),
                    'messages': []
                })
                
                if 'messages' not in item:
                    item['messages'] = []
                
                # Add user message
                item['messages'].append({
                    'role': 'user',
                    'content': message,
                    'timestamp': int(time.time() * 1000)
                })

                # Add assistant message with metadata
                item['messages'].append({
                    'role': 'assistant',
                    'content': response_text,
                    'timestamp': int(time.time() * 1000),
                    'source': response_source,      # "mcp-tool" or "openai-tools"
                    'tools_used': tools_used        # List of tool names called
                })
                
                item['updatedAt'] = int(time.time() * 1000)
                item['messageCount'] = len(item['messages'])
                
                conversations_table.put_item(Item=item)
                print(f"OK: Saved to DynamoDB ({len(item['messages'])} messages)")
            except Exception as e:
                print(f"WARNING: DynamoDB save failed: {e}")
        
        return {
            "message": response_text,
            "conversationId": conversation_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": response_source
        }
        
    except Exception as e:
        print(f"[ERROR] Chat service error")
        print(f"[ERROR] Error type: {type(e).__name__}")
        print(f"[ERROR] Error message: {str(e)}")
        print(f"[ERROR] User: {user.get('email', 'unknown')}")
        print(f"[ERROR] Conversation ID: {conversation_id}")
        print(f"[ERROR] Message: {message[:100]}...")
        import traceback
        traceback.print_exc()

        # Create user-friendly error message with technical details
        error_type = type(e).__name__
        error_msg = str(e)

        # Different error messages for different scenarios
        if "OpenAI" in error_msg or "openai" in error_msg.lower():
            detail = f"OpenAI API error: {error_msg}. Please try again in a moment."
        elif "DynamoDB" in error_msg or "dynamodb" in error_msg.lower():
            detail = f"Database error: {error_msg}. Your message was processed but may not have been saved."
        elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            detail = f"Request timeout: The operation took too long to complete. Please try a simpler query or try again."
        elif "validation" in error_msg.lower() or "invalid" in error_msg.lower():
            detail = f"Validation error: {error_msg}. Please check your input and try again."
        else:
            detail = f"{error_type}: {error_msg}"

        raise HTTPException(status_code=500, detail=detail)

