// API Configuration
// Automatically detects if running locally or in production

const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'  // Local development
    : 'https://remote-karola-metasoft-c608a8ea.koyeb.app';  // Production (Netlify)

export default {
    API_BASE_URL
};
