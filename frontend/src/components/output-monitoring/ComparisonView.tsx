import { QueryResult, ENGINE_CONFIG } from './types'
import { GitCompare, CheckCircle, XCircle } from 'lucide-react'

interface ComparisonViewProps {
    results: QueryResult[]
}

export function ComparisonView({ results }: ComparisonViewProps) {
    if (results.length < 2) {
        return (
            <div className="p-4 text-center text-zinc-500">
                Need at least 2 engine responses for comparison
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-500/10 rounded-lg">
                    <GitCompare className="w-4 h-4 text-purple-400" />
                </div>
                <div>
                    <h3 className="text-lg font-bold text-zinc-100">Response Comparison</h3>
                    <p className="text-xs text-zinc-500">
                        Side-by-side comparison of AI engine responses
                    </p>
                </div>
            </div>

            {/* Comparison Grid */}
            <div className={`grid gap-4 ${results.length === 2 ? 'grid-cols-2' : 'grid-cols-3'}`}>
                {results.map((result, i) => {
                    const config = ENGINE_CONFIG[result.engine] || {
                        name: result.engine,
                        color: 'text-zinc-400',
                        bgColor: 'bg-zinc-500/10'
                    }
                    const hasCitations = result.citations.length > 0

                    return (
                        <div
                            key={`${result.engine}-${i}`}
                            className={`border rounded-xl p-4 ${hasCitations
                                    ? 'border-emerald-500/30 bg-emerald-900/5'
                                    : 'border-zinc-800 bg-zinc-900/30'
                                }`}
                        >
                            {/* Engine Header */}
                            <div className="flex items-center justify-between mb-3 pb-3 border-b border-zinc-800">
                                <div className="flex items-center gap-2">
                                    <span className={`text-sm font-bold ${config.color}`}>
                                        {config.name}
                                    </span>
                                </div>
                                {hasCitations ? (
                                    <span className="flex items-center gap-1 text-xs text-emerald-400">
                                        <CheckCircle className="w-3 h-3" />
                                        Cited
                                    </span>
                                ) : (
                                    <span className="flex items-center gap-1 text-xs text-zinc-500">
                                        <XCircle className="w-3 h-3" />
                                        Not cited
                                    </span>
                                )}
                            </div>

                            {/* Response Preview */}
                            <div className="text-sm text-zinc-400 leading-relaxed max-h-60 overflow-y-auto">
                                {result.error ? (
                                    <span className="text-red-400">{result.error}</span>
                                ) : (
                                    <p className="whitespace-pre-wrap">
                                        {result.response.length > 500
                                            ? result.response.substring(0, 500) + '...'
                                            : result.response}
                                    </p>
                                )}
                            </div>

                            {/* Stats Footer */}
                            <div className="mt-3 pt-3 border-t border-zinc-800 flex items-center justify-between text-xs text-zinc-600">
                                <span>{result.tokens_used} tokens</span>
                                <span>{result.latency_ms}ms</span>
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Citation Summary */}
            <div className="p-4 bg-zinc-900/50 border border-zinc-800 rounded-lg">
                <h4 className="text-sm font-bold text-zinc-300 mb-2">Citation Summary</h4>
                <div className="flex flex-wrap gap-3">
                    {results.map((result, i) => {
                        const config = ENGINE_CONFIG[result.engine]
                        const hasCitations = result.citations.length > 0

                        return (
                            <div
                                key={`${result.engine}-${i}`}
                                className={`flex items-center gap-2 px-3 py-2 rounded-lg ${hasCitations ? 'bg-emerald-900/20' : 'bg-zinc-800'
                                    }`}
                            >
                                {hasCitations ? (
                                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                                ) : (
                                    <XCircle className="w-4 h-4 text-zinc-500" />
                                )}
                                <span className={`text-sm ${hasCitations ? 'text-emerald-400' : 'text-zinc-500'}`}>
                                    {config?.name || result.engine}
                                </span>
                                {hasCitations && (
                                    <span className="text-xs text-emerald-600">
                                        ({result.citations.length})
                                    </span>
                                )}
                            </div>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}
