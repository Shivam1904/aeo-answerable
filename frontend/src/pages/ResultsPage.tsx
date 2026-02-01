import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Bot, AlertTriangle } from 'lucide-react'
import { ReportProvider, type ReportData } from '../context/ReportContext'
import { Sidebar, ViewState } from '../components/dashboard/Sidebar' // Import ViewState
import { Overview } from './results/Overview'
import { SiteMetrics } from './results/SiteMetrics'
import { PageDetail } from './results/PageDetail'


export default function ResultsPage() {
    const { jobId } = useParams()
    const navigate = useNavigate()
    const [status, setStatus] = useState<'loading' | 'complete' | 'error'>('loading')
    const [data, setData] = useState<ReportData | null>(null)
    const [error, setError] = useState('')
    const [currentView, setCurrentView] = useState<ViewState>({ type: 'overview' })

    useEffect(() => {
        if (!jobId) return

        const poll = async () => {
            try {
                const res = await fetch(`/api/scan/${jobId}`)
                const result = await res.json()

                if (result.status === 'complete') {
                    setData(result.result)
                    setStatus('complete')
                } else if (result.status === 'error') {
                    setError(result.error)
                    setStatus('error')
                } else {
                    setTimeout(poll, 2000)
                }
            } catch (e: any) {
                setError(e.message)
                setStatus('error')
            }
        }

        poll()
    }, [jobId])

    const hostname = data?.pages[0]?.url ? new URL(data.pages[0].url).hostname : 'Unknown'

    if (status === 'loading') {
        return (
            <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6">
                <div className="relative mb-8">
                    <div className="w-16 h-16 border-2 border-border border-t-primary rounded-full animate-spin" />
                    <div className="absolute inset-0 flex items-center justify-center">
                        <Bot className="w-6 h-6 text-text-primary animate-pulse" />
                    </div>
                </div>
                <h2 className="text-xl font-bold text-text-primary mb-2">Generating Report</h2>
                <p className="text-text-secondary">Analyzing core AEO signals...</p>
            </div>
        )
    }

    if (status === 'error') {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center p-6">
                <div className="text-center max-w-md">
                    <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                        <AlertTriangle className="w-8 h-8 text-red-500" />
                    </div>
                    <h2 className="text-xl font-bold text-text-primary mb-2">Scan Failed</h2>
                    <p className="text-text-secondary mb-8">{error}</p>
                    <button
                        onClick={() => navigate('/')}
                        className="px-6 py-2 bg-surface text-text-primary font-medium rounded hover:bg-surface-highlight border border-border transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        )
    }

    // Helper to render page details
    const renderContent = () => {
        if (currentView.type === 'overview') return <Overview />
        if (currentView.type === 'metrics') return <SiteMetrics />

        if (currentView.type === 'page-detail') {
            const page = data?.pages.find(p => p.url === currentView.url)
            if (!page) return <div>Page not found</div>
            return <PageDetail page={page} />
        }
    }

    return (
        <ReportProvider value={{ data, status, error, hostname }}>
            <div className="min-h-screen bg-background text-text-primary font-sans selection:bg-primary/30 selection:text-indigo-200">
                <Sidebar
                    currentView={currentView}
                    onViewChange={setCurrentView}
                    hostname={hostname}
                />

                {/* Main Content Area */}
                <main className="pl-64 min-h-screen transition-all">
                    <div className="p-8 max-w-7xl mx-auto animation-fade-in">
                        {renderContent()}
                    </div>
                </main>
            </div>
        </ReportProvider>
    )
}
