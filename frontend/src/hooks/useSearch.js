import { useState } from 'react';
import { searchPapers } from '../api/searchAPI';

export const useSearch = () => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTime, setSearchTime] = useState(null);
  const [totalCount, setTotalCount] = useState(0);

  // AI Answer state
  const [aiAnswer, setAiAnswer] = useState(null);
  const [rag_enabled, setRagEnabled] = useState(false);


  const performSearch = async (query, mode = 'hybrid', limit = 10) => {
    if (!query || !query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults([]);
    setAiAnswer(null);
    
    const startTime = performance.now();

    try {
      const data = await searchPapers(query, mode, limit);
      
      const endTime = performance.now();
      const searchDuration = (endTime - startTime) / 1000; // Convert to seconds
      
      // Set search results
      setResults(data.results || []);
      setTotalCount(data.total_count || data.results?.length || 0);
      setSearchTime(searchDuration);
      setError(null);

      // Set AI answer if available
      if (data.ai_answer){
        setAiAnswer({
          answer: data.ai_answer.answer,
          model: data.ai_answer.model,
          tokensUsed: data.ai_answer.tokens_used,
          generationTime: data.ai_answer.generation_time,
          error: data.ai_answer.error || null
        });
        console.log('AI Answer received', {
          model: data.ai_answer.model,
          tokens: data.ai_answer.tokens_used,
          time: data.ai_answer.generation_time
        });
      } else {
        console.log('No AI answer in response')
      }

      setRagEnabled(data.rag_enabled || false);
      
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
      setAiAnswer(null);
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setError(null);
    setSearchTime(null);
    setTotalCount(0);
    setAiAnswer(null);
  };

  return {
    results,
    isLoading,
    error,
    searchTime,
    totalCount,
    aiAnswer,
    rag_enabled,
    performSearch,
    clearResults,
  };
};