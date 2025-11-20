import React from 'react';
import { Github, ExternalLink, Settings, CheckCircle, XCircle, Loader2, HardDrive } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { useIntegrationStore } from '@/store/integration-store';
import { useToast } from '@/hooks/use-toast';

interface IntegrationStatusProps {
  provider: 'github' | 'jira' | 'drive';
  className?: string;
}

const providerConfig = {
  github: {
    name: 'GitHub',
    icon: Github,
    color: 'bg-gray-900 text-white',
    scopes: ['read:user', 'repo:read', 'read:org', 'read:project'],
  },
  jira: {
    name: 'Jira',
    icon: ExternalLink,
    color: 'bg-blue-600 text-white',
    scopes: ['read:jira-user', 'read:jira-work', 'read:me'],
  },
  drive: {
    name: 'Google Drive',
    icon: HardDrive,
    color: 'bg-gradient-to-r from-blue-500 via-red-500 via-yellow-500 to-green-500 text-white',
    scopes: ['drive.file', 'drive.readonly'],
  },
};

export default function IntegrationStatus({ provider, className = '' }: IntegrationStatusProps) {
  const { toast } = useToast();
  const {
    getConnection,
    isConnected,
    isConnecting,
    connectingProvider,
    connectProvider,
    disconnectProvider,
  } = useIntegrationStore();

  const connection = getConnection(provider);
  const connected = isConnected(provider);
  const connecting = isConnecting && connectingProvider === provider;
  const config = providerConfig[provider];
  const Icon = config.icon;

  const handleConnect = async () => {
    try {
      // Don't show success toast here - OAuth will redirect and show toast after callback
      await connectProvider(provider);
    } catch (error) {
      // Only show error toast if OAuth redirect fails
      toast({
        title: 'Connection Failed',
        description: (error as Error).message,
        variant: 'destructive',
      });
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnectProvider(provider);
      toast({
        title: 'Integration Disconnected',
        description: `Disconnected from ${config.name}`,
      });
    } catch (error) {
      toast({
        title: 'Disconnect Failed',
        description: (error as Error).message,
        variant: 'destructive',
      });
    }
  };

  if (!connected) {
    return (
      <Button
        onClick={handleConnect}
        disabled={connecting}
        variant="outline"
        size="sm"
        className={className}
      >
        {connecting ? (
          <Loader2 className="h-4 w-4 animate-spin mr-2" />
        ) : (
          <Icon className="h-4 w-4 mr-2" />
        )}
        Connect {config.name}
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="default"
          size="sm"
          className={`${className} ${config.color} font-semibold shadow-sm`}
          title={connection?.username ? `Connected as: ${connection.username}` : 'Connected'}
        >
          <Icon className="h-4 w-4 mr-2" />
          <span className="hidden sm:inline">{connection?.username || config.name}</span>
          <CheckCircle className="h-3 w-3 ml-2" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64">
        <div className="px-3 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Icon className="h-4 w-4 mr-2" />
              <span className="font-medium">{config.name}</span>
            </div>
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              Connected
            </Badge>
          </div>
          {connection?.username && (
            <p className="text-sm text-muted-foreground mt-1">
              {connection.username}
            </p>
          )}
          {connection?.connectedAt && (
            <p className="text-xs text-muted-foreground">
              Connected {new Date(connection.connectedAt).toLocaleDateString()}
            </p>
          )}
        </div>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={handleDisconnect} className="text-red-600">
          <XCircle className="h-4 w-4 mr-2" />
          Disconnect
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
