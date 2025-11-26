import { useState, useEffect } from 'react';

// Simple stub for language translation. Returns the key as is.
const useLanguage = () => {
  const [lang, setLang] = useState('en');
  const t = (key) => key; // identity translation function
  return { t, lang, setLang };
};

export default useLanguage;
