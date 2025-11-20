import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useConversationStore } from '@/store/conversation-store-enhanced';
import { useAuthStore } from '@/store/auth-store';
import { callAgentCore } from '@/lib/agentcore';
import { useToast } from '@/hooks/use-toast';
import { Send, Loader2 } from 'lucide-react';
import PromptSelector from './PromptSelector';

interface MessageInputProps {
  value?: string;
  onChange?: (value: string) => void;
}

export default function MessageInput({ value, onChange }: MessageInputProps) {
  const [internalMessage, setInternalMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const {
    activeConversationId,
    getActiveConversation,
    addMessage,
    createConversation,
    setActiveConversation,
    loadConversationMessages,
    updateConversationTitle
  } = useConversationStore();
  const { idToken } = useAuthStore();
  const { toast } = useToast();

  // Support controlled and uncontrolled usage
  const currentMessage = value !== undefined ? value : internalMessage;
  const setCurrentMessage = (newValue: string) => {
    if (value !== undefined && onChange) {
      onChange(newValue);
    } else {
      setInternalMessage(newValue);
    }
  };

  // Clear internal state when external value changes
  useEffect(() => {
    if (value !== undefined && value !== internalMessage) {
      setInternalMessage(value);
    }
  }, [value]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!currentMessage.trim() || isLoading) {
      return;
    }
  
    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    setIsLoading(true);
  
    try {
      // Check authentication
      if (!idToken) {
        toast({
          title: "Authentication Required",
          description: "Please login first to send messages.",
          variant: "destructive",
        });
        setIsLoading(false);
        return;
      }

      // 1. Create conversation FIRST if needed (BEFORE API call)
      let conversationId = activeConversationId;
      const isNewConversation = !conversationId;
      if (!conversationId) {
        conversationId = await createConversation(userMessage);
        setActiveConversation(conversationId);
      }

      // 2. Add user message to UI immediately (optimistic update)
      await addMessage(conversationId, {
        content: userMessage,
        role: 'user',
      });

      // 3. Call API with correct conversation ID (with 60s timeout)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

      let response;
      try {
        response = await fetch('/agentcore/run', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${idToken}`
          },
          body: JSON.stringify({
            message: userMessage,
            conversationId: conversationId  // Use the actual conversation ID
          }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);
      } catch (fetchError: any) {
        clearTimeout(timeoutId);
        if (fetchError.name === 'AbortError') {
          throw new Error('Request timeout - The server took too long to respond (>60s). Please try again.');
        }
        throw fetchError;
      }

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // 4. Add assistant response to UI
      await addMessage(conversationId, {
        content: data.message,
        role: 'assistant',
      });

      // 5. Reload messages from backend to ensure sync
      await loadConversationMessages(conversationId);

      // 6. Update conversation title if this is the first message
      if (isNewConversation) {
        const title = userMessage.slice(0, 50) + (userMessage.length > 50 ? '...' : '');
        await updateConversationTitle(conversationId, title);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handlePromptSelect = (prompt: any, variables: Record<string, string>) => {
    // Replace variables in prompt content
    let content = prompt.content;
    Object.entries(variables).forEach(([key, value]) => {
      content = content.replace(new RegExp(`{{${key}}}`, 'g'), value);
    });
    
    setCurrentMessage(content);
  };

  return (
    <div className="border-t bg-background p-4">
      {/* Prompt Selector removed - use sidebar search instead */}

      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <Textarea
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message or use a prompt template... (Press Enter to send, Shift+Enter for new line)"
            disabled={isLoading}
            className="min-h-[60px] resize-none pr-12"
            rows={2}
          />
        </div>
        
        <Button
          type="submit"
          size="sm"
          disabled={!currentMessage.trim() || isLoading}
          className="h-[60px] px-3"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </form>
      
      <div className="mt-2 text-xs text-muted-foreground text-center">
        {isLoading ? (
          <span className="flex items-center justify-center gap-1">
            <Loader2 className="h-3 w-3 animate-spin" />
            Processing your message...
          </span>
        ) : (
          <span className="flex items-center justify-center gap-1">
            ✨ Ready to chat with AI assistance
          </span>
        )}
      </div>
    </div>
  );
}