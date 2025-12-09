import React from "react";
import { Sparkles, Clock, Zap } from "lucide-react";

export default function AIAnswerCard({ aiAnswer, query, totalPapers}) {
    if (!aiAnswer) return null;

    const hasError = aiAnswer.error;
    
    return (
        <div className="w-full max-w-6xl mx-auto mb-6 mt-5">
            <div className={`rounded-2xl border ${hasError ? 'border-rose-200 bg-rose-50' : 'border-gray-200 bg-white'} p-6 shadow-sm`}>
              {/* Header */}
              <div className="flex items-center gap-3 mb-4  pb-3 border-b border-gray-200">
                <div className="flex items-center gap-2">
                    <Sparkles className="text-gray-900" size={20} />
                    <h3 className="text-lg font-semibold text-gray-900">AI Answer</h3>
                </div>

                <div className="ml-auto flex items-center gap-3 text-xs text-gray-500">
                    <div className="flex items-center gap-1">
                        <Zap size={14} />
                        <span>{aiAnswer.model}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Clock size={14} />
                        <span>{aiAnswer.generationTime?.toFixed(2)}s</span>
                    </div>
                    {aiAnswer.tokensUsed > 0 && (
                        <div>
                            <span>{aiAnswer.tokensUsed} tokens</span>
                        </div>
                    )}
                </div>
              </div>
              
              {/* Query Display */}
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-1 font-medium">Your Question:</p>
                <p className="text-gray-900">{query}</p>
              </div>

              {/* Answer or Error */}
              {hasError ? (
                <div className="bg-rose-100 rounded-xl p-4 border border-rose-200">
                    <p className="text-sm text-rose-800">
                        <strong> Error generating AI answer:</strong> {aiAnswer.error}
                    </p>
                    <p className="text-xs text-rose-600 mt-2">
                        Search results are still available below. The AI answer generation encountered an issue.
                    </p>
                </div>
              ): (
                <>
                <div className="mb-3">
                    <p className="text-sm text-gray-600 mb-2 font-medium">Answer:</p>
                    <div className="prose prose-sm max-w-none">
                        <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                            {aiAnswer.answer}
                        </p>
                    </div>
                </div>

                {/* Footer Info */}
                <div className="mt-4 pt-3 border-t border-gray-200">
                    <p className="text-xs text-gray-500">
                        Answer generated from analysis of {totalPapers} research papers
                    </p>
                </div>
                </>
            )}
            </div>
        </div>
    );
}