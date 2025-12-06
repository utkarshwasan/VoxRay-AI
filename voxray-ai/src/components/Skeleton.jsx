import React from 'react';
import clsx from 'clsx';

const Skeleton = ({ className }) => {
  return (
    <div className={clsx("animate-pulse bg-white/10 rounded-lg", className)} />
  );
};

export const ResultSkeleton = () => {
  return (
    <div className="space-y-6 w-full">
      {/* Primary Finding Skeleton */}
      <div className="rounded-xl border border-white/10 p-6 bg-white/5">
        <div className="flex justify-between mb-4">
          <div className="space-y-2">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-8 w-48" />
          </div>
          <Skeleton className="h-6 w-20 rounded-full" />
        </div>
        <div className="flex items-center gap-2 mt-4">
          <Skeleton className="h-2 w-2 rounded-full" />
          <Skeleton className="h-4 w-32" />
        </div>
      </div>

      {/* Details Skeleton */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Skeleton className="h-5 w-1 rounded-full" />
          <Skeleton className="h-6 w-32" />
        </div>
        <div className="space-y-3">
          <div className="rounded-xl bg-white/5 border border-white/10 p-4">
            <div className="flex justify-between mb-2">
              <div className="flex items-center gap-3">
                <Skeleton className="h-5 w-5 rounded-full" />
                <Skeleton className="h-5 w-40" />
              </div>
              <Skeleton className="h-4 w-12" />
            </div>
            <Skeleton className="h-2 w-full rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Skeleton;
