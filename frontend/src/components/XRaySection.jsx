import React, { useState, useRef } from 'react';
// eslint-disable-next-line no-unused-vars
import { AnimatePresence, motion } from 'framer-motion';
import { Upload, Activity, AlertCircle, CheckCircle, TrendingUp, FileUp, Sparkles, Info, BrainCircuit } from 'lucide-react';
import axios from 'axios';
import clsx from 'clsx';
import MagneticButton from './MagneticButton';
import InteractiveXRayViewer from './InteractiveXRayViewer';
import { ResultSkeleton } from './Skeleton';
import ConfidenceGauge from './ConfidenceGauge';
import Tooltip from './Tooltip';
import { useUser } from '@stackframe/react';
import { stackApp } from '../stack';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const XRaySection = ({ onResultChange, selectedResult }) => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  
  // New State for AI Analysis
  const [aiAnalysis, setAiAnalysis] = useState("");
  const [analyzingAI, setAnalyzingAI] = useState(false);

  const fileInputRef = useRef(null);
  
  // Explainability state
  const [explainSrc, setExplainSrc] = useState(null);
  const [explaining, setExplaining] = useState(false);

  // Stack Auth user for authenticated requests
  const user = useUser();

  // Sync with external selection (Sidebar)
  React.useEffect(() => {
    if (selectedResult) {
      setResult(selectedResult);
      // If we select a result from history that doesn't have analysis stored, we might want to regenerate or leave blank.
      // For now, we'll clear it unless it was passed (future enhancement)
      setAiAnalysis(""); 
    }
  }, [selectedResult]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      setAiAnalysis("");
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
      setAiAnalysis("");
      if (onResultChange) onResultChange(null);
    }
  };

  const clearFile = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setExplainSrc(null);
    setAiAnalysis("");
    if (onResultChange) onResultChange(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const getAuthHeaders = async () => {
    try {
      const currentUser = await stackApp.getUser();
      if (currentUser) {
        if (typeof currentUser.getAuthJson === 'function') {
          const authJson = await currentUser.getAuthJson();
          const token = authJson?.accessToken || authJson?.access_token || authJson?.token;
          if (token) return { 'x-stack-access-token': token };
        }
        if (typeof currentUser.getAuthHeaders === 'function') {
          const headers = await currentUser.getAuthHeaders();
          if (headers && Object.keys(headers).length > 0) return headers;
        }
      }
      if (user && typeof user.getAuthJson === 'function') {
        const authJson = await user.getAuthJson();
        const token = authJson?.accessToken || authJson?.access_token;
        if (token) return { 'x-stack-access-token': token };
      }
      return {};
    } catch (e) {
      console.warn('Failed to get auth token', e);
      return {};
    }
  };

  // Function to fetch concise AI analysis
  const generateAIAnalysis = async (diagnosisData) => {
    setAnalyzingAI(true);
    try {
      const authHeaders = await getAuthHeaders();
      // Construct a prompt for the LLM
      const prompt = `The patient's X-Ray shows ${diagnosisData.diagnosis} with ${(diagnosisData.confidence * 100).toFixed(1)}% confidence. Provide a concise, professional 3-4 line clinical analysis summarising what this condition implies and standard next steps. Keep it strictly under 60 words.`;
      
      const response = await axios.post(`${API_BASE_URL}/chat`, { 
        message: prompt,
        context: `Diagnosis: ${diagnosisData.diagnosis}`
      }, {
        headers: { ...authHeaders }
      });
      
      setAiAnalysis(response.data.response);
    } catch (error) {
      console.error("AI Analysis failed", error);
      // Provide informative fallback with diagnosis info
      const diagnosisName = diagnosisData.diagnosis?.replace(/^\d+_/, '').replace(/_/g, ' ') || 'Unknown';
      const confidenceStr = (diagnosisData.confidence * 100).toFixed(1);
      setAiAnalysis(
        `Analysis complete: ${diagnosisName} detected with ${confidenceStr}% confidence. ` +
        `AI Voice Assistant is temporarily offline. Please consult a medical professional for detailed interpretation.`
      );
    } finally {
      setAnalyzingAI(false);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setAnalyzing(true);
    setAiAnalysis(""); // Clear previous
    
    try {
        const formData = new FormData();
        formData.append('image_file', file);
        
        const authHeaders = await getAuthHeaders();
        const response = await axios.post(`${API_BASE_URL}/predict/image`, formData, {
            headers: { 'Content-Type': 'multipart/form-data', ...authHeaders }
        });
        
        const data = response.data;
        setResult(data);
        if (onResultChange) onResultChange(data);
        
        // Trigger AI Analysis after successful prediction
        generateAIAnalysis(data);

    } catch (error) {
        console.error("Analysis failed", error);
        if (error.response?.status === 401) {
          alert("Authentication required. Please log in.");
        } else if (error.response?.status === 503) {
          // Model is still loading or unavailable
          alert("AI Engine is warming up. Please try again in 30 seconds.");
        } else if (error.code === 'ERR_NETWORK') {
          alert("Cannot connect to server. Please check if the backend is running.");
        } else {
          alert("Analysis failed. Please try again.");
        }
    } finally {
        setAnalyzing(false);
    }
  };

  const handleExplain = async () => {
    if (!file) return;
    setExplaining(true);
    setExplainSrc(null);
    
    try {
        const formData = new FormData();
        formData.append('image_file', file);
        
        const authHeaders = await getAuthHeaders();
        const response = await axios.post(`${API_BASE_URL}/predict/explain`, formData, {
            headers: { 'Content-Type': 'multipart/form-data', ...authHeaders }
        });
        
        const heatmapDataUrl = `data:image/png;base64,${response.data.heatmap_b64}`;
        setExplainSrc(heatmapDataUrl);

    } catch (error) {
        console.error("Explanation failed", error);
        alert("Explanation generation failed.");
    } finally {
        setExplaining(false);
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
        
        <div className="flex items-center gap-4 mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-400 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-white">X-Ray Analysis</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column: Upload (Unchanged) */}
          <div className="flex flex-col gap-6">
            <div 
              className={clsx(
                "relative min-h-[440px] rounded-2xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center p-4 group overflow-visible",
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
                      overlaySrc={explainSrc}
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
            </MagneticButton>

            {result && file && (
              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                disabled={explaining}
                onClick={handleExplain}
                className={clsx(
                  "w-full h-10 rounded-lg font-medium text-white transition-all flex items-center justify-center gap-2 border",
                  explaining 
                    ? "opacity-50 cursor-not-allowed bg-slate-700 border-slate-600" 
                    : "bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border-emerald-500/30 hover:from-emerald-500/30 hover:to-teal-500/30"
                )}
              >
                {explaining ? (
                  <>
                    <Sparkles className="w-4 h-4 animate-pulse" />
                    <span>Generating Explanation...</span>
                  </>
                ) : explainSrc ? (
                  <>
                    <Sparkles className="w-4 h-4 text-emerald-400" />
                    <span className="text-emerald-300">Explanation Active</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Explain Diagnosis</span>
                  </>
                )}
              </motion.button>
            )}
          </div>

          {/* Right Column: Results */}
          <div className="flex flex-col justify-center">
            <AnimatePresence mode="wait">
              {analyzing ? (
                <motion.div key="skeleton" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <ResultSkeleton />
                </motion.div>
              ) : result ? (
                <motion.div key="result" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
                  
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

                  {/* Enhanced Analysis Section */}
                  <div>
                    <h4 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                      <BrainCircuit className="w-5 h-5 text-indigo-400" />
                      AI Analysis Details
                    </h4>
                    
                    <div className="relative overflow-hidden rounded-xl bg-black/20 border border-white/10 p-5 transition-colors">
                        {analyzingAI ? (
                            <div className="flex items-center gap-3 text-indigo-200/60 animate-pulse">
                                <Sparkles className="w-4 h-4" />
                                <span className="text-sm">Generating concise clinical summary...</span>
                            </div>
                        ) : aiAnalysis ? (
                            <div className="prose prose-invert prose-sm max-w-none">
                                <p className="text-indigo-100/90 leading-relaxed text-sm">
                                    {aiAnalysis}
                                </p>
                            </div>
                        ) : (
                            <p className="text-white/40 text-sm italic">Analysis will appear here after processing.</p>
                        )}
                        
                        {/* Shimmer Effect while analyzing */}
                        {analyzingAI && (
                             <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full animate-[shimmer_1.5s_infinite]" />
                        )}
                    </div>

                    {/* Disclaimer / Caution Box */}
                    <motion.div 
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        className="mt-4 flex gap-3 items-start p-3 rounded-lg bg-amber-500/10 border border-amber-500/20"
                    >
                        <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                        <p className="text-xs text-amber-200/80 leading-relaxed">
                            <span className="font-bold text-amber-400">Disclaimer:</span> I am an AI assistant, not a doctor. This analysis is generated for informational purposes only and may contain errors. Please consult a qualified medical professional for a detailed diagnosis and treatment plan.
                        </p>
                    </motion.div>
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

export default XRaySection;
