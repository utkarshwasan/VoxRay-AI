/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        slate: { 900: "#0F172A" }, // Keep for legacy compatibility if needed
        // Clinical Neutrals (Replaces generic slate/gray)
        clinical: {
          50: '#F8FAFC',   // Light backgrounds
          100: '#F1F5F9',  // Card backgrounds
          200: '#E2E8F0',  // Borders
          300: '#CBD5E1',  // Muted text
          400: '#94A3B8',  // Icons
          700: '#334155',  // Secondary text
          800: '#1E293B',  // Primary text
          900: '#0F172A',  // Dark mode base
          950: '#020617',  // Deepest dark
        },
        
        // Diagnostic Status Colors (Precise, not vibrant)
        diagnostic: {
          normal: '#10B981',      // Emerald - Clear findings
          warning: '#F59E0B',     // Amber - Moderate concern
          critical: '#EF4444',    // Red - Urgent attention
          info: '#3B82F6',        // Blue - Informational
        },
        
        // Accent Colors for Medical Context
        medical: {
          primary: '#6366F1',     // Indigo - Main actions
          secondary: '#8B5CF6',   // Purple - Secondary features
          accent: '#06B6D4',      // Cyan - Highlights for imaging
        },

        // Legacy palette mappings for backward compatibility
        indigo: { 
          500: "#6366F1", 
          600: "#4F46E5", 
          900: "#312E81" 
        },
        emerald: {
          200: "#A7F3D0",
          400: "#34D399",
          500: "#10B981",
          600: "#059669",
          900: "#064E3B",
        },
        purple: { 
          200: "#E9D5FF", 
          400: "#C084FC",
          500: "#A855F7",
          600: "#9333EA" 
        },
        red: {
          400: "#F87171",
          500: "#EF4444",
        },
        amber: {
          400: "#FBBF24",
          500: "#F59E0B", // Added 500
        },
      },
      fontFamily: {
        sans: [
          "Inter", // Priority
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "Menlo",
          "Monaco", 
          "Consolas", 
          "monospace"
        ]
      },
      fontSize: {
        'diagnostic-xs': ['10px', { lineHeight: '14px', letterSpacing: '0.5px' }],
        'diagnostic-sm': ['12px', { lineHeight: '16px', letterSpacing: '0.3px' }],
        'diagnostic-base': ['14px', { lineHeight: '20px' }],
        'diagnostic-lg': ['16px', { lineHeight: '24px' }],
        'diagnostic-xl': ['20px', { lineHeight: '28px', letterSpacing: '-0.02em' }],
      },
      boxShadow: {
        'clinical-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'clinical-md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'clinical-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.15)',
        'clinical-glow': '0 0 20px rgba(99, 102, 241, 0.15)',
        'emerald': '0 20px 60px -12px rgba(16, 185, 129, 0.5)',
        'indigo': '0 20px 60px -12px rgba(99, 102, 241, 0.5)', 
      },
      animation: {
        "spin-slow": "spin 20s linear infinite",
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        float: "float 6s ease-in-out infinite",
        shimmer: "shimmer 2s linear infinite",
        dataFadeIn: "dataFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        shimmer: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
        dataFadeIn: {
          "from": { opacity: "0", transform: "translateY(4px)" },
          "to": { opacity: "1", transform: "translateY(0)" },
        }
      },
    },
  },
  plugins: [],
};
