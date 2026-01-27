import React, { useState, useRef, useCallback, useEffect } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, X, Sun, Contrast, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSmoothPan } from '../hooks/useSmoothPan';
import { useSmoothZoom } from '../hooks/useSmoothZoom';

/**
 * Reusable image control slider component with label and value display
 */
const ImageControl = ({ icon: Icon, label, value, onChange, min, max, colorClass, unit = '%' }) => (
  <div className="flex flex-col gap-2 min-w-[140px] w-full">
    {/* Header: Label + Inline Value */}
    <div className="flex justify-between items-center text-xs font-medium">
      <div className="flex items-center gap-2 text-white/80">
        <Icon className={`w-3.5 h-3.5 ${colorClass}`} />
        <span>{label}</span>
      </div>
      <span className={`font-mono tabular-nums ${colorClass}`}>
        {Math.round(value)}{unit}
      </span>
    </div>

    {/* Input Slider */}
    <div className="relative h-6 flex items-center">
        <input
            type="range"
            min={min}
            max={max}
            value={value}
            onChange={onChange}
            className={`w-full h-1.5 cursor-pointer rounded-full appearance-none bg-slate-700/50 
            [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 
            [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer
            [&::-webkit-slider-thumb]:shadow-md [&::-webkit-slider-thumb]:transition-transform
            [&::-webkit-slider-thumb]:hover:scale-110
            ${colorClass === 'text-yellow-400' ? '[&::-webkit-slider-thumb]:bg-yellow-400' : ''}
            ${colorClass === 'text-blue-400' ? '[&::-webkit-slider-thumb]:bg-blue-400' : ''}
            ${colorClass === 'text-emerald-400' ? '[&::-webkit-slider-thumb]:bg-emerald-400' : ''}
            `}
            aria-label={`${label} control`}
        />
    </div>
  </div>
);

/**
 * Zoom control button component
 */
const ControlBtn = ({ onClick, icon: Icon, label }) => (
  <motion.button
    whileHover={{ scale: 1.1 }}
    whileTap={{ scale: 0.95 }}
    onClick={onClick}
    className="w-9 h-9 bg-slate-900/80 backdrop-blur-sm rounded-lg flex items-center justify-center 
      border border-white/10 text-white hover:bg-white/10 hover:border-white/20 
      transition-all shadow-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
    title={label}
    aria-label={label}
  >
    <Icon className="w-4 h-4" />
  </motion.button>
);

