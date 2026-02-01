import { Code2 } from 'lucide-react'
import { useReport } from '../../context/ReportContext'
import { METRIC_CONFIG } from '../../components/results/config'
import { MetricsDeepDive } from '../../components/results/MetricsDeepDive'

export function SiteMetrics() {
    const { data } = useReport()

    if (!data) return null

    // Compute site-wide averges for each metric
    const metricAverages: Record<string, number> = {}

    // Initialize
    Object.keys(METRIC_CONFIG).forEach(key => metricAverages[key] = 0)

    data.pages.forEach(page => {
        const metrics = page.metrics || {}
        Object.entries(metrics).forEach(([key, val]: [string, any]) => {
            if (metricAverages[key] !== undefined) {
                metricAverages[key] += val.score
            }
        })
    })

    // Average out
    Object.keys(metricAverages).forEach(key => {
        metricAverages[key] = metricAverages[key] / (data.pages.length || 1)
    })

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <header>
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-indigo-500/10 rounded-lg">
                        <Code2 className="w-5 h-5 text-indigo-400" />
                    </div>
                    <h2 className="text-2xl font-bold text-text-primary">Structural Analysis</h2>
                </div>
                <p className="text-text-secondary">Auditing your code to see if an AI *can* read it.</p>
            </header>

            <div className="pt-4 border-t border-border">
                <MetricsDeepDive metrics={metricAverages} />
            </div>
        </div>
    )
}
