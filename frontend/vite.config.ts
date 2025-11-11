import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5002',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'monaco-editor': ['monaco-editor', '@monaco-editor/react'],
          'diff-viewer': ['react-diff-viewer-continued', 'diff', 'diff2html'],
          'export-utils': ['file-saver', 'jszip', 'jspdf'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['monaco-editor'],
  },
});
