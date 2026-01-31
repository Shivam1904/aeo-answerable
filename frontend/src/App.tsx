import { useState } from 'react'
import {
    Search, ArrowRight, Activity, Zap, Layers,
    FileText, AlertTriangle, ChevronDown, ChevronRight,
    ShieldCheck, Terminal, Bot, Sparkles, Check, X,
    BarChart2, List, Hash, FileCode2, Clock, User, Link2
} from 'lucide-react'


// --- Types ---
interface MetricResult {
    metric: string
    score: number
    weight: number
    [key: string]: any
}

interface MetricsData {
    [key: string]: MetricResult
}

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
    page_score?: number
    metrics?: MetricsData
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

// Metric categories for display
const METRIC_CATEGORIES = {
    structure: {
        name: 'Structure & Efficiency',
        icon: Layers,
        metrics: ['dom_to_token_ratio', 'main_content_detectability', 'semantic_tree_depth', 'heading_hierarchy_validity']
    },
    content: {
        name: 'Content Quality',
        icon: FileText,
        metrics: ['heading_predictive_power', 'liftable_units_density', 'answer_first_compliance', 'anaphora_resolution']
    },
    retrieval: {
        name: 'Retrieval Readiness',
        icon: BarChart2,
        metrics: ['chunk_boundary_integrity', 'duplicate_boilerplate_rate']
    },
    schema: {
        name: 'Schema & Trust',
        icon: FileCode2,
        metrics: ['entity_schema_mapping', 'schema_coverage_by_intent', 'schema_quality_relationships', 'citation_source_density', 'freshness_signal_strength', 'author_eeat_signals']
    }
}

