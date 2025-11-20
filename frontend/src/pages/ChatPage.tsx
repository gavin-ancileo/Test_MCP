import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Header from '@/components/Header';
import ConversationSidebar from '@/components/ConversationSidebar';
import MessageList from '@/components/MessageList';
import MessageInput from '@/components/MessageInput';
import QuickActionsPanel from '@/components/QuickActionsPanel';
import { useConversationStore } from '@/store/conversation-store-enhanced';
import { useIsMobile } from '@/hooks/use-mobile';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog';
import { Menu } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAuthStore } from '@/store/auth-store';
import { useIntegrationStore } from '@/store/integration-store';

export default function ChatPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const {
    activeConversationId,
    createConversation,
    setActiveConversation,
    addMessage,
    getActiveConversation,
    syncConversations,
    conversations
  } = useConversationStore();
  const { idToken, user, fetchUserInfo, userRoles } = useAuthStore();
  const { fetchAllIntegrations, setConnecting } = useIntegrationStore();
  const isMobile = useIsMobile();
  const [inputValue, setInputValue] = useState('');

  // Fetch user roles on mount if user is logged in
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData && userRoles.length === 0) {
      try {
        const parsed = JSON.parse(userData);
        if (parsed.email) {
          fetchUserInfo(parsed.email, parsed.name);
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }
  }, []);

  // Load conversations from DynamoDB on mount
  useEffect(() => {
    if (user && conversations.length === 0) {
      syncConversations().catch(err => {
        console.error('Failed to sync conversations from DynamoDB:', err);
      });
    }
  }, [user, conversations.length, syncConversations]);

  // Handle OAuth redirect callback
  useEffect(() => {
    const integration = searchParams.get('integration');
    const status = searchParams.get('status');

    if (integration && status === 'success') {
      // Clear connecting state
      localStorage.removeItem('oauth_connecting_provider');
      setConnecting(undefined);

      // Fetch updated integrations
      fetchAllIntegrations();

      // Show success toast
      toast({
        title: 'Integration Connected',
        description: `Successfully connected to ${integration}`,
      });

      // Clean up URL
      searchParams.delete('integration');
      searchParams.delete('status');
      setSearchParams(searchParams);
    } else if (integration && status === 'error') {
      // OAuth failed or cancelled
      localStorage.removeItem('oauth_connecting_provider');
      setConnecting(undefined);

      // Show error toast
      toast({
        title: 'Integration Failed',
        description: `Failed to connect to ${integration}`,
        variant: 'destructive',
      });

      // Clean up URL
      searchParams.delete('integration');
      searchParams.delete('status');
      setSearchParams(searchParams);
    } else {
      // User navigated back without completing OAuth - clear spinner
      const connectingProvider = localStorage.getItem('oauth_connecting_provider');
      if (connectingProvider && !integration) {
        localStorage.removeItem('oauth_connecting_provider');
        setConnecting(undefined);
      }
    }
  }, [searchParams, setSearchParams, toast, fetchAllIntegrations, setConnecting]);

  const handleStartNewChat = async () => {
    const newId = await createConversation();
    setActiveConversation(newId);
  };

  const handlePromptSelect = (prompt: any, variables: Record<string, string>) => {
    // Replace variables in prompt content
    let message = prompt.content;
    Object.entries(variables).forEach(([key, value]) => {
      message = message.replace(new RegExp(`{{${key}}}`, 'g'), value);
    });
    setInputValue(message);
    toast({
      title: "Prompt Template Applied",
      description: `Using: ${prompt.name}`,
    });
  };

  const SidebarContent = () => <ConversationSidebar />;

  return (
    <div className="flex h-screen flex-col bg-background">
      <Header />
      
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop Sidebar */}
        {!isMobile && (
          <div className="w-80 shrink-0">
            <SidebarContent />
          </div>
        )}

        {/* Mobile Sidebar */}
        {isMobile && (
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="ghost" size="sm" className="fixed top-4 left-4 z-50 md:hidden">
                <Menu className="h-5 w-5" />
              </Button>
            </DialogTrigger>
            <DialogContent className="w-80 p-0 h-full max-w-none">
              <SidebarContent />
            </DialogContent>
          </Dialog>
        )}

        {/* Main Chat Area */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {activeConversationId ? (
            <>
              <MessageList />
              <MessageInput 
                value={inputValue}
                onChange={setInputValue}
              />
            </>
          ) : (
            <div className="flex flex-1 items-center justify-center">
              <div className="text-center space-y-6 max-w-md px-4">
                <div className="space-y-2">
                  <h2 className="text-2xl font-semibold">Welcome to AAP Enduser</h2>
                  <p className="text-muted-foreground">
                    Start a conversation with our AI assistant. Connect your GitHub, Jira, and Google Drive accounts 
                    for enhanced productivity features and intelligent integrations.
                  </p>
                  {user?.email && (
                    <p className="text-sm text-primary font-medium">
                      Signed in as {user.email}
                    </p>
                  )}
                </div>
                
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Button onClick={handleStartNewChat} size="lg" className="w-full sm:w-auto">
                    Start New Conversation
                  </Button>
                  <Button onClick={() => navigate('/dashboard')} variant="outline" size="lg" className="w-full sm:w-auto">
                    Back to Dashboard
                  </Button>
                </div>
                
                <div className="text-sm text-muted-foreground space-y-2">
                  <p><strong>Try asking about:</strong></p>
                  <ul className="text-xs space-y-1 text-left max-w-xs mx-auto">
                    <li>💼 "Show my Jira tickets"</li>
                    <li>🔀 "My open pull requests"</li>
                    <li>📊 "What changed in owner/repo this week?"</li>
                    <li>❓ General questions and assistance</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Sidebar - Quick Actions (Desktop only) */}
        {!isMobile && (
          <div className="w-80 border-l border-border bg-muted/30 p-4 overflow-y-auto">
            <QuickActionsPanel onPromptSelect={handlePromptSelect} />
          </div>
        )}
      </div>
    </div>
  );
}