import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Search, ArrowRight, Zap, Layers,
    ShieldCheck, Activity, Terminal, Bot
} from 'lucide-react'

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
                    <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Methodology</a>
                    <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">GitHub</a>
                    <a href="#" className="px-4 py-2 text-xs font-medium bg-white text-black rounded-full hover:bg-gray-200 transition-colors">
                        Documentation
                    </a>
                </div>
            </div>
        </nav>
    )
}

export default function HomePage() {
    const [url, setUrl] = useState('')
    const [mode, setMode] = useState<'fast' | 'rendered'>('fast')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')
    const navigate = useNavigate()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!url.trim()) return

        setIsLoading(true)
        setError('')

        let targetUrl = url.trim()
        if (!/^https?:\/\//i.test(targetUrl)) {
            targetUrl = 'https://' + targetUrl
        }

        try {
            const res = await fetch('/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: targetUrl, mode, max_pages: 50 })
            })
            if (!res.ok) throw new Error('Scan failed to start')
            const { job_id } = await res.json()

            // Navigate to results page with job ID
            navigate(`/results/${job_id}`)
        } catch (e: any) {
            setError(e.message)
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-[#050505]">
            <Navbar />

            <div className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden pt-20">
                {/* Background Effects */}
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-[128px] pointer-events-none" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[128px] pointer-events-none" />

                <div className="relative z-10 max-w-5xl mx-auto px-6 text-center space-y-8">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-indigo-400 mb-4">
                        <Terminal className="w-3 h-3" />
                        <span>v0.2.0 • Core AEO Metrics</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white leading-tight">
                        Make your content <br />
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-white">
                            Answer-Ready.
                        </span>
                    </h1>

                    <p className="text-xl text-gray-400 max-w-2xl mx-auto font-light leading-relaxed">
                        The SEO era is fading. AEO is here. <br />
                        Audit your site's ability to be understood, retrieved, and cited by AI.
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
                                    type="text"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="example.com"
                                    className="flex-1 bg-transparent text-white placeholder-gray-600 outline-none text-base h-12"
                                    required
                                    disabled={isLoading}
                                />
                                <button
                                    type="submit"
                                    disabled={isLoading}
                                    className="px-6 h-12 bg-white text-black font-medium rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2 disabled:opacity-50"
                                >
                                    {isLoading ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                                            Starting...
                                        </>
                                    ) : (
                                        <>Audit <ArrowRight className="w-4 h-4" /></>
                                    )}
                                </button>
                            </div>
                        </form>

                        {error && (
                            <p className="text-red-400 text-sm">{error}</p>
                        )}

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
                            <div key={i} className="p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors group">
                                <f.icon className="w-8 h-8 text-gray-600 group-hover:text-indigo-400 transition-colors mb-4" />
                                <h3 className="text-white font-medium mb-2">{f.title}</h3>
                                <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}
