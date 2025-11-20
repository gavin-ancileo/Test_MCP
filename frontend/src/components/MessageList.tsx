import { useEffect, useRef } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { useConversationStore, type Message } from '@/store/conversation-store-enhanced';
import { useAuthStore } from '@/store/auth-store';
import { formatDistanceToNow } from 'date-fns';
import { Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MessageBubbleProps {
  message: Message;
  userEmail?: string;
}

function MessageBubble({ message, userEmail }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const initials = userEmail ? userEmail.charAt(0).toUpperCase() : 'U';

  return (
    <div className={cn('flex gap-3 mb-4', isUser && 'flex-row-reverse')}>
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className={cn(
          'text-xs font-medium',
          isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'
        )}>
          {isUser ? initials : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>
      
      <div className={cn('flex flex-col space-y-1 max-w-[80%]', isUser && 'items-end')}>
        <div className={cn(
          'rounded-lg px-3 py-2 text-sm break-words',
          isUser 
            ? 'bg-primary text-primary-foreground' 
            : 'bg-muted text-muted-foreground'
        )}>
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
        <span className="text-xs text-muted-foreground/70">
          {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
        </span>
      </div>
    </div>
  );
}

export default function MessageList() {
  const { getActiveConversation } = useConversationStore();
  const { user } = useAuthStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const activeConversation = getActiveConversation();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeConversation?.messages]);

  if (!activeConversation) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center space-y-2">
          <div className="mx-auto h-12 w-12 rounded-full bg-muted flex items-center justify-center">
            <Bot className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium">No conversation selected</h3>
          <p className="text-sm text-muted-foreground max-w-sm">
            Select an existing conversation or start a new one to begin chatting with the AI assistant.
          </p>
        </div>
      </div>
    );
  }

  if (activeConversation.messages.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center space-y-2">
          <div className="mx-auto h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Bot className="h-6 w-6 text-primary" />
          </div>
          <h3 className="text-lg font-medium">Start a conversation</h3>
          <p className="text-sm text-muted-foreground max-w-sm">
            Send a message below to begin your conversation with the AI assistant.
          </p>
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1 px-4">
      <div className="py-4">
        {activeConversation.messages.map((message) => (
          <MessageBubble 
            key={message.id} 
            message={message} 
            userEmail={user?.email}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </ScrollArea>
  );
}