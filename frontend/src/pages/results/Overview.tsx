import { RotateCw } from 'lucide-react'
import { useReport } from '../../context/ReportContext'
import { SiteOverview } from '../../components/results/SiteOverview'

interface OverviewProps {
    onScan?: () => void
    isScanning?: boolean
}

export function Overview({ onScan, isScanning }: OverviewProps) {
    const { data } = useReport()
    if (!data) return null

    return (
        <div className="max-w-6xl mx-auto">
            <header className="mb-8 flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-text-primary">Executive Summary</h2>
                    <p className="text-text-secondary">High-level analysis of your site's AI answerability status.</p>
                </div>
                {onScan && (
                    <button
                        onClick={onScan}
                        disabled={isScanning}
                        className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <RotateCw className={`w-4 h-4 ${isScanning ? 'animate-spin' : ''}`} />
                        {isScanning ? 'Scanning...' : 'Run New Scan'}
                    </button>
                )}
            </header>

            <SiteOverview pages={data.pages} />

            {/* Future: Add more aggregated charts here */}
        </div>
    )
}
