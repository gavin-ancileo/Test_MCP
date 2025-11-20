import { useAdminStore } from '@/store/admin-store';
import { cn } from '@/lib/utils';
import { FileText, Users, TestTube, Settings } from 'lucide-react';

const tabs = [
  { id: 'prompts' as const, label: 'Prompts', icon: FileText },
  { id: 'users' as const, label: 'Users', icon: Users },
  { id: 'test' as const, label: 'Test', icon: TestTube },
  { id: 'settings' as const, label: 'Settings', icon: Settings },
];

export function AdminTabs() {
  const { activeTab, setActiveTab } = useAdminStore();

  return (
    <div className="border-b border-gray-200 bg-gray-50">
      <nav className="flex space-x-0">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors',
                activeTab === tab.id
                  ? 'border-primary text-primary bg-white'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              )}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </nav>
    </div>
  );
}