/* eslint-env node */
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    // alias removed for debugging
  },
  server: {
    port: 5173,
    strictPort: true,
  },
  build: {
    // Better error messages in production
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate heavy dependencies
          'react-vendor': ['react', 'react-dom'],
          'framer': ['framer-motion'],
        }
      }
    }
  },
  // Ensure consistent environment
  define: {
    // eslint-disable-next-line no-undef
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'production')
  }
})
