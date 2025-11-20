import React, { useState, useEffect } from 'react';
import { Users, Shield, Mail, Calendar, Edit, Trash2, UserPlus } from 'lucide-react';
import { getCurrentUser, ROLES } from '@/lib/rbac';
import { useToast } from '@/hooks/use-toast';
import { authenticatedFetch } from '@/lib/auth-utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';

interface User {
  email: string;
  name: string;
  roles: string[];
  is_admin: boolean;
  created_at: string;
}

const AVAILABLE_ROLES = [
  'HR', 'BA', 'PM', 'QA', 'DEV',
  'TECH_LEAD', 'FINANCE', 'CYBERSECURITY',
  'DEVOPS', 'ADMIN', 'ALL'
];

const UsersPanel: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserName, setNewUserName] = useState('');
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [isAdminChecked, setIsAdminChecked] = useState(false);
  const { toast } = useToast();

  const API_URL = '/mcp-server';

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await authenticatedFetch(`${API_URL}/users`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setUsers(data.users || []);
    } catch (error) {
      console.error('Load users error:', error);
      toast({
        title: "Error",
        description: "Failed to load users",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setSelectedRoles(user.roles);
    setIsAdminChecked(user.is_admin);
  };

  const handleSaveUser = async () => {
    if (!editingUser) return;

    try {
      const response = await authenticatedFetch(`${API_URL}/users/${encodeURIComponent(editingUser.email)}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          roles: selectedRoles,
          is_admin: isAdminChecked,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update user');
      }

      toast({
        title: 'Success',
        description: `User ${editingUser.email} updated successfully`,
      });

      setEditingUser(null);
      loadUsers();
    } catch (error) {
      console.error('Error updating user:', error);
      toast({
        title: 'Error',
        description: 'Failed to update user',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteUser = async (email: string) => {
    if (!confirm(`Are you sure you want to delete user ${email}?`)) {
      return;
    }

    try {
      const response = await authenticatedFetch(`${API_URL}/users/${encodeURIComponent(email)}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete user');
      }

      toast({
        title: 'Success',
        description: `User ${email} deleted successfully`,
      });

      loadUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete user',
        variant: 'destructive',
      });
    }
  };

  const toggleRole = (role: string) => {
    setSelectedRoles(prev =>
      prev.includes(role)
        ? prev.filter(r => r !== role)
        : [...prev, role]
    );
  };

  const handleOpenInviteDialog = () => {
    setNewUserEmail('');
    setNewUserName('');
    setSelectedRoles(['ALL']);
    setIsAdminChecked(false);
    setInviteDialogOpen(true);
  };

  const handleInviteUser = async () => {
    // Validate email
    if (!newUserEmail || !newUserEmail.includes('@')) {
      toast({
        title: 'Invalid Email',
        description: 'Please enter a valid email address',
        variant: 'destructive',
      });
      return;
    }

    // Validate name
    if (!newUserName || newUserName.trim().length === 0) {
      toast({
        title: 'Invalid Name',
        description: 'Please enter a user name',
        variant: 'destructive',
      });
      return;
    }

    // Validate roles
    if (selectedRoles.length === 0) {
      toast({
        title: 'No Roles Selected',
        description: 'Please select at least one role',
        variant: 'destructive',
      });
      return;
    }

    try {
      // Create user via login endpoint (will auto-create if not exists)
      const response = await authenticatedFetch(`${API_URL}/users/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: newUserEmail,
          name: newUserName,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create user');
      }

      const userData = await response.json();

      // Now update the user's roles
      const updateResponse = await authenticatedFetch(`${API_URL}/users/${encodeURIComponent(newUserEmail)}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          roles: selectedRoles,
          is_admin: isAdminChecked,
        }),
      });

      if (!updateResponse.ok) {
        throw new Error('User created but failed to set roles');
      }

      toast({
        title: 'User Invited Successfully',
        description: `${newUserEmail} can now login via Google SSO`,
      });

      setInviteDialogOpen(false);
      loadUsers();
    } catch (error) {
      console.error('Error inviting user:', error);
      toast({
        title: 'Error',
        description: 'Failed to invite user',
        variant: 'destructive',
      });
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const currentUser = getCurrentUser();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Users Management</h2>
          <p className="text-gray-600 mt-1">Manage user roles and permissions</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadUsers}>
            Refresh Users
          </Button>
          <Button onClick={handleOpenInviteDialog} className="flex items-center gap-2">
            <UserPlus className="w-4 h-4" />
            Invite User
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <Users className="w-8 h-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">{users.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <Shield className="w-8 h-8 text-red-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Admins</p>
              <p className="text-2xl font-bold text-gray-900">
                {users.filter(u => u.is_admin).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <Users className="w-8 h-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Regular Users</p>
              <p className="text-2xl font-bold text-gray-900">
                {users.filter(u => !u.is_admin).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-500">Loading users...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="p-8 text-center">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No users found</p>
          </div>
        ) : (
          <div className="p-4 space-y-4">
            {(users || []).map((user) => (
              <div
                key={user.email}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="font-medium">{user.name || user.email}</div>
                    {user.is_admin && (
                      <Badge variant="destructive" className="flex items-center gap-1">
                        <Shield className="w-3 h-3" />
                        Admin
                      </Badge>
                    )}
                  </div>
                  <div className="text-sm text-gray-500 flex items-center mb-2">
                    <Mail className="w-3 h-3 mr-1" />
                    {user.email}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(user.roles || []).map((role) => (
                      <Badge key={role} variant="secondary">
                        {role}
                      </Badge>
                    ))}
                  </div>
                  <div className="text-xs text-gray-400 mt-2">
                    Created: {formatDate(user.created_at)}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEditUser(user)}
                  >
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                  {user.email !== currentUser?.email && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteUser(user.email)}
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Delete
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Edit User Dialog */}
      <Dialog open={!!editingUser} onOpenChange={(open) => !open && setEditingUser(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit User Roles</DialogTitle>
            <DialogDescription>
              Update roles and permissions for {editingUser?.email}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Admin Checkbox */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="admin"
                checked={isAdminChecked}
                onCheckedChange={(checked) => setIsAdminChecked(!!checked)}
              />
              <Label htmlFor="admin" className="flex items-center gap-2 cursor-pointer">
                <Shield className="w-4 h-4" />
                <span className="font-medium">Admin (Full Access)</span>
              </Label>
            </div>

            {/* Roles */}
            <div className="space-y-3">
              <div className="font-medium text-sm">Roles</div>
              <div className="grid grid-cols-2 gap-3">
                {AVAILABLE_ROLES.map((role) => (
                  <div key={role} className="flex items-center space-x-2">
                    <Checkbox
                      id={`role-${role}`}
                      checked={selectedRoles.includes(role)}
                      onCheckedChange={() => toggleRole(role)}
                    />
                    <Label htmlFor={`role-${role}`} className="cursor-pointer">
                      {role}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* Info */}
            <div className="text-sm text-muted-foreground bg-blue-50 p-3 rounded-lg border border-blue-200">
              <strong>Note:</strong> Admin users see all prompts regardless of their roles.
              Non-admin users only see prompts that match their assigned roles.
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingUser(null)}>
              Cancel
            </Button>
            <Button onClick={handleSaveUser}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Invite User Dialog */}
      <Dialog open={inviteDialogOpen} onOpenChange={setInviteDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Invite New User</DialogTitle>
            <DialogDescription>
              Add a new user to the system. They will be able to login via Google SSO.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Email Input */}
            <div className="space-y-2">
              <Label htmlFor="email">Email Address *</Label>
              <Input
                id="email"
                type="email"
                placeholder="user@ancileo.com"
                value={newUserEmail}
                onChange={(e) => setNewUserEmail(e.target.value)}
                required
              />
              <p className="text-xs text-muted-foreground">
                User will login using this email via Google SSO
              </p>
            </div>

            {/* Name Input */}
            <div className="space-y-2">
              <Label htmlFor="name">Full Name *</Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                value={newUserName}
                onChange={(e) => setNewUserName(e.target.value)}
                required
              />
            </div>

            {/* Admin Checkbox */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="invite-admin"
                checked={isAdminChecked}
                onCheckedChange={(checked) => setIsAdminChecked(!!checked)}
              />
              <Label htmlFor="invite-admin" className="flex items-center gap-2 cursor-pointer">
                <Shield className="w-4 h-4" />
                <span className="font-medium">Admin (Full Access)</span>
              </Label>
            </div>

            {/* Roles */}
            <div className="space-y-3">
              <div className="font-medium text-sm">Roles *</div>
              <div className="grid grid-cols-2 gap-3">
                {AVAILABLE_ROLES.map((role) => (
                  <div key={role} className="flex items-center space-x-2">
                    <Checkbox
                      id={`invite-role-${role}`}
                      checked={selectedRoles.includes(role)}
                      onCheckedChange={() => toggleRole(role)}
                    />
                    <Label htmlFor={`invite-role-${role}`} className="cursor-pointer">
                      {role}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* Info */}
            <div className="text-sm bg-blue-50 p-3 rounded-lg border border-blue-200">
              <strong>Note:</strong> The user will be pre-created in the system. When they login via Google SSO with this email, they will automatically have the assigned roles and permissions.
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setInviteDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleInviteUser}>
              <UserPlus className="w-4 h-4 mr-2" />
              Invite User
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UsersPanel;