
import { useEffect, useState } from 'react'
import { Clock } from 'lucide-react'
import { HistoryItem } from '../../types'


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
            <div className="px-4 py-3 bg-surface/50 border border-border rounded-lg flex items-center gap-2 text-sm font-medium text-text-secondary">
                <Clock className="w-4 h-4" />
                Recent Analyses
            </div>

            <div className="space-y-2">
                {isLoading ? (
                    <div className="p-4 text-xs text-text-secondary text-center animate-pulse">Loading history...</div>
                ) : (
                    history.map((item, idx) => (
                        <button
                            key={idx}
                            onClick={() => onSelect(item.query_text)}
                            className={`w-full text-left p-3 rounded-lg border transition-all group ${currentQuery === item.query_text
                                ? 'bg-indigo-500/10 border-indigo-500/50'
                                : 'bg-surface/20 border-border hover:bg-surface-highlight hover:border-border'
                                }`}
                        >
                            <div className="flex items-start justify-between">
                                <span className={`text-sm font-medium line-clamp-2 ${currentQuery === item.query_text ? 'text-primary' : 'text-text-primary group-hover:text-primary'
                                    }`}>
                                    {item.query_text}
                                </span>
                            </div>

                            <div className="mt-2 flex items-center justify-between text-xs">
                                <span className="text-text-secondary">{timeAgo(item.last_run)}</span>
                                <div className="flex items-center gap-2">
                                    {item.citation_count > 0 && (
                                        <span className="flex items-center gap-1 text-emerald-500/80">
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
