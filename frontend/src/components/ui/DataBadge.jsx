import React from 'react';
import clsx from 'clsx';

export const DataBadge = ({ status = 'info', value, label, className }) => {
  const statusColors = {
    normal: 'text-diagnostic-normal bg-diagnostic-normal/10 border-diagnostic-normal/20',
    warning: 'text-diagnostic-warning bg-diagnostic-warning/10 border-diagnostic-warning/20',
    critical: 'text-diagnostic-critical bg-diagnostic-critical/10 border-diagnostic-critical/20',
    info: 'text-diagnostic-info bg-diagnostic-info/10 border-diagnostic-info/20',
    neutral: 'text-clinical-300 bg-white/5 border-white/10',
  };
  
  return (
    <div className={clsx('inline-flex items-center px-3 py-1.5 rounded-lg border text-diagnostic-sm font-medium transition-colors', statusColors[status], className)}>
      {label && <span className="opacity-70 mr-2">{label}:</span>}
      <span className="font-bold tracking-wide">{value}</span>
    </div>
  );
};
