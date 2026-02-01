import { useState } from 'react'
import { PageData } from '../../context/ReportContext'
import { MetricsDeepDive } from '../../components/results/MetricsDeepDive'
import { OutputMonitoring } from './OutputMonitoring'
import { BarChart3, Radio } from 'lucide-react'

interface PageDetailProps {
    page: PageData
}

type TabType = 'metrics' | 'output-monitoring'

export function PageDetail({ page }: PageDetailProps) {
    const [activeTab, setActiveTab] = useState<TabType>('metrics')

    // Pass full metric objects, not just scores
    const metricsMap = page.metrics ? { ...page.metrics } : {}

    const pagePath = new URL(page.url).pathname
    const pageHost = new URL(page.url).hostname

    const tabs: { id: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
        { id: 'metrics', label: 'Metrics', icon: BarChart3 },
        { id: 'output-monitoring', label: 'Output Monitoring', icon: Radio }
    ]

    return (
        <div className="max-w-4xl mx-auto animation-fade-in">
            <div className="flex items-start justify-between mb-8 pb-8 border-b border-zinc-800">
                <div>
                    <h2 className="text-2xl font-bold text-zinc-100 mb-1">{page.title || 'Untitled Page'}</h2>
                    <div className="flex items-center gap-2 font-mono text-zinc-500 text-sm">
                        <span className="text-zinc-400">{pageHost}</span>
                        <span className="text-zinc-600">/</span>
                        <span className="text-indigo-400">{pagePath}</span>
                    </div>
                </div>
                {page.page_score !== undefined && (
                    <div className="text-right">
                        <div className="text-4xl font-black text-white">{Math.round(page.page_score * 100)}</div>
                        <div className="text-xs text-zinc-500 uppercase tracking-widest font-bold">Page Score</div>
                    </div>
                )}
            </div>

            {/* Tab Navigation */}
            <div className="mb-6">
                <div className="flex gap-2 p-1 bg-zinc-900/50 border border-zinc-800 rounded-lg w-fit">
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
            </div>

            {/* Tab Content */}
            {activeTab === 'metrics' && (
                <>
                    <div className="mb-6">
                        <div className="p-4 bg-indigo-900/10 border border-indigo-500/20 rounded-lg">
                            <h4 className="text-sm font-bold text-indigo-200 mb-2">Page-Level Diagnostics</h4>
                            <p className="text-xs text-zinc-400">
                                Below is the detailed breakdown of the core AEO signals for this specific URL.
                                Compare these against the Site Average to find specific outliers.
                            </p>
                        </div>
                    </div>
                    <MetricsDeepDive metrics={metricsMap} />
                </>
            )}

            {activeTab === 'output-monitoring' && (
                <OutputMonitoring targetUrl={page.url} />
            )}
        </div>
    )
}
