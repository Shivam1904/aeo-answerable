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
        <div className="max-w-4xl mx-auto">
            <header className="mb-8">
                <h2 className="text-2xl font-bold text-zinc-100">Site Metrics Deep Dive</h2>
                <p className="text-zinc-400">Analysis of all 22 core AEO signals across the entire site.</p>
            </header>

            <MetricsDeepDive metrics={metricAverages} />
        </div>
    )
}
