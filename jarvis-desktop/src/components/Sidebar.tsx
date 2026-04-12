import { Settings, Trash2, MessageSquare, Globe, Activity, Zap, Bot } from 'lucide-react';

type ActivePanel = 'chat' | 'workspace' | 'agents';

interface SidebarProps {
  status: string;
  onClear: () => void;
  activePanel: ActivePanel;
  onPanelChange: (panel: ActivePanel) => void;
}

export default function Sidebar({ status, onClear, activePanel, onPanelChange }: SidebarProps) {
  return (
    <div className="w-64 bg-[var(--color-panel)] border-r border-[var(--color-border)] flex flex-col">
      {/* Logo / Brand */}
      <div className="px-6 py-5 border-b border-[var(--color-border)]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-[var(--color-text)]">Jarvis</h1>
            <p className="text-xs text-[var(--color-text-secondary)]">AI Assistant v2.1</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <button
          onClick={() => onPanelChange('chat')}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
            activePanel === 'chat'
              ? 'bg-[var(--color-accent)]/10 text-[var(--color-accent)]'
              : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-card)]'
          }`}
        >
          <MessageSquare className="w-5 h-5" />
          <span className="font-medium">Chat</span>
        </button>

        <button
          onClick={() => onPanelChange('workspace')}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
            activePanel === 'workspace'
              ? 'bg-[var(--color-accent)]/10 text-[var(--color-accent)]'
              : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-card)]'
          }`}
        >
          <Globe className="w-5 h-5" />
          <span className="font-medium">Workspace</span>
        </button>

        <button
          onClick={() => onPanelChange('agents')}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
            activePanel === 'agents'
              ? 'bg-[var(--color-accent)]/10 text-[var(--color-accent)]'
              : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-card)]'
          }`}
        >
          <Bot className="w-5 h-5" />
          <span className="font-medium">Agents</span>
        </button>
      </nav>

      {/* Status */}
      <div className="px-3 py-4 border-t border-[var(--color-border)]">
        <div className="px-3 py-2 bg-[var(--color-card)] rounded-lg">
          <p className="text-xs text-[var(--color-text-secondary)] mb-1">Status</p>
          <p className="text-sm font-medium text-[var(--color-text)] capitalize">{status}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="px-3 py-4 border-t border-[var(--color-border)] space-y-2">
        <button
          onClick={onClear}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[var(--color-text-secondary)] hover:bg-[var(--color-card)] transition-all"
        >
          <Trash2 className="w-5 h-5" />
          <span className="font-medium">Clear Chat</span>
        </button>

        <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[var(--color-text-secondary)] hover:bg-[var(--color-card)] transition-all">
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </button>
      </div>
    </div>
  );
}
