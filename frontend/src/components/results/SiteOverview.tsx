import { CATEGORY_CONFIG, METRIC_CONFIG } from './config'

interface SiteOverviewProps {
    pages: any[] // We need the full page list to compute averages
}

function SiteScoreRing({ score, size = 160 }: { score: number, size?: number }) {
    const pct = Math.round(score * 100)
    const radius = (size - 12) / 2
    const circumference = 2 * Math.PI * radius
    const offset = circumference - (score * circumference)

    // Semantic colors only for the DATA, not the decoration
    const color = pct >= 80 ? '#22c55e' : pct >= 50 ? '#eab308' : '#ef4444'

    return (
        <div className="relative" style={{ width: size, height: size }}>
            <svg className="transform -rotate-90" width={size} height={size}>
                {/* Track */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke="var(--border)"
                    strokeWidth="12"
                    className="opacity-50"
                />
                {/* Indicator */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={color}
                    strokeWidth="12"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    className="transition-all duration-1000"
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-black text-text-primary">{pct}</span>
                <span className="text-xs text-text-secondary uppercase font-bold tracking-wider mt-1">AEO Score</span>
            </div>
        </div>
    )
}

function CategoryStat({ config, score }: { config: any, score: number }) {
    const pct = Math.round(score * 100)
    const color = pct >= 80 ? 'text-emerald-400' : pct >= 50 ? 'text-amber-400' : 'text-rose-400'
    const barColor = pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-rose-500'

    return (
        <div className="flex flex-col p-4 bg-surface border border-border rounded-lg hover:border-text-secondary/30 transition-colors">
            <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-surface-highlight rounded border border-border">
                    <config.icon className="w-4 h-4 text-text-secondary" />
                </div>
                <span className="text-xs font-bold text-text-secondary uppercase tracking-wider">{config.label}</span>
            </div>

            <div className="flex items-end justify-between mb-2">
                <span className={`text-2xl font-black ${color}`}>{pct}%</span>
            </div>

            <div className="h-1.5 w-full bg-surface-highlight rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full ${barColor} opacity-80`}
                    style={{ width: `${pct}%` }}
                />
            </div>
        </div>
    )
}

export function SiteOverview({ pages }: SiteOverviewProps) {
    if (!pages || pages.length === 0) return null

    // 1. Calculate Site-Wide Average Score
    const totalScore = pages.reduce((acc, p) => {
        const s = p.page_score ?? (p.audits.structure.score + p.audits.clarity.score) / 2
        return acc + s
    }, 0)
    const avgScore = totalScore / pages.length

    // 2. Calculate Aggregated Category Scores
    const catTotals: Record<string, number> = {}
    const catCounts: Record<string, number> = {}

    // Initialize
    Object.keys(CATEGORY_CONFIG).forEach(key => {
        catTotals[key] = 0
        catCounts[key] = 0
    })

    pages.forEach(page => {
        const metrics = page.metrics || {}
        // Group metrics by category for this page first
        const pageCatSums: Record<string, number[]> = {}

        Object.entries(metrics).forEach(([key, val]: [string, any]) => {
            const conf = METRIC_CONFIG[key]
            if (conf) {
                if (!pageCatSums[conf.category]) pageCatSums[conf.category] = []
                pageCatSums[conf.category].push(val.score)
            }
        })

        // Add this page's category averages to the site totals
        Object.entries(pageCatSums).forEach(([cat, scores]) => {
            if (scores.length > 0) {
                const avg = scores.reduce((a, b) => a + b, 0) / scores.length
                catTotals[cat] += avg
                catCounts[cat]++
            }
        })
    })

    return (
        <div className="mb-10 p-8 rounded-xl bg-surface/30 border border-border">
            <div className="flex flex-col lg:flex-row items-start gap-12">

                {/* Visual Score */}
                <div className="shrink-0 flex flex-col items-center gap-4">
                    <SiteScoreRing score={avgScore} />
                    <div className="text-center">
                        <div className="text-sm font-bold text-text-primary">
                            {pages.length} Pages Analyzed
                        </div>
                    </div>
                </div>

                {/* Grid Breakdown */}
                <div className="flex-1 w-full">
                    <div className="mb-6">
                        <h2 className="text-xl font-bold text-text-primary mb-2">Site Performance Vitals</h2>
                        <p className="text-sm text-text-secondary max-w-2xl">
                            Aggregate performance across all scanned pages. Use this to identify systemic issues
                            (e.g., if Schema is consistently low across the site).
                        </p>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
                        {Object.entries(CATEGORY_CONFIG).map(([key, config]) => {
                            const count = catCounts[key] || 1
                            const score = catTotals[key] / count
                            return <CategoryStat key={key} config={config} score={score} />
                        })}
                    </div>
                </div>
            </div>
        </div>
    )
}
