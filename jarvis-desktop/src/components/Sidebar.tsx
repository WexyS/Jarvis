import { Bot, Code2, Search, Monitor, Zap, MemoryStick, Shield } from 'lucide-react';

interface SidebarProps {
  status: any;
  onClear: () => void;
}

const AGENT_INFO: Record<string, { icon: React.ReactNode; desc: string; color: string }> = {
  coder: {
    icon: <Code2 className="w-5 h-5" />,
    desc: 'Writes, executes & self-heals code',
    color: 'text-purple-400'
  },
  researcher: {
    icon: <Search className="w-5 h-5" />,
    desc: 'Multi-hop web research with citations',
    color: 'text-blue-400'
  },
  rpa_operator: {
    icon: <Monitor className="w-5 h-5" />,
    desc: 'Screen control, OCR & automation',
    color: 'text-orange-400'
  }
};

export default function Sidebar({ status, onClear }: SidebarProps) {
  const agents = status?.agents || {};
  const providers = status?.llm_providers || {};
  const memory = status?.memory || {};

  return (
    <div className="w-64 bg-jarvis-panel border-r border-jarvis-border flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-jarvis-border">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-jarvis-primary/10 border-2 border-jarvis-primary/30 flex items-center justify-center">
              <Bot className="w-5 h-5 text-jarvis-primary" />
            </div>
            <div className="absolute -inset-1 rounded-full border border-jarvis-primary/20 animate-pulse-slow" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-wider">J.A.R.V.I.S</h1>
            <p className="text-xs text-jarvis-textMuted">v2.0 Multi-Agent</p>
          </div>
        </div>
      </div>

      {/* Agents */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <h2 className="text-xs font-semibold text-jarvis-textMuted uppercase tracking-wider">Agents</h2>
        {Object.entries(AGENT_INFO).map(([key, info]) => {
          const agent = agents[key] as any;
          const isActive = agent?.status === 'busy';
          const isReady = agent?.status === 'idle';
          
          return (
            <div
              key={key}
              className={`p-3 rounded-lg border transition-all ${
                isActive 
                  ? 'bg-jarvis-primary/5 border-jarvis-primary/30' 
                  : isReady 
                    ? 'bg-jarvis-bg border-jarvis-border/50' 
                    : 'bg-jarvis-bg/50 border-jarvis-border/30 opacity-60'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className={info.color}>{info.icon}</span>
                <span className="text-sm font-medium text-white capitalize">
                  {key.replace('_', ' ')}
                </span>
                <div className={`ml-auto w-2 h-2 rounded-full ${
                  isActive ? 'bg-jarvis-primary animate-pulse' : 
                  isReady ? 'bg-jarvis-accent' : 'bg-jarvis-textMuted'
                }`} />
              </div>
              <p className="text-xs text-jarvis-textMuted">{info.desc}</p>
              {agent?.tasks_completed > 0 && (
                <p className="text-xs text-jarvis-textMuted mt-1">
                  ✓ {agent.tasks_completed} tasks completed
                </p>
              )}
            </div>
          );
        })}

        {/* LLM Providers */}
        <div className="pt-4 border-t border-jarvis-border">
          <h2 className="text-xs font-semibold text-jarvis-textMuted uppercase tracking-wider mb-2">Providers</h2>
          {Object.entries(providers).map(([key, val]: [string, any]) => (
            <div key={key} className="flex items-center justify-between py-1.5 text-xs">
              <span className="text-jarvis-textMuted capitalize">{key.replace('_', ' ')}</span>
              <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                val.available 
                  ? 'bg-jarvis-accent/10 text-jarvis-accent' 
                  : 'bg-jarvis-danger/10 text-jarvis-danger'
              }`}>
                {val.available ? 'OK' : 'OFF'}
              </span>
            </div>
          ))}
        </div>

        {/* Memory */}
        {memory.vector_entries > 0 && (
          <div className="pt-4 border-t border-jarvis-border">
            <h2 className="text-xs font-semibold text-jarvis-textMuted uppercase tracking-wider mb-2">Memory</h2>
            <div className="flex items-center gap-2 text-xs text-jarvis-textMuted">
              <MemoryStick className="w-4 h-4" />
              <span>{memory.vector_entries} vectors</span>
            </div>
            {memory.graph_nodes > 0 && (
              <div className="flex items-center gap-2 text-xs text-jarvis-textMuted mt-1">
                <Shield className="w-4 h-4" />
                <span>{memory.graph_nodes} graph nodes</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-jarvis-border">
        <button
          onClick={onClear}
          className="w-full px-3 py-2 rounded-lg bg-jarvis-bg border border-jarvis-border text-jarvis-textMuted hover:text-white hover:border-jarvis-primary/50 transition-all text-sm"
        >
          Clear Chat
        </button>
      </div>
    </div>
  );
}
