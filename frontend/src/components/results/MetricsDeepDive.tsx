import { CATEGORY_CONFIG, METRIC_CONFIG } from './config'

interface MetricsDeepDiveProps {
    scores: Record<string, number>
}

export function MetricsDeepDive({ scores }: MetricsDeepDiveProps) {
    return (
        <div className="space-y-8">
            {Object.entries(CATEGORY_CONFIG).map(([catKey, catConfig]) => (
                <div key={catKey} className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-900/20">
                    {/* Category Header */}
                    <div className="px-6 py-4 bg-zinc-900/50 border-b border-zinc-800 flex items-center gap-3">
                        <div className="p-2 bg-zinc-950 rounded-lg border border-zinc-800">
                            <catConfig.icon className="w-5 h-5 text-zinc-400" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-zinc-200">{catConfig.label}</h3>
                            <p className="text-xs text-zinc-500">{catConfig.description}</p>
                        </div>
                    </div>

                    {/* Metrics List */}
                    <div className="divide-y divide-zinc-800">
                        {Object.entries(METRIC_CONFIG)
                            .filter(([_, mConfig]) => mConfig.category === catKey)
                            .map(([mKey, mConfig]) => {
                                const score = scores[mKey] || 0
                                const pct = Math.round(score * 100)
                                const color = pct >= 80 ? 'text-emerald-400' : pct >= 50 ? 'text-amber-400' : 'text-rose-400'
                                const barColor = pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-rose-500'

                                return (
                                    <div key={mKey} className="p-6 hover:bg-zinc-900/30 transition-colors">
                                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                                            <div className="flex items-center gap-3">
                                                <mConfig.icon className="w-4 h-4 text-zinc-600" />
                                                <span className="font-mono text-sm font-medium text-zinc-300">{mConfig.label}</span>
                                            </div>
                                            <div className="flex items-center gap-4">
                                                <div className="w-32 h-2 bg-zinc-800 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full ${barColor}`}
                                                        style={{ width: `${pct}%` }}
                                                    />
                                                </div>
                                                <span className={`text-sm font-bold w-12 text-right ${color}`}>{pct}%</span>
                                            </div>
                                        </div>
                                        <p className="text-sm text-zinc-500 pl-7 leading-relaxed">
                                            {mConfig.description}
                                        </p>
                                    </div>
                                )
                            })}
                    </div>
                </div>
            ))}
        </div>
    )
}
