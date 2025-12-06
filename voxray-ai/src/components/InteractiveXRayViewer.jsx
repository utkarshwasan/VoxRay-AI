import React from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { ZoomIn, ZoomOut, RotateCcw, Maximize } from 'lucide-react';
import { motion } from 'framer-motion';

const InteractiveXRayViewer = ({ src, alt, onClose }) => {
  return (
    <div className="relative w-full h-full flex items-center justify-center bg-black/40 rounded-lg overflow-hidden group">
      <TransformWrapper
        initialScale={1}
        minScale={0.5}
        maxScale={4}
        centerOnInit
      >
        {({ zoomIn, zoomOut, resetTransform }) => (
          <>
            <div className="absolute top-4 left-4 z-20 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <ControlBtn onClick={() => zoomIn()} icon={ZoomIn} label="Zoom In" />
              <ControlBtn onClick={() => zoomOut()} icon={ZoomOut} label="Zoom Out" />
              <ControlBtn onClick={() => resetTransform()} icon={RotateCcw} label="Reset" />
            </div>

            <TransformComponent wrapperClass="!w-full !h-full" contentClass="!w-full !h-full flex items-center justify-center">
              <img 
                src={src} 
                alt={alt} 
                className="max-h-[320px] w-auto object-contain rounded-lg shadow-2xl" 
              />
            </TransformComponent>
          </>
        )}
      </TransformWrapper>

      {onClose && (
        <motion.button
          whileHover={{ scale: 1.1, rotate: 90 }}
          whileTap={{ scale: 0.9 }}
          onClick={onClose}
          className="absolute top-2 right-2 z-20 w-8 h-8 bg-slate-900/80 backdrop-blur rounded-full flex items-center justify-center border border-white/20 text-white hover:bg-red-500/80 transition-colors"
        >
          <Maximize className="w-4 h-4 rotate-45" />
        </motion.button>
      )}
    </div>
  );
};

const ControlBtn = ({ onClick, icon: Icon, label }) => (
  <button
    onClick={onClick}
    className="w-8 h-8 bg-black/50 backdrop-blur rounded-lg flex items-center justify-center border border-white/10 text-white hover:bg-white/20 transition-all"
    title={label}
  >
    <Icon className="w-4 h-4" />
  </button>
);

export default InteractiveXRayViewer;
