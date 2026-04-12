/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        jarvis: {
          bg: '#050a10',
          panel: '#0a1423',
          border: '#1e3a5f',
          primary: '#00d4ff',
          primaryDim: '#005580',
          accent: '#00ff88',
          danger: '#ff3366',
          warning: '#ffcc00',
          text: '#e0f0ff',
          textMuted: '#5a7b9c'
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 8s linear infinite',
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      }
    },
  },
  plugins: [],
}
