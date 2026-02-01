
import { CheckCircle, XCircle, ExternalLink, Bot } from 'lucide-react'
import { QueryResult, ENGINE_CONFIG } from './types'

interface EngineResponseCardProps {
    result: QueryResult
}

export function EngineResponseCard({ result }: EngineResponseCardProps) {
    const hasCitations = result.citations.length > 0
    const hasError = !!result.error
    const config = ENGINE_CONFIG[result.engine] || {
        name: result.engine,
        color: 'text-zinc-400',
        bgColor: 'bg-zinc-500/10'
    }

    return (
        <div className="group border border-zinc-800 bg-zinc-900/20 rounded-xl overflow-hidden hover:border-zinc-700 transition-all">
            {/* Minimal Header */}
            <div className="px-6 py-4 flex items-center justify-between bg-zinc-900/30">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${config.bgColor}`}>
                        <Bot className={`w-4 h-4 ${config.color}`} />
                    </div>
                    <div>
                        <h4 className="font-bold text-zinc-200">{config.name}</h4>
                    </div>
                </div>

                {/* Status Badge */}
                <div>
                    {hasCitations && !hasError && (
                        <span className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="text-xs font-medium text-emerald-400">Cited You</span>
                        </span>
                    )}
                    {!hasCitations && !hasError && (
                        <span className="flex items-center gap-1.5 px-3 py-1 bg-zinc-800/50 border border-zinc-700 rounded-full">
                            <XCircle className="w-3.5 h-3.5 text-zinc-500" />
                            <span className="text-xs font-medium text-zinc-500">No Mention</span>
                        </span>
                    )}
                </div>
            </div>

            {/* Content */}
            <div className="p-6">
                {hasError ? (
                    <div className="p-4 bg-red-900/10 border border-red-900/20 rounded-lg">
                        <p className="text-sm text-red-400">
                            <strong>Error:</strong> {result.error}
                        </p>
                    </div>
                ) : (
                    <>
                        <div className="prose prose-invert prose-sm max-w-none">
                            <p className="text-zinc-300 leading-relaxed whitespace-pre-wrap">
                                {result.response}
                            </p>
                        </div>

                        {/* Citations (More Prominent) */}
                        {hasCitations && (
                            <div className="mt-6 pt-5 border-t border-zinc-800/50">
                                <h5 className="text-xs font-bold text-emerald-400 uppercase tracking-wide mb-3 flex items-center gap-2">
                                    <ExternalLink className="w-3 h-3" />
                                    Sources Found
                                </h5>
                                <div className="grid gap-2">
                                    {result.citations.map((citation, i) => (
                                        <a
                                            key={i}
                                            href={citation.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="block p-3 bg-zinc-900 border border-zinc-800 hover:border-emerald-500/30 rounded-lg transition-colors group/link"
                                        >
                                            <div className="flex items-start justify-between gap-2">
                                                <div className="text-xs font-mono text-indigo-400 group-hover/link:text-indigo-300 break-all">
                                                    {citation.url}
                                                </div>
                                                <ExternalLink className="w-3 h-3 text-zinc-600 group-hover/link:text-emerald-400" />
                                            </div>
                                            {citation.snippet && (
                                                <p className="mt-1 text-xs text-zinc-500 line-clamp-1 italic">
                                                    "...{citation.snippet}..."
                                                </p>
                                            )}
                                        </a>
                                    ))}
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    )
}
