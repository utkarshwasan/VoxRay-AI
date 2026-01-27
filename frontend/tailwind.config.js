/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        slate: { 900: "#0F172A" },
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
        pink: {
          400: "#F472B6",
          600: "#DB2777",
        },
        amber: {
          400: "#FBBF24",
        },
        yellow: {
          500: "#EAB308",
        },
        teal: {
          500: "#14B8A6",
        },
        orange: {
          500: "#F97316",
        },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Oxygen",
          "Ubuntu",
          "Cantarell",
          "Fira Sans",
          "Droid Sans",
          "Helvetica Neue",
          "sans-serif",
        ],
      },
      boxShadow: {
        'emerald': '0 20px 60px -12px rgba(16, 185, 129, 0.5)',
        'indigo': '0 20px 60px -12px rgba(99, 102, 241, 0.5)',
        'purple': '0 20px 60px -12px rgba(147, 51, 234, 0.5)',
        'red': '0 20px 60px -12px rgba(239, 68, 68, 0.5)',
      },
      animation: {
        "spin-slow": "spin 20s linear infinite",
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        float: "float 6s ease-in-out infinite",
        shimmer: "shimmer 2s linear infinite",
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
      },
    },
  },
  plugins: [],
};
