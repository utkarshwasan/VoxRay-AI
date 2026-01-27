import { SignIn } from "@stackframe/react";

export default function Login() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-black/90 relative overflow-hidden">
      {/* Ambient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/20 via-black to-purple-900/20" />
      <div className="absolute top-[-20%] left-[-20%] w-[50%] h-[50%] bg-indigo-500/10 rounded-full blur-[120px]" />
      <div className="absolute bottom-[-20%] right-[-20%] w-[50%] h-[50%] bg-purple-500/10 rounded-full blur-[120px]" />

      <div className="relative z-10 w-full max-w-md p-8 glass-panel rounded-2xl border border-white/10 shadow-2xl">
        <h2 className="text-3xl font-bold text-white text-center mb-2">Welcome Back</h2>
        <p className="text-indigo-200/60 text-center mb-8">Sign in to access VoxRay AI</p>
        
        <SignIn 
          fullPage={false} 
          redirectUrl="/"
          // Stack Auth components handle their own styling, but we wrap nicely
        />
      </div>
    </div>
  );
}
