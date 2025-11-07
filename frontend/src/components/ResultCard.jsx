import React, { useState } from "react";

export default function ResultCard({ result, index }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const abstract = result.abstract || result.snippet || "";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition">
      {/* Header */}
      <div className="flex justify-between text-sm text-gray-500 mb-2">
        <span>Result #{index + 1}</span>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-2 leading-tight">
        {result.title}
      </h3>

      {/* Metadata */}
      <div className="text-sm text-gray-600 mb-3">
        {result.year && <span>{result.year}</span>}
      </div>

      {/* Abstract */}
      <p className="text-gray-700 leading-relaxed">
        {isExpanded ? abstract : abstract.slice(0, 200)} 
        {abstract.length > 200 && !isExpanded && "…"}
      </p>

      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="text-gray-900 mt-3 text-sm font-medium hover:underline"
      >
        {isExpanded ? "Show Less" : "View Full Abstract"}
      </button>
    </div>
  );
}
