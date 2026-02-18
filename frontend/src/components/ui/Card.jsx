import React from 'react';
import clsx from 'clsx';

export const Card = ({ variant = 'default', children, className, ...props }) => {
  const variants = {
    default: 'glass-clinical',
    normal: 'card-normal glass-clinical',
    warning: 'card-warning glass-clinical',
    critical: 'card-critical glass-clinical',
    ghost: 'bg-transparent border border-white/5',
  };
  
  return (
    <div 
      className={clsx('rounded-xl p-6 transition-all duration-300', variants[variant], className)} 
      {...props}
    >
      {children}
    </div>
  );
};
