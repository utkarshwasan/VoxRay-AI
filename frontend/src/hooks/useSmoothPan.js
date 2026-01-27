import { useRef } from 'react';

const DEFAULT_PAN_CONFIG = {
  sensitivity: 0.6,           // Reduced from typical 2.5
  deadzone: 2,                // Ignore sub-2px movements (mouse jitter)
  smoothing: 0.15,            // Light inertia for smooth feel
  maxVelocity: 40             // Prevent jumps on fast mouse flicks
};

export const useSmoothPan = (config = DEFAULT_PAN_CONFIG) => {
  const velocityRef = useRef({ x: 0, y: 0 });
  const lastDeltaRef = useRef({ x: 0, y: 0 });
  
  const calculatePanDelta = (rawDeltaX, rawDeltaY) => {
    // Apply deadzone
    const absX = Math.abs(rawDeltaX);
    const absY = Math.abs(rawDeltaY);
    
    const adjustedX = absX < config.deadzone ? 0 : rawDeltaX;
    const adjustedY = absY < config.deadzone ? 0 : rawDeltaY;
    
    // Apply sensitivity
    const targetX = adjustedX * config.sensitivity;
    const targetY = adjustedY * config.sensitivity;
    
    // Smooth interpolation (lerp)
    velocityRef.current.x += (targetX - velocityRef.current.x) * config.smoothing;
    velocityRef.current.y += (targetY - velocityRef.current.y) * config.smoothing;
    
    // Clamp to max velocity
    const clampedX = Math.max(-config.maxVelocity, 
                      Math.min(config.maxVelocity, velocityRef.current.x));
    const clampedY = Math.max(-config.maxVelocity, 
                      Math.min(config.maxVelocity, velocityRef.current.y));
    
    return { x: clampedX, y: clampedY };
  };
  
  return { calculatePanDelta };
};
