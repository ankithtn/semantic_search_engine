import React, { useState } from "react";

export default function ResultCard({ result, index }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const abstract = result.abstract || result.snippet || "";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition mb-4">
      {/* Header and metadata */}
      <div className="flex items-center gap-3 text-sm text-gray-500 mb-2">
        <span className="font-medium">Result #{index + 1}</span>
        {result.year && (
          <>
          <span>•</span>
          <span>{result.year}</span>
          </>
        )}
        {result.journal && (
          <>
          <span>•</span>
          <span className="text-gray-600">{result.journal}</span>
          </>
        )}
      </div>

      {/* Title */}
      <h3 className="text-lg text-left font-semibold text-gray-900 mb-2 mt-4 leading-tight">
        {result.title}
      </h3>


      {/* Abstract */}
      <p className="text-gray-700 text-justify leading-relaxed">
        {isExpanded ? abstract : abstract.slice(0, 200)} 
        {abstract.length > 200 && !isExpanded && "…"}
      </p>

      {/* Expand/collapse button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="text-gray-900 mt-3 text-sm font-medium hover:underline"
      >
        {isExpanded ? "Show Less" : "Show more"}
      </button>
    </div>
  );
}
