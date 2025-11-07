import React, { useState } from 'react';
import SearchBar from './components/SearchBar';
import ModeSelector from './components/ModeSelector';
import ResultsList from './components/ResultsList';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import { useSearch } from './hooks/useSearch';

function App() {
  const [selectedMode, setSelectedMode] = useState('hybrid');
  const [currentQuery, setCurrentQuery] = useState('');
  
  const { 
    results, 
    isLoading, 
    error, 
    searchTime, 
    totalCount, 
    performSearch 
  } = useSearch();

  const handleSearch = (query) => {
    setCurrentQuery(query);
    performSearch(query, selectedMode, 10);
  };

  const handleModeChange = (mode) => {
    setSelectedMode(mode);
    // Re-search with new mode if there's a current query
    if (currentQuery) {
      performSearch(currentQuery, mode, 10);
    }
  };

  const handleRetry = () => {
    if (currentQuery) {
      performSearch(currentQuery, selectedMode, 10);
    }
  };

  return (
    <div className="relative min-h-screen w-full bg-gradient-to-b from-white to-gray-50 text-gray-900">
      {/* background accents */}
      <GradientBlobs />

      {/* navbar */}
      <nav className="sticky top-0 z-20 backdrop-blur supports-[backdrop-filter]:bg-white/50 border-b border-gray-200/60">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded-md bg-gradient-to-br from-indigo-500 to-cyan-500" />
            <span className="font-semibold tracking-tight">Search</span>
          </div>
          <div className="text-sm text-gray-500">React • FastAPI • Weaviate</div>
        </div>
      </nav>
      
      {/* Header Section */}
      <header className="pt-16 pb-8 ">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-3">
            Semantic Search Engine
          </h1>
          <p className="text-xl text-gray-600">
            Search intelligently across thousands of medical research papers
          </p>
        </div>
      </header>

      {/* Search Section */}
      <main className="pb-12">
        <div className="container mx-auto px-4 flex flex-col items-center text-center">
          {/* Mode Selector */}
          <ModeSelector 
            selectedMode={selectedMode} 
            onModeChange={handleModeChange} 
          />

          {/* Search Bar */}
          <SearchBar 
            onSearch={handleSearch} 
            isLoading={isLoading} 
          />

          {/* Current Search Info */}
          {currentQuery && !isLoading && (
            <div className="text-center mt-4 text-gray-600">
              Searching for: <span className="font-semibold">"{currentQuery}"</span>
              {' '}using <span className="font-semibold capitalize">{selectedMode}</span> mode
            </div>
          )}

          {/* Loading State */}
          {isLoading && <LoadingSpinner message="Searching..." />}

          {/* Error State */}
          {error && !isLoading && (
            <ErrorMessage message={error} onRetry={handleRetry} />
          )}

          {/* Results */}
          {!isLoading && !error && results.length > 0 && (
            <ResultsList 
              results={results} 
              searchTime={searchTime} 
              totalCount={totalCount} 
            />
          )}

          {/* No Results */}
          {!isLoading && !error && currentQuery && results.length === 0 && (
            <div className="text-center mt-12 text-gray-600">
              <p className="text-xl font-semibold mb-2">No results found</p>
              <p>Try a different search query or change the search mode</p>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-7  border-t border-gray-250 bg-white">
        <div className="container mx-auto px-4 text-center text-gray-600 text-sm">
          <p>Semantic Search Engine • Built with React + FastAPI + Weaviate</p>
          <p className="mt-1">
            Backend: <a 
              href="http://localhost:8000/docs" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              API Docs
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

function GradientBlobs() {
return (
<div aria-hidden className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
<div className="absolute -top-24 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-gradient-to-br from-indigo-400/20 to-cyan-400/20 blur-3xl" />
<div className="absolute top-1/3 -left-24 h-72 w-72 rounded-full bg-gradient-to-br from-fuchsia-400/20 to-purple-400/20 blur-3xl" />
<div className="absolute bottom-0 right-0 h-80 w-80 translate-x-1/3 translate-y-1/3 rounded-full bg-gradient-to-br from-amber-300/20 to-rose-300/20 blur-3xl" />
</div>
);
}

export default App;