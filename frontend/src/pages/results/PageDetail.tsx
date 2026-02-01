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
            <div className="flex items-start justify-between mb-8 pb-8 border-b border-border">
                <div>
                    <h2 className="text-2xl font-bold text-text-primary mb-1">{page.title || 'Untitled Page'}</h2>
                    <div className="flex items-center gap-2 font-mono text-text-secondary text-sm">
                        <span className="text-text-secondary">{pageHost}</span>
                        <span className="text-text-secondary/50">/</span>
                        <span className="text-primary">{pagePath}</span>
                    </div>
                </div>
                {page.page_score !== undefined && (
                    <div className="text-right">
                        <div className="text-4xl font-black text-text-primary">{Math.round(page.page_score * 100)}</div>
                        <div className="text-xs text-text-secondary uppercase tracking-widest font-bold">Page Score</div>
                    </div>
                )}
            </div>

            <div className="mb-6">
                <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
                    <h4 className="text-sm font-bold text-primary mb-2">Page-Level Diagnostics</h4>
                    <p className="text-xs text-text-secondary">
                        Below is the detailed breakdown of the core AEO signals for this specific URL.
                        Compare these against the Site Average to find specific outliers.
                    </p>
                </div>
            </div>

            <MetricsDeepDive metrics={metricsMap} />
        </div>
    )
}
