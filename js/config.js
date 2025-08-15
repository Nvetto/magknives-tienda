// Detectamos si estamos en el entorno local o en producción (Netlify)
const esEntornoLocal = ['127.0.0.1', 'localhost'].includes(window.location.hostname);

// Definimos la URL del backend según el entorno
const API_BASE_URL = esEntornoLocal 
    ? 'http://127.0.0.1:5000' // URL para desarrollo local
    : 'https://magknives-backend.onrender.com'; 