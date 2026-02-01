import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Minus, Calendar, AlertTriangle } from 'lucide-react'

interface TrendDatapoint {
    timestamp: string
    engine: string
    cited: boolean
    citation_count: number
    accuracy_score: number | null
    latency_ms: number
}

interface TrendChartProps {
    targetUrl: string
    query: string
    engine?: string
}

export function TrendChart({ targetUrl, query, engine }: TrendChartProps) {
    const [data, setData] = useState<TrendDatapoint[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!targetUrl || !query) return

        const fetchTrends = async () => {
            setLoading(true)
            setError(null)

            try {
                const params = new URLSearchParams({
                    target_url: targetUrl,
                    query: query,
                    days: '30'
                })
                if (engine) params.append('engine', engine)

                const response = await fetch(`/api/output-monitoring/trends?${params}`)
                if (!response.ok) throw new Error('Failed to fetch trends')

                const result = await response.json()
                setData(result.datapoints || [])
            } catch (e: any) {
                setError(e.message)
            } finally {
                setLoading(false)
            }
        }

        fetchTrends()
    }, [targetUrl, query, engine])

    if (loading) {
        return (
            <div className="p-4 text-center text-zinc-500">
                Loading trend data...
            </div>
        )
    }

    if (error) {
        return (
            <div className="p-4 text-center text-red-400">
                {error}
            </div>
        )
    }

    if (data.length === 0) {
        return (
            <div className="p-6 border border-zinc-800 rounded-xl bg-zinc-900/30 text-center">
                <Calendar className="w-8 h-8 text-zinc-600 mx-auto mb-3" />
                <p className="text-zinc-400 text-sm">No historical data yet</p>
                <p className="text-zinc-600 text-xs mt-1">
                    Run this query multiple times to see trends
                </p>
            </div>
        )
    }

    // Calculate trend
    const recentData = data.slice(-5)
    const olderData = data.slice(0, Math.max(0, data.length - 5))
    
    const recentCitationRate = recentData.filter(d => d.cited).length / recentData.length
    const olderCitationRate = olderData.length > 0 
        ? olderData.filter(d => d.cited).length / olderData.length 
        : recentCitationRate

    const trend = recentCitationRate - olderCitationRate
    const hasRegression = trend < -0.2 && olderData.length > 0

    // Group by date for display
    const groupedByDate: Record<string, TrendDatapoint[]> = {}
    data.forEach(dp => {
        const date = dp.timestamp.split('T')[0]
        if (!groupedByDate[date]) groupedByDate[date] = []
        groupedByDate[date].push(dp)
    })

    return (
        <div className="border border-zinc-800 rounded-xl bg-zinc-900/30 p-5">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/10 rounded-lg">
                        <TrendingUp className="w-4 h-4 text-blue-400" />
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-zinc-200">Citation Trends</h4>
                        <p className="text-xs text-zinc-500">Last 30 days</p>
                    </div>
                </div>

                {/* Trend Indicator */}
                <div className={`flex items-center gap-1 px-3 py-1 rounded-full ${
                    trend > 0.1 
                        ? 'bg-emerald-900/20 text-emerald-400' 
                        : trend < -0.1 
                        ? 'bg-red-900/20 text-red-400'
                        : 'bg-zinc-800 text-zinc-400'
                }`}>
                    {trend > 0.1 ? (
                        <TrendingUp className="w-3 h-3" />
                    ) : trend < -0.1 ? (
                        <TrendingDown className="w-3 h-3" />
                    ) : (
                        <Minus className="w-3 h-3" />
                    )}
                    <span className="text-xs font-medium">
                        {trend > 0.1 ? 'Improving' : trend < -0.1 ? 'Declining' : 'Stable'}
                    </span>
                </div>
            </div>

            {/* Regression Alert */}
            {hasRegression && (
                <div className="mb-4 p-3 bg-amber-900/10 border border-amber-900/20 rounded-lg flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
                    <div>
                        <p className="text-sm text-amber-400 font-medium">Citation Rate Dropped</p>
                        <p className="text-xs text-zinc-500 mt-0.5">
                            AI engines are citing your site less frequently than before
                        </p>
                    </div>
                </div>
            )}

            {/* Simple Timeline */}
            <div className="space-y-2">
                {Object.entries(groupedByDate).slice(-7).map(([date, points]) => {
                    const citedCount = points.filter(p => p.cited).length
                    const totalCount = points.length
                    const citedPercent = Math.round((citedCount / totalCount) * 100)

                    return (
                        <div key={date} className="flex items-center gap-3">
                            <span className="text-xs text-zinc-600 w-20 font-mono">
                                {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                            </span>
                            <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full transition-all ${
                                        citedPercent >= 50 ? 'bg-emerald-500' : citedPercent > 0 ? 'bg-amber-500' : 'bg-zinc-700'
                                    }`}
                                    style={{ width: `${citedPercent}%` }}
                                />
                            </div>
                            <span className={`text-xs w-12 text-right ${
                                citedPercent >= 50 ? 'text-emerald-400' : citedPercent > 0 ? 'text-amber-400' : 'text-zinc-600'
                            }`}>
                                {citedCount}/{totalCount}
                            </span>
                        </div>
                    )
                })}
            </div>

            {/* Stats */}
            <div className="mt-4 pt-4 border-t border-zinc-800 grid grid-cols-3 gap-4 text-center">
                <div>
                    <div className="text-lg font-bold text-zinc-100">
                        {data.length}
                    </div>
                    <div className="text-xs text-zinc-500">Total Queries</div>
                </div>
                <div>
                    <div className="text-lg font-bold text-emerald-400">
                        {Math.round(recentCitationRate * 100)}%
                    </div>
                    <div className="text-xs text-zinc-500">Recent Rate</div>
                </div>
                <div>
                    <div className="text-lg font-bold text-zinc-100">
                        {Math.round(data.reduce((sum, d) => sum + d.latency_ms, 0) / data.length)}ms
                    </div>
                    <div className="text-xs text-zinc-500">Avg Latency</div>
                </div>
            </div>
        </div>
    )
}
