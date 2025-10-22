import React from "react";

const ModeSelector = ({selectedMode, onModeChange}) => {
    const modes = [
        {id: 'semantic', label: 'Semantic', description: 'Meaning-based search'},
        {id: 'keyword', label: 'Keyword', description: 'Exact word matching'},
        {id: 'hybrid', label: 'Hybrid', description: 'Best of both worlds'},
    ];

    return  (
        <div className="flex justify-center gap-3 mb-8">
            {modes.map((mode) => (
                <button
                key = {mode.id}
                onClick={() => onModeChange(mode.id)}
                className={`
                    px-6 py-3 rounded-full font-medium transition-all duration-200
                    ${
                        selectedMode === mode.id
                        ? 'big-blue-600 text-white shadow -lg scale-105'
                        : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
                    }
                `}
                title={mode.description}
                >
                    {mode.label}
                </button>
            ))}
        </div>
    );
};