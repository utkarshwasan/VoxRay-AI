import React from 'react';
// eslint-disable-next-line no-unused-vars
import { AnimatePresence, motion } from 'framer-motion';
import { Clock, ChevronRight, Activity } from 'lucide-react';
import clsx from 'clsx';

const Sidebar = ({ recentScans, onSelectScan, currentScanId }) => {
  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-80 flex-shrink-0 hidden lg:flex flex-col gap-4"
    >
      <div className="glass-panel bg-noise rounded-2xl p-6 flex-grow overflow-hidden flex flex-col h-[calc(100vh-8rem)] sticky top-24">
        <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
          <Clock className="w-5 h-5 text-indigo-400" />
          Recent Scans
        </h3>

        <div className="flex-grow overflow-y-auto space-y-3 pr-2 custom-scrollbar">
          <AnimatePresence initial={false}>
            {recentScans.length === 0 ? (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center text-white/40 py-12 text-sm flex flex-col items-center gap-3"
              >
                <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center">
                  <Activity className="w-6 h-6 text-white/20" />
                </div>
                <p>No recent scans</p>
              </motion.div>
            ) : (
              recentScans.map((scan) => (
                <motion.div
                  key={scan.id}
                  layout
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={() => onSelectScan(scan)}
                  className={clsx(
                    "p-4 rounded-xl border transition-all cursor-pointer group relative overflow-hidden",
                    currentScanId === scan.id
                      ? "bg-indigo-500/20 border-indigo-500/50 shadow-lg shadow-indigo-500/10"
                      : "bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20 hover:scale-[1.02]"
                  )}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className={clsx(
                      "text-sm font-bold tracking-wide",
                      scan.diagnosis.includes("NORMAL") ? "text-emerald-300" : "text-amber-300"
                    )}>
                      {scan.diagnosis.replace(/^\d+_/, '').replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] uppercase tracking-wider text-white/40 font-medium bg-white/5 px-2 py-0.5 rounded-full">
                      {scan.timestamp}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between mt-2">
                     <div className="flex items-center gap-2">
                       <div className={clsx(
                         "w-1.5 h-1.5 rounded-full",
                         scan.diagnosis.includes("NORMAL") ? "bg-emerald-400" : "bg-amber-400"
                       )} />
                       <span className="text-xs text-white/60 font-medium">
                         {(scan.confidence * 100).toFixed(1)}% Confidence
                       </span>
                     </div>
                     <ChevronRight className={clsx(
                       "w-4 h-4 text-white/40 transition-transform duration-300",
                       currentScanId === scan.id ? "translate-x-1 text-indigo-400" : "group-hover:translate-x-1"
                     )} />
                  </div>

                  {/* Active Indicator */}
                  {currentScanId === scan.id && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-indigo-500" />
                  )}
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
