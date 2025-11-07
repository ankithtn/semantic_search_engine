import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingSpinner({ message = "Searching..." }) {
  return (
    <div className="mx-auto mt-10 flex w-full max-w-xs items-center justify-center gap-3 rounded-2xl border border-gray-200 bg-white/70 backdrop-blur p-4 shadow-sm">
      <span className="relative inline-flex h-4 w-4">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-gray-400 opacity-25"></span>
        <span className="relative inline-flex h-4 w-4 rounded-full bg-gray-600"></span>
      </span>
      <span className="text-sm text-gray-700">{message}</span>
    </div>
  );
}
