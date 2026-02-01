import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'

// Import Dashboard Components
import { ReportProvider } from '../context/ReportContext'
import { Sidebar, ViewState } from '../components/dashboard/Sidebar'
import { Navbar } from '../components/common/Navbar'
import { Overview } from './results/Overview'
import { SiteMetrics } from './results/SiteMetrics'
import { PageDetail } from './results/PageDetail'
import { OutputMonitoring } from './results/OutputMonitoring'
import { SmartLoader } from '../components/dashboard/SmartLoader'

export default function HomePage() {
    const { productId } = useParams()
    const navigate = useNavigate()

    // Data State
    const [product, setProduct] = useState<any>(null)
    const [latestScan, setLatestScan] = useState<any>(null)
    const [status, setStatus] = useState<'loading' | 'complete' | 'error' | 'idle' | 'running'>('loading')
    const [error, setError] = useState('')

    // View State (for the dashboard sidebar)
    const [currentView, setCurrentView] = useState<ViewState>({ type: 'overview' })

    const loadDashboard = async () => {
        try {
            // Load Product
            const p = await api.products.get(productId!)
            setProduct(p)

            // Check for Latest Scan
            const scan = await api.products.getLatestScan(productId!)
            if (scan && scan.found) {
                setLatestScan(scan)
                if (scan.status === 'complete') {
                    setStatus('complete')
                } else if (scan.status === 'error') {
                    setLatestScan(null)
                    setStatus('idle')
                } else {
                    // Running/Pending
                    setStatus('loading')
                    // Start polling
                    pollScan(scan.job_id)
                }
            } else {
                console.log('No scan found, auto-starting...')
                startAutoScan(p)
            }
        } catch (err: any) {
            console.error(err)
            setError('Failed to load dashboard data')
        }
    }

    const startAutoScan = async (p: any) => {
        setStatus('loading')
        try {
            const res = await api.scan.start(p.domain, p.id, p.default_mode || 'fast')
            setLatestScan({ status: 'running', job_id: res.job_id })
            pollScan(res.job_id)
        } catch (e: any) {
            console.error(e)
            setError('Failed to start auto-scan')
            setStatus('error')
        }
    }

    const pollScan = async (jobId: string) => {
        const interval = setInterval(async () => {
            try {
                const res = await api.scan.getStatus(jobId)
                if (res.status === 'complete') {
                    setLatestScan({ found: true, result: res.result, status: 'complete', timestamp: res.timestamp })
                    setStatus('complete')
                    clearInterval(interval)
                } else if (res.status === 'error') {
                    setStatus('error')
                    clearInterval(interval)
                }
            } catch (e) {
                console.error(e)
            }
        }, 3000)
    }

    useEffect(() => {
        if (!productId) {
            navigate('/products')
            return
        }
        loadDashboard()
    }, [productId])

    // Action: Start Audit
    const handleRecrawl = async () => {
        if (!product) return
        startAutoScan(product)
    }

    if (!product && !error) {
        return <div className="min-h-screen bg-[#050505] flex items-center justify-center text-gray-500">Loading Dashboard...</div>
    }

    // --- RENDER HELPERS ---

    const renderContent = () => {
        if (currentView.type === 'overview') return (
            <Overview
                onScan={handleRecrawl}
                isScanning={status === 'loading' || status === 'running'}
            />
        )
        if (currentView.type === 'metrics') return <SiteMetrics />
        if (currentView.type === 'monitoring') {
            const siteUrl = latestScan?.result?.pages?.length > 0 ? new URL(latestScan.result.pages[0].url).origin : ''
            return siteUrl ? <OutputMonitoring targetUrl={siteUrl} /> : <div>No URL available for monitoring.</div>
        }

        if (currentView.type === 'page-detail') {
            const page = latestScan?.result?.pages?.find((p: any) => p.url === currentView.url)
            if (!page) return <div>Page not found</div>
            return <PageDetail page={page} />
        }
        return null
    }

    // 1. Loading State (Running or Auto-Start)
    // We treat 'idle' as loading here because it immediately triggers auto-scan
    if (status === 'loading' || status === 'idle') {
        return (
            <div className="min-h-screen bg-background flex flex-col">
                <Navbar product={product} />
                <div className="flex-1 flex items-center justify-center">
                    <SmartLoader />
                </div>
            </div>
        )
    }

    // 3. Error State
    if (status === 'error') {
        return (
            <div className="min-h-screen bg-background">
                <Navbar product={product} />
                <div className="min-h-screen flex flex-col items-center justify-center text-center">
                    <h2 className="text-xl font-bold text-red-500 mb-2">Audit Failed</h2>
                    <p className="text-text-secondary mb-6">{error || latestScan?.error || 'Unknown error occurred.'}</p>
                    <button
                        onClick={handleRecrawl}
                        className="px-6 py-2 bg-surface hover:bg-surface-highlight text-text-primary rounded transition-colors border border-border"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        )
    }

    // 4. Complete State (Dashboard) - Matches ResultsPage.tsx structure
    let hostname = 'Unknown'
    try {
        let u = product.domain
        if (!u.startsWith('http')) {
            u = 'https://' + u
        }
        hostname = new URL(u).hostname
    } catch (e) {
        // Fallback or leave as Unknown
        hostname = product.domain
    }

    return (
        <ReportProvider value={{
            data: latestScan.result,
            status: 'complete',
            error: '',
            hostname
        }}>
            <div className="min-h-screen bg-background text-text-primary font-sans selection:bg-primary/30 selection:text-indigo-200">
                <Navbar product={product} />

                {/* Sidebar & Content Layout */}
                <div className="pt-20 flex min-h-screen">
                    {/* Fixed Sidebar */}
                    <div className="fixed top-20 left-0 bottom-0 w-64 border-r border-border bg-background">
                        <Sidebar
                            currentView={currentView}
                            onViewChange={setCurrentView}
                            hostname={hostname}
                            productName={product.name}
                        />
                    </div>

                    {/* Main Content Area */}
                    <main className="ml-64 flex-1 transition-all bg-background">
                        <div className="p-8 max-w-7xl mx-auto animation-fade-in">
                            {renderContent()}
                        </div>
                    </main>
                </div>
            </div>
        </ReportProvider>
    )
}
