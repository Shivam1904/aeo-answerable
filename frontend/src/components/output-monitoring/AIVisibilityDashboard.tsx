import { useMemo } from 'react'
import { TrendingUp, Heart, Hash, Eye, Target, Zap } from 'lucide-react'
import { MultiEngineResponse, ENGINE_CONFIG } from './types'

interface PromptResult {
    prompt: {
        id: string
        query: string
        category: string
        priority: string
    }
    result: MultiEngineResponse | null
}

interface AIVisibilityDashboardProps {
    results: PromptResult[]
    brandName: string
}

interface VisibilityMetrics {
    overallVisibility: number
    overallSentiment: number
    avgPosition: number
    engineBreakdown: Record<string, { visibility: number; cited: number; total: number }>
    categoryBreakdown: Record<string, { visibility: number; sentiment: number }>
    recommendations: string[]
}

export function AIVisibilityDashboard({ results, brandName }: AIVisibilityDashboardProps) {
    const metrics = useMemo(() => calculateMetrics(results, brandName), [results, brandName])

    const completedResults = results.filter(r => r.result)

    if (completedResults.length === 0) {
        return (
            <div className="border border-zinc-800 rounded-xl bg-zinc-900/30 p-8 text-center">
                <div className="p-4 bg-indigo-500/10 rounded-full w-fit mx-auto mb-4">
                    <Eye className="w-8 h-8 text-indigo-400" />
                </div>
                <h3 className="text-lg font-bold text-zinc-200 mb-2">AI Visibility Dashboard</h3>
                <p className="text-zinc-500 text-sm">
                    Run the smart prompts above to see your AI visibility metrics
                </p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Main Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Visibility Score */}
                <div className="p-6 border border-zinc-800 rounded-xl bg-zinc-900/30">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-emerald-500/10 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-emerald-400" />
                        </div>
                        <span className="text-sm font-medium text-zinc-400">Visibility</span>
                    </div>
                    <div className="flex items-end gap-2">
                        <span className={`text-4xl font-black ${getVisibilityColor(metrics.overallVisibility)}`}>
                            {metrics.overallVisibility}%
                        </span>
                    </div>
                    <p className="mt-2 text-xs text-zinc-500">
                        {getVisibilityDescription(metrics.overallVisibility)}
                    </p>
                    <div className="mt-3 w-full bg-zinc-800 rounded-full h-2">
                        <div
                            className={`h-2 rounded-full transition-all ${getVisibilityBarColor(metrics.overallVisibility)}`}
                            style={{ width: `${metrics.overallVisibility}%` }}
                        />
                    </div>
                </div>

                {/* Sentiment Score */}
                <div className="p-6 border border-zinc-800 rounded-xl bg-zinc-900/30">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-pink-500/10 rounded-lg">
                            <Heart className="w-5 h-5 text-pink-400" />
                        </div>
                        <span className="text-sm font-medium text-zinc-400">Sentiment</span>
                    </div>
                    <div className="flex items-end gap-2">
                        <span className={`text-4xl font-black ${getSentimentColor(metrics.overallSentiment)}`}>
                            {metrics.overallSentiment}
                        </span>
                        <span className="text-sm text-zinc-500 mb-2">/100</span>
                    </div>
                    <p className="mt-2 text-xs text-zinc-500">
                        {getSentimentDescription(metrics.overallSentiment)}
                    </p>
                    <div className="mt-3 flex items-center gap-2">
                        <span className="text-xs text-red-400">😠</span>
                        <div className="flex-1 bg-zinc-800 rounded-full h-2 relative">
                            <div
                                className="absolute top-0 h-2 bg-gradient-to-r from-red-500 via-yellow-500 to-emerald-500 rounded-full"
                                style={{ width: '100%' }}
                            />
                            <div
                                className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full border-2 border-zinc-900 shadow-lg transition-all"
                                style={{ left: `calc(${metrics.overallSentiment}% - 6px)` }}
                            />
                        </div>
                        <span className="text-xs text-emerald-400">😊</span>
                    </div>
                </div>

                {/* Average Position */}
                <div className="p-6 border border-zinc-800 rounded-xl bg-zinc-900/30">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-blue-500/10 rounded-lg">
                            <Hash className="w-5 h-5 text-blue-400" />
                        </div>
                        <span className="text-sm font-medium text-zinc-400">Avg Position</span>
                    </div>
                    <div className="flex items-end gap-2">
                        <span className={`text-4xl font-black ${getPositionColor(metrics.avgPosition)}`}>
                            {metrics.avgPosition > 0 ? metrics.avgPosition.toFixed(1) : '—'}
                        </span>
                    </div>
                    <p className="mt-2 text-xs text-zinc-500">
                        {getPositionDescription(metrics.avgPosition)}
                    </p>
                    {metrics.avgPosition > 0 && (
                        <div className="mt-3 flex items-center gap-1">
                            {[1, 2, 3, 4, 5].map(pos => (
                                <div
                                    key={pos}
                                    className={`w-6 h-6 rounded flex items-center justify-center text-xs font-bold ${Math.round(metrics.avgPosition) === pos
                                            ? 'bg-indigo-500 text-white'
                                            : 'bg-zinc-800 text-zinc-500'
                                        }`}
                                >
                                    {pos}
                                </div>
                            ))}
                            <span className="text-xs text-zinc-600 ml-1">+</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Engine Breakdown */}
            <div className="border border-zinc-800 rounded-xl bg-zinc-900/30 p-6">
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-purple-500/10 rounded-lg">
                        <Zap className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-zinc-200">Visibility by Engine</h4>
                        <p className="text-xs text-zinc-500">How often each AI engine cites your brand</p>
                    </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    {Object.entries(metrics.engineBreakdown).map(([engine, data]) => {
                        const config = ENGINE_CONFIG[engine] || { name: engine, color: 'text-zinc-400', bgColor: 'bg-zinc-500/10' }
                        return (
                            <div key={engine} className="text-center p-3 bg-zinc-800/50 rounded-lg">
                                <div className={`text-xs ${config.color} mb-2`}>{config.name}</div>
                                <div className="text-2xl font-bold text-zinc-100">
                                    {Math.round(data.visibility)}%
                                </div>
                                <div className="text-[10px] text-zinc-500">
                                    {data.cited}/{data.total} cited
                                </div>
                            </div>
                        )
                    })}
                </div>
            </div>

            {/* Recommendations */}
            {metrics.recommendations.length > 0 && (
                <div className="border border-amber-500/20 rounded-xl bg-amber-900/10 p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-amber-500/10 rounded-lg">
                            <Target className="w-5 h-5 text-amber-400" />
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-amber-200">Recommendations</h4>
                            <p className="text-xs text-zinc-500">Based on your AI visibility analysis</p>
                        </div>
                    </div>
                    <ul className="space-y-2">
                        {metrics.recommendations.map((rec, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                                <span className="text-amber-400 mt-0.5">→</span>
                                {rec}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    )
}

function calculateMetrics(results: PromptResult[], brandName: string): VisibilityMetrics {
    const completedResults = results.filter(r => r.result)

    if (completedResults.length === 0) {
        return {
            overallVisibility: 0,
            overallSentiment: 50,
            avgPosition: 0,
            engineBreakdown: {},
            categoryBreakdown: {},
            recommendations: []
        }
    }

    // Calculate overall visibility (% of engine responses that cite the brand)
    let totalCitations = 0
    let totalResponses = 0
    const engineStats: Record<string, { cited: number; total: number }> = {}
    const categoryStats: Record<string, { cited: number; total: number; sentimentSum: number }> = {}
    const allPositions: number[] = []
    const allResponses: string[] = []

    completedResults.forEach(({ prompt, result }) => {
        if (!result) return

        result.results.forEach(engineResult => {
            totalResponses++

            // Engine tracking
            if (!engineStats[engineResult.engine]) {
                engineStats[engineResult.engine] = { cited: 0, total: 0 }
            }
            engineStats[engineResult.engine].total++

            // Category tracking
            if (!categoryStats[prompt.category]) {
                categoryStats[prompt.category] = { cited: 0, total: 0, sentimentSum: 0 }
            }
            categoryStats[prompt.category].total++

            if (engineResult.citations.length > 0) {
                totalCitations++
                engineStats[engineResult.engine].cited++
                categoryStats[prompt.category].cited++

                // Track positions
                engineResult.citations.forEach(c => {
                    if (c.position > 0) allPositions.push(c.position)
                })
            }

            allResponses.push(engineResult.response)
        })
    })

    const overallVisibility = totalResponses > 0
        ? Math.round((totalCitations / totalResponses) * 100)
        : 0

    // Calculate sentiment
    const overallSentiment = calculateOverallSentiment(allResponses.join(' '), brandName)

    // Calculate average position
    const avgPosition = allPositions.length > 0
        ? allPositions.reduce((a, b) => a + b, 0) / allPositions.length
        : 0

    // Build engine breakdown
    const engineBreakdown: Record<string, { visibility: number; cited: number; total: number }> = {}
    Object.entries(engineStats).forEach(([engine, stats]) => {
        engineBreakdown[engine] = {
            visibility: stats.total > 0 ? (stats.cited / stats.total) * 100 : 0,
            cited: stats.cited,
            total: stats.total
        }
    })

    // Build category breakdown
    const categoryBreakdown: Record<string, { visibility: number; sentiment: number }> = {}
    Object.entries(categoryStats).forEach(([category, stats]) => {
        categoryBreakdown[category] = {
            visibility: stats.total > 0 ? (stats.cited / stats.total) * 100 : 0,
            sentiment: 50 // Placeholder
        }
    })

    // Generate recommendations
    const recommendations = generateRecommendations(overallVisibility, overallSentiment, avgPosition, engineBreakdown, brandName)

    return {
        overallVisibility,
        overallSentiment,
        avgPosition,
        engineBreakdown,
        categoryBreakdown,
        recommendations
    }
}

function calculateOverallSentiment(text: string, brandName: string): number {
    const lowerText = text.toLowerCase()
    const lowerBrand = brandName.toLowerCase()

    // Find sentences mentioning the brand
    const sentences = text.split(/[.!?]+/)
    const brandSentences = sentences.filter(s => s.toLowerCase().includes(lowerBrand))

    const positiveWords = ['great', 'excellent', 'good', 'best', 'amazing', 'love', 'recommend', 'helpful', 'powerful', 'innovative', 'reliable', 'trusted', 'leading', 'popular', 'top', 'quality', 'impressive', 'effective']
    const negativeWords = ['bad', 'poor', 'worst', 'terrible', 'hate', 'avoid', 'expensive', 'complicated', 'difficult', 'limited', 'outdated', 'issues', 'problems', 'lacking', 'mediocre', 'disappointing']

    let positive = 0
    let negative = 0

    const textToAnalyze = brandSentences.length > 0 ? brandSentences.join(' ') : text
    const words = textToAnalyze.toLowerCase().split(/\s+/)

    words.forEach(word => {
        if (positiveWords.some(pw => word.includes(pw))) positive++
        if (negativeWords.some(nw => word.includes(nw))) negative++
    })

    const total = positive + negative
    if (total === 0) return 60 // Neutral-positive default

    return Math.round((positive / total) * 100)
}

function generateRecommendations(
    visibility: number,
    sentiment: number,
    position: number,
    engines: Record<string, { visibility: number; cited: number; total: number }>,
    brandName: string
): string[] {
    const recs: string[] = []

    if (visibility < 30) {
        recs.push(`Create more authoritative content about ${brandName} to increase AI visibility`)
        recs.push('Add schema markup to help AI engines understand your content structure')
    } else if (visibility < 60) {
        recs.push('Focus on creating comparison content and "best of" articles')
        recs.push('Build more backlinks from authoritative sources')
    }

    if (sentiment < 50) {
        recs.push('Address negative perceptions by highlighting positive case studies and reviews')
        recs.push('Create content showcasing customer success stories')
    }

    if (position > 3) {
        recs.push('Create more comprehensive, in-depth content to improve ranking position')
    }

    // Engine-specific recommendations
    Object.entries(engines).forEach(([engine, stats]) => {
        if (stats.visibility < 20 && stats.total >= 2) {
            const engineName = ENGINE_CONFIG[engine]?.name || engine
            recs.push(`Low visibility on ${engineName} - consider optimizing content for this AI model`)
        }
    })

    // Limit to 4 recommendations
    return recs.slice(0, 4)
}

function getVisibilityColor(visibility: number): string {
    if (visibility >= 70) return 'text-emerald-400'
    if (visibility >= 40) return 'text-amber-400'
    return 'text-red-400'
}

function getVisibilityBarColor(visibility: number): string {
    if (visibility >= 70) return 'bg-emerald-500'
    if (visibility >= 40) return 'bg-amber-500'
    return 'bg-red-500'
}

function getVisibilityDescription(visibility: number): string {
    if (visibility >= 70) return 'Excellent! AI engines frequently cite your brand'
    if (visibility >= 40) return 'Good visibility, but room for improvement'
    if (visibility > 0) return 'Low visibility - AIs rarely mention your brand'
    return 'No visibility data yet'
}

function getSentimentColor(sentiment: number): string {
    if (sentiment >= 70) return 'text-emerald-400'
    if (sentiment >= 50) return 'text-amber-400'
    return 'text-red-400'
}

function getSentimentDescription(sentiment: number): string {
    if (sentiment >= 80) return 'Very positive brand perception'
    if (sentiment >= 60) return 'Generally positive sentiment'
    if (sentiment >= 40) return 'Mixed or neutral sentiment'
    return 'Negative sentiment detected'
}

function getPositionColor(position: number): string {
    if (position <= 0) return 'text-zinc-500'
    if (position <= 2) return 'text-emerald-400'
    if (position <= 4) return 'text-amber-400'
    return 'text-red-400'
}

function getPositionDescription(position: number): string {
    if (position <= 0) return 'No citation positions recorded'
    if (position <= 2) return 'Excellent! Top positions in AI responses'
    if (position <= 4) return 'Good positioning in AI answers'
    return 'Consider improving content to rank higher'
}
