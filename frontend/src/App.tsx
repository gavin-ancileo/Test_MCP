import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import ProtectedRoute from '@/components/ProtectedRoute';
import LandingPage from '@/pages/LandingPage';
import ChatPage from '@/pages/ChatPage';
import Dashboard from '@/components/Dashboard';
import DevvLogin from '@/components/DevvLogin';
import Login from '@/components/Login';
import Callback from '@/components/Callback';
import AdminLayout from '@/components/admin/AdminLayout';
import SettingsPage from '@/pages/SettingsPage';
import MyWorkflowsPage from '@/pages/MyWorkflowsPage';
import NotFoundPage from '@/pages/NotFoundPage';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/devv-login" element={<DevvLogin />} />
          <Route path="/callback" element={<Callback />} />
          
          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          
          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/my-workflows"
            element={
              <ProtectedRoute>
                <MyWorkflowsPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/*"
            element={
              <ProtectedRoute>
                <AdminLayout />
              </ProtectedRoute>
            }
          />
          
          <Route 
            path="/settings" 
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            } 
          />
          
          {/* 404 Route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
        
        <Toaster />
      </div>
    </Router>
  );
}

export default App;