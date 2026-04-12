/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'jarvis-bg': 'rgb(var(--color-bg) / <alpha-value>)',
        'jarvis-bg-secondary': 'rgb(var(--color-bg-secondary) / <alpha-value>)',
        'jarvis-bg-tertiary': 'rgb(var(--color-bg-tertiary) / <alpha-value>)',
        'jarvis-panel': 'rgb(var(--color-panel) / <alpha-value>)',
        'jarvis-card': 'rgb(var(--color-card) / <alpha-value>)',
        'jarvis-border': 'rgb(var(--color-border) / <alpha-value>)',
        'jarvis-border-light': 'rgb(var(--color-border-light) / <alpha-value>)',
        'jarvis-text': 'rgb(var(--color-text) / <alpha-value>)',
        'jarvis-text-secondary': 'rgb(var(--color-text-secondary) / <alpha-value>)',
        'jarvis-text-tertiary': 'rgb(var(--color-text-tertiary) / <alpha-value>)',
        'jarvis-text-muted': 'rgb(var(--color-text-muted) / <alpha-value>)',
        'jarvis-accent': 'rgb(var(--color-accent) / <alpha-value>)',
        'jarvis-accent-hover': 'rgb(var(--color-accent-hover) / <alpha-value>)',
        'jarvis-success': 'rgb(var(--color-success) / <alpha-value>)',
        'jarvis-warning': 'rgb(var(--color-warning) / <alpha-value>)',
        'jarvis-danger': 'rgb(var(--color-danger) / <alpha-value>)',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
