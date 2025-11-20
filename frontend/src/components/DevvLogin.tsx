import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { auth } from '@devvai/devv-code-backend';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, ArrowRight } from 'lucide-react';

export default function DevvLogin() {
  const [step, setStep] = useState<'email' | 'otp'>('email');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      toast({
        title: 'Error',
        description: 'Please enter your email address',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    
    try {
      await auth.sendOTP(email);
      
      toast({
        title: 'Code Sent!',
        description: 'Please check your email for the verification code.',
      });
      
      setStep('otp');
    } catch (error) {
      console.error('Send OTP error:', error);
      toast({
        title: 'Failed to Send Code',
        description: error instanceof Error ? error.message : 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!otp) {
      toast({
        title: 'Error',
        description: 'Please enter the verification code',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await auth.verifyOTP(email, otp);
      
      // Store user info in localStorage for compatibility
      localStorage.setItem('devv_user', JSON.stringify(response.user));
      localStorage.setItem('devv_authenticated', 'true');
      
      toast({
        title: 'Login Successful!',
        description: `Welcome back, ${response.user.name || response.user.email}!`,
      });
      
      // Redirect to dashboard
      navigate('/dashboard');
      
    } catch (error) {
      console.error('Verify OTP error:', error);
      toast({
        title: 'Invalid Code',
        description: error instanceof Error ? error.message : 'Please check your code and try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToEmail = () => {
    setStep('email');
    setOtp('');
  };

  const handleResendCode = async () => {
    setIsLoading(true);
    try {
      await auth.sendOTP(email);
      toast({
        title: 'Code Resent!',
        description: 'A new verification code has been sent to your email.',
      });
    } catch (error) {
      toast({
        title: 'Failed to Resend',
        description: 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center pb-2">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground">
            {step === 'email' ? <Mail className="h-8 w-8" /> : <Lock className="h-8 w-8" />}
          </div>
          
          <CardTitle className="text-2xl font-bold">
            {step === 'email' ? 'Welcome to AAP' : 'Verify Your Email'}
          </CardTitle>
          
          <CardDescription>
            {step === 'email' 
              ? 'Enter your email to receive a verification code' 
              : `We sent a code to ${email}`
            }
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {step === 'email' ? (
            <form onSubmit={handleSendOTP} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  required
                  className="text-base"
                />
              </div>
              
              <Button 
                type="submit" 
                className="w-full" 
                size="lg"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Sending Code...
                  </>
                ) : (
                  <>
                    Send Verification Code
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOTP} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="otp">Verification Code</Label>
                <Input
                  id="otp"
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  disabled={isLoading}
                  required
                  className="text-base text-center tracking-widest font-mono"
                  maxLength={6}
                />
              </div>
              
              <Button 
                type="submit" 
                className="w-full" 
                size="lg"
                disabled={isLoading || otp.length !== 6}
              >
                {isLoading ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Verifying...
                  </>
                ) : (
                  'Verify & Login'
                )}
              </Button>
              
              <div className="flex flex-col space-y-2 text-sm">
                <button
                  type="button"
                  onClick={handleResendCode}
                  disabled={isLoading}
                  className="text-primary hover:underline"
                >
                  Resend code
                </button>
                
                <button
                  type="button"
                  onClick={handleBackToEmail}
                  disabled={isLoading}
                  className="text-muted-foreground hover:underline"
                >
                  ← Change email address
                </button>
              </div>
            </form>
          )}
          
          <div className="pt-4 text-center text-xs text-muted-foreground border-t">
            Secure authentication powered by Devv.ai
          </div>
        </CardContent>
      </Card>
    </div>
  );
}