import axios, { mergeConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 30000;

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
        'Content-Type': 'application.json',
    },
});

// Request interceptor (for logging, auth tokens later)
apiClient.interceptors.request.use(
    (config) => {
        console.log('API Request:', config.method?.toUpperCase(), config.url);
        return config;
    },
    (error) => {
        return Promise.reject(error)
    }
);

// Response interceptor (for erro handling)
apiClient.interceptors.response.use(
    (response) => {
        console.log('API Response:', response.status, response.config.url);
        return response
    },
    (error) => {
        console.error('API Error', error.message);
        return Promise.reject(error)
    }
);

/**
 * Search API endpoint
 * @param {string} query - Search queryy
 * @param {string} mode - Search mode: 'semantic', 'hybrid', 'keyword'
 * @param {number} limit - Number of results to return
 * @returns {Promise} - API response
 */

export const searchPapers = async (query, mode = 'hybrid', limit = 10) => {
    try {
        const response = await apiClient.post('/api/search', {
            query,
            mode,
            limit,
        });
        return response.data
    } catch (error){
        if(error.response) {
            // Server responded with erro
            throw new Error(error.response.data.detail || 'Search failed');
        } else if (error.request) {
            // Request made but no response
            throw new Error('No response from server. Please check if backend is running.');
        } else{
            //other errors
            throw new Error('Failed to make search request');
        }
    }
};

/**
 * Health check endpoint
 * @returns {Promise} - API health status
 */

export const healthCheck = async () => {
    try {
        const response = await apiClient.get('/health');
        return response.data;
    } catch (error) {
        throw new Error('Backend is not responding');
    }
};

export default apiClient;