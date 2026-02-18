import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Sparkles, LayoutGrid, Mic, FileText, User } from 'lucide-react';
import { UserButton } from '@stackframe/react';
import clsx from 'clsx';

// Components
import XRaySection from '../components/XRaySection';
import VoiceSection from '../components/VoiceSection';
import Worklist from '../components/Worklist';
import Sidebar from '../components/Sidebar';
import { useFeatureFlags } from '../contexts/FeatureFlagContext';

export default function Dashboard() {
  const [activeView, setActiveView] = useState('analysis');
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [recentScans, setRecentScans] = useState([]);
  const { flags } = useFeatureFlags();

  const handleNewScan = (result) => {
    if (result) {
        const newScan = {
            id: Date.now(),
            diagnosis: result.diagnosis,
            confidence: result.confidence,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            fullResult: result
        };
        setRecentScans(prev => [newScan, ...prev]);
        setDiagnosisResult(newScan);
    } else {
        setDiagnosisResult(null);
    }
  };

  const menuItems = [
      { id: 'analysis', label: 'Analysis', icon: LayoutGrid },
      { id: 'worklist', label: 'Worklist', icon: FileText },
      { id: 'voice', label: 'Voice Assistant', icon: Mic },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-clinical-950 via-slate-900 to-clinical-950 text-clinical-100 font-sans selection:bg-medical-primary/30">
      
      {/* Professional Medical Header */}
      <header className="sticky top-0 z-50 glass-clinical border-b border-white/[0.08] backdrop-blur-xl">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-medical-primary to-medical-secondary flex items-center justify-center shadow-lg shadow-medical-primary/20">
              <Activity className="w-5 h-5 text-white animate-pulse-slow" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                VoxRay AI <span className="text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-clinical-300 font-mono tracking-wider">CLINICAL</span>
              </h1>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            {/* View Navigation (Desktop) */}
            <nav className="hidden md:flex bg-white/5 rounded-lg p-1 border border-white/5">
                {menuItems.map(item => (
                    <button
                        key={item.id}
                        onClick={() => setActiveView(item.id)}
                        className={clsx(
                            "px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-200 flex items-center gap-2",
                            activeView === item.id 
                                ? "bg-medical-primary text-white shadow-sm" 
                                : "text-clinical-400 hover:text-white hover:bg-white/5"
                        )}
                    >
                        <item.icon className="w-4 h-4" />
                        {item.label}
                    </button>
                ))}
            </nav>

            <div className="h-6 w-px bg-white/10 hidden md:block" />
            
            {/* User Profile */}
            <UserButton showUserInfo={true} />
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Left Sidebar - History (Only visible in Analysis Mode) */}
            <AnimatePresence>
                {activeView === 'analysis' && (
                    <motion.div 
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20, width: 0 }}
                        className="lg:col-span-3 hidden lg:block"
                    >
                        <Sidebar 
                            recentScans={recentScans}
                            onSelectScan={(scan) => setDiagnosisResult(scan)}
                            currentScanId={diagnosisResult?.id}
                        />
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Main Stage */}
            <div className={clsx(
                "transition-all duration-300",
                activeView === 'analysis' ? "lg:col-span-9" : "lg:col-span-12"
            )}>
                <AnimatePresence mode="wait">
                    {activeView === 'analysis' && (
                        <motion.div
                            key="analysis"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                        >
                            <XRaySection 
                                onResultChange={handleNewScan}
                                selectedResult={diagnosisResult?.fullResult}
                            />
                        </motion.div>
                    )}

                    {activeView === 'worklist' && (
                        <motion.div
                            key="worklist"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="max-w-5xl mx-auto"
                        >
                            <Worklist 
                                onSelectScan={(item) => {
                                    // Mock converting worklist item to result for analysis
                                    const result = {
                                        id: item.id,
                                        diagnosis: item.diagnosis,
                                        confidence: item.confidence,
                                        fullResult: { diagnosis: item.diagnosis, confidence: item.confidence } // Mock
                                    }
                                    setDiagnosisResult(result);
                                    setActiveView('analysis');
                                }}
                            />
                        </motion.div>
                    )}

                    {activeView === 'voice' && (
                        <motion.div
                            key="voice"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="max-w-4xl mx-auto"
                        >
                            <VoiceSection currentDiagnosis={diagnosisResult} />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
      </main>
    </div>
  );
}
