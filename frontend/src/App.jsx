import React, { useState } from 'react';
import SearchBar from './components/SearchBar';
import ModeSelector from './components/ModeSelector';
import ResultsList from './components/ResultsList';
import AIAnswerCard from './components/AIAnswerCard';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import { useSearch } from './hooks/useSearch';

function App() {
  const [selectedMode, setSelectedMode] = useState('semantic');
  const [currentQuery, setCurrentQuery] = useState('');
  
  const { 
    results, 
    isLoading, 
    error, 
    searchTime, 
    totalCount, 
    aiAnswer,  // Get AI answer from hook
    ragEnabled, // Get RAG status from hook
    performSearch,
    clearResults 
  } = useSearch();

  const handleSearch = (query) => {
    setCurrentQuery(query);   // Store query for AI answer display
    performSearch(query, selectedMode, 10);
  };

  const handleRetry = () => {
    if (currentQuery) {
      handleSearch(currentQuery);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          SemSearchNet
        </h1>
        <p className="text-gray-600">
          Semantic Search Engine for Medical Research Papers
          {ragEnabled && <span className="ml-2 text-xs bg-gray-900 text-white px-2 py-1 rounded-full">AI-Powered</span>}
        </p>
      </div>

      {/* Search Bar */}
      <SearchBar onSearch={handleSearch} isLoading={isLoading} />

      {/* Mode Selector */}
      <ModeSelector 
        selectedMode={selectedMode} 
        onModeChange={setSelectedMode} 
      />

      {/* Loading State */}
      {isLoading && <LoadingSpinner message="Searching and generating AI answer..." />}

      {/* Error State */}
      {error && !isLoading && (
        <ErrorMessage message={error} onRetry={handleRetry} />
      )}

      {/* Results Display */}
      {!isLoading && !error && results.length > 0 && (
        <>
          {/* AI Answer Card - Display FIRST */}
          {aiAnswer && (
            <AIAnswerCard 
              aiAnswer={aiAnswer}
              query={currentQuery}
              totalPapers={Math.min(10, results.length)}
            />
          )}

          {/* Existing: Papers List */}
          <ResultsList 
            results={results} 
            searchTime={searchTime} 
            totalCount={totalCount} 
          />
        </>
      )}

      {/* Empty State */}
      {!isLoading && !error && results.length === 0 && currentQuery && (
        <div className="text-center mt-10">
          <p className="text-gray-600">No results found. Try a different query.</p>
        </div>
      )}
    </div>
  );
}

export default App;
