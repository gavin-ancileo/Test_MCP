import { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { ArrowRight, MessageSquare, Shield, Zap } from 'lucide-react';

export default function LandingPage() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [isRedirecting, setIsRedirecting] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    // Check for both Devv authentication and Cognito authentication
    const devvAuth = localStorage.getItem('devv_authenticated');
    const devvSid = localStorage.getItem('DEVV_CODE_SID');
    const cognitoToken = localStorage.getItem('access_token');
    
    setIsAuthenticated(!!(devvAuth === 'true' || devvSid || cognitoToken));
  }, []);

  // Redirect if already authenticated
  if (isAuthenticated === true) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleLogin = () => {
    try {
      setIsRedirecting(true);
      window.location.href = '/login';
    } catch (error) {
      console.error('Login error:', error);
      toast({
        title: 'Authentication Error',
        description: 'Failed to navigate to login. Please try again.',
        variant: 'destructive',
      });
      setIsRedirecting(false);
    }
  };

  const features = [
    {
      icon: MessageSquare,
      title: 'Intelligent Conversations',
      description: 'Engage with advanced AI agents for natural, context-aware interactions.',
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Built with enterprise-grade security and compliance standards.',
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Optimized for speed and performance with real-time responses.',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/30">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="text-center">
            <div className="mx-auto mb-8 flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <MessageSquare className="h-8 w-8" />
            </div>
            
            <h1 className="mx-auto max-w-4xl font-bold tracking-tight text-4xl sm:text-5xl lg:text-6xl">
              Welcome to{' '}
              <span className="bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
                AAP Enduser
              </span>
            </h1>
            
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
              Experience the next generation of AI-powered conversations. Connect with intelligent agents 
              that understand your needs and provide meaningful insights.
            </p>

            <div className="mt-10 flex items-center justify-center">
              <Button 
                size="lg" 
                onClick={handleLogin}
                disabled={isRedirecting}
                className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-3 text-base font-medium"
              >
                {isRedirecting ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Redirecting...
                  </>
                ) : (
                  <>
                    Login with Company SSO
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>

            <p className="mt-6 text-sm text-muted-foreground">
              Secure authentication via AWS Cognito
            </p>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Powerful Features
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">
            Built for modern enterprises with cutting-edge AI capabilities
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="relative overflow-hidden border-0 bg-white/50 backdrop-blur-sm">
                <CardHeader>
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* CTA Section */}
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <Card className="border-0 bg-primary text-primary-foreground">
          <CardContent className="px-6 py-12 text-center sm:px-12">
            <h3 className="text-2xl font-bold tracking-tight sm:text-3xl">
              Ready to get started?
            </h3>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-primary-foreground/80">
              Join thousands of users who are already experiencing the future of AI conversations.
            </p>
            <Button
              size="lg"
              variant="secondary"
              onClick={handleLogin}
              disabled={isRedirecting}
              className="mt-8 bg-white text-primary hover:bg-white/90"
            >
              {isRedirecting ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  Redirecting...
                </>
              ) : (
                <>
                  Get Started Now
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}