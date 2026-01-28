import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { StackHandler, useUser } from '@stackframe/react';
import { stackApp } from '../stack';

export default function OAuthCallbackHandler() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = useUser();
  // const [isProcessing, setIsProcessing] = useState(true); // Removed unused state

  // Check if OAuth params exist
  const searchParams = new URLSearchParams(location.search);
  const hasCode = searchParams.has('code');
  const hasState = searchParams.has('state');

  useEffect(() => {
    // If params are missing, redirect to login
    if (!hasCode || !hasState) {
      console.warn('OAuth callback accessed without required params. Redirecting to login.');
      navigate('/login', { replace: true });
      return;
    }
  }, [hasCode, hasState, navigate]);

  // Watch for user authentication to complete, then redirect
  useEffect(() => {
    if (user) {
      // User is now authenticated, redirect to dashboard
      console.log('User authenticated, redirecting to dashboard...');
      navigate('/', { replace: true });
    }
  }, [user, navigate]);

  // Fallback timeout: if StackHandler doesn't complete in 5 seconds, redirect anyway
  useEffect(() => {
    const timeout = setTimeout(() => {
      // isProcessing was used here to gate, but if we assume fallback always runs if not unmounted/navigate happened:
        console.log('Fallback redirect triggered after timeout');
        navigate('/', { replace: true });
    }, 5000);

    return () => clearTimeout(timeout);
  }, [navigate]);

  // If params are missing, show redirect message
  if (!hasCode || !hasState) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black text-white">
        <p>Redirecting to login...</p>
      </div>
    );
  }

  // Render StackHandler to process the OAuth callback
  // StackHandler will exchange the code for tokens
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white">
      <StackHandler app={stackApp} />
      <p className="mt-4 text-gray-400">Processing login...</p>
    </div>
  );
}
