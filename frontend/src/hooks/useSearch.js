import { useState } from 'react';
import { searchPapers } from '../api/searchAPI';

export const useSearch = () => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTime, setSearchTime] = useState(null);
  const [totalCount, setTotalCount] = useState(0);

  const performSearch = async (query, mode = 'hybrid', limit = 10) => {
    if (!query || !query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults([]);
    
    const startTime = performance.now();

    try {
      const data = await searchPapers(query, mode, limit);
      
      const endTime = performance.now();
      const searchDuration = (endTime - startTime) / 1000; // Convert to seconds
      
      setResults(data.results || []);
      setTotalCount(data.total_count || data.results?.length || 0);
      setSearchTime(searchDuration);
      setError(null);
      
      console.log(`Search completed in ${searchDuration.toFixed(2)}s`);
    } catch (err) {
      console.error('Search error:', err);
      
      // Check if it's a network error (backend not running)
      if (err.message.includes('Network Error') || err.message.includes('ERR_CONNECTION_REFUSED')) {
        setError('Cannot connect to backend. Make sure the API server is running at http://localhost:8000');
      } else if (err.message.includes('timeout')) {
        setError('Search request timed out. Try again.');
      } else {
        setError(err.message || 'An error occurred during search');
      }
      
      setResults([]);
      setTotalCount(0);
      setSearchTime(null);
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setError(null);
    setSearchTime(null);
    setTotalCount(0);
  };

  return {
    results,
    isLoading,
    error,
    searchTime,
    totalCount,
    performSearch,
    clearResults,
  };
};