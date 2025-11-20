import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import HealthCheck from '@/components/HealthCheck';
import IntegrationStatus from '@/components/IntegrationStatus';
import { useIntegrationStore } from '@/store/integration-store';
import { Badge } from '@/components/ui/badge';
import { Server, Globe, Shield, Cpu, Settings, ArrowLeft } from 'lucide-react';
import { getCurrentUser, hasPermission, PERMISSIONS } from '@/lib/rbac';
import { useNavigate } from 'react-router-dom';

export default function SettingsPage() {
  const navigate = useNavigate();
  const user = getCurrentUser();
  const { connections } = useIntegrationStore();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm font-medium">Back to Dashboard</span>
              </button>
              <div className="w-px h-6 bg-gray-300" />
              <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Settings
              </h1>
            </div>
            <div className="flex items-center gap-4">
              {user && (
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">{user.name}</div>
                  <div className="text-xs text-gray-500">{user.role} • {user.authMethod}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="container max-w-4xl mx-auto py-8 space-y-8">
        <div className="space-y-2">
          <p className="text-muted-foreground">
            {hasPermission(PERMISSIONS.ADMIN_PANEL_ACCESS) 
              ? "Manage integrations and view system configuration" 
              : "Manage your integrations and user settings"
            }
          </p>
        </div>

      {/* System Status - Admin Only */}
      {hasPermission(PERMISSIONS.ADMIN_PANEL_ACCESS) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              System Status
            </CardTitle>
            <CardDescription>
              Current status of backend services and integrations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium mb-2">Backend API</h4>
                <HealthCheck showDetails />
              </div>
              
              <Separator />
              
              <div>
                <h4 className="text-sm font-medium mb-2">Environment Configuration</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">API Base URL:</span>
                      <Badge variant="outline" className="text-xs font-mono">
                        {import.meta.env.VITE_API_BASE_URL || 'Not configured'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Cognito Domain:</span>
                      <Badge variant="outline" className="text-xs font-mono">
                        {import.meta.env.VITE_COGNITO_DOMAIN?.split('//')[1] || 'Not configured'}
                      </Badge>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Environment:</span>
                      <Badge variant="secondary">
                        {import.meta.env.VITE_ENVIRONMENT || 'Development'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Build Mode:</span>
                      <Badge variant="secondary">
                        {import.meta.env.MODE}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Integrations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Integrations
          </CardTitle>
          <CardDescription>
            Manage your connected services and OAuth permissions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="text-sm font-medium">GitHub Integration</h4>
              <IntegrationStatus provider="github" />
              <p className="text-xs text-muted-foreground">
                Access to repositories, pull requests, and commit history
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Jira Integration</h4>
              <IntegrationStatus provider="jira" />
              <p className="text-xs text-muted-foreground">
                Access to assigned issues, project details, and user profile
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Google Drive Integration</h4>
              <IntegrationStatus provider="drive" />
              <p className="text-xs text-muted-foreground">
                Access to document upload, folder management, and file access
              </p>
            </div>
          </div>
          
          <Separator />
          
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Integration Scopes</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-muted-foreground">
              <div>
                <p className="font-medium text-foreground mb-1">GitHub Scopes:</p>
                <ul className="space-y-1">
                  <li>• read:user - Access to user profile</li>
                  <li>• repo:read - Read repository content</li>
                  <li>• read:org - Organization membership</li>
                  <li>• read:project - Project board access</li>
                </ul>
              </div>
              <div>
                <p className="font-medium text-foreground mb-1">Jira Scopes:</p>
                <ul className="space-y-1">
                  <li>• read:jira-user - User profile access</li>
                  <li>• read:jira-work - Issue and project access</li>
                  <li>• read:me - Basic profile information</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* User Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            User Information
          </CardTitle>
          <CardDescription>
            Your authenticated user details and session info
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Email:</span>
                  <span className="text-sm font-medium">{user?.email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Name:</span>
                  <span className="text-sm font-medium">{user?.name || 'Not provided'}</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Session:</span>
                  <Badge variant="outline" className="text-xs">
                    Active
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Token Storage:</span>
                  <Badge variant="outline" className="text-xs">
                    Memory Only
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Role:</span>
                  <Badge variant="outline" className="text-xs">
                    {hasPermission(PERMISSIONS.ADMIN_PANEL_ACCESS) ? 'Administrator' : 'End User'}
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* System Information - Admin Only */}
      {hasPermission(PERMISSIONS.ADMIN_PANEL_ACCESS) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-5 w-5" />
              System Information
            </CardTitle>
            <CardDescription>
              Technical details about the application
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Application:</span>
                  <span className="font-mono">AAP Enduser v1.0.0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Framework:</span>
                  <span className="font-mono">React + TypeScript</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">UI Library:</span>
                  <span className="font-mono">Tailwind + shadcn/ui</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Build Tool:</span>
                  <span className="font-mono">Vite</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Authentication:</span>
                  <span className="font-mono">Dual (Cognito + Devv)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Deployment:</span>
                  <span className="font-mono">Devv.ai Preview</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      </div>
    </div>
  );
}