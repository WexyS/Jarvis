import { useJarvis } from './hooks/useJarvis';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import InputBox from './components/InputBox';
import StatusBadge from './components/StatusBadge';
import { AlertTriangle, WifiOff } from 'lucide-react';

function App() {
  const {
    messages,
    isStreaming,
    currentResponse,
    isConnected,
    error,
    status,
    sendMessage,
    clearMessages,
  } = useJarvis();

  return (
    <div className="flex h-screen bg-jarvis-bg">
      {/* Sidebar */}
      <Sidebar status={status} onClear={clearMessages} />

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-3 border-b border-jarvis-border bg-jarvis-panel">
          <h2 className="text-sm font-medium text-jarvis-textMuted">
            {isStreaming ? 'Processing...' : 'Ready'}
          </h2>
          <StatusBadge status={status} isConnected={isConnected} />
        </header>

        {/* Error banner */}
        {error && (
          <div className="mx-6 mt-3 p-3 rounded-lg bg-jarvis-danger/10 border border-jarvis-danger/30 flex items-center gap-3">
            <AlertTriangle className="w-4 h-4 text-jarvis-danger flex-shrink-0" />
            <p className="text-sm text-jarvis-danger flex-1">{error}</p>
            {!isConnected && <WifiOff className="w-4 h-4 text-jarvis-danger" />}
          </div>
        )}

        {/* Chat area */}
        <ChatArea
          messages={messages}
          currentResponse={currentResponse}
          isStreaming={isStreaming}
        />

        {/* Input */}
        <InputBox
          onSend={sendMessage}
          disabled={isStreaming}
          isConnected={isConnected}
        />
      </div>
    </div>
  );
}

export default App;
