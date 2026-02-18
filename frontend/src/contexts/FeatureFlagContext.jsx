import React, { createContext, useContext, useEffect, useState } from 'react';
import { fetchFeatureFlags } from '../utils/featureFlags';

const FeatureFlagContext = createContext({ 
  flags: {}, 
  loading: true,
  refreshFlags: async () => {} 
});

export function FeatureFlagProvider({ children }) {
  const [flags, setFlags] = useState({});
  const [loading, setLoading] = useState(true);
  
  const loadFlags = async () => {
    try {
      const fetchedFlags = await fetchFeatureFlags();
      setFlags(fetchedFlags);
    } catch (err) {
      console.error("Critical error loading flags", err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadFlags();
  }, []);
  
  return (
    <FeatureFlagContext.Provider value={{ flags, loading, refreshFlags: loadFlags }}>
      {children}
    </FeatureFlagContext.Provider>
  );
}

export const useFeatureFlags = () => useContext(FeatureFlagContext);
