import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square, Sparkles, Activity, RefreshCw, Volume2, AlertCircle } from 'lucide-react';
import axios from 'axios';
import AudioRecorderPolyfill from 'audio-recorder-polyfill';
import { useUser } from '@stackframe/react';
import PropTypes from 'prop-types';


// --- CONFIG ---
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const RECORDING_LIMIT = 60; // seconds
const WARNING_TIME = 30;
const CRITICAL_TIME = 50;
const MAX_HISTORY_LENGTH = 6;
const MAX_MESSAGE_LENGTH = 500;

// Voice Activity Detection (VAD) for Sterile Mode
// Voice Activity Detection (VAD) for Sterile Mode
const SILENCE_THRESHOLD = 0.025;      // Optimized for time-domain (0.025 = -32dB)
const SILENCE_DURATION_MS = 1500;     // 1.5 seconds of silence triggers stop
const MIN_SPEECH_DURATION_MS = 500;   // Minimum recording before silence detection
const VAD_INTERVAL_MS = 50;           // Polling rate

// Quick action definitions with specific prompts
const QUICK_ACTIONS = [
  { label: 'Explain Findings', prompt: 'Explain the radiological findings detected in this scan' },
  { label: 'Check Severity', prompt: 'What is the severity level of this condition and what does it mean' },
  { label: 'Next Steps', prompt: 'What are the recommended next steps for this diagnosis' }
];

