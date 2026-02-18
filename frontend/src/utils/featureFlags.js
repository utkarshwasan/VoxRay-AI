const DEFAULT_FLAGS = {
  ensemble_model: false,
  multilingual_voice: false,
  advanced_heatmap: false,
  dicom_support: false,
  mobile_pwa: false,
};

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchFeatureFlags() {
  try {
    // Attempt to fetch from backend
    const response = await fetch(`${API_BASE_URL}/api/feature-flags`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Short timeout to prevent blocking UI blocked on flags (Increased to 10s for cold boot via 5000 first then 10000)
      signal: AbortSignal.timeout(10000)
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        // Endpoint doesn't exist yet, use defaults without error
        console.debug('Feature flag endpoint not found, using defaults');
        return DEFAULT_FLAGS;
      }
      throw new Error(`Failed to fetch flags: ${response.status}`);
    }
    
    const flags = await response.json();
    return { ...DEFAULT_FLAGS, ...flags };
  } catch (error) {
    console.warn('Feature flags fetch failed, using defaults:', error);
    return DEFAULT_FLAGS;
  }
}

export function isFlagEnabled(flags, key) {
  return flags && flags[key] === true;
}
