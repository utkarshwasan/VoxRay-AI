import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { StackProvider, StackTheme } from "@stackframe/react";
import { stackApp } from "./stack";
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StackProvider app={stackApp}>
    <StackTheme>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </StackTheme>
  </StackProvider>
)
