import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 30000;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (for logging, auth tokens later)
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (for error handling)
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Error:', error.message);
    return Promise.reject(error);
  }
);

/**
 * Search API endpoint
 * @param {string} query - Search query
 * @param {string} mode - Search mode: 'hybrid', 'semantic', or 'keyword'
 * @param {number} limit - Number of results to return
 * @returns {Promise} - API response
 */
export const searchPapers = async (query, mode = 'hybrid', limit = 10) => {
  try {
    console.log(' Sending search request:', { query, mode, limit });
    console.log('API URL:', API_BASE_URL);
    
    const response = await apiClient.post('/api/search', {
      query,
      mode,
      limit,
    });
    return response.data;
  } catch (error) {
    console.error('Search API Error:', error);
    
    if (error.response) {
      // Server responded with error
      console.error('Server error:', error.response.status, error.response.data);
      throw new Error(error.response.data.detail || 'Search failed');
    } else if (error.request) {
      // Request made but no response
      console.error('No response from server. Is backend running?');
      throw new Error('Cannot connect to backend. Make sure the API server is running at ' + API_BASE_URL);
    } else {
      // Other errors
      console.error('Request setup error:', error.message);
      throw new Error('Failed to make search request: ' + error.message);
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