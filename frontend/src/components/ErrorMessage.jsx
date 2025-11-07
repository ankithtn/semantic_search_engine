import React from "react";
import { AlertCircle, RefreshCcw } from "lucide-react";

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="max-w-xl mx-auto mt-10">
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-5 shadow-sm">
        <div className="flex items-start gap-3">
          <AlertCircle className="text-rose-500 mt-0.5" size={20} />
          <div className="flex-1">
            <div className="font-semibold text-rose-800">Something went wrong</div>
            <p className="mt-1 text-sm text-rose-700">
              {message || "An error occurred while searching. Please try again."}
            </p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="mt-3 inline-flex items-center gap-2 rounded-full border border-rose-300 bg-white px-3 py-1.5 text-sm text-rose-700 hover:bg-rose-100"
              >
                <RefreshCcw size={16} />
                Try again
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="mt-3 rounded-xl bg-white/70 backdrop-blur p-4 text-sm text-gray-600 border border-gray-200">
        <div className="font-medium mb-1">Common fixes</div>
        <ul className="list-disc list-inside space-y-1">
          <li>Backend is running? (http://localhost:8000/docs)</li>
          <li>Weaviate is up? (http://localhost:8080)</li>
          <li>Check network / proxy / CORS</li>
          <li>Try a longer or different query</li>
        </ul>
      </div>
    </div>
  );
};

export default ErrorMessage;
