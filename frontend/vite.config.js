import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Prevent duplicate React instances in production
      'react': path.resolve(__dirname, 'node_modules/react'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom'),
    },
    dedupe: ['react', 'react-dom']
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
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'production')
  }
})
