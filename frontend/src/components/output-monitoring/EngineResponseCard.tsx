import { useState } from 'react'
import { ChevronDown, ChevronRight, Bot, CheckCircle, XCircle, ExternalLink } from 'lucide-react'
import { ENGINE_CONFIG, QueryResult } from './types'
import { AdvancedMetrics } from './AdvancedMetrics'

interface EngineResponseCardProps {
    result: QueryResult
    brandName?: string
}

export function EngineResponseCard({ result, brandName }: EngineResponseCardProps) {
    const [isExpanded, setIsExpanded] = useState(true)

    const hasCitations = result.citations.length > 0
    const hasError = !!result.error
    const config = ENGINE_CONFIG[result.engine] || {
        name: result.engine,
        color: 'text-text-secondary',
        bgColor: 'bg-surface/10'
    }

    return (
        <div className="group border border-border bg-surface/20 rounded-xl overflow-hidden hover:border-text-secondary/30 transition-all">
            {/* Header (Clickable for toggle) */}
            <div
                onClick={() => setIsExpanded(!isExpanded)}
                className="px-6 py-4 flex items-center justify-between bg-surface/30 cursor-pointer hover:bg-surface/50 transition-colors select-none"
            >
                <div className="flex items-center gap-3">
                    <div className="text-text-secondary group-hover:text-text-primary transition-colors">
                        {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </div>

                    <div className={`p-2 rounded-lg ${config.bgColor}`}>
                        <Bot className={`w-4 h-4 ${config.color}`} />
                    </div>
                    <div>
                        <h4 className="font-bold text-text-primary">{config.name}</h4>
                    </div>
                </div>

                {/* Status Badges */}
                <div className="flex items-center gap-2">
                    {result.analysis?.recommendation && (
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${result.analysis.recommendation === 'Winner' ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400' :
                                result.analysis.recommendation.includes('Contender') ? 'bg-blue-500/10 border-blue-500/20 text-blue-400' :
                                    'bg-surface-highlight border-border text-text-secondary'
                            }`}>
                            {result.analysis.recommendation}
                        </span>
                    )}

                    {hasCitations && !hasError && (
                        <span className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="text-xs font-medium text-emerald-400">Cited You</span>
                        </span>
                    )}
                    {!hasCitations && !hasError && (
                        <span className="flex items-center gap-1.5 px-3 py-1 bg-surface-highlight border border-border rounded-full">
                            <XCircle className="w-3.5 h-3.5 text-text-secondary" />
                            <span className="text-xs font-medium text-text-secondary">No Mention</span>
                        </span>
                    )}
                </div>
            </div>

            {/* Content (Collapsible) */}
            {isExpanded && (
                <div className="p-6 border-t border-border/50 animate-in slide-in-from-top-2 fade-in duration-200">
                    {hasError ? (
                        <div className="p-4 bg-red-900/10 border border-red-900/20 rounded-lg">
                            <p className="text-sm text-red-400">
                                <strong>Error:</strong> {result.error}
                            </p>
                        </div>
                    ) : (
                        <>
                            {/* Advanced Metrics Visualization */}
                            {result.analysis && (
                                <div className="mb-6">
                                    <AdvancedMetrics analysis={result.analysis} brandName={brandName} />
                                </div>
                            )}

                            <div className="prose prose-invert prose-sm max-w-none">
                                <p className="text-text-primary leading-relaxed whitespace-pre-wrap">
                                    {result.response}
                                </p>
                            </div>

                            {/* Citations (More Prominent) */}
                            {hasCitations && (
                                <div className="mt-6 pt-5 border-t border-border">
                                    <h5 className="text-xs font-bold text-emerald-400 uppercase tracking-wide mb-3 flex items-center gap-2">
                                        <ExternalLink className="w-3 h-3" />
                                        Sources Found
                                    </h5>
                                    <div className="grid gap-3">
                                        {result.citations.map((citation, i) => (
                                            <a
                                                key={i}
                                                href={citation.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="relative overflow-hidden group/link flex flex-col p-3 bg-surface border border-border hover:border-emerald-500/30 rounded-xl transition-all hover:shadow-lg hover:shadow-emerald-500/5"
                                            >
                                                <div className="flex items-start justify-between gap-3">
                                                    <div className="flex-1 min-w-0">
                                                        <div className="text-[10px] font-mono text-emerald-500/60 uppercase tracking-tighter mb-1">Source Link</div>
                                                        <div className="text-xs font-medium text-text-primary group-hover/link:text-emerald-400 transition-colors truncate">
                                                            {citation.url}
                                                        </div>
                                                    </div>
                                                    <div className="mt-4 p-1.5 bg-surface-highlight rounded-lg group-hover/link:bg-emerald-500/10 transition-colors">
                                                        <ExternalLink className="w-3 h-3 text-text-secondary group-hover/link:text-emerald-400" />
                                                    </div>
                                                </div>
                                                {citation.snippet && (
                                                    <div className="mt-2 text-[11px] text-text-secondary italic line-clamp-2 border-l-2 border-border pl-3 group-hover/link:border-emerald-500/30 transition-colors">
                                                        "{citation.snippet}"
                                                    </div>
                                                )}

                                                {/* Decorative background bar on hover */}
                                                <div className="absolute left-0 bottom-0 h-0.5 w-0 bg-emerald-500 group-hover/link:w-full transition-all duration-300" />
                                            </a>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    )
}
