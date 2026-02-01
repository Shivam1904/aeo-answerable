import { useState, useEffect } from 'react'
import { Lightbulb, Zap, Loader2 } from 'lucide-react'

interface SuggestedQuery {
    query: string
    topic: string
    type: string
    priority: number
}

interface SuggestedQueriesProps {
    url: string
    content: string
    title?: string
    onSelectQuery: (query: string) => void
}

export function SuggestedQueries({ url, content, title, onSelectQuery }: SuggestedQueriesProps) {
    const [queries, setQueries] = useState<SuggestedQuery[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!content || content.length < 100) return

        const fetchSuggestions = async () => {
            setLoading(true)
            setError(null)

            try {
                const response = await fetch('/api/output-monitoring/suggested-queries', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url,
                        content: content.substring(0, 10000), // Limit content size
                        title: title || ''
                    })
                })

                if (!response.ok) throw new Error('Failed to generate suggestions')

                const data = await response.json()
                setQueries(data.queries || [])
            } catch (e: any) {
                setError(e.message)
            } finally {
                setLoading(false)
            }
        }

        fetchSuggestions()
    }, [url, content, title])

    if (!content || content.length < 100) {
        return null
    }

    return (
        <div className="border border-zinc-800 rounded-xl bg-zinc-900/30 p-5">
            <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-amber-500/10 rounded-lg">
                    <Lightbulb className="w-4 h-4 text-amber-400" />
                </div>
                <div>
                    <h4 className="text-sm font-bold text-zinc-200">Suggested Test Queries</h4>
                    <p className="text-xs text-zinc-500">Auto-generated based on your content</p>
                </div>
            </div>

            {loading && (
                <div className="flex items-center gap-2 text-sm text-zinc-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Analyzing content...</span>
                </div>
            )}

            {error && (
                <p className="text-sm text-red-400">{error}</p>
            )}

            {!loading && queries.length > 0 && (
                <div className="space-y-2">
                    {queries.slice(0, 8).map((q, i) => (
                        <button
                            key={i}
                            onClick={() => onSelectQuery(q.query)}
                            className="w-full text-left p-3 rounded-lg border border-zinc-700 bg-zinc-900/50 hover:bg-zinc-800 hover:border-zinc-600 transition-colors group"
                        >
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-zinc-300 group-hover:text-zinc-100">
                                    {q.query}
                                </span>
                                <Zap className="w-3 h-3 text-zinc-600 group-hover:text-amber-400 transition-colors" />
                            </div>
                            <div className="mt-1 flex items-center gap-2">
                                <span className="text-xs text-zinc-600 bg-zinc-800 px-2 py-0.5 rounded">
                                    {q.type}
                                </span>
                                <span className="text-xs text-zinc-600">
                                    {q.topic}
                                </span>
                            </div>
                        </button>
                    ))}
                </div>
            )}

            {!loading && queries.length === 0 && !error && (
                <p className="text-sm text-zinc-500">
                    Enter content to generate suggested queries
                </p>
            )}
        </div>
    )
}
