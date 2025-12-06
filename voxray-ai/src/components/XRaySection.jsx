import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, Activity, AlertCircle, CheckCircle, TrendingUp, FileUp } from 'lucide-react';
import axios from 'axios';
import clsx from 'clsx';
import MagneticButton from './MagneticButton';
import InteractiveXRayViewer from './InteractiveXRayViewer';
import { ResultSkeleton } from './Skeleton';
import ConfidenceGauge from './ConfidenceGauge';
import Tooltip from './Tooltip';

const XRaySection = ({ onResultChange, selectedResult }) => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  // Sync with external selection (Sidebar)
  React.useEffect(() => {
    if (selectedResult) {
      setResult(selectedResult);
      // We don't have the image for history items in this demo, so we keep the preview as is
      // or clear it if it doesn't match. For now, let's leave the preview alone 
      // or maybe clear it to avoid confusion if it doesn't match the result.
      // But clearing it might look weird. 
      // Let's just update the result card.
    }
  }, [selectedResult]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      if (onResultChange) onResultChange(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const selectedFile = e.dataTransfer.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      if (onResultChange) onResultChange(null);
    }
  };

  const clearFile = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    if (onResultChange) onResultChange(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setAnalyzing(true);
    
    try {
        const formData = new FormData();
        formData.append('image_file', file);
        
        const response = await axios.post('http://127.0.0.1:8000/predict/image', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        setResult(response.data);
        if (onResultChange) onResultChange(response.data);

    } catch (error) {
        console.error("Analysis failed", error);
        alert("Analysis failed. Ensure backend is running.");
    } finally {
        setAnalyzing(false);
    }
  };

  const getSeverityConfig = (diagnosis) => {
    const d = diagnosis?.toUpperCase() || "";
    if (d.includes("NORMAL")) return { color: "from-emerald-400 to-teal-500", icon: CheckCircle, label: "Low Severity", text: "text-emerald-200", bg: "bg-emerald-500/20", border: "border-emerald-500/30" };
    if (d.includes("PNEUMONIA")) return { color: "from-amber-400 to-yellow-500", icon: TrendingUp, label: "Medium Severity", text: "text-amber-200", bg: "bg-amber-500/20", border: "border-amber-500/30" };
    return { color: "from-red-400 to-orange-500", icon: AlertCircle, label: "High Severity", text: "text-red-200", bg: "bg-red-500/20", border: "border-red-500/30" };
  };

  const severity = result ? getSeverityConfig(result.diagnosis) : null;

  return (
    <section className="relative">
      <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 to-purple-500/5 rounded-2xl blur-xl" />
      <div className="relative glass-panel bg-noise rounded-2xl p-8 overflow-hidden">
        
        {/* Section Header */}
        <div className="flex items-center gap-4 mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-400 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-white">X-Ray Analysis</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column: Upload */}
          <div className="flex flex-col gap-6">
            <div 
              className={clsx(
                "relative min-h-[360px] rounded-2xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center p-6 group overflow-hidden",
                preview ? "border-indigo-500/50 bg-black/20" : "border-white/20 bg-white/5 hover:border-indigo-400/50 hover:bg-white/10 hover:scale-[1.02]"
              )}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
            >
              <input 
                type="file" 
                ref={fileInputRef}
                className="hidden" 
                accept="image/*"
                onChange={handleFileChange}
              />

              <AnimatePresence mode="wait">
                {preview ? (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="relative w-full h-full flex items-center justify-center"
                  >
                    <InteractiveXRayViewer 
                      src={preview} 
                      alt="X-Ray Preview" 
                      onClose={clearFile}
                    />
                  </motion.div>
                ) : (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center flex flex-col items-center gap-4"
                  >
                    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-white/20 flex items-center justify-center animate-float">
                      <FileUp className="w-10 h-10 text-indigo-300" />
                    </div>
                    <div>
                      <p className="text-lg font-medium text-white mb-1">Drop X-Ray image here</p>
                      <p className="text-sm text-indigo-200/60">or click to upload</p>
                    </div>
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="mt-4 px-6 py-2 rounded-lg bg-white/5 border border-white/20 text-sm font-medium hover:bg-white/10 transition-all hover:scale-105"
                    >
                      Select File
                    </button>
                    <p className="text-xs text-white/30 mt-4">Supports DICOM, JPEG, PNG (max 10MB)</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <MagneticButton
              disabled={!file || analyzing}
              onClick={handleAnalyze}
              className={clsx(
                "w-full h-12 rounded-lg font-medium text-white shadow-lg transition-all relative overflow-hidden",
                !file || analyzing ? "opacity-50 cursor-not-allowed bg-slate-700" : "bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 shadow-indigo-500/25"
              )}
            >
              {analyzing ? (
                <div className="flex items-center justify-center gap-2">
                  <Activity className="w-5 h-5 animate-spin" />
                  <span>Analyzing Scan...</span>
                </div>
              ) : (
                <span>Analyze X-Ray</span>
              )}
              {analyzing && (
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full animate-[shimmer_1.5s_infinite]" />
              )}
            </MagneticButton>
          </div>

          {/* Right Column: Results */}
          <div className="flex flex-col justify-center">
            <AnimatePresence mode="wait">
              {analyzing ? (
                <motion.div
                  key="skeleton"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <ResultSkeleton />
                </motion.div>
              ) : result ? (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-6"
                >
                  {/* Primary Finding Badge */}
                  <motion.div 
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className={clsx(
                        "relative overflow-hidden rounded-xl border p-6 backdrop-blur-sm",
                        severity.bg, severity.border
                    )}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <span className="text-xs font-medium text-emerald-200/70 uppercase tracking-wider">Primary Finding</span>
                        <h3 className="text-2xl font-bold text-white mt-1">{result.diagnosis.replace(/^\d+_/, '').replace(/_/g, ' ')}</h3>
                      </div>
                      <div className={clsx("px-3 py-1 rounded-lg bg-white/10 backdrop-blur text-xs font-bold border border-white/10", severity.text)}>
                        {(result.confidence * 100).toFixed(1)}% Confidence
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-4">
                      <div className={clsx("w-2 h-2 rounded-full animate-pulse", severity.text.replace('text-', 'bg-'))} />
                      <span className={clsx("text-sm font-medium", severity.text)}>{severity.label}</span>
                    </div>
                  </motion.div>

                  {/* Detailed Analysis */}
                  <div>
                    <h4 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                      <span className="w-1 h-5 bg-indigo-500 rounded-full" />
                      Analysis Details
                    </h4>
                    <div className="space-y-3">
                      <DiagnosisCard 
                        label={result.diagnosis} 
                        confidence={result.confidence} 
                        severity={severity}
                        index={0}
                      />
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center justify-center h-full text-center p-8 opacity-50"
                >
                  <div className="w-24 h-24 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-4 rotate-12">
                    <Activity className="w-12 h-12 text-white/50" />
                  </div>
                  <p className="text-lg text-white/60">Upload an X-Ray image to begin analysis</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
};

const MEDICAL_DEFINITIONS = {
  "PNEUMONIA": "Infection that inflames air sacs in one or both lungs, which may fill with fluid.",
  "NORMAL": "No significant abnormalities detected in the chest X-ray.",
  "INFILTRATION": "A substance denser than air, such as pus, blood, or protein, which lingers within the parenchyma of the lungs.",
  "ATELECTASIS": "Complete or partial collapse of the entire lung or area (lobe) of the lung.",
  "EFFUSION": "A buildup of fluid between the tissues that line the lungs and the chest.",
  "NODULE": "A small abnormal growth in the lung, often benign but requires monitoring.",
  "PNEUMOTHORAX": "A collapsed lung. This occurs when air leaks into the space between your lung and chest wall.",
  "CONSOLIDATION": "A region of normally compressible lung tissue that has filled with liquid instead of air."
};

import useTypewriter from '../hooks/useTypewriter';

const DiagnosisCard = ({ label, confidence, severity, index }) => {
  const cleanLabel = label.replace(/^\d+_/, '').replace(/_/g, ' ');
  const typedLabel = useTypewriter(cleanLabel, 50);
  const definition = MEDICAL_DEFINITIONS[cleanLabel.toUpperCase()] || "Medical condition detected in X-Ray analysis.";

  return (
    <motion.div
      initial={{ opacity: 0, x: -20, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      transition={{ delay: index * 0.1 + 0.3, type: "spring", stiffness: 300, damping: 25 }}
      whileHover={{ scale: 1.02, x: 4, backgroundColor: "rgba(255, 255, 255, 0.12)" }}
      className="relative overflow-hidden rounded-xl bg-black/20 border border-white/10 p-4 transition-colors group flex items-center justify-between gap-4"
    >
      <div className="flex-grow">
        <div className="flex items-center gap-3 mb-2">
          <severity.icon className={clsx("w-5 h-5", severity.text)} />
          <Tooltip content={definition}>
            <span className="font-medium text-white text-lg border-b border-dashed border-white/30 cursor-help">
              {typedLabel}
              <span className="animate-pulse">|</span>
            </span>
          </Tooltip>
        </div>
        <p className={clsx("text-sm", severity.text)}>{severity.label}</p>
      </div>

      <div className="flex-shrink-0">
        <ConfidenceGauge 
          value={confidence} 
          color={severity.text.replace('text-', 'text-')} 
          size={64}
        />
      </div>

      {/* Shimmer Overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:animate-[shimmer_2s_infinite]" />
    </motion.div>
  );
};

export default XRaySection;