const InteractiveXRayViewer = ({ src, alt, onClose, overlaySrc }) => {
  // Window/Level controls (Brightness/Contrast)
  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const [overlayOpacity, setOverlayOpacity] = useState(0.5);

  const containerRef = useRef(null);
  const imageRef = useRef(null);
  
  // State for Pan and Zoom
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [isDragging, setIsDragging] = useState(false);
  
  // --- Hooks ---
  const { calculatePanDelta } = useSmoothPan({
    sensitivity: 0.6,      // Calibrated for medical precision
    deadzone: 2,
    smoothing: 0.15,
    maxVelocity: 40
  });

  // Note: we're passing setZoom to the hook, but we also manage some zoom logic here for wheel
  const { zoom: smoothZoom, targetZoomRef } = useSmoothZoom(1.0, setZoom);

  // --- Helpers ---
  
  // Constrain Pan to keep image within view (with some overscroll)
  const constrainPan = useCallback((proposedPan, currentZoom) => {
    if (!containerRef.current || !imageRef.current) return proposedPan;

    const containerRec = containerRef.current.getBoundingClientRect();
    // Native image size isn't directly available unless we load it, 
    // but we can use the current rendered size if zoom was 1
    // A better approach for exact constraints is to know naturalWidth/Height.
    // tailored for the typical simplified viewer: allow dragging until edge acts as center
    
    // Simple constraint: don't let the image fly completely off screen
    // Allow moving the image until its center hits the edge of the container
    const maxPanX = (containerRec.width * 1.5 * currentZoom) / 2; 
    const maxPanY = (containerRec.height * 1.5 * currentZoom) / 2;

    return {
      x: Math.max(-maxPanX, Math.min(maxPanX, proposedPan.x)),
      y: Math.max(-maxPanY, Math.min(maxPanY, proposedPan.y))
    };
  }, []);


  // --- Event Handlers ---

  const handleMouseDown = useCallback((e) => {
    if (e.button !== 0) return; // Only left click
    setIsDragging(true);
    e.preventDefault();
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging) return;
    
    const delta = calculatePanDelta(e.movementX, e.movementY);
    
    // Apply zoom-aware scaling: Higher zoom = slower pan
    const zoomFactor = 1 / Math.sqrt(zoom);
    
    setPan(prev => constrainPan({
      x: prev.x + delta.x * zoomFactor,
      y: prev.y + delta.y * zoomFactor
    }, zoom));
  }, [isDragging, zoom, calculatePanDelta, constrainPan]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleWheel = useCallback((e) => {
    if (!containerRef.current) return;
    e.preventDefault();

    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    // 1. Calculate new Target Zoom
    const ZOOM_SENSITIVITY = 0.001;
    const delta = -e.deltaY * ZOOM_SENSITIVITY;
    const newTargetZoom = Math.max(0.5, Math.min(5.0, zoom + delta)); // Simplified: direct update for now or use hook logic
    
    // We will manually update zoom here to sync with pan, 
    // effectively bypassing the smooth loop for the *calculation* but we can still use it if we want.
    // For the specific "Zoom to Cursor" requirement, direct calculation is often more robust than 
    // trying to sync two independent animation loops (pan & zoom).
    
    // Let's implement the precise Zoom-To-Cursor logic here directly:
    
    // Calculate mouse position relative to center (0,0 of pan coordinates)
    // The image center is at (containerWidth/2 + pan.x, containerHeight/2 + pan.y)
    // Mouse relative to Image Center:
    const containerCenterX = rect.width / 2;
    const containerCenterY = rect.height / 2;
    
    // This is the vector from the center of the container to the mouse
    const mouseFromCenterX = mouseX - containerCenterX;
    const mouseFromCenterY = mouseY - containerCenterY;
    
    // And from the center of the *image* (which is offset by pan)
    // const mouseFromImageCenterX = mouseFromCenterX - pan.x;
    // const mouseFromImageCenterY = mouseFromCenterY - pan.y;

    // Calculate Zoom Ratio
    const zoomRatio = newTargetZoom / zoom;

    // New Pan:
    // We want the point under the mouse to stay under the mouse.
    // (Point - Newcenter) = (Point - OldCenter) * ratio
    // ... logic simplifies to adjusting pan by the displacement of the point relative to center
    
    const newPanX = pan.x - (mouseFromCenterX - pan.x) * (zoomRatio - 1);
    const newPanY = pan.y - (mouseFromCenterY - pan.y) * (zoomRatio - 1);

    setZoom(newTargetZoom);
    setPan({ x: newPanX, y: newPanY });

  }, [zoom, pan]);

  // Button Controls
  const handleZoomIn = () => setZoom(z => Math.min(z * 1.2, 5));
  const handleZoomOut = () => setZoom(z => Math.max(z / 1.2, 0.5));
  const handleReset = useCallback(() => {
    setPan({ x: 0, y: 0 });
    setZoom(1);
    setBrightness(100);
    setContrast(100);
  }, []);

  // --- Styles ---
  const imageStyle = {
    filter: `brightness(${brightness}%) contrast(${contrast}%)`,
    transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
    cursor: isDragging ? 'grabbing' : 'grab',
  };

  return (
    <div className="relative w-full h-full flex flex-col">
      {/* Close Button - Top Right, Small & Subtle */}
      {onClose && (
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={onClose}
          className="absolute top-3 right-3 z-50 w-7 h-7 bg-red-500/90 backdrop-blur-sm rounded-md 
            flex items-center justify-center border border-white/10 text-white 
            hover:bg-red-600 transition-all shadow-md
            focus:outline-none focus:ring-2 focus:ring-red-500/50"
          aria-label="Remove image"
        >
          <X className="w-3.5 h-3.5 stroke-[2.5]" />
        </motion.button>
      )}

      {/* Image Viewer Area */}
      <div 
        ref={containerRef}
        className="flex-grow flex items-center justify-center bg-black/40 rounded-t-lg overflow-hidden relative min-h-[280px]"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      >
          {/* Zoom Controls - Left Side, Always Visible */}
          <div className="absolute top-4 left-4 z-20 flex flex-col gap-2 pointer-events-auto">
            <ControlBtn onClick={handleZoomIn} icon={ZoomIn} label="Zoom In" />
            <ControlBtn onClick={handleZoomOut} icon={ZoomOut} label="Zoom Out" />
            <ControlBtn onClick={handleReset} icon={RotateCcw} label="Reset View" />
          </div>

          <div className="relative w-full h-full flex items-center justify-center pointer-events-none">
              {/* Wrapper div to center the transformed image */}
              <img 
                ref={imageRef}
                src={src} 
                alt={alt} 
                className="max-h-[80%] max-w-[80%] w-auto h-auto object-contain rounded-lg shadow-2xl pointer-events-auto select-none" 
                style={imageStyle}
                draggable={false}
              />
              {/* Grad-CAM Overlay */}
              {overlaySrc && (
                <img
                  src={overlaySrc}
                  alt="Explanation Heatmap"
                  className="absolute inset-0 w-full h-full object-contain rounded-lg pointer-events-none"
                  style={{ 
                    ...imageStyle, // Apply same transform to overlay
                    opacity: overlayOpacity,
                    mixBlendMode: 'overlay',
                    filter: 'none' // Don't double apply brightness/contrast to heatmap usually, or maybe yes? default to no
                  }}
                  draggable={false}
                />
              )}
          </div>
      </div>

      {/* Control Panel - Grid Layout */}
      <div className="p-4 bg-slate-800/95 backdrop-blur-md rounded-b-lg border-t border-white/10 shadow-lg relative z-40">
        <div className={`grid gap-4 transition-all duration-300 ease-in-out ${overlaySrc ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1 md:grid-cols-2'}`}>
            {/* Primary Controls Group */}
            <div className="contents md:flex md:gap-8 md:items-end w-full"> 
                {/* Brightness */}
                <ImageControl 
                    icon={Sun}
                    label="Brightness"
                    value={brightness}
                    onChange={(e) => setBrightness(Number(e.target.value))}
                    min={50}
                    max={150}
                    colorClass="text-yellow-400"
                />
                
                {/* Contrast */}
                <ImageControl 
                    icon={Contrast}
                    label="Contrast"
                    value={contrast}
                    onChange={(e) => setContrast(Number(e.target.value))}
                    min={50}
                    max={150}
                    colorClass="text-blue-400"
                />
            </div>

            {/* Heatmap Control - Animated Expansion */}
            <AnimatePresence>
                {overlaySrc && (
                    <motion.div
                        initial={{ opacity: 0, height: 0, marginTop: 0 }}
                        animate={{ opacity: 1, height: 'auto', marginTop: 16 }}
                        exit={{ opacity: 0, height: 0, marginTop: 0 }}
                        transition={{ duration: 0.3, ease: 'easeInOut' }}
                        className="col-span-1 md:col-span-2 w-full border-t border-white/10 pt-4"
                    >
                         <ImageControl 
                            icon={Sparkles}
                            label="Heatmap Opacity"
                            value={overlayOpacity * 100}
                            onChange={(e) => setOverlayOpacity(Number(e.target.value) / 100)}
                            min={0}
                            max={100}
                            colorClass="text-emerald-400"
                        />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default InteractiveXRayViewer;
