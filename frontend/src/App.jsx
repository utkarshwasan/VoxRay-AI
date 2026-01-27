import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Sparkles } from 'lucide-react';
import { Routes, Route } from 'react-router-dom';
import { UserButton } from '@stackframe/react';
import XRaySection from './components/XRaySection';
import VoiceSection from './components/VoiceSection';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import OAuthCallbackHandler from './components/OAuthCallbackHandler';

const ParticleSystem = () => {
  const [particles, setParticles] = useState([]);
  useEffect(() => {
    const newParticles = Array.from({ length: 30 }).map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 4 + 2,
      duration: Math.random() * 10 + 10,
      delay: Math.random() * 5,
    }));
    setParticles(newParticles);
  }, []);
  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-white/20"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.5, 0.2],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: p.duration,
            repeat: Infinity,
            delay: p.delay,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
};

const GradientOrbs = () => {
  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      <div className="absolute top-0 left-0 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 animate-pulse-slow" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 animate-pulse-slow" style={{ animationDelay: '1s' }} />
    </div>
  );
};

function Dashboard() {
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [recentScans, setRecentScans] = useState([]);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 text-white relative overflow-x-hidden font-sans selection:bg-indigo-500/30">
      <ParticleSystem />
      <GradientOrbs />

      <div className="relative z-10 max-w-7xl mx-auto flex flex-col min-h-screen">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="sticky top-4 z-50 backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl mx-4 mb-8 shadow-xl shadow-black/5"
        >
          <div className="container mx-auto px-6 py-8 flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="relative w-12 h-12 flex items-center justify-center rounded-xl bg-gradient-to-br from-indigo-400 to-purple-600 shadow-lg shadow-indigo-500/20">
                <Activity className="w-7 h-7 text-white animate-spin-slow" />
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                  VoxRay AI
                  <Sparkles className="w-5 h-5 text-indigo-400 animate-pulse" />
                </h1>
                <p className="text-indigo-200/80 text-sm font-medium">
                  Test VoxRay Vision, Voice, and Intelligence models in one place
                </p>
              </div>
            </div>
            
            {/* Stack Auth User Button */}
            <UserButton showUserInfo={false} />
          </div>
        </motion.header>

        {/* Main Content */}
        <main className="flex-grow container mx-auto px-6 py-8 flex gap-8">
           <Sidebar 
             recentScans={recentScans} 
             onSelectScan={(scan) => setDiagnosisResult(scan)}
             currentScanId={diagnosisResult?.id}
           />
           
           <div className="flex-grow flex flex-col gap-8 min-w-0">
              <XRaySection 
                onResultChange={handleNewScan} 
                selectedResult={diagnosisResult?.fullResult}
              />
              <VoiceSection currentDiagnosis={diagnosisResult} />
           </div>
        </main>

        {/* Footer */}
        <footer className="py-8 text-center text-indigo-200/40 text-sm">
          <p>VoxRay AI Demo Console - For testing and demonstration purposes only</p>
        </footer>
      </div>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/handler/*" element={<OAuthCallbackHandler />} />
      {/* Protected Routes */}
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Dashboard />} />
      </Route>
    </Routes>
  );
}

export default App;
