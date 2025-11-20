import React, { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Sparkles } from 'lucide-react';
import IntegrationStatus from './IntegrationStatus';
import PromptSelector from './PromptSelector';
import { useIntegrationStore } from '@/store/integration-store';

interface Prompt {
  code: string;
  name: string;
  categories: string[];
  content: string;
  variables?: string[];
  output_folder?: string;
}

interface QuickActionsPanelProps {
  onPromptSelect?: (prompt: Prompt, variables: Record<string, string>) => void;
}

export default function QuickActionsPanel({ onPromptSelect }: QuickActionsPanelProps) {
  const { fetchAllIntegrations } = useIntegrationStore();

  // Fetch integrations status on mount
  useEffect(() => {
    fetchAllIntegrations();
  }, [fetchAllIntegrations]);

  return (
    <div className="space-y-4">
      {/* Integration Status */}
      <Card className="w-full">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Integrations</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-col space-y-2">
            <IntegrationStatus provider="github" className="w-full justify-start" />
            <IntegrationStatus provider="jira" className="w-full justify-start" />
            <IntegrationStatus provider="drive" className="w-full justify-start" />
          </div>
        </CardContent>
      </Card>

      {/* Prompt Templates Section */}
      <Card className="w-full">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center text-lg">
            <Sparkles className="h-5 w-5 mr-2" />
            Prompt Templates
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Use pre-built templates to quickly generate documents, analyze data, or automate tasks.
          </p>
          <PromptSelector onPromptSelect={onPromptSelect} variant="panel" />
        </CardContent>
      </Card>
    </div>
  );
}
