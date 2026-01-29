import React, { Suspense } from 'react';

/**
 * Reusable Suspense wrapper with customizable fallback
 * Prevents React Error #426 by providing proper boundaries
 */
const SuspenseWrapper = ({ 
  children, 
  fallback = null,
  type = 'default' // 'default', 'card', 'full', 'inline'
}) => {
  
  const getFallback = () => {
    if (fallback) return fallback;
    
    switch (type) {
      case 'card':
        return (
          <div className="animate-pulse bg-slate-800/50 rounded-2xl p-6 min-h-[200px]">
            <div className="h-4 bg-slate-700 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
            <div className="h-20 bg-slate-700 rounded"></div>
          </div>
        );
      
      case 'full':
        return (
          <div className="min-h-screen flex items-center justify-center">
            <div className="animate-spin w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full"></div>
          </div>
        );
      
      case 'inline':
        return (
          <span className="inline-flex items-center gap-2 text-slate-400">
            <div className="animate-spin w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full"></div>
            Loading...
          </span>
        );
      
      default:
        return (
          <div className="flex items-center justify-center p-8">
            <div className="animate-pulse flex flex-col items-center gap-4">
              <div className="w-16 h-16 bg-slate-700 rounded-full"></div>
              <div className="h-4 bg-slate-700 rounded w-32"></div>
            </div>
          </div>
        );
    }
  };

  return (
    <Suspense fallback={getFallback()}>
      {children}
    </Suspense>
  );
};

export default SuspenseWrapper;
