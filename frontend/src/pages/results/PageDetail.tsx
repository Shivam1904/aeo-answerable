import { PageData } from '../../context/ReportContext'
import { MetricsDeepDive } from '../../components/results/MetricsDeepDive'

interface PageDetailProps {
    page: PageData
}

export function PageDetail({ page }: PageDetailProps) {
    // Pass full metric objects, not just scores
    const metricsMap = page.metrics ? { ...page.metrics } : {}

    const pagePath = new URL(page.url).pathname
    const pageHost = new URL(page.url).hostname

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

            <div className="mb-6">
                <div className="p-4 bg-indigo-900/10 border border-indigo-500/20 rounded-lg">
                    <h4 className="text-sm font-bold text-indigo-200 mb-2">Page-Level Diagnostics</h4>
                    <p className="text-xs text-zinc-400">
                        Below is the detailed breakdown of the 22 AEO signals for this specific URL.
                        Compare these against the Site Average to find specific outliers.
                    </p>
                </div>
            </div>

            <MetricsDeepDive metrics={metricsMap} />
        </div>
    )
}
