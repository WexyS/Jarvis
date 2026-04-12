import { useState, useEffect } from 'react';
import { Globe, Code, Layers, Loader2, CheckCircle, AlertCircle, FolderOpen, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface WorkspaceItem {
  id: string;
  type: 'clone' | 'generated' | 'synthesized';
  name: string;
  url?: string;
  description: string;
  components: string[];
  tech_stack: string;
  path: string;
  created_at: string;
}

export default function WorkspacePanel() {
  const [activeTab, setActiveTab] = useState<'clone' | 'generate' | 'synthesize'>('clone');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [workspace, setWorkspace] = useState<WorkspaceItem[]>([]);

  // Form states
  const [cloneUrl, setCloneUrl] = useState('');
  const [generateIdea, setGenerateIdea] = useState('');
  const [synthesizeCommand, setSynthesizeCommand] = useState('');

  // Load workspace items
  useEffect(() => {
    loadWorkspace();
  }, []);

  const loadWorkspace = async () => {
    try {
      const resp = await fetch('http://localhost:8000/api/v2/workspace/list');
      const data = await resp.json();
      setWorkspace(data.items || []);
    } catch (err) {
      console.error('Failed to load workspace:', err);
    }
  };

  const handleClone = async () => {
    if (!cloneUrl.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const resp = await fetch('http://localhost:8000/api/v2/workspace/clone', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: cloneUrl,
          extract_components: true,
        }),
      });

      const data = await resp.json();
      
      if (data.success) {
        setResult(`✅ Successfully cloned: ${data.item.name}`);
        setCloneUrl('');
        loadWorkspace();
      } else {
        setError(`❌ Clone failed: ${data.error}`);
      }
    } catch (err: any) {
      setError(`❌ Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!generateIdea.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const resp = await fetch('http://localhost:8000/api/v2/workspace/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: generateIdea,
          tech_stack: 'html-css-js',
        }),
      });

      const data = await resp.json();
      
      if (data.success) {
        setResult(`✅ Generated app: ${data.item.name}`);
        setGenerateIdea('');
        loadWorkspace();
      } else {
        setError(`❌ Generation failed: ${data.error}`);
      }
    } catch (err: any) {
      setError(`❌ Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSynthesize = async () => {
    if (!synthesizeCommand.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const resp = await fetch('http://localhost:8000/api/v2/workspace/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_command: synthesizeCommand,
          target_project: 'synthesized-app',
        }),
      });

      const data = await resp.json();
      
      if (data.success) {
        setResult(`✅ Synthesized: ${data.item.name}`);
        setSynthesizeCommand('');
        loadWorkspace();
      } else {
        setError(`❌ Synthesis failed: ${data.error}`);
      }
    } catch (err: any) {
      setError(`❌ Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const openInExplorer = (path: string) => {
    // Open folder in file explorer
    fetch('http://localhost:8000/api/v2/workspace/open-folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path }),
    }).catch(console.error);
  };

  return (
    <div className="workspace-panel bg-white">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Workspace</h1>
        <p className="text-gray-600">Clone websites, generate apps, or synthesize new projects from templates</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex items-center gap-2 mb-6 p-1 bg-gray-100 rounded-lg w-fit">
        <button
          onClick={() => setActiveTab('clone')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${
            activeTab === 'clone'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Globe className="w-4 h-4" />
          Clone Site
        </button>
        <button
          onClick={() => setActiveTab('generate')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${
            activeTab === 'generate'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Code className="w-4 h-4" />
          Generate App
        </button>
        <button
          onClick={() => setActiveTab('synthesize')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${
            activeTab === 'synthesize'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Layers className="w-4 h-4" />
          Synthesize
        </button>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {/* CLONE TAB */}
        {activeTab === 'clone' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="p-6 bg-gray-50 rounded-xl border border-gray-200">
              <h3 className="text-lg font-semibold mb-3">Clone a Website</h3>
              <p className="text-sm text-gray-600 mb-4">
                Enter a URL to clone the website. Playwright will render it, extract components, and save the structure.
              </p>
              <div className="flex gap-3">
                <input
                  type="url"
                  value={cloneUrl}
                  onChange={(e) => setCloneUrl(e.target.value)}
                  placeholder="https://example.com"
                  className="flex-1"
                  disabled={loading}
                />
                <button
                  onClick={handleClone}
                  disabled={loading || !cloneUrl.trim()}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-medium rounded-lg transition-all disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4" />}
                  {loading ? 'Cloning...' : 'Clone'}
                </button>
              </div>
            </div>

            {/* Features */}
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <Globe className="w-6 h-6 text-blue-600 mb-2" />
                <h4 className="font-medium mb-1">Full Rendering</h4>
                <p className="text-xs text-gray-600">Playwright renders JS-heavy sites</p>
              </div>
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <Layers className="w-6 h-6 text-purple-600 mb-2" />
                <h4 className="font-medium mb-1">Component Extraction</h4>
                <p className="text-xs text-gray-600">Detects navbar, hero, cards, etc.</p>
              </div>
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <FolderOpen className="w-6 h-6 text-green-600 mb-2" />
                <h4 className="font-medium mb-1">Saved Structure</h4>
                <p className="text-xs text-gray-600">Metadata and components stored</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* GENERATE TAB */}
        {activeTab === 'generate' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="p-6 bg-gray-50 rounded-xl border border-gray-200">
              <h3 className="text-lg font-semibold mb-3">Generate an App from Idea</h3>
              <p className="text-sm text-gray-600 mb-4">
                Describe your app idea and AI will generate a complete, working application.
              </p>
              <textarea
                value={generateIdea}
                onChange={(e) => setGenerateIdea(e.target.value)}
                placeholder="A todo list application with dark mode and local storage..."
                rows={3}
                className="w-full mb-4"
                disabled={loading}
              />
              <button
                onClick={handleGenerate}
                disabled={loading || !generateIdea.trim()}
                className="w-full px-6 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white font-medium rounded-lg transition-all disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Code className="w-4 h-4" />}
                {loading ? 'Generating...' : 'Generate App'}
              </button>
            </div>

            {/* Tips */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">💡 Tips for better results:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Be specific about features</li>
                <li>• Mention the tech stack you prefer</li>
                <li>• Include design preferences</li>
              </ul>
            </div>
          </motion.div>
        )}

        {/* SYNTHESIZE TAB */}
        {activeTab === 'synthesize' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="p-6 bg-gray-50 rounded-xl border border-gray-200">
              <h3 className="text-lg font-semibold mb-3">Synthesize from Templates</h3>
              <p className="text-sm text-gray-600 mb-4">
                Combine existing cloned templates to create a new application using RAG.
              </p>
              <textarea
                value={synthesizeCommand}
                onChange={(e) => setSynthesizeCommand(e.target.value)}
                placeholder="Create a dashboard with the navbar from site A and the cards from site B..."
                rows={3}
                className="w-full mb-4"
                disabled={loading}
              />
              <button
                onClick={handleSynthesize}
                disabled={loading || !synthesizeCommand.trim()}
                className="w-full px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white font-medium rounded-lg transition-all disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Layers className="w-4 h-4" />}
                {loading ? 'Synthesizing...' : 'Synthesize'}
              </button>
            </div>
          </motion.div>
        )}

        {/* Result/Error */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3"
            >
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
              <p className="text-sm text-green-800 flex-1">{result}</p>
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-800 flex-1">{error}</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Workspace Items */}
        {workspace.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold mb-4">Recent Projects ({workspace.length})</h3>
            <div className="space-y-3">
              {workspace.slice(0, 10).map((item) => (
                <div
                  key={item.id}
                  className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">
                        {item.type === 'clone' ? '🌐' : item.type === 'generated' ? '💻' : '🔄'}
                      </span>
                      <h4 className="font-medium">{item.name}</h4>
                    </div>
                    <button
                      onClick={() => openInExplorer(item.path)}
                      className="p-1 hover:bg-gray-100 rounded"
                      title="Open in Explorer"
                    >
                      <ExternalLink className="w-4 h-4 text-gray-600" />
                    </button>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{item.description}</p>
                  <div className="flex items-center gap-2 flex-wrap">
                    {item.components.slice(0, 5).map((comp) => (
                      <span key={comp} className="px-2 py-0.5 text-xs bg-gray-100 rounded">
                        {comp}
                      </span>
                    ))}
                    <span className="text-xs text-gray-500">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
