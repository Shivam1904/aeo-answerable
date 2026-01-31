import { useState } from 'react'
import { LayoutDashboard, BarChart2, FileText, ArrowLeft, ChevronDown, ChevronRight, Search, File } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useReport } from '../../context/ReportContext'

export type ViewState =
    | { type: 'overview' }
    | { type: 'metrics' }
    | { type: 'page-detail', url: string }

interface SidebarProps {
    currentView: ViewState
    onViewChange: (view: ViewState) => void
    hostname: string
}

export function Sidebar({ currentView, onViewChange, hostname }: SidebarProps) {
    const navigate = useNavigate()
    const { data } = useReport()
    const [isPagesExpanded, setIsPagesExpanded] = useState(true)
    const [pageSearch, setPageSearch] = useState('')

    const filteredPages = data?.pages.filter(p =>
        p.title.toLowerCase().includes(pageSearch.toLowerCase()) ||
        p.url.toLowerCase().includes(pageSearch.toLowerCase())
    ).sort((a, b) => (b.page_score || 0) - (a.page_score || 0)) || []

    return (
        <div className="w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col h-screen fixed left-0 top-0 z-50">
            {/* Header */}
            <div className="p-6 border-b border-zinc-800 shrink-0">
                <div className="flex items-center gap-3 mb-4">
                    <button
                        onClick={() => navigate('/')}
                        className="p-1.5 -ml-2 rounded-md hover:bg-zinc-900 text-zinc-500 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4 text-zinc-400" />
                    </button>
                    <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Report</span>
                </div>
                <h1 className="text-lg font-bold text-zinc-100 truncate" title={hostname}>
                    {hostname}
                </h1>
            </div>

            {/* Nav */}
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
                {/* Overview */}
                <button
                    onClick={() => onViewChange({ type: 'overview' })}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${currentView.type === 'overview'
                            ? 'bg-zinc-900 text-zinc-100 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.05)] border border-zinc-800'
                            : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50'
                        }`}
                >
                    <LayoutDashboard className={`w-4 h-4 ${currentView.type === 'overview' ? 'text-indigo-400' : 'text-zinc-600'}`} />
                    Overview
                </button>

                {/* Metrics */}
                <button
                    onClick={() => onViewChange({ type: 'metrics' })}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${currentView.type === 'metrics'
                            ? 'bg-zinc-900 text-zinc-100 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.05)] border border-zinc-800'
                            : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50'
                        }`}
                >
                    <BarChart2 className={`w-4 h-4 ${currentView.type === 'metrics' ? 'text-indigo-400' : 'text-zinc-600'}`} />
                    Site Metrics
                </button>

                {/* Page Inventory Group */}
                <div className="pt-4">
                    <button
                        onClick={() => setIsPagesExpanded(!isPagesExpanded)}
                        className="w-full flex items-center justify-between px-3 py-2 text-xs font-bold text-zinc-500 uppercase tracking-widest hover:text-zinc-300 transition-colors"
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
                                    <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-zinc-600" />
                                    <input
                                        type="text"
                                        placeholder="Find page..."
                                        value={pageSearch}
                                        onChange={(e) => setPageSearch(e.target.value)}
                                        className="w-full pl-7 pr-2 py-1.5 bg-zinc-900/50 border border-zinc-800 rounded text-xs text-zinc-300 focus:outline-none focus:border-zinc-700 placeholder:text-zinc-700"
                                    />
                                </div>
                            </div>

                            {/* Page List */}
                            <div className="space-y-0.5">
                                {filteredPages.map(page => {
                                    const isActive = currentView.type === 'page-detail' && currentView.url === page.url
                                    const path = new URL(page.url).pathname || '/'
                                    return (
                                        <button
                                            key={page.url}
                                            onClick={() => onViewChange({ type: 'page-detail', url: page.url })}
                                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-xs text-left transition-colors ${isActive
                                                    ? 'bg-zinc-900 text-indigo-300 border border-zinc-800'
                                                    : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/30'
                                                }`}
                                        >
                                            <File className={`w-3 h-3 shrink-0 ${isActive ? 'text-indigo-500' : 'text-zinc-700'}`} />
                                            <span className="truncate font-mono opacity-90">{path}</span>
                                        </button>
                                    )
                                })}
                                {filteredPages.length === 0 && (
                                    <div className="px-3 py-2 text-[10px] text-zinc-600 italic">
                                        No pages found
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-zinc-800 shrink-0">
                <div className="p-3 bg-zinc-900 rounded-lg border border-zinc-800">
                    <div className="text-[10px] text-zinc-500 font-medium uppercase tracking-wider mb-1">Status</div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-xs text-zinc-300">Analysis Complete</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
