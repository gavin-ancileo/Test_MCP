import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import IntegrationStatus from '@/components/IntegrationStatus';
import HealthCheck from '@/components/HealthCheck';
import { useAuthStore } from '@/store/auth-store';
import { getAgentCoreConfig } from '@/lib/agentcore';
import { buildLogoutUrl } from '@/lib/auth-utils';
import { getCurrentUser, hasPermission, PERMISSIONS } from '@/lib/rbac';
import { LogOut, User, Settings, MessageSquare } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export default function Header() {
  const { user: authUser, isAuthenticated } = useAuthStore();
  const agentCoreConfig = getAgentCoreConfig();
  const location = useLocation();

  // Get current user with RBAC permissions
  const currentUser = getCurrentUser();
  const isAdmin = hasPermission(PERMISSIONS.ADMIN_PANEL_ACCESS);
  
  // Use RBAC user data if available, fallback to auth-store
  const user = currentUser || authUser;

  const handleLogout = async () => {
    // Clear all auth data
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('devv_authenticated');
    localStorage.removeItem('devv_user');
    localStorage.removeItem('DEVV_CODE_SID');
    
    // If on chat page, redirect to homepage, otherwise use Cognito logout
    if (location.pathname === '/chat') {
      window.location.href = '/';
    } else {
      const logoutUrl = await buildLogoutUrl();
      window.location.href = logoutUrl;
    }
  };

  const getEnvironmentBadge = () => {
    if (agentCoreConfig.isDemoMode) {
      return (
        <Badge variant="outline" className="text-xs font-medium bg-yellow-50 text-yellow-700 border-yellow-200">
          Demo
        </Badge>
      );
    }
    
    return (
      <Badge variant="outline" className="text-xs font-medium bg-green-50 text-green-700 border-green-200">
        Live
      </Badge>
    );
  };

  const getUserInitials = (email: string) => {
    return email
      .split('@')[0]
      .split('.')
      .map(part => part.charAt(0).toUpperCase())
      .slice(0, 2)
      .join('');
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/80 backdrop-blur-sm">
      <div className="flex h-16 items-center justify-between px-4 md:px-6">
        {/* Logo and Brand */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground font-bold text-sm">
              AAP
            </div>
            <span className="font-semibold text-lg text-foreground">AAP Enduser</span>
          </div>
          <HealthCheck />
          {getEnvironmentBadge()}

        </div>

        {/* User Menu */}
        <div className="flex items-center space-x-2">
          {isAuthenticated && user ? (
            <>
              {/* Integration Status (Desktop) */}
              <div className="hidden lg:flex items-center space-x-2">
                <IntegrationStatus provider="github" />
                <IntegrationStatus provider="jira" />
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                    <Avatar className="h-9 w-9">
                      <AvatarImage src="" alt={user.email} />
                      <AvatarFallback className="bg-primary/10 text-primary font-medium">
                        {getUserInitials(user.email)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-64" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {user.name || 'User'}
                      </p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  
                  {/* Mobile Integration Status */}
                  <div className="lg:hidden px-2 py-2">
                    <p className="text-xs font-medium text-muted-foreground mb-2">INTEGRATIONS</p>
                    <div className="space-y-2">
                      <IntegrationStatus provider="github" className="w-full justify-start" />
                      <IntegrationStatus provider="jira" className="w-full justify-start" />
                    </div>
                  </div>
                  <DropdownMenuSeparator className="lg:hidden" />
                  
                  <DropdownMenuItem asChild className="cursor-pointer">
                    <Link to="/chat">
                      <MessageSquare className="mr-2 h-4 w-4" />
                      <span>Chat</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild className="cursor-pointer">
                    <Link to="/settings">
                      <Settings className="mr-2 h-4 w-4" />
                      <span>Settings</span>
                    </Link>
                  </DropdownMenuItem>
                  {isAdmin && (
                    <DropdownMenuItem asChild className="cursor-pointer">
                      <Link to="/admin">
                        <User className="mr-2 h-4 w-4" />
                        <span>Admin Panel</span>
                      </Link>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    className="cursor-pointer text-red-600 focus:text-red-600"
                    onClick={handleLogout}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Sign out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">Not authenticated</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}