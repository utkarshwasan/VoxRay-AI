import { useState, useEffect } from 'react';

const useTypewriter = (text, speed = 30) => {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    if (!text) {
      setDisplayedText('');
      return;
    }

    setDisplayedText('');
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        // Use substring to ensure we always display a valid prefix of the text
        // This prevents issues where characters might be skipped due to state update batching
        i++;
        setDisplayedText(text.substring(0, i));
      } else {
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed]);

  return displayedText;
};

export default useTypewriter;
