import React from 'react';
import ResultCard from './ResultCard';

const ResultsList = ({results, searchTime, totalCount}) => {
    if(!results || results.length === 0) {
        return null;
    }

    return (
        <div className='w-full max-w-5xl mx-auto mt-8'>
            {/*Stats Bar*/}
            <div className='bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg mb-6'>
                <div className='flex justify-between items-center text-sm'>
                    <div className='flex gap-6'>
                        <span className='text-gray-700'>
                            Found <strong className='text-blue-700'>{totalCount || results.length}</strong> results
                        </span>
                        {searchTime && (
                            <span className='text-gray-700'>
                                Search time: <strong className='text-blue-700'>{searchTime.toFixed(2)}s</strong>
                            </span>
                        )}
                    </div>
                    <span className='text-gray-600'>
                        Showing 1-{results.length}
                    </span>
                </div>
            </div>
            
            {/* Results */}
            <div className='space-y-4'>
                {results.map((results, index) => (
                    <ResultCard key = {index} result = {result} index={index}/>
                ))}
            </div>

            {/* Load more (placeholder for pagination)*/}
            {results.length >= 10 && (
                <div className='text-center mt-8'>
                    <button className='px-6 py-3 bg-white border-2 border-blue-600 text-blue-600
                    rounded-lg hover:bg-blue-50 transition-colors font-medium'>
                        Load More Results
                    </button>
                </div>
            )}
        </div>
    );
};

export default ResultsList;