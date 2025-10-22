import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ message = 'Searching...' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="animate-spin text-blue-600 mb-4" size={48} />
      <p className="text-gray-600 text-lg font-medium">{message}</p>
      <p className="text-gray-400 text-sm mt-2">
        Analyzing {message === 'Searching...' ? 'thousands' : 'your query'} of documents...
      </p>
    </div>
  );
};

export default LoadingSpinner;