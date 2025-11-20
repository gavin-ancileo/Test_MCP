import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { useConversationStore } from '@/store/conversation-store-enhanced';
import { formatDistanceToNow } from 'date-fns';
import { MessageSquare, Plus, Trash2, Home } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useNavigate } from 'react-router-dom';

export default function ConversationSidebar() {
  const navigate = useNavigate();
  const {
    conversations,
    activeConversationId,
    createConversation,
    setActiveConversation,
    deleteConversation,
  } = useConversationStore();

  const handleNewConversation = async () => {
    const newId = await createConversation();
    setActiveConversation(newId);
  };

  const handleDeleteConversation = (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation();
    deleteConversation(conversationId);
  };

  return (
    <div className="flex h-full flex-col border-r bg-muted/30">
      {/* Header with Back Button */}
      <div className="p-4 border-b space-y-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/dashboard')}
          className="w-full justify-start -mx-1"
        >
          <Home className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        
        <Separator />
        
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">
            Conversations
          </h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleNewConversation}
            className="h-8 w-8 p-0 hover:bg-primary/10"
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Conversations List */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <MessageSquare className="h-8 w-8 text-muted-foreground/50 mb-2" />
              <p className="text-sm text-muted-foreground">No conversations yet</p>
              <p className="text-xs text-muted-foreground/80 mt-1">
                Click + to start a new chat
              </p>
            </div>
          ) : (
            // Sort conversations by updatedAt in descending order (newest first)
            [...conversations]
              .sort((a, b) => {
                const aTime = typeof a.updatedAt === 'number' ? a.updatedAt : new Date(a.updatedAt).getTime();
                const bTime = typeof b.updatedAt === 'number' ? b.updatedAt : new Date(b.updatedAt).getTime();
                return bTime - aTime; // Descending order
              })
              .map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => setActiveConversation(conversation.id)}
                className={cn(
                  'group relative flex items-center justify-between rounded-lg px-3 py-2 cursor-pointer transition-colors hover:bg-accent',
                  activeConversationId === conversation.id && 'bg-accent border border-border/50'
                )}
              >
                <div className="flex-1 min-w-0 pr-2">
                  <p className="text-sm font-medium truncate">
                    {conversation.title}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {conversation.messages.length > 0 
                      ? `${conversation.messages.length} message${conversation.messages.length === 1 ? '' : 's'}`
                      : 'New conversation'
                    }
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(conversation.updatedAt), { addSuffix: true })}
                  </p>
                </div>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => handleDeleteConversation(e, conversation.id)}
                  className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive transition-opacity"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 border-t">
        <Button
          variant="outline"
          size="sm"
          onClick={handleNewConversation}
          className="w-full justify-start"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Conversation
        </Button>
      </div>
    </div>
  );
}