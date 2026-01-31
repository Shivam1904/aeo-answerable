import { useReport } from '../../context/ReportContext'
import { SiteOverview } from '../../components/results/SiteOverview' // Reusing the component we just built

export function Overview() {
    const { data } = useReport()
    if (!data) return null

    // Calculate aggregates logic is inside SiteOverview now, but SiteOverview expects "pages"
    // Wait, SiteOverview handles the aggregation itself.

    return (
        <div className="max-w-6xl mx-auto">
            <header className="mb-8">
                <h2 className="text-2xl font-bold text-zinc-100">Executive Summary</h2>
                <p className="text-zinc-400">High-level analysis of your site's AI answerability status.</p>
            </header>

            <SiteOverview pages={data.pages} />

            {/* Future: Add more aggregated charts here */}
        </div>
    )
}
