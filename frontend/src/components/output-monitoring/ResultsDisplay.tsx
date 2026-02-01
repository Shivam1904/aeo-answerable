
import { CheckCircle, ThumbsUp, ThumbsDown, Minus, Target, Sparkles } from 'lucide-react'
import { MultiEngineResponse } from './types'
import { EngineResponseCard } from './EngineResponseCard'
import { aggregateInsights } from './insightUtils'

interface ResultsDisplayProps {
    results: MultiEngineResponse
}

export function ResultsDisplay({ results }: ResultsDisplayProps) {
    const citedCount = results.results.filter(r => r.citations.length > 0).length
    const totalEngines = results.results.length

    // Client-side "AI" Analysis
    const insights = aggregateInsights(results.results)

    return (
        <div className="space-y-8 animation-fade-in">
            {/* Query Context */}
            {/* Unified Analysis Summary Card */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 overflow-hidden shadow-sm">
                {/* Header: Query */}
                <div className="p-6 border-b border-zinc-800/50 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1">
                        <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Analysis Report</h3>
                        <p className="text-xl font-semibold text-zinc-100 leading-tight">
                            "{results.query}"
                        </p>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-zinc-500">
                        <Target className="w-4 h-4" />
                        <span>Multi-Engine Audit</span>
                    </div>
                </div>

                {/* Metrics Grid (Compact Row) */}
                <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-zinc-800/50 bg-zinc-900/30">
                    {/* 1. Visibility */}
                    <div className="p-6 flex flex-col justify-center">
                        <div className="flex items-start justify-between mb-2">
                            <span className="text-sm font-medium text-zinc-400">Visibility</span>
                            <CheckCircle className={`w-4 h-4 ${results.citation_rate > 0.5 ? 'text-emerald-500' : 'text-zinc-600'}`} />
                        </div>
                        <div className="flex items-baseline gap-2">
                            <span className="text-2xl font-bold text-zinc-100">
                                {Math.round(results.citation_rate * 100)}%
                            </span>
                            <span className="text-xs text-zinc-500">citation rate</span>
                        </div>
                        <div className="mt-2 text-xs text-zinc-500">
                            {citedCount} / {totalEngines} engines
                        </div>
                    </div>

                    {/* 2. Sentiment */}
                    <div className="p-6 flex flex-col justify-center">
                        <div className="flex items-start justify-between mb-2">
                            <span className="text-sm font-medium text-zinc-400">Sentiment</span>
                            {insights.sentimentLabel === 'Positive' ? <ThumbsUp className="w-4 h-4 text-blue-500" /> : <Minus className="w-4 h-4 text-zinc-600" />}
                        </div>
                        <div className="flex items-baseline gap-2">
                            <span className={`text-2xl font-bold ${insights.sentimentLabel === 'Positive' ? 'text-blue-400' :
                                    insights.sentimentLabel === 'Negative' ? 'text-red-400' : 'text-zinc-300'
                                }`}>
                                {insights.sentimentLabel}
                            </span>
                        </div>
                        <div className="mt-3 w-full bg-zinc-800/50 h-1.5 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full ${insights.sentimentScore > 60 ? 'bg-blue-500' :
                                    insights.sentimentScore < 40 ? 'bg-red-500' : 'bg-zinc-500'
                                    }`}
                                style={{ width: `${insights.sentimentScore}%` }}
                            />
                        </div>
                    </div>

                    {/* 3. Themes */}
                    <div className="p-6 flex flex-col justify-center">
                        <span className="text-sm font-medium text-zinc-400 mb-3">Key Themes</span>
                        <div className="flex flex-wrap gap-1.5">
                            {insights.keyThemes.length > 0 ? (
                                insights.keyThemes.slice(0, 3).map(theme => (
                                    <span key={theme} className="px-2 py-1 bg-zinc-800/50 border border-zinc-700/50 text-zinc-300 text-[10px] uppercase font-medium rounded">
                                        {theme}
                                    </span>
                                ))
                            ) : (
                                <span className="text-xs text-zinc-600 italic">No specific themes detected</span>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Engine Responses Header */}
            <div className="pt-4">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-gradient-to-br from-zinc-800 to-zinc-900 rounded-lg border border-zinc-700/50">
                        <Sparkles className="w-4 h-4 text-purple-400" />
                    </div>
                    <h3 className="text-xl font-bold text-zinc-100">AI Engine Reponses</h3>
                </div>

                <div className="space-y-4">
                    {results.results.map((result) => (
                        <EngineResponseCard key={result.engine} result={result} />
                    ))}
                </div>
            </div>
        </div>
    )
}
