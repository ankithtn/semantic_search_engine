import React from "react";

export default function ModeSelector({ selectedMode, onModeChange }) {
  const modes = [
    { id: "semantic", label: "Semantic" },
    { id: "keyword", label: "Keyword" },
    { id: "hybrid", label: "Hybrid" },
  ];

  return (
    <div className="mt-8 flex items-center justify-center gap-3">
      {modes.map((m) => (
        <button
          key={m.id}
          onClick={() => onModeChange(m.id)}
          className={
            selectedMode === m.id
              ? "rounded-full border border-gray-900 bg-gray-900 text-white px-5 py-2.5 text-sm font-medium shadow-sm transition hover:bg-gray-800"
              : "rounded-full border border-gray-300 bg-white text-gray-700 px-5 py-2.5 text-sm font-medium transition hover:bg-gray-50"
          }
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
