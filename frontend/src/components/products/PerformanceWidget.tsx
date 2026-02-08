import { ResponsiveContainer, AreaChart, Area, YAxis } from 'recharts'
import { Activity, BarChart3, Database } from 'lucide-react'

interface PerformanceWidgetProps {
    trend: number[]
    avgCitationRate: number
    totalQueries: number
    lastScanStatus: string
}

export function PerformanceWidget({ trend, avgCitationRate, totalQueries, lastScanStatus }: PerformanceWidgetProps) {
    const data = trend.map((val, i) => ({ val, i }))

    // Status color mapping
    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'complete': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
            case 'running': return 'text-blue-400 bg-blue-400/10 border-blue-400/20 animate-pulse'
            case 'error': return 'text-red-400 bg-red-400/10 border-red-400/20'
            default: return 'text-zinc-500 bg-zinc-500/10 border-zinc-500/20'
        }
    }

    return (
        <div className="mt-6 space-y-4 pt-4 border-t border-border/50">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-surface-highlight/50 border border-border/50">
                    <div className="flex items-center gap-2 text-zinc-500 mb-1">
                        <Activity className="w-3 h-3" />
                        <span className="text-[10px] font-medium uppercase tracking-wider">Adv. SoV</span>
                    </div>
                    <div className="text-lg font-bold text-text-primary">
                        {avgCitationRate}%
                    </div>
                </div>
                <div className="p-3 rounded-lg bg-surface-highlight/50 border border-border/50">
                    <div className="flex items-center gap-2 text-zinc-500 mb-1">
                        <BarChart3 className="w-3 h-3" />
                        <span className="text-[10px] font-medium uppercase tracking-wider">Queries</span>
                    </div>
                    <div className="text-lg font-bold text-text-primary">
                        {totalQueries}
                    </div>
                </div>
            </div>

            {/* Sparkline */}
            <div className="h-16 w-full -mx-1">
                {trend.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data}>
                            <defs>
                                <linearGradient id="colorSoV" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <YAxis hide domain={[0, 100]} />
                            <Area
                                type="monotone"
                                dataKey="val"
                                stroke="#6366f1"
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#colorSoV)"
                                animationDuration={1000}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-full flex items-center justify-center border border-dashed border-border/50 rounded-lg text-[10px] text-zinc-600">
                        No trend data available
                    </div>
                )}
            </div>

            {/* Last Scan Status */}
            <div className="flex items-center justify-between text-[10px]">
                <div className="flex items-center gap-1.5 text-zinc-500">
                    <Database className="w-3 h-3" />
                    <span>LATEST SCAN</span>
                </div>
                <span className={`px-2 py-0.5 rounded-full border border-solid font-bold uppercase ${getStatusColor(lastScanStatus)}`}>
                    {lastScanStatus}
                </span>
            </div>
        </div>
    )
}
