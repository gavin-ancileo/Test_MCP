import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '@/store/auth-store';
import { exchangeCodeForToken, getAuthConfig } from '../lib/auth-utils';

export default function Callback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState('');
  const [status, setStatus] = useState('Processing...');
  const { fetchUserInfo } = useAuthStore();

  useEffect(() => {
    handleCallback();
  }, []);

  const handleCallback = async () => {
    try {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const errorParam = searchParams.get('error');

      if (errorParam) {
        throw new Error(`OAuth error: ${errorParam}`);
      }

      if (!code || !state) {
        throw new Error('No authorization code or state received');
      }

      setStatus('Exchanging authorization code...');

      // Use auth-utils to exchange code for tokens (with PKCE)
      const { idToken, accessToken } = await exchangeCodeForToken(code, state);

      console.log('✅ Tokens received successfully');
      setStatus('Login successful!');

      // Store tokens in both localStorage AND Zustand store
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('id_token', idToken);

      // Update Zustand store with ID token (fixes chat authentication check)
      useAuthStore.getState().setIdToken(idToken);

      // Decode ID token to get user info
      const idTokenPayload = JSON.parse(atob(idToken.split('.')[1]));

      // Log full token payload (without sensitive data) for debugging
      console.log('🔍 ID Token claims:', {
        email: idTokenPayload.email,
        sub: idTokenPayload.sub,
        name: idTokenPayload.name,
        given_name: idTokenPayload.given_name,
        family_name: idTokenPayload.family_name,
        'cognito:username': idTokenPayload['cognito:username'],
        'cognito:groups': idTokenPayload['cognito:groups'],
        token_use: idTokenPayload.token_use,
        iss: idTokenPayload.iss
      });

      const userData = {
        email: idTokenPayload.email || idTokenPayload['cognito:username'],
        sub: idTokenPayload.sub,
        name: idTokenPayload.name || idTokenPayload.email || 'User',
        given_name: idTokenPayload.given_name,
        family_name: idTokenPayload.family_name,
      };

      localStorage.setItem('user', JSON.stringify(userData));

      // Also update Zustand store with user object (fixes admin panel access)
      useAuthStore.getState().setUser(userData);

      console.log('✅ Login successful:', userData);

      // Fetch user roles from backend
      setStatus('Loading user permissions...');
      await fetchUserInfo(userData.email, userData.name);

      // Wait for auth store to finish loading (prevents race condition)
      let retries = 0;
      while (useAuthStore.getState().isLoading && retries < 50) {
        await new Promise(resolve => setTimeout(resolve, 100));
        retries++;
      }

      console.log('✅ User permissions loaded, redirecting to dashboard...');

      // Redirect to dashboard
      setTimeout(() => {
        navigate('/dashboard');
      }, 500);

    } catch (err) {
      console.error('❌ Callback error:', err);
      setError((err as Error).message);
      setStatus('Authentication failed');
      
      // Redirect to login after 5 seconds
      setTimeout(() => {
        navigate('/login');
      }, 5000);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        {!error ? (
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto mb-6"></div>
            <h2 className="text-xl font-semibold mb-2">{status}</h2>
            <p className="text-gray-600">Please wait...</p>
          </div>
        ) : (
          <div className="text-center">
            <div className="text-red-500 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold mb-2 text-red-600">{status}</h2>
            <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
              <p className="text-sm text-red-800 font-mono break-words">{error}</p>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Check browser console (F12) for more details
            </p>
            <p className="text-sm text-gray-500">Redirecting to login in 5 seconds...</p>
            <button 
              onClick={() => navigate('/login')}
              className="mt-4 px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Back to Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
}