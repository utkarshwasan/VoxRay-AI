import React from 'react';
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { StackProvider, StackTheme } from "@stackframe/react";
import { stackApp } from "./stack";
import './index.css'
import App from './App.jsx'

// Global error logging for production debugging
window.addEventListener('error', (event) => {
  console.error('🔴 Global error:', event.error);
  console.error('📍 Error location:', event.filename, event.lineno, event.colno);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('🔴 Unhandled promise rejection:', event.reason);
  console.error('📍 Promise:', event.promise);
});

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <StackProvider app={stackApp}>
      <StackTheme>
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <App />
        </BrowserRouter>
      </StackTheme>
    </StackProvider>
  </React.StrictMode>
)
