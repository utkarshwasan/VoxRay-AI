import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('🔴 ErrorBoundary caught an error:', error);
    console.error('📍 Component stack:', errorInfo.componentStack);
    
    this.setState({ errorInfo });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[300px] flex flex-col items-center justify-center bg-slate-900/50 rounded-2xl border border-red-500/30 p-8">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-white mb-2">
            Something went wrong
          </h2>
          <p className="text-slate-400 text-center mb-4 max-w-md">
            {this.props.fallbackMessage || 
              "We encountered an error while displaying this content. Please try again."}
          </p>
          
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details className="text-xs text-slate-500 bg-slate-800 p-4 rounded-lg mb-4 max-w-lg overflow-auto">
              <summary className="cursor-pointer text-slate-400 mb-2">
                Error Details (Dev Only)
              </summary>
              <pre className="whitespace-pre-wrap">
                {this.state.error.toString()}
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
          
          <button
            onClick={this.handleRetry}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
