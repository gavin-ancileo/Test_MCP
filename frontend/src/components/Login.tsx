import React from 'react';
import { buildAuthUrl } from '../lib/auth-utils';

export default function Login() {
  const handleLogin = async () => {
    try {
      const cognitoUrl = await buildAuthUrl();
      console.log('🔗 Redirecting to Cognito:', cognitoUrl);
      window.location.href = cognitoUrl;
    } catch (error) {
      console.error('Failed to build auth URL:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-6">AAP Login</h2>
          <p className="text-gray-600 mb-6">
            Click below to login with your company SSO
          </p>
          
          <button
            onClick={handleLogin}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium"
          >
            Login with Company SSO
          </button>
        </div>
      </div>
    </div>
  );
}