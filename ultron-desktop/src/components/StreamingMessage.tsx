import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

interface StreamingMessageProps {
  content: string;
  isStreaming?: boolean;
}

export default function StreamingMessage({ content, isStreaming }: StreamingMessageProps) {
  const [copied, setCopied] = useState<string | null>(null);

  const copyToClipboard = async (code: string, id: string) => {
    await navigator.clipboard.writeText(code);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="prose prose-invert max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const isInline = !match;
            const codeStr = String(children).replace(/\n$/, '');
            const codeId = `code-${Math.random().toString(36).substr(2, 9)}`;
            
            return isInline ? (
              <code className={className} {...props}>
                {children}
              </code>
            ) : (
              <div className="relative group my-4">
                <div className="absolute right-2 top-2 flex gap-1">
                  <span className="text-xs text-ultron-textMuted bg-ultron-panel px-2 py-1 rounded">
                    {match?.[1] || 'code'}
                  </span>
                  <button
                    onClick={() => copyToClipboard(codeStr, codeId)}
                    className="p-1 rounded bg-ultron-panel hover:bg-ultron-border transition-colors"
                    title="Copy code"
                  >
                    {copied === codeId ? (
                      <Check className="w-4 h-4 text-ultron-accent" />
                    ) : (
                      <Copy className="w-4 h-4 text-ultron-textMuted" />
                    )}
                  </button>
                </div>
                <SyntaxHighlighter
                  style={vscDarkPlus as any}
                  language={match?.[1] || 'text'}
                  PreTag="div"
                  customStyle={{
                    margin: 0,
                    borderRadius: '0.5rem',
                    background: '#0a1423',
                    border: '1px solid #1e3a5f'
                  }}
                >
                  {codeStr}
                </SyntaxHighlighter>
              </div>
            );
          },
          p: ({ children }) => <p className="my-2 leading-relaxed">{children}</p>,
          ul: ({ children }) => <ul className="list-disc pl-6 my-2">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-6 my-2">{children}</ol>,
          li: ({ children }) => <li className="my-1">{children}</li>,
          a: ({ href, children }) => (
            <a href={href} className="text-ultron-primary hover:underline" target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-ultron-primary pl-4 py-2 my-2 bg-ultron-panel rounded-r text-ultron-textMuted">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border-collapse border border-ultron-border">
                {children}
              </table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border border-ultron-border px-4 py-2 bg-ultron-panel font-semibold">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border border-ultron-border px-4 py-2">{children}</td>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
      {isStreaming && <span className="inline-block w-2 h-5 bg-ultron-primary ml-1 animate-pulse" />}
    </div>
  );
}
