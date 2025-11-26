import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import axios from 'axios'

// Set default base URL for API requests
// Uses VITE_API_URL if set (Netlify), otherwise falls back to Koyeb production URL
axios.defaults.baseURL = import.meta.env.VITE_API_URL || "https://remote-karola-metasoft-c608a8ea.koyeb.app";

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
