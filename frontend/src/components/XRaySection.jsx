import React, { useState, useRef, startTransition } from 'react';
// eslint-disable-next-line no-unused-vars
import { AnimatePresence, motion } from 'framer-motion';
import { Upload, Activity, AlertCircle, CheckCircle, TrendingUp, FileUp, Sparkles, Info, BrainCircuit, ShieldCheck } from 'lucide-react';
import axios from 'axios';
import clsx from 'clsx';
import MagneticButton from './MagneticButton';
import InteractiveXRayViewer from './InteractiveXRayViewer';
import { ResultSkeleton } from './Skeleton';
import ConfidenceGauge from './ConfidenceGauge';
import Tooltip from './Tooltip';
import { useUser } from '@stackframe/react';
import { stackApp } from '../stack';
import { useFeatureFlags } from '../contexts/FeatureFlagContext';
import { Card } from './ui/Card';
import { DataBadge } from './ui/DataBadge';

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
  const { flags } = useFeatureFlags();

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
      
      // Use startTransition for state updates
      startTransition(() => {
        setAiAnalysis(response.data.response);
      });
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
    
    const useEnsemble = flags?.ensemble_model === true;
    
    try {
        const formData = new FormData();
        formData.append('image_file', file);
        
        const authHeaders = await getAuthHeaders();
        // V2 Integration with Fallback
        const endpoint = useEnsemble 
            ? `${API_BASE_URL}/v2/predict/image` 
            : `${API_BASE_URL}/predict/image`;
            
        let response;
        try {
             response = await axios.post(endpoint, formData, {
                headers: { 'Content-Type': 'multipart/form-data', ...authHeaders }
            });
        } catch (err) {
            // Graceful Fallback for V2 -> V1
             if (useEnsemble && err.response?.status === 503) {
                 console.warn("V2 Ensemble unavailable, falling back to V1");
                 response = await axios.post(`${API_BASE_URL}/predict/image`, formData, {
                    headers: { 'Content-Type': 'multipart/form-data', ...authHeaders }
                 });
             } else {
                 throw err;
             }
        }
        
        const data = response.data;
        
        // Use startTransition for heavy state updates to prevent React suspense crashes
        startTransition(() => {
          setResult(data);
          if (onResultChange) onResultChange(data);
        });
        
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
    if (d.includes("NORMAL")) return { variant: "normal", icon: CheckCircle, label: "Low Severity" };
    if (d.includes("PNEUMONIA")) return { variant: "warning", icon: TrendingUp, label: "Medium Severity" };
    return { variant: "critical", icon: AlertCircle, label: "High Severity" };
  };

  const severity = result ? getSeverityConfig(result.diagnosis) : null;

  return (
    <section className="relative">
      <Card variant="default" className="relative overflow-hidden border-white/10">
        
        <div className="flex items-center gap-4 mb-8 border-b border-white/5 pb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Diagnostic Imaging</h2>
            <div className="flex items-center gap-2 mt-1">
                 <span className="text-xs text-clinical-400 uppercase tracking-wider font-semibold">X-Ray Analysis Protocol</span>
                 {flags?.ensemble_model && (
                     <span className="px-2 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-[10px] text-indigo-300 font-medium flex items-center gap-1">
                         <ShieldCheck className="w-3 h-3" />
                         Ensemble V2 Active
                     </span>
                 )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column: Upload (Unchanged) */}
          <div className="flex flex-col gap-6">
            <div 
              className={clsx(
                "relative min-h-[440px] rounded-2xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center p-4 group overflow-visible",
                preview ? "border-indigo-500/50 bg-black/40" : "border-white/10 bg-white/[0.02] hover:border-indigo-400/30 hover:bg-white/[0.04]"
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
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
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
                    <div className="w-20 h-20 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center animate-float">
                      <FileUp className="w-9 h-9 text-indigo-300/80" />
                    </div>
                    <div>
                      <p className="text-lg font-medium text-clinical-100 mb-1">Drop DICOM/Image here</p>
                      <p className="text-sm text-clinical-400">or click to browse secure files</p>
                    </div>
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="mt-4 px-6 py-2.5 rounded-lg bg-medical-primary/10 border border-medical-primary/30 text-medical-primary text-sm font-medium hover:bg-medical-primary/20 transition-all hover:scale-105"
                    >
                      Select Diagnostic Image
                    </button>
                    <p className="text-xs text-clinical-500 mt-4">HIPAA Compliant Transfer • Max 10MB</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <MagneticButton
              disabled={!file || analyzing}
              onClick={handleAnalyze}
              className={clsx(
                "w-full h-12 rounded-xl font-semibold text-white shadow-lg transition-all relative overflow-hidden flex items-center justify-center",
                !file || analyzing ? "opacity-50 cursor-not-allowed bg-slate-800" : "bg-gradient-to-r from-medical-primary to-medical-secondary hover:shadow-clinical-glow scale-100 active:scale-[0.98]"
              )}
            >
              {analyzing ? (
                <div className="flex items-center justify-center gap-3">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span className="tracking-wide text-sm">Running Inference...</span>
                </div>
              ) : (
                <span className="tracking-wide">Analyze Scan</span>
              )}
            </MagneticButton>

            {result && file && (
              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                disabled={explaining}
                onClick={handleExplain}
                className={clsx(
                  "w-full h-10 rounded-xl font-medium text-sm transition-all flex items-center justify-center gap-2 border",
                  explaining 
                    ? "opacity-50 cursor-not-allowed bg-slate-800 border-slate-700 text-slate-400" 
                    : "bg-emerald-500/10 border-emerald-500/20 text-emerald-300 hover:bg-emerald-500/20"
                )}
              >
                {explaining ? (
                  <>
                    <Sparkles className="w-4 h-4 animate-pulse" />
                    <span>Processing Heatmap...</span>
                  </>
                ) : explainSrc ? (
                  <>
                    <Sparkles className="w-4 h-4 text-emerald-400" />
                    <span>Explanation Overlay Active</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Generate AI Explainability</span>
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
                  
                  {/* Primary Finding Card */}
                  <Card 
                    variant={severity.variant}
                    className="relative overflow-hidden border-l-4 backdrop-blur-md"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                             <severity.icon className={clsx("w-5 h-5", 
                                severity.variant === 'normal' ? 'text-diagnostic-normal' : 
                                severity.variant === 'warning' ? 'text-diagnostic-warning' : 'text-diagnostic-critical'
                             )} />
                             <span className="text-xs font-bold text-clinical-300 uppercase tracking-widest">Primary Diagnosis</span>
                        </div>
                        <h3 className="text-3xl font-bold text-white tracking-tight">{result.diagnosis.replace(/^\d+_/, '').replace(/_/g, ' ')}</h3>
                      </div>
                      <div className="flex flex-col items-end">
                         <DataBadge 
                            status={severity.variant} 
                            value={`${(result.confidence * 100).toFixed(1)}%`} 
                            label="Confidence"
                            className="mb-2"
                         />
                         <span className="text-[10px] text-clinical-400 uppercase tracking-wider font-medium">{flags?.ensemble_model ? 'Ensemble V2' : 'ResNet50 V1'}</span>
                      </div>
                    </div>
                    
                    {/* Severity Progress Bar */}
                    <div className="w-full h-1.5 bg-slate-900/50 rounded-full overflow-hidden mt-4">
                        <div 
                            className={clsx("h-full rounded-full transition-all duration-1000", 
                                severity.variant === 'normal' ? 'bg-diagnostic-normal w-1/3' : 
                                severity.variant === 'warning' ? 'bg-diagnostic-warning w-2/3' : 'bg-diagnostic-critical w-full'
                            )}
                        />
                    </div>
                    <div className="flex justify-between mt-1.5">
                        <span className="text-[10px] text-clinical-400 font-medium">Benign</span>
                        <span className="text-[10px] text-clinical-400 font-medium">Critical</span>
                    </div>
                  </Card>

                  {/* Enhanced Analysis Section */}
                  <div>
                    <h4 className="text-sm font-semibold text-clinical-200 mb-3 flex items-center gap-2 uppercase tracking-wider">
                      <BrainCircuit className="w-4 h-4 text-medical-accent" />
                      Clinical & AI Insights
                    </h4>
                    
                    <div className="relative overflow-hidden rounded-xl bg-black/20 border border-white/5 p-6 transition-colors min-h-[120px]">
                        {analyzingAI ? (
                            <div className="flex flex-col gap-3">
                                <div className="h-4 bg-white/5 rounded w-3/4 animate-pulse" />
                                <div className="h-4 bg-white/5 rounded w-full animate-pulse delay-75" />
                                <div className="h-4 bg-white/5 rounded w-2/3 animate-pulse delay-150" />
                                <div className="flex items-center gap-2 text-medical-accent/70 text-xs mt-2">
                                    <Sparkles className="w-3 h-3 animate-spin-slow" />
                                    <span>Synthesizing clinical summary...</span>
                                </div>
                            </div>
                        ) : aiAnalysis ? (
                            <div className="prose prose-invert prose-sm max-w-none">
                                <p className="text-clinical-100 leading-relaxed text-sm border-l-2 border-medical-accent/30 pl-4">
                                    {aiAnalysis}
                                </p>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full text-clinical-500 gap-2 py-4">
                                <BrainCircuit className="w-8 h-8 opacity-20" />
                                <p className="text-sm italic">Analysis ready for processing</p>
                            </div>
                        )}
                    </div>

                    {/* Disclaimer / Caution Box */}
                    <motion.div 
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        className="mt-4 flex gap-3 items-start p-3 rounded-lg bg-amber-500/[0.05] border border-amber-500/10"
                    >
                        <Info className="w-4 h-4 text-amber-500/80 flex-shrink-0 mt-0.5" />
                        <p className="text-[10px] text-amber-200/60 leading-relaxed">
                            <span className="font-semibold text-amber-500/80">Clinical Disclaimer:</span> AI analysis is adjunctive. Final diagnosis requires radiologist verification. 
                        </p>
                    </motion.div>
                  </div>
                </motion.div>
              ) : (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center justify-center h-full text-center p-8 opacity-40 min-h-[300px]"
                >
                  <div className="w-24 h-24 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 rotate-3">
                    <Activity className="w-10 h-10 text-white" />
                  </div>
                  <h3 className="text-xl font-medium text-white mb-2">Ready for Analysis</h3>
                  <p className="text-sm text-clinical-400 max-w-xs mx-auto">Upload a medical image to initialize the diagnostic pipeline.</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </Card>
    </section>
  );
};

export default XRaySection;
