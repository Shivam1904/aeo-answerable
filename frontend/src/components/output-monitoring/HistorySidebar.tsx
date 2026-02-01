
import { useEffect, useState } from 'react'
import { Clock, ChevronRight, MessageSquare, Search } from 'lucide-react'

interface HistoryItem {
    query_text: string
    last_run: string
    engine_count: number
    citation_count: number
}

interface HistorySidebarProps {
    onSelect: (query: string) => void
    currentQuery: string
}

export function HistorySidebar({ onSelect, currentQuery }: HistorySidebarProps) {
    const [history, setHistory] = useState<HistoryItem[]>([])
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        fetch('/api/output-monitoring/history')
            .then(res => res.json())
            .then(data => setHistory(data))
            .catch(console.error)
            .finally(() => setIsLoading(false))
    }, [])

    // Time ago formatter
    const timeAgo = (dateStr: string) => {
        const diff = Date.now() - new Date(dateStr).getTime()
        const mins = Math.floor(diff / 60000)
        if (mins < 60) return `${mins}m ago`
        const hours = Math.floor(mins / 60)
        if (hours < 24) return `${hours}h ago`
        return `${Math.floor(hours / 24)}d ago`
    }

    if (history.length === 0 && !isLoading) return null

    return (
        <div className="w-full lg:w-64 shrink-0 space-y-4">
            <div className="px-4 py-3 bg-zinc-900/50 border border-zinc-800 rounded-lg flex items-center gap-2 text-sm font-medium text-zinc-400">
                <Clock className="w-4 h-4" />
                Recent Analyses
            </div>

            <div className="space-y-2">
                {isLoading ? (
                    <div className="p-4 text-xs text-zinc-500 text-center animate-pulse">Loading history...</div>
                ) : (
                    history.map((item, idx) => (
                        <button
                            key={idx}
                            onClick={() => onSelect(item.query_text)}
                            className={`w-full text-left p-3 rounded-lg border transition-all group ${currentQuery === item.query_text
                                    ? 'bg-indigo-500/10 border-indigo-500/50'
                                    : 'bg-zinc-900/20 border-zinc-800 hover:bg-zinc-800 hover:border-zinc-700'
                                }`}
                        >
                            <div className="flex items-start justify-between">
                                <span className={`text-sm font-medium line-clamp-2 ${currentQuery === item.query_text ? 'text-indigo-200' : 'text-zinc-300 group-hover:text-zinc-100'
                                    }`}>
                                    {item.query_text}
                                </span>
                            </div>

                            <div className="mt-2 flex items-center justify-between text-xs">
                                <span className="text-zinc-500">{timeAgo(item.last_run)}</span>
                                <div className="flex items-center gap-2">
                                    {item.citation_count > 0 && (
                                        <span className="flex items-center gap-1 text-emerald-400/80">
                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                            Cited
                                        </span>
                                    )}
                                </div>
                            </div>
                        </button>
                    ))
                )}
            </div>
        </div>
    )
}
