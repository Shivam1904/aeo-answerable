import { useEffect, useState } from 'react'
import { Clock, Trash2, ChevronRight, ChevronDown, History } from 'lucide-react'
import { HistoryItem, MultiEngineResponse } from '../../types'
import { api } from '../../api'
import { ResultsDisplay } from './ResultsDisplay'

interface HistorySidebarProps {
    onSelect?: (query: string) => void // Optional now as we expand inline
    currentQuery?: string
    productId?: string | number
}

export function HistorySidebar({ onSelect: _onSelect, currentQuery: _currentQuery, productId }: HistorySidebarProps) {
    const [history, setHistory] = useState<HistoryItem[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [expandedItem, setExpandedItem] = useState<string | null>(null)
    const [details, setDetails] = useState<Record<string, MultiEngineResponse>>({})
    const [loadingDetails, setLoadingDetails] = useState<Record<string, boolean>>({})

    useEffect(() => {
        loadHistory()
    }, [productId])

    const loadHistory = () => {
        api.monitoring.getHistory(productId)
            .then(data => setHistory(data))
            .catch(console.error)
            .finally(() => setIsLoading(false))
    }

    const toggleExpand = async (queryText: string) => {
        if (expandedItem === queryText) {
            setExpandedItem(null)
            return
        }

        setExpandedItem(queryText)

        // Load details if not present
        if (!details[queryText]) {
            setLoadingDetails(prev => ({ ...prev, [queryText]: true }))
            try {
                const data = await api.monitoring.getHistoryDetails(queryText)
                setDetails(prev => ({ ...prev, [queryText]: data }))
            } catch (error) {
                console.error("Failed to load details", error)
            } finally {
                setLoadingDetails(prev => ({ ...prev, [queryText]: false }))
            }
        }
    }

    const handleDelete = async (queryText: string, e: React.MouseEvent) => {
        e.stopPropagation()
        if (!window.confirm('Delete this analysis?')) return

        const originalHistory = [...history]
        setHistory(prev => prev.filter(item => item.query_text !== queryText))

        try {
            await api.monitoring.deleteHistory(queryText)
        } catch (error) {
            console.error('Failed to delete:', error)
            setHistory(originalHistory)
            alert('Failed to delete history item.')
        }
    }

    const timeAgo = (dateStr: string) => {
        const diff = Date.now() - new Date(dateStr).getTime()
        const mins = Math.floor(diff / 60000)
        if (mins < 60) return `${mins}m ago`
        const hours = Math.floor(mins / 60)
        if (hours < 24) return `${hours}h ago`
        return `${Math.floor(hours / 24)}d ago`
    }

    if (history.length === 0 && !isLoading) {
        return (
            <div className="text-center py-12 text-text-secondary">
                <History className="w-12 h-12 mx-auto mb-4 opacity-20" />
                <p>No history yet.</p>
            </div>
        )
    }

    return (
        <div className="w-full space-y-4">
            <div className="flex items-center justify-between px-2">
                <h3 className="text-lg font-bold text-text-primary">Analysis History</h3>
                <button onClick={loadHistory} className="text-xs text-indigo-400 hover:text-indigo-300">
                    Refresh
                </button>
            </div>

            <div className="space-y-3">
                {isLoading ? (
                    Array.from({ length: 3 }).map((_, i) => (
                        <div key={i} className="h-24 rounded-xl bg-surface/30 animate-pulse border border-border/50" />
                    ))
                ) : (
                    history.map((item, idx) => {
                        const isExpanded = expandedItem === item.query_text
                        const itemDetails = details[item.query_text]
                        const isLoadingItem = loadingDetails[item.query_text]

                        return (
                            <div
                                key={`${item.query_text}-${idx}`}
                                className={`rounded-xl border transition-all overflow-hidden ${isExpanded
                                    ? 'bg-surface border-indigo-500/30 ring-1 ring-indigo-500/30 shadow-lg'
                                    : 'bg-surface/20 border-border hover:bg-surface/40'
                                    }`}
                            >
                                <button
                                    onClick={() => toggleExpand(item.query_text)}
                                    className="w-full text-left p-4 flex items-start gap-4"
                                >
                                    <div className={`mt-1 p-1.5 rounded-lg transition-colors ${isExpanded ? 'bg-indigo-500/20 text-indigo-400' : 'bg-surface-highlight text-text-secondary'}`}>
                                        {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-start justify-between gap-4">
                                            <h4 className={`font-medium text-sm leading-relaxed ${isExpanded ? 'text-primary' : 'text-text-primary'}`}>
                                                {item.query_text}
                                            </h4>
                                            <div
                                                onClick={(e) => handleDelete(item.query_text, e)}
                                                className="shrink-0 p-1.5 text-text-secondary hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
                                                title="Delete Analysis"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </div>
                                        </div>

                                        <div className="mt-2 flex items-center gap-4 text-xs text-text-secondary">
                                            <span className="flex items-center gap-1.5">
                                                <Clock className="w-3.5 h-3.5" />
                                                {timeAgo(item.last_run)}
                                            </span>
                                            {item.citation_count > 0 && (
                                                <span className="text-emerald-400 font-medium">
                                                    {item.citation_count} Citations
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </button>

                                {isExpanded && (
                                    <div className="border-t border-border bg-surface/30 p-4 md:p-6 animate-in slide-in-from-top-2 fade-in duration-300">
                                        {isLoadingItem ? (
                                            <div className="py-8 text-center space-y-3">
                                                <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
                                                <p className="text-sm text-text-secondary">Loading details...</p>
                                            </div>
                                        ) : itemDetails ? (
                                            <ResultsDisplay results={itemDetails} />
                                        ) : (
                                            <div className="py-4 text-center text-red-400 text-sm">
                                                Failed to load details.
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )
                    })
                )}
            </div>
        </div>
    )
}
