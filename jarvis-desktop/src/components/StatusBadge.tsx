import { Activity, Cpu, Database, Layers } from 'lucide-react';

interface StatusBadgeProps {
  status: any;
  isConnected: boolean;
}

export default function StatusBadge({ status, isConnected }: StatusBadgeProps) {
  if (!status) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-jarvis-panel border border-jarvis-border">
        <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse" />
        <span className="text-xs text-jarvis-textMuted">Connecting...</span>
      </div>
    );
  }

  const activeProviders = Object.entries(status.llm_providers || {})
    .filter(([_, v]: [string, any]) => v.available)
    .map(([k]) => k);

  const agents = status.agents || {};
  const activeAgents = Object.values(agents).filter((a: any) => a.status === 'idle').length;

  return (
    <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-jarvis-panel border border-jarvis-border">
      {/* Connection status */}
      <div className="flex items-center gap-2">
        <Activity className={`w-4 h-4 ${isConnected ? 'text-jarvis-accent' : 'text-jarvis-danger'}`} />
        <span className={`text-xs font-medium ${isConnected ? 'text-jarvis-accent' : 'text-jarvis-danger'}`}>
          {isConnected ? 'Online' : 'Offline'}
        </span>
      </div>

      <div className="w-px h-4 bg-jarvis-border" />

      {/* Agents */}
      <div className="flex items-center gap-1.5 text-jarvis-textMuted" title={`${activeAgents} agents ready`}>
        <Layers className="w-3.5 h-3.5" />
        <span className="text-xs">{activeAgents}</span>
      </div>

      {/* Providers */}
      <div className="flex items-center gap-1.5 text-jarvis-textMuted" title={`Providers: ${activeProviders.join(', ') || 'None'}`}>
        <Cpu className="w-3.5 h-3.5" />
        <span className="text-xs">{activeProviders.length}</span>
      </div>

      {/* Memory */}
      {status.memory && (
        <div className="flex items-center gap-1.5 text-jarvis-textMuted" title={`${status.memory.vector_entries || 0} vector entries`}>
          <Database className="w-3.5 h-3.5" />
          <span className="text-xs">{status.memory.vector_entries || 0}</span>
        </div>
      )}
    </div>
  );
}
