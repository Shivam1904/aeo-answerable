import { useState } from 'react'
import { Code2, Radio } from 'lucide-react'
import { useReport } from '../../context/ReportContext'
import { METRIC_CONFIG } from '../../components/results/config'
import { MetricsDeepDive } from '../../components/results/MetricsDeepDive'
import { OutputMonitoring } from './OutputMonitoring'

export function SiteMetrics() {
    const { data } = useReport()
    const [activeTab, setActiveTab] = useState<'structure' | 'monitoring'>('structure')

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

    // Derive site URL from the first page or use a fallback
    const siteUrl = data.pages.length > 0 ? new URL(data.pages[0].url).origin : ''

    const tabs = [
        {
            id: 'structure' as const,
            label: 'Structural Analysis',
            icon: Code2,
            description: "auditing your code to see if an AI *can* read it"
        },
        {
            id: 'monitoring' as const,
            label: 'Output Monitoring',
            icon: Radio,
            description: "running prompts to see what the AI says"
        }
    ]

    const activeTabInfo = tabs.find(t => t.id === activeTab)!

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <header>
                <h2 className="text-2xl font-bold text-zinc-100">{activeTabInfo.label}</h2>
                <p className="text-zinc-400">{activeTabInfo.description}</p>
            </header>

            {/* Tab Navigation */}
            <div className="flex items-center gap-2 p-1 bg-zinc-900/50 border border-zinc-800 rounded-lg w-fit">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === tab.id
                            ? 'bg-indigo-600 text-white'
                            : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800'
                            }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="pt-4 border-t border-zinc-800">
                {activeTab === 'structure' && (
                    <MetricsDeepDive metrics={metricAverages} />
                )}

                {activeTab === 'monitoring' && siteUrl && (
                    <OutputMonitoring targetUrl={siteUrl} />
                )}
            </div>
        </div>
    )
}
