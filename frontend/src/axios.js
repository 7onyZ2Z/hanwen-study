import axios from 'axios';

// In production (Docker), requests to /api/... will be proxied by Nginx to the backend
// In development, Vite proxy will handle this
const instance = axios.create({
  baseURL: '/api', 
});

// Request interceptor to add token
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default instance;
