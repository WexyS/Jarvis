import { Settings, Trash2, MessageSquare, Globe, Activity, Zap } from 'lucide-react';

type ActivePanel = 'chat' | 'workspace';

interface SidebarProps {
  status: string;
  onClear: () => void;
  activePanel: ActivePanel;
  onPanelChange: (panel: ActivePanel) => void;
}

export default function Sidebar({ status, onClear, activePanel, onPanelChange }: SidebarProps) {
  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo / Brand */}
      <div className="px-6 py-5 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">Jarvis</h1>
            <p className="text-xs text-gray-500">AI Assistant v2.1</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <button
          onClick={() => onPanelChange('chat')}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
            activePanel === 'chat'
              ? 'bg-blue-50 text-blue-700'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
        >
          <MessageSquare className="w-5 h-5" />
          <span className="font-medium">Chat</span>
        </button>

        <button
          onClick={() => onPanelChange('workspace')}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
            activePanel === 'workspace'
              ? 'bg-blue-50 text-blue-700'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
        >
          <Globe className="w-5 h-5" />
          <span className="font-medium">Workspace</span>
        </button>

        <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-700 hover:bg-gray-100 transition-all">
          <Activity className="w-5 h-5" />
          <span className="font-medium">Agents</span>
        </button>
      </nav>

      {/* Status */}
      <div className="px-3 py-4 border-t border-gray-200">
        <div className="px-3 py-2 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-600 mb-1">Status</p>
          <p className="text-sm font-medium text-gray-900 capitalize">{status}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="px-3 py-4 border-t border-gray-200 space-y-2">
        <button
          onClick={onClear}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-700 hover:bg-gray-100 transition-all"
        >
          <Trash2 className="w-5 h-5" />
          <span className="font-medium">Clear Chat</span>
        </button>

        <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-700 hover:bg-gray-100 transition-all">
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </button>
      </div>
    </div>
  );
}
