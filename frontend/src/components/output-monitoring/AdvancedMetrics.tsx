
import { AnalysisData } from '../../types'
import { Trophy, TrendingUp, AlertTriangle, CheckCircle, ThumbsUp, ThumbsDown, Minus } from 'lucide-react'

interface AdvancedMetricsProps {
    analysis?: AnalysisData
    brandName?: string
}

export function AdvancedMetrics({ analysis, brandName = "Brand" }: AdvancedMetricsProps) {
    if (!analysis) return null

    // const getSentimentColor = (score: number) => {
    //     if (score > 20) return 'text-green-500 bg-green-500/10'
    //     if (score < -20) return 'text-red-500 bg-red-500/10'
    //     return 'text-yellow-500 bg-yellow-500/10'
    // }

    const getRecommendationIcon = (rec: string) => {
        switch (rec?.toLowerCase()) {
            case 'winner': return <Trophy className="w-5 h-5 text-yellow-500" />
            case 'top contender': return <TrendingUp className="w-5 h-5 text-blue-500" />
            case 'not recommended': return <AlertTriangle className="w-5 h-5 text-red-500" />
            default: return <CheckCircle className="w-5 h-5 text-gray-400" />
        }
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 animate-in fade-in slide-in-from-bottom-2">
            {/* Share of Voice Card */}
            <div className="p-4 rounded-xl border border-border bg-surface/50">
                <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">Share of Voice</h4>
                <div className="flex items-end gap-2">
                    <span className="text-3xl font-bold text-text-primary">{analysis.share_of_voice || 0}%</span>
                    <span className="text-xs text-text-secondary mb-1">focus on {brandName}</span>
                </div>
                <div className="w-full bg-surface/80 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div
                        className="bg-indigo-500 h-full rounded-full transition-all duration-1000"
                        style={{ width: `${analysis.share_of_voice || 0}%` }}
                    />
                </div>
            </div>

            {/* Recommendation Status */}
            <div className="p-4 rounded-xl border border-border bg-surface/50">
                <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">Verdict</h4>
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-surface border border-border">
                        {getRecommendationIcon(analysis.recommendation || "")}
                    </div>
                    <div>
                        <div className="font-bold text-text-primary text-lg">{analysis.recommendation || "Neutral"}</div>
                        <div className="text-xs text-text-secondary">AI classification</div>
                    </div>
                </div>
            </div>

            {/* Attribute Sentiment */}
            {analysis.key_attributes && analysis.key_attributes.length > 0 && (
                <div className="col-span-1 md:col-span-2 p-4 rounded-xl border border-border bg-surface/50">
                    <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">Key Attributes</h4>
                    <div className="flex flex-wrap gap-2">
                        {analysis.key_attributes.map((attr, idx) => (
                            <div key={idx} className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-surface text-sm">
                                <span className="text-text-primary font-medium">{attr.name}</span>
                                {attr.sentiment === 'Positive' && <ThumbsUp className="w-3.5 h-3.5 text-green-500" />}
                                {attr.sentiment === 'Negative' && <ThumbsDown className="w-3.5 h-3.5 text-red-500" />}
                                {attr.sentiment === 'Neutral' && <Minus className="w-3.5 h-3.5 text-gray-400" />}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Hallucination Alert - Only show if present */}
            {analysis.hallucinations && analysis.hallucinations.length > 0 && (
                <div className="col-span-1 md:col-span-2 p-4 rounded-xl border border-red-200 bg-red-50/10">
                    <div className="flex items-center gap-2 mb-2 text-red-500">
                        <AlertTriangle className="w-4 h-4" />
                        <h4 className="text-xs font-bold uppercase tracking-wider">Potential Inaccuracies</h4>
                    </div>
                    <ul className="space-y-1">
                        {analysis.hallucinations.map((h, i) => (
                            <li key={i} className="text-sm text-text-secondary pl-5 relative before:content-['•'] before:absolute before:left-1 before:text-red-400">
                                {h}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    )
}
