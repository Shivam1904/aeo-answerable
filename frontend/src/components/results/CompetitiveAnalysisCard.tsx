import { Sparkles } from 'lucide-react'
import { MultiEngineResponse } from '../../types'

interface CompetitiveAnalysisCardProps {
    sotaInsights: NonNullable<MultiEngineResponse['sota_insights']>
}

export function CompetitiveAnalysisCard({ sotaInsights }: CompetitiveAnalysisCardProps) {
    return (
        <div className="rounded-xl border border-border bg-surface/50 overflow-hidden shadow-sm animate-in fade-in slide-in-from-bottom-2">
            <div className="p-6 border-b border-border">
                <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-1">Competitive Intelligence</h3>
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-bold text-text-primary">Share of Voice & Sentiment</h2>
                    <span className="px-2 py-1 bg-indigo-500/10 text-indigo-400 text-xs font-medium rounded-full border border-indigo-500/20">
                        SOTA Analysis
                    </span>
                </div>
            </div>

            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* 1. Share of Voice */}
                <div className="space-y-4">
                    <h4 className="text-sm font-medium text-text-primary">Competitive Visibility</h4>
                    <div className="space-y-3">
                        {sotaInsights.share_of_voice && Object.entries(sotaInsights.share_of_voice).map(([brand, score]) => (
                            <div key={brand} className="space-y-1">
                                <div className="flex justify-between text-xs">
                                    <span className="text-text-secondary">{brand}</span>
                                    <span className="font-medium text-text-primary">{score}%</span>
                                </div>
                                <div className="h-2 bg-surface-highlight rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                                        style={{ width: `${score}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* 2. Sentiment Radar */}
                <div className="space-y-4">
                    <h4 className="text-sm font-medium text-text-primary">Brand vs Industry Sentiment</h4>
                    <div className="space-y-6 pt-2">
                        {/* Brand */}
                        <div className="space-y-1 relative">
                            <div className="flex justify-between text-xs mb-1">
                                <span className="font-medium text-text-primary">Your Brand</span>
                                <span className={sotaInsights.sentiment_profile?.brand_sentiment > 50 ? 'text-emerald-400' : 'text-text-secondary'}>
                                    {sotaInsights.sentiment_profile?.brand_sentiment || 0}/100
                                </span>
                            </div>
                            <div className="h-2 bg-surface-highlight rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-emerald-500 rounded-full"
                                    style={{ width: `${sotaInsights.sentiment_profile?.brand_sentiment || 0}%` }}
                                />
                            </div>
                        </div>

                        {/* Industry */}
                        <div className="space-y-1 relative">
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-text-secondary">Industry Baseline</span>
                                <span className="text-text-secondary">{sotaInsights.sentiment_profile?.industry_benchmark || 0}/100</span>
                            </div>
                            <div className="h-2 bg-surface-highlight rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-text-secondary/30 rounded-full"
                                    style={{ width: `${sotaInsights.sentiment_profile?.industry_benchmark || 0}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Key Takeaways */}
            {sotaInsights.key_takeaways.length > 0 && (
                <div className="p-4 bg-surface-highlight/30 border-t border-border">
                    <ul className="space-y-2">
                        {sotaInsights.key_takeaways.map((takeaway, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                                <Sparkles className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0" />
                                <span>{takeaway}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    )
}