// Human-readable metric names
const METRIC_LABELS: { [key: string]: string } = {
    dom_to_token_ratio: 'DOM-to-Token Ratio',
    main_content_detectability: 'Main Content Detectability',
    semantic_tree_depth: 'Semantic Tree Depth',
    heading_hierarchy_validity: 'Heading Hierarchy',
    heading_predictive_power: 'Heading Predictive Power',
    liftable_units_density: 'Liftable Units Density',
    answer_first_compliance: 'Answer-First Compliance',
    anaphora_resolution: 'Anaphora Resolution',
    chunk_boundary_integrity: 'Chunk Boundary Integrity',
    duplicate_boilerplate_rate: 'Duplicate/Boilerplate Rate',
    entity_schema_mapping: 'Entity-Schema Mapping',
    schema_coverage_by_intent: 'Schema Coverage by Intent',
    schema_quality_relationships: 'Schema Quality & Relationships',
    citation_source_density: 'Citation Source Density',
    freshness_signal_strength: 'Freshness Signals',
    author_eeat_signals: 'Author & E-E-A-T'
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
                    <span>v0.2.0 • 22 AEO Metrics</span>
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

function ScoreBar({ score, size = 'md' }: { score: number, size?: 'sm' | 'md' }) {
    const pct = Math.round(score * 100)
    const color = pct >= 80 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-500'
    const height = size === 'sm' ? 'h-1' : 'h-1.5'

    return (
        <div className={`w-full bg-white/10 rounded-full overflow-hidden ${height}`}>
            <div className={`${height} ${color}`} style={{ width: `${pct}%` }}></div>
        </div>
    )
}

function MetricRow({ name, data }: { name: string, data: MetricResult }) {
    const [expanded, setExpanded] = useState(false)
    const score = Math.round(data.score * 100)
    const weight = Math.round(data.weight * 100)

    const scoreColor = score >= 80 ? 'text-green-400' : score >= 50 ? 'text-yellow-400' : 'text-red-400'

    return (
        <div className="border-b border-white/5 last:border-b-0">
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
            >
                <div className="flex items-center gap-3">
                    {expanded ? <ChevronDown className="w-3 h-3 text-gray-500" /> : <ChevronRight className="w-3 h-3 text-gray-500" />}
                    <span className="text-gray-300 text-sm">{METRIC_LABELS[name] || name}</span>
                </div>
                <div className="flex items-center gap-4">
                    <span className="text-xs text-gray-600">{weight}% weight</span>
                    <span className={`text-sm font-bold ${scoreColor}`}>{score}%</span>
                </div>
            </button>
            {expanded && (
                <div className="px-4 pb-3 pl-10">
                    <div className="text-xs text-gray-500 space-y-1 bg-white/[0.02] rounded p-3">
                        {Object.entries(data).map(([key, value]) => {
                            if (['metric', 'score', 'weight'].includes(key)) return null
                            if (typeof value === 'object') return null
                            return (
                                <div key={key} className="flex justify-between">
                                    <span className="text-gray-400">{key.replace(/_/g, ' ')}:</span>
                                    <span className="text-gray-300">{typeof value === 'number' ? value.toFixed(3) : String(value)}</span>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}
        </div>
    )
}

function MetricCategory({ category, metrics }: { category: typeof METRIC_CATEGORIES.structure, metrics?: MetricsData }) {
    const [expanded, setExpanded] = useState(true)

    const categoryMetrics = category.metrics
        .map(name => metrics?.[name] ? { name, data: metrics[name] } : null)
        .filter(Boolean) as { name: string, data: MetricResult }[]

    if (categoryMetrics.length === 0) return null

    const avgScore = categoryMetrics.reduce((acc, m) => acc + m.data.score, 0) / categoryMetrics.length
    const CategoryIcon = category.icon

    return (
        <div className="glass-panel overflow-hidden">
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full px-4 py-3 flex items-center justify-between border-b border-white/5 hover:bg-white/[0.02] transition-colors"
            >
                <div className="flex items-center gap-3">
                    <CategoryIcon className="w-4 h-4 text-indigo-400" />
                    <span className="text-white font-medium text-sm">{category.name}</span>
                </div>
                <div className="flex items-center gap-3">
                    <span className={`text-sm font-bold ${avgScore >= 0.8 ? 'text-green-400' : avgScore >= 0.5 ? 'text-yellow-400' : 'text-red-400'}`}>
                        {Math.round(avgScore * 100)}%
                    </span>
                    {expanded ? <ChevronDown className="w-4 h-4 text-gray-500" /> : <ChevronRight className="w-4 h-4 text-gray-500" />}
                </div>
            </button>
            {expanded && (
                <div>
                    {categoryMetrics.map(({ name, data }) => (
                        <MetricRow key={name} name={name} data={data} />
                    ))}
                </div>
            )}
        </div>
    )
}

function PageDetail({ page, onClose }: { page: PageData, onClose: () => void }) {
    const score = page.page_score ? Math.round(page.page_score * 100) : Math.round(((page.audits.structure.score + page.audits.clarity.score) / 2) * 100)

    return (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6">
            <div className="glass-panel max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between shrink-0">
                    <div>
                        <h2 className="text-white font-medium">{page.title || 'Untitled Page'}</h2>
                        <p className="text-xs text-gray-500 font-mono">{page.url}</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <X className="w-4 h-4 text-gray-400" />
                    </button>
                </div>

                {/* Score Header */}
                <div className="px-6 py-6 border-b border-white/5 bg-gradient-to-r from-indigo-900/10 to-transparent shrink-0">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-indigo-300 text-sm font-medium mb-1 flex items-center gap-2">
                                <Sparkles className="w-4 h-4" /> Page AEO Score
                            </p>
                            <div className="text-5xl font-black text-white tracking-tighter">{score}</div>
                        </div>
                        <div className="text-right">
                            <p className="text-gray-400 text-xs mb-2">{page.metrics ? Object.keys(page.metrics).length : 0} metrics analyzed</p>
                            <ScoreBar score={score / 100} size="md" />
                        </div>
                    </div>
                </div>

                {/* Metrics */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {page.metrics ? (
                        Object.entries(METRIC_CATEGORIES).map(([key, category]) => (
                            <MetricCategory key={key} category={category} metrics={page.metrics} />
                        ))
                    ) : (
                        <div className="text-center py-12 text-gray-500">
                            <p>No detailed metrics available for this page.</p>
                            <p className="text-xs mt-2">This page was scanned with an older version.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

function StatCard({ label, value, subtext, icon: Icon }: { label: string, value: string | number, subtext?: string, icon?: any }) {
    return (
        <div className="glass-panel p-6 flex flex-col justify-between h-full">
            <div>
                <p className="text-gray-500 text-sm font-medium mb-1 flex items-center gap-2">
                    {Icon && <Icon className="w-3 h-3" />}
                    {label}
                </p>
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
    const [selectedPage, setSelectedPage] = useState<PageData | null>(null)

    // Calculate scores from new metrics if available, fallback to legacy
    const calculatePageScore = (page: PageData) => {
        if (page.page_score) return page.page_score
        return (page.audits.structure.score + page.audits.clarity.score) / 2
    }

    const avgScore = Math.round(data.pages.reduce((acc, p) => acc + calculatePageScore(p), 0) / (data.pages.length || 1) * 100)

    // Group metrics by category for summary
    const getAvgMetricScore = (metricName: string) => {
        const scores = data.pages
            .map(p => p.metrics?.[metricName]?.score)
            .filter((s): s is number => s !== undefined)
        return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0
    }

    const structureHealth = Math.round(
        (getAvgMetricScore('heading_hierarchy_validity') ||
            data.pages.reduce((acc, p) => acc + (p.audits.structure?.score || 0), 0) / (data.pages.length || 1)) * 100
    )

    const contentClarity = Math.round(
        (getAvgMetricScore('anaphora_resolution') ||
            data.pages.reduce((acc, p) => acc + (p.audits.clarity?.score || 0), 0) / (data.pages.length || 1)) * 100
    )

    const schemaScore = Math.round(getAvgMetricScore('entity_schema_mapping') * 100) || 0

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
                        <p className="text-gray-500 text-sm">{data.pages.length} pages analyzed • 22 AEO metrics</p>
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
                                <div className="text-6xl font-black text-white mb-2 tracking-tighter">{avgScore}</div>
                                <p className="text-gray-400 text-xs">Composite readiness for AI retrieval & citation.</p>
                            </div>
                        </div>
                    </div>
                    <StatCard label="Structure Health" value={`${structureHealth}%`} subtext="Hierarchy + DOM" icon={Layers} />
                    <StatCard label="Content Clarity" value={`${contentClarity}%`} subtext="Pronouns & chunks" icon={FileText} />
                    <StatCard label="Schema Coverage" value={`${schemaScore}%`} subtext="Entity mapping" icon={FileCode2} />
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
                                const score = Math.round(calculatePageScore(p) * 100)
                                const hasMetrics = !!p.metrics && Object.keys(p.metrics).length > 0
                                return (
                                    <div
                                        key={i}
                                        onClick={() => setSelectedPage(p)}
                                        className="px-6 py-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors group cursor-pointer"
                                    >
                                        <div className="flex flex-col gap-1">
                                            <span className="text-gray-300 font-mono text-sm truncate max-w-md group-hover:text-white transition-colors">
                                                {new URL(p.url).pathname || '/'}
                                            </span>
                                            <span className="text-xs text-gray-600">{p.title || 'No Title'}</span>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            {hasMetrics && (
                                                <span className="text-xs text-indigo-400/60 bg-indigo-500/10 px-2 py-0.5 rounded">
                                                    {Object.keys(p.metrics!).length} metrics
                                                </span>
                                            )}
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
                        {/* Quick Metrics Summary */}
                        <div className="glass-panel p-6">
                            <h3 className="text-white font-medium mb-4 flex items-center gap-2">
                                <Activity className="w-4 h-4 text-indigo-400" /> Key Findings
                            </h3>
                            <div className="space-y-4">
                                {[
                                    { label: 'DOM Efficiency', score: getAvgMetricScore('dom_to_token_ratio'), icon: Hash },
                                    { label: 'Main Content', score: getAvgMetricScore('main_content_detectability'), icon: FileText },
                                    { label: 'Heading Quality', score: getAvgMetricScore('heading_predictive_power'), icon: List },
                                    { label: 'Chunk Integrity', score: getAvgMetricScore('chunk_boundary_integrity'), icon: Layers },
                                ].map((item, i) => (
                                    <div key={i} className="space-y-1">
                                        <div className="flex justify-between text-xs text-gray-400">
                                            <span className="flex items-center gap-1">
                                                <item.icon className="w-3 h-3" /> {item.label}
                                            </span>
                                            <span>{Math.round(item.score * 100)}%</span>
                                        </div>
                                        <ScoreBar score={item.score} size="sm" />
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Pro Tips */}
                        <div className="p-4 rounded-xl border border-indigo-500/20 bg-indigo-500/5">
                            <h4 className="text-indigo-300 text-sm font-medium mb-2">Pro Tip</h4>
                            <p className="text-xs text-indigo-200/60 leading-relaxed">
                                {getAvgMetricScore('entity_schema_mapping') < 0.5
                                    ? 'Add JSON-LD schema markup to improve entity-schema mapping and help AI systems verify your facts.'
                                    : getAvgMetricScore('answer_first_compliance') < 0.5
                                        ? 'Start sections with direct answers instead of introductory fluff for better extractability.'
                                        : 'Add more specific entities (names, dates, prices) to improve citation likelihood.'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Page Detail Modal */}
            {selectedPage && (
                <PageDetail page={selectedPage} onClose={() => setSelectedPage(null)} />
            )}
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
                <h2 className="text-xl font-medium text-white">Auditing with 22 AEO Metrics</h2>
                <p className="text-gray-500 text-sm">Analyzing structure, content, schema, and retrieval...</p>
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
