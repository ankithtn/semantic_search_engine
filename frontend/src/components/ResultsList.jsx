import React from "react";
import ResultCard from "./ResultCard";

export default function ResultsList({ results, searchTime, totalCount }) {
  return (
    <div className="w-full max-w-6xl mx-auto mt-10">
      <div className="text-center text-sm text-gray-600 mb-4">
        {totalCount} results · {searchTime?.toFixed(2)}s
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {results.map((result, index) => (
          <ResultCard key={index} result={result} index={index} />
        ))}
      </div>
    </div>
  );
}
