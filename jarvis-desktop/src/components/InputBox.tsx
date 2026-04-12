import { useState, useRef, useEffect } from 'react';
import { Send, Code, Search, Monitor, Mic } from 'lucide-react';

type Mode = 'chat' | 'code' | 'research' | 'rpa';

interface InputBoxProps {
  onSend: (message: string, mode: Mode) => void;
  disabled: boolean;
  isConnected: boolean;
}

const MODES: { key: Mode; label: string; icon: React.ReactNode; color: string }[] = [
  { key: 'chat', label: 'Chat', icon: <Send className="w-4 h-4" />, color: 'bg-jarvis-primary' },
  { key: 'code', label: 'Code', icon: <Code className="w-4 h-4" />, color: 'bg-purple-500' },
  { key: 'research', label: 'Research', icon: <Search className="w-4 h-4" />, color: 'bg-blue-500' },
  { key: 'rpa', label: 'RPA', icon: <Monitor className="w-4 h-4" />, color: 'bg-orange-500' },
];

export default function InputBox({ onSend, disabled, isConnected }: InputBoxProps) {
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<Mode>('chat');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + 'px';
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || disabled || !isConnected) return;
    onSend(trimmed, mode);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-jarvis-border bg-jarvis-panel p-4">
      {/* Mode selector */}
      <div className="flex items-center gap-2 mb-3">
        {MODES.map((m) => (
          <button
            key={m.key}
            onClick={() => setMode(m.key)}
            disabled={!isConnected}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              mode === m.key
                ? `${m.color} text-white shadow-lg`
                : 'bg-jarvis-bg border border-jarvis-border text-jarvis-textMuted hover:text-white hover:border-jarvis-primary/50'
            }`}
          >
            {m.icon}
            {m.label}
          </button>
        ))}
        
        {/* Voice button placeholder */}
        <button
          disabled
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium bg-jarvis-bg border border-jarvis-border text-jarvis-textMuted/50 cursor-not-allowed ml-auto"
          title="Voice input coming soon"
        >
          <Mic className="w-4 h-4" />
          Voice
        </button>
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="flex gap-3">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            mode === 'chat' ? "Ask me anything..." :
            mode === 'code' ? "Describe the code you need..." :
            mode === 'research' ? "What should I research?" :
            "What should I do on your computer?"
          }
          disabled={!isConnected || disabled}
          rows={1}
          className="flex-1 bg-jarvis-bg border border-jarvis-border rounded-xl px-4 py-3 text-jarvis-text placeholder-jarvis-textMuted/50 resize-none focus:outline-none focus:border-jarvis-primary/50 focus:ring-1 focus:ring-jarvis-primary/20 transition-all disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!input.trim() || !isConnected || disabled}
          className="px-6 py-3 bg-jarvis-primary hover:bg-jarvis-primary/80 disabled:bg-jarvis-border disabled:text-jarvis-textMuted/50 text-white font-medium rounded-xl transition-all disabled:cursor-not-allowed shadow-lg shadow-jarvis-primary/20"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>

      {/* Status text */}
      <div className="mt-2 text-xs text-jarvis-textMuted/50 text-center">
        {isConnected ? (
          disabled ? 'Processing...' : `Press Enter to send, Shift+Enter for new line`
        ) : (
          <span className="text-jarvis-danger">Disconnected — waiting for backend...</span>
        )}
      </div>
    </div>
  );
}
