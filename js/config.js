// Detectamos si estamos en el entorno local o en producción (Netlify)
const esEntornoLocal = window.location.hostname === '127.0.0.1';

// Definimos la URL del backend según el entorno
const API_BASE_URL = esEntornoLocal 
    ? 'http://127.0.0.1:5000' // URL para desarrollo local
    : 'https://magknives-backend.onrender.com'; 