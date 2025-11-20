import { useEffect, useState } from 'react';
import { checkBackendHealth } from '@/lib/auth-utils';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CheckCircle, XCircle, Loader2, RefreshCw } from 'lucide-react';

interface HealthCheckProps {
  className?: string;
  showDetails?: boolean;
}

export default function HealthCheck({ className = '', showDetails = false }: HealthCheckProps) {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Get backend configuration
  const backendUrl = '/agentcore'; // Force use local
  const isConfigured = true; // Always configured

  const performHealthCheck = async () => {
    setIsChecking(true);
    setError(null);
    
    try {
      const result = await checkBackendHealth();
      setIsHealthy(result.healthy);
      setLastCheck(new Date());
      
      if (!result.healthy && result.error) {
        setError(result.error);
      }
    } catch (err) {
      setIsHealthy(false);
      setError(err instanceof Error ? err.message : 'Health check failed');
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    // Only perform health check if backend is configured
    if (isConfigured) {
      // Perform initial health check
      performHealthCheck();
      
      // Set up periodic health checks every 5 minutes
      const interval = setInterval(performHealthCheck, 5 * 60 * 1000);
      
      return () => clearInterval(interval);
    } 
    // else {
    //   // If not configured, set to demo mode immediately
    //   setIsHealthy(false);
    //   setError('No backend configured - running in demo mode');
    // }
  }, [isConfigured]);

  const getStatusBadge = () => {
    if (isChecking) {
      return (
        <Badge variant="secondary" className="gap-1">
          <Loader2 className="h-3 w-3 animate-spin" />
          Checking...
        </Badge>
      );
    }
    
    if (isHealthy === null) {
      return (
        <Badge variant="secondary" className="gap-1">
          <Loader2 className="h-3 w-3 animate-spin" />
          Initializing...
        </Badge>
      );
    }
    
    if (isHealthy) {
      return (
        <Badge variant="success" className="gap-1 bg-green-100 text-green-700 hover:bg-green-100">
          <CheckCircle className="h-3 w-3" />
          Connected
        </Badge>
      );
    }
    
    return (
      <Badge variant="success" className="gap-1 bg-green-100 text-green-700 hover:bg-green-100">
        <CheckCircle className="h-3 w-3" />
        Ready
      </Badge>
    );
  };

  if (!showDetails) {
    return <div className={className}>{getStatusBadge()}</div>;
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Backend Status:</span>
          {getStatusBadge()}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={performHealthCheck}
          disabled={isChecking}
          className="gap-1"
        >
          <RefreshCw className={`h-3 w-3 ${isChecking ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Always show endpoint configuration */}
      <div className="bg-muted/30 border rounded-lg p-3">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium">Backend Endpoint:</span>
        </div>
        {isConfigured ? (
          <div className="space-y-1">
            <code className="text-xs bg-muted px-2 py-1 rounded font-mono break-all block">
              {backendUrl}
            </code>
            <div className="text-xs text-muted-foreground">
              Health Check: <code>{backendUrl}/healthz</code>
            </div>
            <div className="text-xs text-muted-foreground">
              Chat API: <code>{backendUrl}/run</code>
            </div>
          </div>
        ) : (
          <div className="text-xs text-muted-foreground">
            ⚠️ No backend URL configured - running in demo mode
          </div>
        )}
      </div>
      
      {lastCheck && (
        <p className="text-xs text-muted-foreground">
          Last checked: {lastCheck.toLocaleTimeString()}
        </p>
      )}
      
      {error && (
        <Alert variant={isConfigured ? "destructive" : "default"}>
          <XCircle className="h-4 w-4" />
          <AlertDescription className="text-sm">
            {isConfigured ? (
              <>
                Backend connection failed: {error}
                <br />
                <span className="text-xs text-muted-foreground mt-1 block">
                  💡 If you just deployed your backend, please wait a moment and click refresh.
                  The app will use demo mode until connection is restored.
                </span>
              </>
            ) : (
              <>
                Running in demo mode: {error}
                <br />
                <span className="text-xs text-muted-foreground mt-1 block">
                  💡 To connect your backend, configure VITE_AGENTCORE_URL in environment settings.
                </span>
              </>
            )}
          </AlertDescription>
        </Alert>
      )}
      
      {isHealthy && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription className="text-sm">
            ✅ Backend API is connected and healthy!
            <br />
            <span className="text-xs text-muted-foreground mt-1 block">
              Chat messages will be sent to your backend server.
            </span>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}