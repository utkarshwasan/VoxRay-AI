import React from 'react';

const PageLoader = () => (
  <div className="min-h-screen bg-slate-900 flex items-center justify-center">
    <div className="flex flex-col items-center gap-4">
      <div className="animate-spin w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full"></div>
      <p className="text-slate-400">Loading VoxRay AI...</p>
    </div>
  </div>
);

export default PageLoader;
