import React, { useState } from "react";
import { Search } from "lucide-react";

export default function SearchBar({ onSearch, isLoading }) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="mt-8 w-full max-w-2xl mx-auto">
      <div className="rounded-2xl border border-gray-200 bg-white/70 backdrop-blur shadow-sm hover:shadow-md transition">
        <div className="flex items-center p-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent outline-none px-4 py-3 text-base placeholder:text-gray-400"
            placeholder="Type your query…"
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="mr-1 inline-flex items-center gap-2 rounded-xl bg-gray-900 px-4 py-3 text-white transition hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            <Search size={18} />
            Search
          </button>
        </div>
      </div>
    </form>
  );
}
