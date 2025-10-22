import React, { useState } from "react";
import {Search} from 'lucide-react';

const SearchBar = ({ onSearch, isLoading}) => {
    const [query, setQuery] = useState ('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query.trim());
        }
    };

    const handleKeyPress = (e) => {
        if (e.key == 'Enter' && !e.shiftKey) {
            handleSubmit(e);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full max-w-4xl mx-auto">
            <div className="relative">
                <input
                type="text"
                value = {query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your query here..."
                disabled={isLoading}
                className="w-full px-6 py-4 pr-14 text-lg border-2 border-gray-300 rounded-xl
                        focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100
                      disabled:bg-gray-100 disabled:cursor-not-allowed
                        transition-all duration-200"
                />
                <button
                type = "submit"
                disabled={isLoading || !query.trim()}
                className="absolute right-2 top-1/2 -translate-y-1/2
                       bg-blue-600 hover:bg-blue-700 text-white
                         px-4 py-2 rounded-lg
                         disabled: bg-gray-400 disabled:cursor-not-allowed
                         transition-all duration-200 flex items-center gap-2"
                >
                    <Search size={20} />
                    {isLoading ? 'Searching...' : 'Search'}   
                </button>
            </div>
             {/* Example queries */}
      <div className="mt-3 text-center text-sm text-gray-500">
        Try: <button 
          type="button"
          onClick={() => setQuery('diabetes treatment')}
          className="text-blue-600 hover:underline mx-1"
        >
          "diabetes treatment"
        </button>
        or
        <button 
          type="button"
          onClick={() => setQuery('covid vaccine effectiveness')}
          className="text-blue-600 hover:underline mx-1"
        >
          "covid vaccine effectiveness"
        </button>
      </div>
    </form>
  );
};

export default SearchBar;