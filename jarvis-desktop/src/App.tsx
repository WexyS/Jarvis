import { useState } from 'react';
import { useJarvis } from './hooks/useJarvis';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import InputBox from './components/InputBox';
import StatusBadge from './components/StatusBadge';
import InspectorPanel from './components/InspectorPanel';
import WorkspacePanel from './components/WorkspacePanel';
import { AlertTriangle, WifiOff, PanelRightClose, PanelRightOpen, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

type ActivePanel = 'chat' | 'workspace';

function App() {
  const {
    messages,
    isStreaming,
    currentResponse,
    isConnected,
    error,
    status,
    providers,
    workspace,
    sendMessage,
    clearMessages,
  } = useJarvis();

  const [activePanel, setActivePanel] = useState<ActivePanel>('chat');
  const [inspectorOpen, setInspectorOpen] = useState(true);

  return (
    <div className="flex h-screen bg-white text-gray-900 font-sans overflow-hidden">
      {/* ── SIDEBAR (260px) - Clean, minimal ────────────────────────── */}
      <Sidebar
        status={status}
        onClear={clearMessages}
        activePanel={activePanel}
        onPanelChange={setActivePanel}
      />

      {/* ── MAIN CONTENT - Focus on content ─────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header - Minimal, clean like verdent.ai */}
        <header className="flex items-center justify-between px-8 py-4 border-b border-gray-200 bg-white">
          <div className="flex items-center gap-4">
            {/* Panel Toggle */}
            <div className="flex items-center gap-2 p-1 bg-gray-100 rounded-lg">
              <button
                onClick={() => setActivePanel('chat')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
                  activePanel === 'chat'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                💬 Chat
              </button>
              <button
                onClick={() => setActivePanel('workspace')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
                  activePanel === 'workspace'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                🌐 Workspace
              </button>
            </div>

            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-gray-400" />
              <h2 className="text-sm font-medium text-gray-600">
                {isStreaming ? 'Processing...' : activePanel === 'chat' ? 'Ready to assist' : 'Workspace'}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <StatusBadge status={status} isConnected={isConnected} />
            <button
              onClick={() => setInspectorOpen(!inspectorOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              title={inspectorOpen ? 'Close Inspector' : 'Open Inspector'}
            >
              {inspectorOpen ? <PanelRightClose className="w-5 h-5" /> : <PanelRightOpen className="w-5 h-5" />}
            </button>
          </div>
        </header>

        {/* Error banner - Subtle, non-intrusive */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mx-8 mt-4 p-4 rounded-lg bg-red-50 border border-red-200 flex items-center gap-3"
            >
              <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-700 flex-1">{error}</p>
              {!isConnected && <WifiOff className="w-4 h-4 text-red-600" />}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Panel content */}
        {activePanel === 'chat' ? (
          <>
            <ChatArea
              messages={messages}
              currentResponse={currentResponse}
              isStreaming={isStreaming}
            />
            <InputBox
              onSend={sendMessage}
              disabled={isStreaming}
              isConnected={isConnected}
            />
          </>
        ) : (
          <WorkspacePanel />
        )}
      </div>

      {/* ── INSPECTOR PANEL (320px) - Clean, organized ─────────────── */}
      <AnimatePresence>
        {inspectorOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 320, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-l border-gray-200 bg-white overflow-hidden"
          >
            <InspectorPanel status={status} providers={providers} workspace={workspace} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
