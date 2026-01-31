import { useState } from 'react'
import {
    Search, ArrowRight, Activity, Zap, Layers,
    FileText, AlertTriangle,
    ShieldCheck, Terminal, Bot, Sparkles
} from 'lucide-react'


// --- Types ---
interface AuditResult {
    score: number
    h1_found?: boolean
    pronoun_density?: number
    skipped_levels?: string[]
}

interface ChunkData {
    semantic: string[]
    sliding: string[]
    consistency_score: number
}

interface PageData {
    url: string
    title: string
    audits: {
        structure: AuditResult
        clarity: AuditResult
    }
    chunks: ChunkData
}

interface ReportData {
    summary: {
        scanned_count: number
        errors: number
    }
    pages: PageData[]
    retrieval_stats?: {
        recall_at_1: number
        recall_at_5: number
        query_count: number
    }
}

// --- Components ---

function Navbar() {
    return (
        <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-[#050505]/80 backdrop-blur-md">
            <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-semibold tracking-tight text-white">aeo.answerable</span>
                </div>
                <div className="flex items-center gap-8">
                    <a href="#" className="nav-link">Methodology</a>
                    <a href="#" className="nav-link">GitHub</a>
                    <a href="#" className="px-4 py-2 text-xs font-medium bg-white text-black rounded-full hover:bg-gray-200 transition-colors">
                        Documentation
                    </a>
                </div>
            </div>
        </nav>
    )
}

function Hero({ onSubmit }: { onSubmit: (url: string, mode: string) => void }) {
    const [url, setUrl] = useState('')
    const [mode, setMode] = useState<'fast' | 'rendered'>('fast')

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (url.trim()) onSubmit(url.trim(), mode)
    }

    return (
        <div className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden pt-20">
            {/* Background Effects */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-[128px] pointer-events-none" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[128px] pointer-events-none" />

            <div className="relative z-10 max-w-5xl mx-auto px-6 text-center space-y-8">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-indigo-400 mb-4 animate-fade-in">
                    <Terminal className="w-3 h-3" />
                    <span>v0.1.0 release</span>
                </div>

                <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white leading-tight">
                    Make your content <br />
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-white">
                        Answer-Ready.
                    </span>
                </h1>

                <p className="text-xl text-gray-400 max-w-2xl mx-auto font-light leading-relaxed">
                    The SEO era is fading. AEO is here. <br />
                    Audit your site's ability to be understood, retrieved, and cited by AI models like GPT-4 and Claude.
                </p>

                {/* Input Area */}
                <div className="w-full max-w-xl mx-auto space-y-4 pt-8">
                    <form onSubmit={handleSubmit} className="relative group">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl opacity-30 group-hover:opacity-60 blur transition duration-500"></div>
                        <div className="relative bg-[#0a0a0a] rounded-xl flex items-center p-1.5 border border-white/10">
                            <div className="pl-4 pr-3 text-gray-500">
                                <Search className="w-5 h-5" />
                            </div>
                            <input
                                type="url"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="https://example.com"
                                className="flex-1 bg-transparent text-white placeholder-gray-600 outline-none text-base h-12"
                                required
                            />
                            <button
                                type="submit"
                                className="px-6 h-12 bg-white text-black font-medium rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
                            >
                                Audit <ArrowRight className="w-4 h-4" />
                            </button>
                        </div>
                    </form>

                    <div className="flex justify-center gap-4 text-sm">
                        <button
                            type="button"
                            onClick={() => setMode('fast')}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all ${mode === 'fast'
                                ? 'bg-indigo-500/10 border-indigo-500/50 text-indigo-400'
                                : 'border-transparent text-gray-500 hover:text-gray-300'
                                }`}
                        >
                            <Zap className="w-3 h-3" /> Fast Mode
                        </button>
                        <button
                            type="button"
                            onClick={() => setMode('rendered')}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all ${mode === 'rendered'
                                ? 'bg-purple-500/10 border-purple-500/50 text-purple-400'
                                : 'border-transparent text-gray-500 hover:text-gray-300'
                                }`}
                        >
                            <Layers className="w-3 h-3" /> Rendered Mode
                        </button>
                    </div>
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-20 text-left">
                    {[
                        { icon: ShieldCheck, title: "Hallucination Resistant", desc: "Ensure your content provides specific, citable facts." },
                        { icon: Activity, title: "Retrieval Optimized", desc: "Structure your data for high RAG recall." },
                        { icon: Bot, title: "Agent Readable", desc: "Clear formatting for LLM context windows." }
                    ].map((f, i) => (
                        <div key={i} className="glass-panel p-6 glass-panel-hover group">
                            <f.icon className="w-8 h-8 text-gray-600 group-hover:text-indigo-400 transition-colors mb-4" />
                            <h3 className="text-white font-medium mb-2">{f.title}</h3>
                            <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

function StatCard({ label, value, subtext }: { label: string, value: string | number, subtext?: string }) {
    return (
        <div className="glass-panel p-6 flex flex-col justify-between h-full">
            <div>
                <p className="text-gray-500 text-sm font-medium mb-1">{label}</p>
                <div className="text-4xl font-bold text-white tracking-tight">{value}</div>
            </div>
            {subtext && (
                <div className="mt-4 flex items-center gap-2">
                    <div className="h-1 flex-1 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500/50 w-full animate-pulse"></div>
                    </div>
                    <span className="text-xs text-indigo-300 font-mono">{subtext}</span>
                </div>
            )}
        </div>
    )
}

function Dashboard({ data, onReset }: { data: ReportData, onReset: () => void }) {
    const avgStructure = Math.round(data.pages.reduce((acc, p) => acc + (p.audits.structure?.score || 0), 0) / (data.pages.length || 1) * 100)
    const avgClarity = Math.round(data.pages.reduce((acc, p) => acc + (p.audits.clarity?.score || 0), 0) / (data.pages.length || 1) * 100)
    const recall = Math.round((data.retrieval_stats?.recall_at_5 ?? 0) * 100)
    const globalScore = Math.round((avgStructure + avgClarity + recall) / 3)
    const hostname = data.pages[0]?.url ? new URL(data.pages[0].url).hostname : 'Target'

    return (
        <div className="min-h-screen bg-[#050505] pt-24 pb-12">
            <Navbar />

            <div className="max-w-7xl mx-auto px-6">
                {/* Header */}
                <header className="flex items-center justify-between mb-12">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <h2 className="text-2xl font-bold text-white">{hostname}</h2>
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-white/10 text-gray-400 border border-white/5 uppercase tracking-wider">
                                Report Ready
                            </span>
                        </div>
                        <p className="text-gray-500 text-sm">Scan completed via {window.location.port ? `localhost:${window.location.port}` : 'CLI'}</p>
                    </div>
                    <button onClick={onReset} className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm font-medium rounded-lg transition-colors border border-white/5">
                        New Audit
                    </button>
                </header>

                {/* Metrics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                    <div className="md:col-span-1">
                        <div className="glass-panel p-6 h-full relative overflow-hidden group">
                            <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/20 to-transparent opacity-50 group-hover:opacity-70 transition-opacity"></div>
                            <div className="relative z-10">
                                <p className="text-indigo-300 text-sm font-medium mb-2 flex items-center gap-2">
                                    <Sparkles className="w-4 h-4" /> AEO Score
                                </p>
                                <div className="text-6xl font-black text-white mb-2 tracking-tighter">{globalScore}</div>
                                <p className="text-gray-400 text-xs">Composite readiness index for LLM retrieval.</p>
                            </div>
                        </div>
                    </div>
                    <StatCard label="Structure Health" value={`${avgStructure}%`} subtext="Hierarchy check" />
                    <StatCard label="Content Clarity" value={`${avgClarity}%`} subtext="Pronoun density" />
                    <StatCard label="Retrieval Recall" value={`${recall}%`} subtext="RAG Sim @ k=5" />
                </div>

                {/* Main Content Area */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Page List */}
                    <div className="lg:col-span-2 glass-panel overflow-hidden">
                        <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
                            <h3 className="text-white font-medium flex items-center gap-2">
                                <FileText className="w-4 h-4 text-gray-500" /> Pages Analyzed
                            </h3>
                            <span className="text-xs text-gray-500 font-mono">{data.pages.length} total</span>
                        </div>
                        <div className="divide-y divide-white/5">
                            {data.pages.map((p, i) => {
                                const score = Math.round(((p.audits.structure.score + p.audits.clarity.score) / 2) * 100)
                                return (
                                    <div key={i} className="px-6 py-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors group">
                                        <div className="flex flex-col gap-1">
                                            <span className="text-gray-300 font-mono text-sm truncate max-w-md group-hover:text-white transition-colors">
                                                {new URL(p.url).pathname || '/'}
                                            </span>
                                            <span className="text-xs text-gray-600">{p.title || 'No Title'}</span>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <div className="text-right">
                                                <div className={`text-sm font-bold ${score > 80 ? 'text-green-400' : score > 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                                                    {score}%
                                                </div>
                                            </div>
                                            {score < 100 && (
                                                <AlertTriangle className="w-4 h-4 text-gray-600 group-hover:text-yellow-500 transition-colors" />
                                            )}
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </div>

                    {/* Sidebar / Insights */}
                    <div className="space-y-6">
                        <div className="glass-panel p-6">
                            <h3 className="text-white font-medium mb-4 flex items-center gap-2">
                                <Activity className="w-4 h-4 text-indigo-400" /> Retrieval Health
                            </h3>
                            <div className="space-y-4">
                                <div className="space-y-1">
                                    <div className="flex justify-between text-xs text-gray-400">
                                        <span>Semantic Density</span>
                                        <span>High</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                                        <div className="h-full bg-indigo-500/80 w-[85%]"></div>
                                    </div>
                                </div>
                                <div className="space-y-1">
                                    <div className="flex justify-between text-xs text-gray-400">
                                        <span>Token Efficiency</span>
                                        <span>Medium</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                                        <div className="h-full bg-indigo-500/40 w-[60%]"></div>
                                    </div>
                                </div>
                                <p className="text-xs text-gray-500 mt-4 leading-relaxed">
                                    Your content chunks are generally well-structured for vector retrieval, but some ambiguity remains in pronoun usage.
                                </p>
                            </div>
                        </div>

                        <div className="p-4 rounded-xl border border-indigo-500/20 bg-indigo-500/5">
                            <h4 className="text-indigo-300 text-sm font-medium mb-2">Pro Tip</h4>
                            <p className="text-xs text-indigo-200/60 leading-relaxed">
                                Add more specific entities (names, dates, prices) to improve "Faithfulness" scores in LLM citation.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

function LoadingView() {
    return (
        <div className="min-h-screen bg-[#050505] flex flex-col items-center justify-center p-6 space-y-8">
            <div className="relative">
                <div className="w-16 h-16 border-2 border-white/10 border-t-white rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                    <Bot className="w-6 h-6 text-white animate-pulse" />
                </div>
            </div>
            <div className="text-center space-y-2">
                <h2 className="text-xl font-medium text-white">Auditing Content Graph</h2>
                <p className="text-gray-500 text-sm">Simulating retrieval queries...</p>
            </div>
        </div>
    )
}

function App() {
    const [appState, setAppState] = useState<'idle' | 'scanning' | 'complete' | 'error'>('idle')
    const [reportData, setReportData] = useState<ReportData | null>(null)
    const [errorMsg, setErrorMsg] = useState('')

    const handleStart = async (url: string, mode: string) => {
        setAppState('scanning')
        try {
            const res = await fetch('/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, mode, max_pages: 50 })
            })
            if (!res.ok) throw new Error('Scan failed to start')
            const { job_id } = await res.json()

            const poll = async () => {
                const statusRes = await fetch(`/api/scan/${job_id}`)
                const status = await statusRes.json()
                if (status.status === 'complete') {
                    setReportData(status.result)
                    setAppState('complete')
                } else if (status.status === 'error') {
                    setErrorMsg(status.error)
                    setAppState('error')
                } else {
                    setTimeout(poll, 2000)
                }
            }
            poll()
        } catch (e: any) {
            setErrorMsg(e.message)
            setAppState('error')
        }
    }

    if (appState === 'scanning') return <LoadingView />
    if (appState === 'complete' && reportData) return <Dashboard data={reportData} onReset={() => setAppState('idle')} />
    if (appState === 'error') return (
        <div className="min-h-screen bg-[#050505] flex items-center justify-center">
            <div className="glass-panel p-8 text-center max-w-md">
                <div className="w-12 h-12 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <AlertTriangle className="w-6 h-6 text-red-500" />
                </div>
                <h2 className="text-xl font-bold text-white mb-2">Scan Failed</h2>
                <p className="text-gray-400 mb-6 text-sm">{errorMsg}</p>
                <button onClick={() => setAppState('idle')} className="text-indigo-400 hover:text-indigo-300 text-sm">Return Home</button>
            </div>
        </div>
    )

    return (
        <>
            <Navbar />
            <Hero onSubmit={handleStart} />
        </>
    )
}

export default App
