import React from "react";
import ResultCard from "./ResultCard";

export default function ResultsList({ results, searchTime, totalCount }) {
  return (
    <div className="w-full max-w-4xl mx-auto mt-8">
      <div className="text-sm text-gray-600 mb-4 px-2">
        {totalCount} results · {searchTime?.toFixed(2)}s
      </div>

      <div>
        {results.map((result, index) => (
          <ResultCard key={index} result={result} index={index} />
        ))}
      </div>
    </div>
  );
}
