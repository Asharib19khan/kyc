import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import axios from 'axios'
import config from './config.js'

// Set backend API URL - HARDCODED to ensure it always works
axios.defaults.baseURL = config.API_BASE_URL;

console.log('🔌 Backend URL:', axios.defaults.baseURL);

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
