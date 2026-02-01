import { CATEGORY_CONFIG, METRIC_CONFIG, type MetricResult } from './config'

interface MetricsDeepDiveProps {
    metrics?: Record<string, MetricResult | number>
}

export function MetricsDeepDive({ metrics = {} }: MetricsDeepDiveProps) {
    return (
        <div className="space-y-8">
            {Object.entries(CATEGORY_CONFIG).map(([catKey, catConfig]) => (
                <div key={catKey} className="border border-border rounded-xl overflow-hidden bg-surface/20">
                    {/* Category Header */}
                    <div className="px-6 py-4 bg-surface-highlight/50 border-b border-border flex items-center gap-3">
                        <div className="p-2 bg-surface rounded-lg border border-border">
                            <catConfig.icon className="w-5 h-5 text-text-secondary" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-text-primary">{catConfig.label}</h3>
                            <p className="text-xs text-text-secondary">{catConfig.description}</p>
                        </div>
                    </div>

                    {/* Metrics List */}
                    <div className="divide-y divide-border">
                        {Object.entries(METRIC_CONFIG)
                            .filter(([_, mConfig]) => mConfig.category === catKey)
                            .map(([mKey, mConfig]) => {
                                // Handle both raw number (legacy/simple) and full MetricResult object
                                const metricData = metrics[mKey]
                                const score = typeof metricData === 'number' ? metricData : metricData?.score || 0
                                const pct = Math.round(score * 100)
                                const color = pct >= 80 ? 'text-emerald-400' : pct >= 50 ? 'text-amber-400' : 'text-rose-400'
                                const barColor = pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-rose-500'

                                // Reasoning Data Extraction
                                const details = typeof metricData === 'object' ? metricData : null

                                return (
                                    <div key={mKey} className="p-6 hover:bg-surface-highlight/30 transition-colors group">
                                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-3">
                                            <div className="flex items-center gap-3">
                                                <mConfig.icon className="w-4 h-4 text-text-secondary group-hover:text-text-primary transition-colors" />
                                                <span className="font-mono text-sm font-medium text-text-primary">{mConfig.label}</span>
                                            </div>
                                            <div className="flex items-center gap-4">
                                                <div className="w-32 h-2 bg-surface-highlight rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full ${barColor}`}
                                                        style={{ width: `${pct}%` }}
                                                    />
                                                </div>
                                                <span className={`text-sm font-bold w-12 text-right ${color}`}>{pct}%</span>
                                            </div>
                                        </div>

                                        <p className="text-sm text-text-secondary pl-7 leading-relaxed mb-3">
                                            {mConfig.description}
                                        </p>

                                        {/* Structured Explanations from Reasoning Engine */}
                                        {details?.explanations && (() => {
                                            const { severity, reasons } = details.explanations

                                            if (!reasons || reasons.length === 0) return null

                                            // Severity-based styling
                                            const severityStyles = {
                                                success: {
                                                    bg: 'bg-emerald-900/10',
                                                    border: 'border-emerald-900/20',
                                                    text: 'text-emerald-400',
                                                    icon: '✓'
                                                },
                                                warning: {
                                                    bg: 'bg-amber-900/10',
                                                    border: 'border-amber-900/20',
                                                    text: 'text-amber-400',
                                                    icon: '⚠'
                                                },
                                                error: {
                                                    bg: 'bg-rose-900/10',
                                                    border: 'border-rose-900/20',
                                                    text: 'text-rose-400',
                                                    icon: '✗'
                                                }
                                            }

                                            const style = severityStyles[severity as keyof typeof severityStyles] || severityStyles.warning

                                            return (
                                                <div className={`ml-7 mt-3 p-3 ${style.bg} border ${style.border} rounded-md`}>
                                                    <div className={`flex items-center gap-2 mb-3 ${style.text}`}>
                                                        <span className="text-sm font-bold">{style.icon}</span>
                                                        <span className="text-xs font-bold uppercase tracking-wide">
                                                            {severity === 'success' ? 'Analysis' : severity === 'warning' ? 'Needs Improvement' : 'Issues Found'}
                                                        </span>
                                                    </div>

                                                    <div className="space-y-3">
                                                        {reasons.map((reason: any, i: number) => {
                                                            const reasonStyles = {
                                                                fact: 'text-text-primary',
                                                                issue: style.text.replace('400', '300'),
                                                                suggestion: 'text-primary'
                                                            }

                                                            const textColor = reasonStyles[reason.type as keyof typeof reasonStyles] || 'text-text-primary'

                                                            return (
                                                                <div key={i} className="text-xs">
                                                                    <div className={`${textColor} leading-relaxed`}>
                                                                        {reason.type === 'suggestion' && '💡 '}
                                                                        {reason.message}
                                                                    </div>

                                                                    {reason.examples && reason.examples.length > 0 && (
                                                                        <ul className="mt-1.5 space-y-1 ml-4">
                                                                            {reason.examples.map((ex: string, j: number) => (
                                                                                <li key={j} className="text-text-secondary font-mono text-[10px] pl-3 border-l border-border">
                                                                                    {ex}
                                                                                </li>
                                                                            ))}
                                                                        </ul>
                                                                    )}
                                                                </div>
                                                            )
                                                        })}
                                                    </div>
                                                </div>
                                            )
                                        })()}
                                    </div>
                                )
                            })}
                    </div>
                </div>
            ))}
        </div>
    )
}
