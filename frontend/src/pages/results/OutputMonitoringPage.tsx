import { Radio } from 'lucide-react'
import { OutputMonitoring } from './OutputMonitoring'
import { useReport } from '../../context/ReportContext'

export function OutputMonitoringPage() {
    const { data } = useReport()

    if (!data) return null

    // Derive site URL from the first page or use a fallback
    // We can also get this from the Product context if we wanted, but report context is fine
    const siteUrl = data.pages.length > 0 ? new URL(data.pages[0].url).origin : ''

    return (
        <div className="max-w-4xl mx-auto space-y-8">


            <div className="pt-4 border-t border-border">
                {siteUrl ? (
                    <OutputMonitoring targetUrl={siteUrl} />
                ) : (
                    <div className="text-text-secondary">No URL available for monitoring.</div>
                )}
            </div>
        </div>
    )
}
