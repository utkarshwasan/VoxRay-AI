import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square, Upload, Play, Pause, Volume2, Loader2 } from 'lucide-react';
import axios from 'axios';
import AudioRecorderPolyfill from 'audio-recorder-polyfill';
import clsx from 'clsx';
import MagneticButton from './MagneticButton';
import AudioVisualizer from './AudioVisualizer';
import useTypewriter from '../hooks/useTypewriter';

const VoiceSection = ({ currentDiagnosis }) => {
  // Lifted TTS State
  const [ttsText, setTtsText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  const handleGenerate = async (textOverride = null) => {
    const textToSpeak = textOverride || ttsText;
    if (!textToSpeak) return;
    
    // If called with override, update state too
    if (textOverride) setTtsText(textOverride);

    setIsGenerating(true);
    try {
        const response = await axios.post('http://127.0.0.1:8000/generate/speech', { text: textToSpeak }, { responseType: 'blob' });
        const url = URL.createObjectURL(response.data);
        setAudioUrl(url);
        setIsPlaying(true);
    } catch (error) {
        console.error("TTS failed", error);
        alert("TTS Generation failed. Ensure backend is running.");
    } finally {
        setIsGenerating(false);
    }
  };

  const togglePlayback = () => {
    if (audioRef.current) {
        if (isPlaying) {
            audioRef.current.pause();
            setIsPlaying(false);
        } else {
            audioRef.current.play();
            setIsPlaying(true);
        }
    }
  };

  return (
    <section className="relative">
      {/* Refined Purple UI */}
      <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 to-purple-500/5 rounded-2xl blur-xl" />
      <div className="relative glass-panel bg-noise rounded-2xl p-8 overflow-hidden">
        
        <div className="flex items-center gap-4 mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-400 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Mic className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-white">Voice Assistant</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 divide-y md:divide-y-0 md:divide-x divide-white/10">
          <STTColumn onChatResponse={handleGenerate} currentDiagnosis={currentDiagnosis} />
          <TTSColumn 
            text={ttsText} 
            setText={setTtsText} 
            isGenerating={isGenerating} 
            handleGenerate={() => handleGenerate()} 
            audioUrl={audioUrl} 
            isPlaying={isPlaying} 
            togglePlayback={togglePlayback} 
            audioRef={audioRef}
            setIsPlaying={setIsPlaying}
          />
        </div>
      </div>
    </section>
  );
};

const STTColumn = ({ onChatResponse, currentDiagnosis }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRequestingPermission, setIsRequestingPermission] = useState(false);
  const [assistantReply, setAssistantReply] = useState("");
  
  // Use Typewriter for Assistant Reply
  const typedReply = useTypewriter(assistantReply, 20);
  
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    setIsRequestingPermission(true);
    try {
      console.log("🎤 Requesting microphone access...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setIsRequestingPermission(false);
      
      const recorder = new AudioRecorderPolyfill(stream);
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.addEventListener('dataavailable', (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      });

      recorder.addEventListener('stop', async () => {
        console.log("🛑 Recording stopped. Processing...");
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioFile = new File([audioBlob], "recording.wav", { type: 'audio/wav' });
        stream.getTracks().forEach(track => track.stop());
        await processAudioFile(audioFile);
      });

      recorder.start(); 
      setIsRecording(true);
      setTranscription("");
      setAssistantReply("");
    } catch (error) {
      setIsRequestingPermission(false);
      console.error("❌ Error accessing microphone:", error);
      alert("Could not access microphone. Please allow permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleRecordToggle = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const processAudioFile = async (file) => {
    if (!file) return;
    setIsProcessing(true);
    try {
      // 1. Transcribe
      const formData = new FormData();
      formData.append('audio_file', file);
      const sttResponse = await axios.post('http://127.0.0.1:8000/transcribe/audio', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
      });
      const transcribedText = sttResponse.data.transcription;
      setTranscription(transcribedText);

      // 2. Chat with LLM (with Context)
      if (transcribedText) {
          console.log("🤖 Sending to LLM:", transcribedText);
          
          // Prepare Context String
          let contextStr = null;
          if (currentDiagnosis) {
            contextStr = `Diagnosis: ${currentDiagnosis.diagnosis}, Confidence: ${(currentDiagnosis.confidence * 100).toFixed(1)}%`;
            console.log("📎 Attaching Context:", contextStr);
          }

          const chatResponse = await axios.post('http://127.0.0.1:8000/chat', { 
            message: transcribedText,
            context: contextStr
          });
          const reply = chatResponse.data.response;
          setAssistantReply(reply);
          
          // 3. Auto-Speak Response
          if (onChatResponse) {
              onChatResponse(reply);
          }
      }

    } catch (error) {
      console.error("❌ Processing failed", error);
      setTranscription("Error: Could not process audio. Check backend.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      processAudioFile(file);
    }
  };

  return (
    <div className="flex flex-col gap-6 md:pr-8 pt-8 md:pt-0">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-1 h-5 bg-indigo-500 rounded-full" />
        <h3 className="text-lg font-medium text-white">Speech-to-Text & Chat</h3>
      </div>

      <div className="flex flex-col items-center justify-center py-8">
        <div className="relative">
          <AnimatePresence>
            {isRecording && (
              <>
                <motion.div
                  initial={{ scale: 1, opacity: 0.8 }}
                  animate={{ scale: 1.4, opacity: 0 }}
                  exit={{ scale: 1, opacity: 0 }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="absolute inset-0 rounded-full border-4 border-red-500/30"
                />
                <motion.div
                  initial={{ scale: 1, opacity: 0.6 }}
                  animate={{ scale: 1.6, opacity: 0 }}
                  exit={{ scale: 1, opacity: 0 }}
                  transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                  className="absolute inset-0 rounded-full border-4 border-red-500/20"
                />
              </>
            )}
          </AnimatePresence>
          
          <MagneticButton
            onClick={handleRecordToggle}
            className={clsx(
              "relative w-24 h-24 rounded-full flex items-center justify-center shadow-2xl transition-all duration-500 z-10",
              isRecording 
                ? "bg-gradient-to-br from-red-500 to-pink-600 shadow-red-500/50" 
                : "bg-gradient-to-br from-indigo-500 to-purple-600 shadow-indigo-500/50"
            )}
          >
            {isRecording ? (
              <Square className="w-10 h-10 text-white fill-current" />
            ) : (
              <Mic className="w-10 h-10 text-white" />
            )}
          </MagneticButton>
        </div>
        <p className="mt-4 text-sm font-medium text-indigo-200/70">
          {isRequestingPermission 
            ? "Requesting Microphone Access..." 
            : isRecording 
              ? "Listening..." 
              : "Click to speak"}
        </p>
      </div>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-white/10" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-slate-900/50 backdrop-blur px-2 text-white/40">or</span>
        </div>
      </div>

      <button 
        onClick={() => fileInputRef.current?.click()}
        className="w-full py-3 rounded-lg bg-white/5 border border-white/20 flex items-center justify-center gap-2 text-sm font-medium text-white hover:bg-white/10 transition-all hover:scale-[1.02]"
      >
        <Upload className="w-4 h-4" />
        Upload Audio File
      </button>
      <input 
        type="file" 
        ref={fileInputRef}
        className="hidden" 
        accept="audio/*"
        onChange={handleFileUpload}
      />

      <div className="flex-grow min-h-[120px] bg-white/5 border border-white/20 rounded-xl p-4 relative overflow-hidden flex flex-col gap-4">
        <div>
            <span className="text-xs font-medium text-indigo-200/50 mb-1 block">You said:</span>
            {isProcessing && !transcription ? (
            <div className="flex items-center gap-2 text-white/60">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing audio...</span>
            </div>
            ) : (
            <p className="text-white/90 leading-relaxed text-sm">
                {transcription || <span className="text-white/30 italic">...</span>}
            </p>
            )}
        </div>
        
        {assistantReply && (
            <div className="pt-3 border-t border-white/10">
                <span className="text-xs font-medium text-purple-200/50 mb-1 block">Assistant:</span>
                <p className="text-purple-100 leading-relaxed text-sm">
                    {typedReply}
                    <span className="animate-pulse">|</span>
                </p>
            </div>
        )}
      </div>
    </div>
  );
};

const TTSColumn = ({ text, setText, isGenerating, handleGenerate, audioUrl, isPlaying, togglePlayback, audioRef, setIsPlaying }) => {
  return (
    <div className="flex flex-col gap-6 md:pl-8 pt-8 md:pt-0">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-1 h-5 bg-purple-500 rounded-full" />
        <h3 className="text-lg font-medium text-white">Text-to-Speech</h3>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium text-purple-200/70">Enter text to convert to speech</label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="The scan shows signs of pneumonia."
          className="w-full min-h-[120px] bg-white/5 border border-white/20 rounded-lg p-3 text-white placeholder-white/40 focus:outline-none focus:border-purple-400/50 focus:ring-2 focus:ring-purple-400/20 transition-all resize-none"
        />
      </div>

      <MagneticButton
        disabled={!text || isGenerating}
        onClick={handleGenerate}
        className={clsx(
          "w-full h-12 rounded-lg font-medium text-white shadow-lg transition-all relative overflow-hidden",
          !text || isGenerating ? "opacity-50 cursor-not-allowed bg-slate-700" : "bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 shadow-purple-500/25"
        )}
      >
        {isGenerating ? (
          <div className="flex items-center justify-center gap-2">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Generating Speech...</span>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-2">
            <Volume2 className="w-5 h-5" />
            <span>Generate Speech</span>
          </div>
        )}
      </MagneticButton>

      <div className="mt-auto">
        <AnimatePresence mode="wait">
          {audioUrl ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-black/20 backdrop-blur border border-white/10 rounded-xl p-4 flex items-center gap-4"
            >
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={togglePlayback}
                className="w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-lg shadow-white/10 flex-shrink-0"
              >
                {isPlaying ? (
                  <Pause className="w-5 h-5 text-indigo-900 fill-current" />
                ) : (
                  <Play className="w-5 h-5 text-indigo-900 fill-current ml-1" />
                )}
              </motion.button>
              
              <div className="flex-grow h-12 flex items-center gap-[2px] overflow-hidden bg-black/20 rounded-lg">
                <AudioVisualizer audioRef={audioRef} isPlaying={isPlaying} />
              </div>
            </motion.div>
          ) : (
            <div className="h-24 bg-white/5 border border-white/10 rounded-xl flex flex-col items-center justify-center text-white/30">
              <Volume2 className="w-8 h-8 mb-2 opacity-50" />
              <span className="text-xs">Audio player will appear here after generation</span>
            </div>
          )}
        </AnimatePresence>
        <audio 
            ref={audioRef} 
            src={audioUrl} 
            onEnded={() => setIsPlaying(false)} 
            className="hidden" 
            autoPlay
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            crossOrigin="anonymous" 
        />
      </div>
    </div>
  );
};

export default VoiceSection;
