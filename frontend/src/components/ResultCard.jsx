import React, {useState} from 'react';
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

const ResultCard = ({result, index}) => {
    const [isExpanded, setIsExpanded] = useState(false);

    //Get score color based on relavance
    const getScoreColor = (score) => {
        if (score >= 0.8) return 'bg-green-100 text-green-800';
        if (score >= 0.6) return 'bg-yellow-100 text-yellow-800';
        return 'bg-gray-100 text-gray-800';
    };

    // Format score as percentage
    const formatScore = (score) => {
        return `${(score * 100).toFixed(0)}%`;
    };

    return (
        <div className="bg-white rounded-lg border-2 border-gray-200 hover:border-blue-400
                        p-6 transition-all duration-200 hover:shadow-lg">
        {/*Header*/}
        <div className='flex justify-between items-start mb-3'>
            <span className='text-sm font-semibold text-gray-500'>
                Result #{index + 1}
            </span>
            {result.score && (
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(result.score)}`}>
                    {formatScore(result.score)} Match
                </span>
            )}
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold text-gray-900 mb-3 leading-tight">
            {result.title}
        </h3>

        {/* Metadata */}
        <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
            {result.year && (
                <span className="flex items-center gap-1">
                    {result.year}
                </span>
            )}
            {result.journal && (
                <span className="flex items-center gap-1">
                    {result.journal}
                </span>
            )}
            {result.pmid && (
                <span className="flex items-center gap-1">
                    PMID: {result.pmid}
                </span>
            )}
        </div>

        {/* Snippet */}
        <div className="text-gray-700 leading-relaxed mb-4">
            {isExpanded ? (
                <p>{result.abstract || result.snippet}</p>
            ) : (
            <p>
                {(result.abstract || result.snippet || '').substring(0, 200)}
                {(result.abstract || result.snippet || '').length > 200 && '...'}
            </p>
        )}
        </div>
        
        {/* Actions */}
        <div className="flex justify-between items-center pt-4 border-t border-gray-200">
            <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 
                    font-medium transition-colors"
            >
                {isExpanded ? (
                    <>
                    <ChevronUp size={18} />
                    Show Less
                    </>
                    ) : (
                    <>
                    <ChevronDown size={18} />
                    View Full Abstract
                    </>
                )}
            </button>
            
            {result.pmid && (
                <a
                href={getPubmedLink(result.pmid)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-blue-600 hover:text-blue-800 
                font-medium transition-colors"
                >
                    PubMed Link
                    <ExternalLink size={16} />
                </a>
            )}
            </div>
        </div>
    );
};

export default ResultCard;