// --- UTILS ---
const generateId = () => {
  return typeof crypto !== 'undefined' && crypto.randomUUID 
    ? crypto.randomUUID() 
    : `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Check if user prefers reduced motion
 */
const prefersReducedMotion = () => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

// --- SUB-COMPONENTS ---

// 1. Voice Orb (The Visual Core) + VAD Debugger
const VoiceOrb = React.memo(({ status, recordingTime, onClick, debugRMS, showDebug }) => {
  // Calculate ring progress (circumference ~289)
  const progress = Math.min((recordingTime / RECORDING_LIMIT) * 289, 289);
  
  const getStrokeColor = () => {
    if (recordingTime >= CRITICAL_TIME) return '#ef4444'; // Red
    if (recordingTime >= WARNING_TIME) return '#f59e0b'; // Amber
    return 'url(#gradient)';
  };

  const getAriaLabel = () => {
    switch (status) {
      case 'IDLE': return 'Start voice recording';
      case 'LISTENING': return 'Stop recording';
      case 'PROCESSING': return 'Processing request';
      case 'SPEAKING': return 'Stop playback';
      default: return 'Voice assistant';
    }
  };

  // Memoize particles to prevent jitter on re-render
  const particles = useMemo(() => [...Array(8)].map((_, i) => ({
    id: i,
    left: `${15 + Math.random() * 70}%`,
    delay: i * 0.3
  })), []);

  return (
    <div className="relative w-24 h-24 flex items-center justify-center">
      {/* Particle System (Only active when listening) */}
      <AnimatePresence>
        {status === 'LISTENING' && (
          <>
            {particles.map((p) => (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 0, scale: 0.5 }}
                animate={{ opacity: [0, 1, 0], y: -70, scale: 0 }}
                transition={{ duration: 2.5, repeat: Infinity, delay: p.delay, ease: "easeOut" }}
                className="absolute w-1.5 h-1.5 bg-white/80 rounded-full pointer-events-none"
                style={{ left: p.left, top: '50%' }}
              />
            ))}
          </>
        )}
      </AnimatePresence>

      {/* Progress Ring SVG */}
      <svg className="absolute inset-0 w-full h-full drop-shadow-[0_0_10px_rgba(239,68,68,0.3)]" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="46" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
        {status === 'LISTENING' && (
          <circle 
            cx="50" cy="50" r="46" 
            fill="none" 
            stroke={getStrokeColor()} 
            strokeWidth="3" 
            strokeLinecap="round" 
            strokeDasharray="289" 
            strokeDashoffset={289 - progress}
            className="transition-all duration-300 ease-linear transform -rotate-90 origin-center" 
          />
        )}
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ef4444" />
            <stop offset="100%" stopColor="#ec4899" />
          </linearGradient>
        </defs>
      </svg>

      {/* Main Interaction Button */}
      <motion.button
        onClick={onClick}
        onKeyDown={(e) => (e.key === ' ' || e.key === 'Enter') && onClick()}
        aria-label={getAriaLabel()}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        animate={status === 'LISTENING' 
          ? { scale: [1, 1.05, 1], boxShadow: "0 0 40px rgba(239,68,68,0.6)" } 
          : { scale: 1, boxShadow: "0 0 0px rgba(0,0,0,0)" }
        }
        transition={{ repeat: status === 'LISTENING' ? Infinity : 0, duration: 2 }}
        className={`relative w-16 h-16 rounded-full flex items-center justify-center border border-white/20 z-10 
          transition-all duration-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900
          ${status === 'LISTENING' 
            ? 'bg-gradient-to-br from-red-500 to-pink-600 focus-visible:ring-red-400' 
            : status === 'PROCESSING'
              ? 'bg-gradient-to-br from-amber-500 to-orange-600 focus-visible:ring-amber-400'
              : status === 'SPEAKING'
                ? 'bg-gradient-to-br from-emerald-500 to-teal-600 shadow-[0_0_30px_rgba(16,185,129,0.4)] focus-visible:ring-emerald-400'
                : 'bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg focus-visible:ring-indigo-400'
          }`}
      >
        {status === 'LISTENING' ? (
          <Square className="w-5 h-5 text-white fill-current rounded-sm" />
        ) : status === 'PROCESSING' ? (
          <RefreshCw className="w-6 h-6 text-white animate-spin" />
        ) : status === 'SPEAKING' ? (
          <Volume2 className="w-6 h-6 text-white" />
        ) : (
          <Mic className="w-6 h-6 text-white" />
        )}
      </motion.button>
      
      {/* Status Text & Timer */}
      <div className="absolute -bottom-8 text-[10px] font-mono font-semibold tracking-widest transition-colors duration-300 w-full text-center">
        {status === 'LISTENING' ? (
          <span className={recordingTime >= CRITICAL_TIME ? 'text-red-400' : recordingTime >= WARNING_TIME ? 'text-amber-400' : 'text-red-300/90'}>
            00:{recordingTime.toString().padStart(2, '0')}
          </span>
        ) : status === 'PROCESSING' ? (
          <span className="text-amber-300/80 animate-pulse">THINKING...</span>
        ) : status === 'SPEAKING' ? (
          <span className="text-emerald-300/80 animate-pulse">SPEAKING</span>
        ) : (
          <span className="text-white/30">HOLD TO SPEAK</span>
        )}
      </div>

      {/* Live Region for Screen Readers */}
      <div role="status" aria-live="polite" className="sr-only">
        {status === 'LISTENING' && `Recording: ${recordingTime} seconds`}
        {status === 'PROCESSING' && 'Processing your request'}
        {status === 'SPEAKING' && 'Playing AI response'}
      </div>

      {/* VAD Visual Debug Overlay (Only in Sterile Mode) */}
      {showDebug && debugRMS > 0.005 && (
        <div className="absolute inset-0 pointer-events-none z-0 flex items-center justify-center">
            {/* Soft Ripple Base - Always visible when sound detected */}
            <motion.div
              animate={{
                scale: [1, 1 + (debugRMS * 3)], // Reduced scale from 15 to 3
                opacity: [0.1, 0.4]
              }}
              transition={{ duration: 0.1, ease: 'easeOut' }}
              className={`absolute rounded-full w-full h-full border-2 ${debugRMS > SILENCE_THRESHOLD ? 'border-emerald-500/30' : 'border-red-500/20'}`}
            />
            
            {/* Threshold Ring Marker - Subtle guide */}
             <div 
               className="absolute rounded-full border border-dashed border-white/20" 
               style={{ 
                 width: `${100 + (SILENCE_THRESHOLD * 200)}%`, // Calibrated visual marker
                 height: `${100 + (SILENCE_THRESHOLD * 200)}%` 
               }} 
             />

             {/* Dynamic Sound Wave */}
            {debugRMS > SILENCE_THRESHOLD && (
                 <motion.div
                  initial={{ scale: 1, opacity: 0.6 }}
                  animate={{ scale: 1.5, opacity: 0 }} // Reduced max scale
                  transition={{ duration: 1, repeat: Infinity, ease: "easeOut" }}
                  className="absolute rounded-full w-full h-full border border-emerald-500/40"
                 />
             )}
        </div>
      )}
    </div>
  );
});
VoiceOrb.displayName = 'VoiceOrb';

// 2. Karaoke Text (Word-by-word reveal)
const KaraokeText = React.memo(({ text }) => {
  const words = useMemo(() => text.split(" "), [text]);
  const [revealedIndex, setRevealedIndex] = useState(-1);

  useEffect(() => {
    setRevealedIndex(-1);
    if (words.length === 0) return;

    let index = -1;
    // Estimated reading speed: ~200ms per word
    const interval = setInterval(() => {
      if (index >= words.length - 1) {
        clearInterval(interval);
      }
      setRevealedIndex(prev => {
        index = prev + 1;
        return index;
      });
    }, 200);
    
    return () => clearInterval(interval);
  }, [text, words.length]);

  return (
    <p>
      {words.map((word, i) => (
        <span 
          key={i} 
          className={`transition-colors duration-200 ${i <= revealedIndex ? 'text-white' : 'text-white/30'}`}
        >
          {word}{" "}
        </span>
      ))}
    </p>
  );
});
KaraokeText.displayName = 'KaraokeText';

// 3. Chat Message (Handles User, AI, and Error messages)
const ChatMessage = React.memo(({ msg, onRetry, isRetrying }) => {
  const isAI = msg.role === 'assistant';
  const isError = msg.role === 'error';
  
  return (
    <motion.div 
      layout
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className={`flex items-start gap-3 ${isAI || isError ? 'pr-6' : 'pl-10 justify-end'}`}
    >
      {(isAI || isError) && (
        <div className={`w-7 h-7 rounded-full border flex items-center justify-center flex-shrink-0 mt-1
          ${isError ? 'bg-rose-900/30 border-rose-500/20' : 'bg-emerald-900/30 border-emerald-500/20'}`}>
          {isError ? <AlertCircle className="w-3.5 h-3.5 text-rose-400" /> : <Sparkles className="w-3.5 h-3.5 text-emerald-400" />}
        </div>
      )}
      
      <div className={`
        relative px-4 py-3 rounded-2xl border text-xs leading-relaxed shadow-lg backdrop-blur-md
        ${isError 
          ? 'bg-rose-900/20 border-rose-500/30 text-rose-200 rounded-tl-none'
          : isAI 
            ? 'bg-white/5 border-white/10 rounded-tl-none text-slate-200' 
            : 'bg-gradient-to-br from-indigo-600 to-purple-700 border-white/10 rounded-tr-none text-white'
        }
      `}>
        {isAI && msg.isNew ? <KaraokeText text={msg.text} /> : <p>{msg.text}</p>}
        
        {/* Retry Button for Errors */}
        {isError && msg.retryable && msg.originalInput && (
          <div className="mt-2 flex gap-2">
            <button 
              onClick={() => onRetry && onRetry(msg.originalInput)}
              disabled={isRetrying}
              className={`px-3 py-1.5 rounded-full border text-[10px] transition-all flex items-center gap-1.5
                ${isRetrying 
                  ? 'bg-white/5 border-white/10 text-white/50 cursor-not-allowed' 
                  : 'bg-white/10 hover:bg-white/20 border-white/10 text-white hover:scale-105'
                }`}
            >
              <RefreshCw className={`w-3 h-3 ${isRetrying ? 'animate-spin' : ''}`} />
              {isRetrying ? 'Retrying...' : 'Retry'}
            </button>
          </div>
        )}
      </div>

      {!isAI && !isError && (
        <div className="w-7 h-7 rounded-full bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center flex-shrink-0 mt-1 text-[9px] text-indigo-200 font-bold">
          You
        </div>
      )}
    </motion.div>
  );
});
ChatMessage.displayName = 'ChatMessage';

// --- MAIN CONTAINER ---

const VoiceSection = ({ currentDiagnosis }) => {
  const [status, setStatus] = useState('IDLE'); // IDLE, LISTENING, PROCESSING, SPEAKING
  const [messages, setMessages] = useState([]);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isSterileMode, setIsSterileMode] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);
  const [debugRMS, setDebugRMS] = useState(0); // For Visual Debugger

  // Refs
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioPlayerRef = useRef(null);
  const scrollRef = useRef(null);
  const timerRef = useRef(null);
  const messagesRef = useRef(messages);
  const isProcessingRef = useRef(false);
  
  // VAD refs for silence detection
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const silenceStartRef = useRef(null);
  const vadIntervalRef = useRef(null);
  const recordingStartTimeRef = useRef(null);
  
  const user = useUser();

  // 1. Auto-scroll to bottom with reduced motion support
  useEffect(() => {
    if (scrollRef.current) {
      const reducedMotion = prefersReducedMotion();
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: reducedMotion ? 'auto' : 'smooth'
      });
    }
  }, [messages, status]);

  // Keep messagesRef in sync
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  // 2. Timer & Auto-Stop Logic
  useEffect(() => {
    if (status === 'LISTENING') {
      timerRef.current = setInterval(() => {
        setRecordingTime(t => {
          if (t >= RECORDING_LIMIT) {
            // Check ref directly to avoid dependency cycle
            if (mediaRecorderRef.current?.state === 'recording') {
              mediaRecorderRef.current.stop();
            }
            return t;
          }
          return t + 1;
        });
      }, 1000);
    } else {
      clearInterval(timerRef.current);
      setRecordingTime(0);
    }
    return () => clearInterval(timerRef.current);
  }, [status]);

  // 3. Audio Memory Cleanup
  useEffect(() => {
    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  // Auth Helper
  const getAuthHeaders = useCallback(async () => {
    try {
      const authJson = user ? await user.getAuthJson() : null;
      return authJson?.accessToken ? { 'x-stack-access-token': authJson.accessToken } : {};
    } catch { return {}; }
  }, [user]);

  // --- CORE LOGIC ---

  /**
   * Add a message to the conversation
   * @param {string} role - 'user', 'assistant', or 'error'
   * @param {string} text - Message content
   * @param {object} extras - Additional properties (isNew, retryable, originalInput)
   */
  const addMessage = useCallback((role, text, extras = {}) => {
    const newMessage = {
      id: generateId(),
      role,
      text,
      timestamp: new Date(),
      ...extras
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  }, []);

  // Unified Handler: Text Input -> Chat -> TTS -> Play
  const processTextQuery = useCallback(async (text) => {
    // Prevent concurrent processing
    if (isProcessingRef.current) {
      console.warn('Already processing a request');
      return;
    }
    
    // Check network connectivity
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      setMessages(prev => [...prev, { 
        id: generateId(), 
        role: 'error', 
        text: 'You appear to be offline. Please check your connection.',
        retryable: false 
      }]);
      return;
    }
    
    isProcessingRef.current = true;
    setStatus('PROCESSING');
    
    // Add user message (deduplicated)
    const currentMessages = messagesRef.current;
    const lastMessage = currentMessages[currentMessages.length - 1];
    const isDuplicate = lastMessage?.role === 'user' && 
                        lastMessage?.text === text &&
                        Date.now() - new Date(lastMessage.timestamp).getTime() < 2000;
    
    if (!isDuplicate) {
      setMessages(prev => [...prev, { id: generateId(), role: 'user', text, timestamp: new Date() }]);
    }

    try {
      const headers = await getAuthHeaders();
      
      // Build context string for backend
      const contextStr = currentDiagnosis 
        ? `Diagnosis: ${currentDiagnosis.diagnosis}, Confidence: ${(currentDiagnosis.confidence * 100).toFixed(1)}%` 
        : null;
      
      // Build history payload (filtered and truncated)
      const historyPayload = currentMessages
        .filter(m => m.role !== 'error')
        .slice(-MAX_HISTORY_LENGTH)
        .map(m => ({ 
          role: m.role, 
          text: m.text.length > MAX_MESSAGE_LENGTH 
            ? m.text.substring(0, MAX_MESSAGE_LENGTH) + '...' 
            : m.text 
        }));

      // Chat API call with history
      const chatRes = await axios.post(`${API_BASE}/chat`, { 
        message: text, 
        context: contextStr,
        history: historyPayload
      }, { headers });
      
      const aiText = chatRes.data.response;

      // TTS API call
      const ttsRes = await axios.post(
        `${API_BASE}/generate/speech`, 
        { text: aiText }, 
        { headers, responseType: 'blob' }
      );
      
      const url = URL.createObjectURL(ttsRes.data);
      setAudioUrl(url);
      
      setMessages(prev => [...prev, { 
        id: generateId(), 
        role: 'assistant', 
        text: aiText, 
        isNew: true, 
        timestamp: new Date() 
      }]);
      
      // Play audio
      setStatus('SPEAKING');
      if (audioPlayerRef.current) {
        audioPlayerRef.current.src = url;
        audioPlayerRef.current.play().catch(err => {
          console.error('Audio playback error:', err);
          setStatus('IDLE');
        });
      }

    } catch (e) {
      console.error('Query processing error:', e);
      setStatus('IDLE');
      
      let errorText = 'Something went wrong. Please try again.';
      if (e.response?.status === 401) {
        errorText = 'Session expired. Please refresh the page.';
      } else if (e.response?.status === 503) {
        errorText = 'Server is unavailable. Please try again later.';
      } else if (e.code === 'ERR_NETWORK') {
        errorText = 'Network error. Please check your connection.';
      }
      
      setMessages(prev => [...prev, { 
        id: generateId(),
        role: 'error', 
        text: errorText, 
        retryable: e.response?.status !== 401,
        originalInput: text
      }]);
    } finally {
      isProcessingRef.current = false;
      setIsRetrying(false);
    }
  }, [currentDiagnosis, getAuthHeaders]);

  // Retry a failed message
  const handleRetry = useCallback((originalInput) => {
    if (originalInput && !isProcessingRef.current) {
      setIsRetrying(true);
      processTextQuery(originalInput);
    }
  }, [processTextQuery]);

  // Clear all messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Handler: Audio Blob -> Transcribe -> processTextQuery
  const processAudioBlob = useCallback(async () => {
    if (audioChunksRef.current.length === 0) {
      setStatus('IDLE');
      return;
    }

    if (isProcessingRef.current) {
      return;
    }

    isProcessingRef.current = true;
    setStatus('PROCESSING');

    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
      audioChunksRef.current = []; // Clear early to prevent reprocessing
      
      const formData = new FormData();
      formData.append('audio_file', audioBlob);
      const headers = await getAuthHeaders();

      const sttRes = await axios.post(`${API_BASE}/transcribe/audio`, formData, { headers });
      const userText = sttRes.data.transcription?.trim();
      
      if (!userText) {
        setStatus('IDLE');
        addMessage('error', "I didn't catch that. Please try again.", { retryable: false });
        isProcessingRef.current = false;
        return;
      }
      
      isProcessingRef.current = false;
      await processTextQuery(userText);

    } catch (e) {
      console.error('Audio processing error:', e);
      setStatus('IDLE');
      addMessage('error', "Couldn't process audio. Please try again.", { retryable: false });
      isProcessingRef.current = false;
    }
  }, [getAuthHeaders, processTextQuery, addMessage]);

  // --- CONTROLS ---

  // VAD Helper: Stop monitoring and cleanup
  const stopVAD = useCallback(() => {
    if (vadIntervalRef.current) {
      clearInterval(vadIntervalRef.current);
      vadIntervalRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close().catch(() => {});
    }
    audioContextRef.current = null;
    analyserRef.current = null;
    silenceStartRef.current = null;
    recordingStartTimeRef.current = null;
  }, []);

  const startRecording = useCallback(async () => {
    if (status !== 'IDLE') return;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new AudioRecorderPolyfill(stream);
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.addEventListener('dataavailable', (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      });
      
      recorder.addEventListener('stop', () => {
        stopVAD(); // Cleanup VAD before processing
        stream.getTracks().forEach(track => track.stop());
        processAudioBlob();
      });

      recorder.start();
      setStatus('LISTENING');
      recordingStartTimeRef.current = Date.now();

      // --- VAD: Setup Audio Analysis (only in sterile mode) ---
      if (isSterileMode) {
        try {
          const audioContext = new (window.AudioContext || window.webkitAudioContext)();
          const source = audioContext.createMediaStreamSource(stream);
          const analyser = audioContext.createAnalyser();
          analyser.fftSize = 512;               // Increased for time-domain
          analyser.smoothingTimeConstant = 0.4;  // Fast decay for snappier feedback
          source.connect(analyser);
          
          audioContextRef.current = audioContext;
          analyserRef.current = analyser;
          silenceStartRef.current = null;

          const dataArray = new Float32Array(analyser.fftSize); // FLOAT for time-domain

          // Monitor volume at 50ms intervals (High-res)
          vadIntervalRef.current = setInterval(() => {
            if (!analyserRef.current || !dataArray) return;
            
            analyserRef.current.getFloatTimeDomainData(dataArray); // WAVEFORM data (Physics-based)
            
            // Calculate True RMS (Root Mean Square) for sound pressure
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
              sum += dataArray[i] * dataArray[i];
            }
            const rms = Math.sqrt(sum / dataArray.length);
            
            setDebugRMS(rms); // Update UI Overlay
            
            const now = Date.now();
            const recordingDuration = now - (recordingStartTimeRef.current || now);
            
            // Only start checking for silence after minimum speech duration
            if (recordingDuration < MIN_SPEECH_DURATION_MS) {
              return;
            }
            
            if (rms < SILENCE_THRESHOLD) {
              // Below threshold - silence detected
              if (!silenceStartRef.current) {
                silenceStartRef.current = now;
              } else if (now - silenceStartRef.current >= SILENCE_DURATION_MS) {
                // Silence duration exceeded - auto-stop
                console.log('VAD: Silence detected, auto-stopping recording');
                if (mediaRecorderRef.current?.state === 'recording') {
                  mediaRecorderRef.current.stop();
                }
              }
            } else {
              // Sound detected - reset silence timer
              silenceStartRef.current = null;
            }
          }, VAD_INTERVAL_MS);

        } catch (vadError) {
          console.warn('VAD setup failed, continuing without auto-stop:', vadError);
        }
      }

    } catch (e) {
      console.error("Microphone error:", e);
      addMessage('error', "Microphone access denied. Please check permissions.", { retryable: false });
    }
  }, [status, processAudioBlob, addMessage, isSterileMode, stopVAD]);

  const stopRecording = useCallback(() => {
    stopVAD(); // Always cleanup VAD first
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      // NOTE: Status update happens in processAudioBlob after 'stop' event fires
    }
  }, [stopVAD]);

  const stopPlayback = useCallback(() => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current.currentTime = 0;
    }
    setStatus('IDLE');
  }, []);

  const handleOrbClick = useCallback(() => {
    if (status === 'IDLE') startRecording();
    else if (status === 'LISTENING') stopRecording();
    else if (status === 'SPEAKING') stopPlayback();
  }, [status, startRecording, stopRecording, stopPlayback]);

  // Sterile mode: Auto-listen after AI response ends
  useEffect(() => {
    if (isSterileMode && status === 'IDLE' && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage?.role === 'assistant') {
        const timer = setTimeout(() => {
          startRecording();
        }, 2000);
        return () => clearTimeout(timer);
      }
    }
  }, [isSterileMode, status, messages, startRecording]);

  // Sterile mode: Auto-prompt on new diagnosis
  useEffect(() => {
    if (isSterileMode && currentDiagnosis && status === 'IDLE' && messages.length === 0) {
      const timer = setTimeout(() => {
        processTextQuery("Explain the findings detected in this scan");
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [isSterileMode, currentDiagnosis, status, messages.length, processTextQuery]);


  return (
    <div className={`relative min-h-[600px] w-full rounded-3xl overflow-hidden shadow-2xl border border-white/10 group bg-slate-950 transition-all duration-500 ${isSterileMode ? 'ring-2 ring-emerald-500/30 scale-[1.01]' : ''}`}>
      
      {/* Background Layers */}
      <div className="absolute inset-0 bg-slate-900 z-0"></div>
      <div className="absolute -top-20 -right-20 w-80 h-80 bg-purple-600/20 rounded-full blur-[100px] animate-blob"></div>
      <div className="absolute -bottom-20 -left-20 w-80 h-80 bg-indigo-600/20 rounded-full blur-[100px] animate-blob delay-2000"></div>
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 z-0"></div>

      {/* Hidden Audio Element */}
      <audio 
        ref={audioPlayerRef} 
        onEnded={() => setStatus('IDLE')}
        onError={(e) => {
          console.error('Audio playback error:', e);
          setStatus('IDLE');
          setMessages(prev => [...prev, { 
            id: generateId(), 
            role: 'error', 
            text: 'Failed to play audio response.', 
            retryable: false 
          }]);
        }}
        className="hidden" 
        aria-hidden="true"
      />

      {/* Main UI Container */}
      <div className="absolute inset-0 flex flex-col z-10">

        {/* Header */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-white/5 bg-slate-900/40 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg border border-white/10">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div className={`absolute -bottom-1 -right-1 w-2.5 h-2.5 rounded-full border-2 border-slate-900 ${status === 'LISTENING' ? 'bg-red-500 animate-pulse' : 'bg-emerald-500'}`} />
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm tracking-tight">VoxRay Voice</h3>
              <p className="text-indigo-200/50 text-[10px] uppercase tracking-wider font-medium">Unified Interface</p>
            </div>
          </div>

          {/* Sterile Mode Toggle */}
          <button 
            onClick={() => setIsSterileMode(!isSterileMode)}
            className="flex items-center gap-2 group cursor-pointer focus:outline-none"
            title="Hands-free mode"
          >
            <span className={`text-[10px] font-medium uppercase tracking-wider transition-colors ${isSterileMode ? 'text-emerald-400' : 'text-slate-500'}`}>Sterile</span>
            <div className={`w-8 h-4 rounded-full border relative transition-colors ${isSterileMode ? 'bg-emerald-900/50 border-emerald-500/30' : 'bg-slate-800 border-white/10'}`}>
              <div className={`absolute top-0.5 w-3 h-3 rounded-full transition-all duration-300 ${isSterileMode ? 'right-0.5 bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]' : 'left-0.5 bg-slate-500'}`} />
            </div>
          </button>
        </div>

        {/* Chat Stream */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto hide-scroll px-5 py-4 space-y-5 scroll-mask relative"
        >
          {/* Medical Context Pill */}
          {currentDiagnosis && (
            <div className="flex justify-center sticky top-0 z-20 mb-4 pointer-events-none">
              <motion.div 
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="px-3 py-1.5 rounded-full bg-slate-800/90 border border-amber-500/20 text-[10px] flex items-center gap-2 backdrop-blur-md shadow-lg"
              >
                <span className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-pulse" aria-hidden="true" />
                <span className="text-slate-400">Context:</span>
                <span className="text-amber-300 font-semibold">
                  {currentDiagnosis.diagnosis.replace(/^\d+_/, '').replace(/_/g, ' ')}
                </span>
                <span className="text-slate-500">
                  ({(currentDiagnosis.confidence * 100).toFixed(0)}%)
                </span>
              </motion.div>
            </div>
          )}

          {/* Messages */}
          <AnimatePresence mode="popLayout">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} msg={msg} onRetry={handleRetry} isRetrying={isRetrying} />
            ))}
          </AnimatePresence>
          
          {/* Empty State */}
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-white/20 gap-3 pb-20">
              <Sparkles className="w-10 h-10 opacity-30" aria-hidden="true" />
              <p className="text-xs text-center">
                {currentDiagnosis 
                  ? "Tap the orb or use a quick action to discuss the findings"
                  : "Upload an X-ray first, then ask questions here"
                }
              </p>
            </div>
          )}
        </div>

        {/* Controls Layer */}
        <div className="h-[200px] relative z-20">
          <div className="absolute bottom-0 left-0 right-0 h-56 bg-gradient-to-t from-slate-900 via-slate-900/90 to-transparent pointer-events-none"></div>

          <div className="relative h-full flex flex-col items-center justify-end pb-14 gap-6">
            
            {/* Quick Actions (Functional) */}
            <AnimatePresence>
              {messages.length === 0 && status === 'IDLE' && currentDiagnosis && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="flex gap-2 flex-wrap justify-center px-4 relative z-30"
                >
                    {QUICK_ACTIONS.map((action) => (
                        <button 
                            key={action.label}
                            onClick={() => processTextQuery(action.prompt)}
                            disabled={status !== 'IDLE'}
                            className={`px-3 py-1.5 rounded-full border text-[10px] transition-all backdrop-blur-sm whitespace-nowrap
                              ${status !== 'IDLE'
                                ? 'bg-white/5 border-white/10 text-white/30 cursor-not-allowed' 
                                : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10 hover:border-white/30 hover:scale-105 active:scale-95'
                              }`}
                        >
                            {action.label}
                        </button>
                    ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* SUPER ORB */}
            <div className="flex items-center gap-8 w-full justify-center px-8 relative z-30">
               <VoiceOrb 
                 status={status} 
                 recordingTime={recordingTime} 
                 onClick={handleOrbClick} 
                 debugRMS={debugRMS}
                 showDebug={isSterileMode}
               />
            </div>
            
          </div>
        </div>

        {/* Footer with HIPAA Badge and Clear Button */}
        <div className="absolute bottom-3 left-4 right-4 flex justify-between items-center z-30">

          
          {/* Clear Chat Button */}
          {messages.length > 0 && (
            <button
              onClick={clearMessages}
              className="px-2 py-1 rounded text-[9px] text-white/30 hover:text-white/60 hover:bg-white/5 transition-all"
              aria-label="Clear conversation"
            >
              Clear Chat
            </button>
          )}
        </div>

      </div>
      
      {/* Top Glass Reflection */}
      <div className="absolute inset-0 bg-gradient-to-tr from-white/5 to-transparent pointer-events-none z-40"></div>
    </div>
  );
};

VoiceSection.propTypes = {
  currentDiagnosis: PropTypes.shape({
    diagnosis: PropTypes.string.isRequired,
    confidence: PropTypes.number.isRequired
  })
};

VoiceSection.defaultProps = {
  currentDiagnosis: null
};

export default VoiceSection;
