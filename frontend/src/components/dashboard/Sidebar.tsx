import { useState } from 'react'
import { LayoutDashboard, BarChart2, FileText, ChevronDown, ChevronRight, Search, File } from 'lucide-react'
import { useReport } from '../../context/ReportContext'

export type ViewState =
    | { type: 'overview' }
    | { type: 'metrics' }
    | { type: 'monitoring' }
    | { type: 'page-detail', url: string }

interface SidebarProps {
    currentView: ViewState
    onViewChange: (view: ViewState) => void
    hostname: string
    productName?: string
}

export function Sidebar({ currentView, onViewChange, hostname, productName }: SidebarProps) {
    // const navigate = useNavigate()
    const { data } = useReport()
    const [isPagesExpanded, setIsPagesExpanded] = useState(true)
    const [pageSearch, setPageSearch] = useState('')

    const filteredPages = data?.pages.filter(p =>
        p.title.toLowerCase().includes(pageSearch.toLowerCase()) ||
        p.url.toLowerCase().includes(pageSearch.toLowerCase())
    ).sort((a, b) => (b.page_score || 0) - (a.page_score || 0)) || []



    return (
        <div className="w-full h-full bg-surface/50 border-r border-border flex flex-col backdrop-blur-xl">
            {/* Header */}
            <div className="p-6 border-b border-border shrink-0">
                {productName && (
                    <h2 className="text-sm font-medium text-text-secondary truncate mb-0.5">{productName}</h2>
                )}
                <h1 className="text-lg font-bold text-text-primary truncate" title={hostname}>
                    {hostname}
                </h1>
            </div>

            {/* Nav */}
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
                {/* Overview */}
                <button
                    onClick={() => onViewChange({ type: 'overview' })}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${currentView.type === 'overview'
                        ? 'bg-surface-highlight text-text-primary shadow-[inset_0_1px_0_0_rgba(255,255,255,0.05)] border border-border'
                        : 'text-text-secondary hover:text-text-primary hover:bg-surface-highlight/50'
                        }`}
                >
                    <LayoutDashboard className={`w-4 h-4 ${currentView.type === 'overview' ? 'text-primary' : 'text-text-secondary'}`} />
                    Overview
                </button>

                {/* Metrics */}
                <button
                    onClick={() => onViewChange({ type: 'metrics' })}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${currentView.type === 'metrics'
                        ? 'bg-surface-highlight text-text-primary shadow-[inset_0_1px_0_0_rgba(255,255,255,0.05)] border border-border'
                        : 'text-text-secondary hover:text-text-primary hover:bg-surface-highlight/50'
                        }`}
                >
                    <BarChart2 className={`w-4 h-4 ${currentView.type === 'metrics' ? 'text-primary' : 'text-text-secondary'}`} />
                    Site Metrics
                </button>

                {/* Agent Output */}
                <button
                    onClick={() => onViewChange({ type: 'monitoring' })}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${currentView.type === 'monitoring'
                        ? 'bg-surface-highlight text-text-primary shadow-[inset_0_1px_0_0_rgba(255,255,255,0.05)] border border-border'
                        : 'text-text-secondary hover:text-text-primary hover:bg-surface-highlight/50'
                        }`}
                >
                    <FileText className={`w-4 h-4 ${currentView.type === 'monitoring' ? 'text-pink-400' : 'text-text-secondary'}`} />
                    Agent Output
                </button>

                {/* Page Inventory Group */}
                <div className="pt-4">
                    <button
                        onClick={() => setIsPagesExpanded(!isPagesExpanded)}
                        className="w-full flex items-center justify-between px-3 py-2 text-xs font-bold text-text-secondary uppercase tracking-widest hover:text-text-primary transition-colors"
                    >
                        <div className="flex items-center gap-2">
                            <FileText className="w-3.5 h-3.5" />
                            <span>Pages</span>
                        </div>
                        {isPagesExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                    </button>

                    {isPagesExpanded && (
                        <div className="mt-2 space-y-1 pl-2">
                            {/* Mini Search */}
                            <div className="px-2 mb-2">
                                <div className="relative">
                                    <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-text-secondary" />
                                    <input
                                        type="text"
                                        placeholder="Find page..."
                                        value={pageSearch}
                                        onChange={(e) => setPageSearch(e.target.value)}
                                        className="w-full pl-7 pr-2 py-1.5 bg-surface-highlight border border-border rounded text-xs text-text-primary focus:outline-none focus:border-border placeholder:text-text-secondary"
                                    />
                                </div>
                            </div>

                            {/* Page List */}
                            <div className="space-y-0.5">
                                {filteredPages.map((page, index) => {
                                    const isActive = currentView.type === 'page-detail' && currentView.url === page.url
                                    const path = new URL(page.url).pathname || '/'
                                    return (
                                        <button
                                            key={`${page.url}-${index}`}
                                            onClick={() => onViewChange({ type: 'page-detail', url: page.url })}
                                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-xs text-left transition-colors ${isActive
                                                ? 'bg-surface-highlight text-primary border border-border'
                                                : 'text-text-secondary hover:text-text-primary hover:bg-surface-highlight/30'
                                                }`}
                                        >
                                            <File className={`w-3 h-3 shrink-0 ${isActive ? 'text-primary' : 'text-text-secondary'}`} />
                                            <span className="truncate font-mono opacity-90">{path}</span>
                                        </button>
                                    )
                                })}
                                {filteredPages.length === 0 && (
                                    <div className="px-3 py-2 text-[10px] text-text-secondary italic">
                                        No pages found
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-border shrink-0">
                <div className="p-3 bg-surface rounded-lg border border-border">
                    <div className="text-[10px] text-text-secondary font-medium uppercase tracking-wider mb-1">Status</div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-xs text-text-primary">Analysis Complete</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
