import { BarChart3, PieChart, Info, Globe } from 'lucide-react'
import { ENGINE_CONFIG, QueryResult } from './types'
import { ActionPlanWidget } from '../results/ActionPlanWidget'
import { SchemaFixer } from '../results/SchemaFixer'
import { useState } from 'react'

interface CompetitiveResultsProps {
    results: {
        query: string
        comparison: Array<{
            url: string
            results: QueryResult[]
            engines_cited: number
            citation_rate: number
            share_of_voice: number
        }>
        total_engines: number
        action_plan?: Array<{
            type: string
            priority: 'high' | 'medium' | 'low'
            title: string
            description: string
            fix_action: string
        }>
    }
    yourUrl: string
}

export function CompetitiveResultsDisplay({ results, yourUrl }: CompetitiveResultsProps) {
    const [showSchemaFixer, setShowSchemaFixer] = useState(false)
    const totalCitations = results.comparison.reduce((sum, item) => sum + item.engines_cited, 0)

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Share of Voice Summary */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-6 shadow-sm">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-indigo-500/10 rounded-lg">
                            <BarChart3 className="w-5 h-5 text-indigo-400" />
                        </div>
                        <div>
                            <h3 className="text-base font-bold text-text-primary">Citation Share (SoV)</h3>
                            <p className="text-xs text-text-secondary">Percentage of total AI engine citations per brand.</p>
                        </div>
                    </div>

                    <div className="space-y-6">
                        {results.comparison.map((item) => {
                            const isUser = item.url === yourUrl
                            return (
                                <div key={item.url} className="space-y-2">
                                    <div className="flex items-center justify-between text-sm">
                                        <div className="flex items-center gap-2">
                                            <span className={`font-bold ${isUser ? 'text-indigo-400' : 'text-text-primary'}`}>
                                                {new URL(item.url).hostname}
                                            </span>
                                            {isUser && <span className="text-[10px] bg-indigo-500/10 text-indigo-400 px-1.5 py-0.5 rounded uppercase font-bold">You</span>}
                                        </div>
                                        <span className="font-mono text-xs text-text-secondary">
                                            {Math.round(item.share_of_voice * 100)}% ({item.engines_cited} citations)
                                        </span>
                                    </div>
                                    <div className="h-3 w-full bg-surface-highlight rounded-full overflow-hidden border border-border/50">
                                        <div
                                            className={`h-full rounded-full transition-all duration-1000 ${isUser ? 'bg-indigo-500' : 'bg-zinc-600'}`}
                                            style={{ width: `${item.share_of_voice * 100}%` }}
                                        />
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>

                <div className="bg-surface border border-border rounded-xl p-6 shadow-sm flex flex-col justify-center">
                    <div className="text-center space-y-2">
                        <div className="inline-flex p-3 bg-emerald-500/10 rounded-full mb-2">
                            <PieChart className="w-6 h-6 text-emerald-400" />
                        </div>
                        <h4 className="text-sm font-bold text-text-primary">Competitive Context</h4>
                        <p className="text-xs text-text-secondary px-4">
                            Across {results.total_engines} engines, there were {totalCitations} total references detected for this query group.
                        </p>
                    </div>
                </div>
            </div>

            {/* Action Plan (Task 4) */}
            {results.action_plan && results.action_plan.length > 0 && (
                <div className="space-y-4 animate-in fade-in slide-in-from-top-4 duration-1000 delay-150">
                    <ActionPlanWidget
                        actions={results.action_plan as any}
                        onFix={(action) => {
                            if (action.type === 'schema') setShowSchemaFixer(true)
                        }}
                    />

                    {showSchemaFixer && (
                        <div className="animate-in zoom-in-95 duration-300">
                            <SchemaFixer domain={new URL(yourUrl).hostname} title="" />
                        </div>
                    )}
                </div>
            )}

            {/* Side-by-Side Responses */}
            <div className="space-y-4">
                <div className="flex items-center gap-3">
                    <Globe className="w-5 h-5 text-text-secondary" />
                    <h3 className="text-lg font-bold text-text-primary">Response Comparison</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {results.comparison.map((brand) => (
                        <div key={brand.url} className={`flex flex-col border rounded-xl overflow-hidden bg-surface ${brand.url === yourUrl ? 'border-indigo-500/50 ring-1 ring-indigo-500/20' : 'border-border'}`}>
                            {/* Brand Header */}
                            <div className={`p-4 border-b flex items-center justify-between ${brand.url === yourUrl ? 'bg-indigo-500/5 border-indigo-500/20' : 'bg-surface-secondary border-border'}`}>
                                <div>
                                    <div className="text-xs font-bold uppercase tracking-wider text-text-secondary opacity-70">Source</div>
                                    <div className="text-sm font-black text-text-primary truncate max-w-[180px]">
                                        {new URL(brand.url).hostname}
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-[10px] font-bold uppercase tracking-wider text-text-secondary opacity-70">Visibility</div>
                                    <div className={`text-sm font-black ${brand.citation_rate > 0.5 ? 'text-emerald-400' : brand.citation_rate > 0 ? 'text-amber-400' : 'text-rose-400'}`}>
                                        {Math.round(brand.citation_rate * 100)}%
                                    </div>
                                </div>
                            </div>

                            {/* Responses */}
                            <div className="p-4 space-y-6 flex-1 bg-surface/50">
                                {brand.results.map((r, i) => {
                                    const engineConf = ENGINE_CONFIG[r.engine] || { name: r.engine, color: 'text-zinc-400' }
                                    return (
                                        <div key={i} className="space-y-2">
                                            <div className="flex items-center justify-between">
                                                <span className={`text-[10px] font-bold uppercase tracking-widest ${engineConf.color}`}>
                                                    {engineConf.name}
                                                </span>
                                                {r.citations.length > 0 && (
                                                    <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-400">
                                                        <Check className="w-2.5 h-2.5" /> Cited
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-xs text-text-secondary line-clamp-6 leading-relaxed bg-background/30 p-2 rounded-lg border border-border/30">
                                                {r.response}
                                            </p>
                                        </div>
                                    )
                                })}
                            </div>

                            {/* Bottom Alert If Gap */}
                            {brand.url !== yourUrl && brand.citation_rate > (results.comparison.find(b => b.url === yourUrl)?.citation_rate || 0) && (
                                <div className="p-3 bg-amber-500/10 border-t border-amber-500/20 flex items-center gap-2">
                                    <Info className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                                    <span className="text-[10px] text-amber-200 leading-tight font-medium">
                                        This competitor has higher visibility for this query.
                                    </span>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

function Check({ className }: { className?: string }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M20 6 9 17l-5-5" /></svg>
    )
}
