import { useState } from 'react';
import { Bot, Code, Search, Monitor, Mail, Activity, Clipboard, FileText, Mic, Calendar, ListTodo, CheckCircle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface AgentInfo {
  name: string;
  icon: React.ReactNode;
  status: 'ready' | 'busy' | 'offline';
  description: string;
  color: string;
}

const agents: AgentInfo[] = [
  {
    name: 'Coder Agent',
    icon: <Code className="w-5 h-5" />,
    status: 'ready',
    description: 'Writes, debugs, and executes code with auto-healing',
    color: 'bg-purple-500',
  },
  {
    name: 'Researcher Agent',
    icon: <Search className="w-5 h-5" />,
    status: 'ready',
    description: 'Multi-hop web research with citation synthesis',
    color: 'bg-blue-500',
  },
  {
    name: 'RPA Operator',
    icon: <Monitor className="w-5 h-5" />,
    status: 'ready',
    description: 'Screen capture, OCR, mouse/keyboard automation',
    color: 'bg-orange-500',
  },
  {
    name: 'Email Agent',
    icon: <Mail className="w-5 h-5" />,
    status: 'ready',
    description: 'IMAP/SMTP inbox reading and smart summarization',
    color: 'bg-green-500',
  },
  {
    name: 'System Monitor',
    icon: <Activity className="w-5 h-5" />,
    status: 'ready',
    description: 'Real-time CPU/RAM/disk monitoring with alerts',
    color: 'bg-red-500',
  },
  {
    name: 'Clipboard Agent',
    icon: <Clipboard className="w-5 h-5" />,
    status: 'ready',
    description: 'Auto-detects and processes clipboard content',
    color: 'bg-yellow-500',
  },
  {
    name: 'Meeting Agent',
    icon: <Mic className="w-5 h-5" />,
    status: 'ready',
    description: 'Live transcription with action item extraction',
    color: 'bg-pink-500',
  },
  {
    name: 'File Organizer',
    icon: <FileText className="w-5 h-5" />,
    status: 'ready',
    description: 'Content-based file classification and cleanup',
    color: 'bg-indigo-500',
  },
  {
    name: 'Calendar Agent',
    icon: <Calendar className="w-5 h-5" />,
    status: 'ready',
    description: 'Event management and scheduling assistant',
    color: 'bg-teal-500',
  },
  {
    name: 'Task Manager',
    icon: <ListTodo className="w-5 h-5" />,
    status: 'ready',
    description: 'Task tracking, prioritization, and reporting',
    color: 'bg-violet-500',
  },
];

export default function AgentsPanel() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  return (
    <div className="h-full bg-[var(--color-bg)] overflow-y-auto">
      {/* Header */}
      <div className="px-8 py-6 border-b border-[var(--color-border)]">
        <div className="flex items-center gap-3 mb-2">
          <Bot className="w-6 h-6 text-[var(--color-accent)]" />
          <h2 className="text-2xl font-bold text-[var(--color-text)]">AI Agents</h2>
        </div>
        <p className="text-sm text-[var(--color-text-secondary)]">
          10 specialized agents ready to assist with various tasks
        </p>
      </div>

      {/* Agents Grid */}
      <div className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {agents.map((agent) => (
            <motion.div
              key={agent.name}
              layout
              onClick={() => setSelectedAgent(selectedAgent === agent.name ? null : agent.name)}
              className={`p-5 rounded-xl border cursor-pointer transition-all ${
                selectedAgent === agent.name
                  ? 'border-[var(--color-accent)] bg-[var(--color-accent)]/5 shadow-md'
                  : 'border-[var(--color-border)] bg-[var(--color-panel)] hover:border-[var(--color-accent)]/50 hover:shadow-sm'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg ${agent.color} text-white flex-shrink-0`}>
                  {agent.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-semibold text-[var(--color-text)]">{agent.name}</h3>
                    <div className="flex items-center gap-1.5">
                      {agent.status === 'ready' ? (
                        <>
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="text-xs text-green-600 dark:text-green-400 font-medium">Ready</span>
                        </>
                      ) : agent.status === 'busy' ? (
                        <>
                          <AlertCircle className="w-4 h-4 text-yellow-500" />
                          <span className="text-xs text-yellow-600 dark:text-yellow-400 font-medium">Busy</span>
                        </>
                      ) : (
                        <span className="text-xs text-gray-400">Offline</span>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-[var(--color-text-secondary)] line-clamp-2">
                    {agent.description}
                  </p>
                </div>
              </div>

              {/* Expanded Details */}
              {selectedAgent === agent.name && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-4 pt-4 border-t border-[var(--color-border)]"
                >
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs font-medium text-[var(--color-text-secondary)] mb-1">Capabilities:</p>
                      <ul className="text-sm text-[var(--color-text)] space-y-1">
                        <li>• Natural language command processing</li>
                        <li>• Autonomous task execution</li>
                        <li>• Real-time status reporting</li>
                        <li>• Error handling and recovery</li>
                      </ul>
                    </div>
                    <button className="w-full px-4 py-2 bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-white font-medium rounded-lg transition-colors text-sm">
                      Activate {agent.name}
                    </button>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>

        {/* System Status */}
        <div className="mt-8 p-6 bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border)]">
          <h3 className="font-semibold text-[var(--color-text)] mb-3 flex items-center gap-2">
            <Activity className="w-5 h-5 text-[var(--color-accent)]" />
            System Overview
          </h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-2xl font-bold text-[var(--color-text)]">10</p>
              <p className="text-xs text-[var(--color-text-secondary)]">Total Agents</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">10</p>
              <p className="text-xs text-[var(--color-text-secondary)]">Active</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--color-text)]">0</p>
              <p className="text-xs text-[var(--color-text-secondary)]">Offline</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
