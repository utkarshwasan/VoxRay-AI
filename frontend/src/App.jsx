import React, { Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import SuspenseWrapper from './components/SuspenseWrapper';
import PageLoader from './components/PageLoader';
import Login from './pages/Login';
import OAuthCallbackHandler from './components/OAuthCallbackHandler';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import { FeatureFlagProvider } from './contexts/FeatureFlagContext';

function App() {
  return (
    <ErrorBoundary fallbackMessage="Application error. Please refresh the page.">
      <FeatureFlagProvider>
        <SuspenseWrapper fallback={<PageLoader />}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/handler/*" element={<OAuthCallbackHandler />} />
            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<Dashboard />} />
            </Route>
          </Routes>
        </SuspenseWrapper>
      </FeatureFlagProvider>
    </ErrorBoundary>
  );
}

export default App;
