import React, { useEffect, useRef } from 'react';

const AudioVisualizer = ({ audioRef, isPlaying }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const analyzerRef = useRef(null);
  const sourceRef = useRef(null);
  const audioContextRef = useRef(null);

  useEffect(() => {
    if (!audioRef.current) return;

    // Initialize Audio Context
    if (!audioContextRef.current) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioContextRef.current = new AudioContext();
      analyzerRef.current = audioContextRef.current.createAnalyser();
      analyzerRef.current.fftSize = 2048; // Higher FFT size for better resolution
      
      try {
        sourceRef.current = audioContextRef.current.createMediaElementSource(audioRef.current);
        sourceRef.current.connect(analyzerRef.current);
        analyzerRef.current.connect(audioContextRef.current.destination);
      } catch (e) {
        console.warn("MediaElementSource already connected", e);
      }
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const bufferLength = analyzerRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    // Configuration for waves
    const waves = [
      { color: "rgba(99, 102, 241, 0.5)", speed: 0.01, amplitude: 0.5, offset: 0 }, // Indigo
      { color: "rgba(168, 85, 247, 0.5)", speed: 0.02, amplitude: 0.4, offset: 2 }, // Purple
      { color: "rgba(236, 72, 153, 0.3)", speed: 0.015, amplitude: 0.3, offset: 4 }, // Pink
    ];

    let frame = 0;

    const draw = () => {
      animationRef.current = requestAnimationFrame(draw);
      analyzerRef.current.getByteFrequencyData(dataArray);

      // Calculate average volume for amplitude modulation
      let sum = 0;
      for (let i = 0; i < bufferLength; i++) {
        sum += dataArray[i];
      }
      const average = sum / bufferLength;
      // Normalize volume (0-1) with some sensitivity adjustment
      const volume = Math.min(1, (average / 128) * 1.5); 

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Base amplitude when idle vs playing
      const baseAmplitude = isPlaying ? volume * (canvas.height / 3) : 2; 
      const centerY = canvas.height / 2;

      waves.forEach((wave, index) => {
        ctx.beginPath();
        ctx.strokeStyle = wave.color;
        ctx.lineWidth = 2;

        for (let x = 0; x < canvas.width; x++) {
          // Sine wave formula: y = A * sin(B * x + C) + D
          // A = Amplitude (dynamic based on volume)
          // B = Frequency (width of wave)
          // C = Phase shift (animation)
          // D = Vertical shift (center)
          
          const waveFrequency = 0.02 + (index * 0.01);
          const phase = frame * wave.speed + wave.offset;
          
          const y = centerY + 
            Math.sin(x * waveFrequency + phase) * 
            (baseAmplitude * wave.amplitude * (1 + Math.sin(frame * 0.005))); // Add some breathing effect

          if (x === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.stroke();
      });

      frame++;
    };

    if (isPlaying) {
      if (audioContextRef.current.state === 'suspended') {
        audioContextRef.current.resume();
      }
      draw();
    } else {
      // Keep animating gently even when paused/idle
      draw();
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [audioRef, isPlaying]);

  return (
    <canvas 
      ref={canvasRef} 
      width={400} 
      height={60} 
      className="w-full h-full"
    />
  );
};

export default AudioVisualizer;
