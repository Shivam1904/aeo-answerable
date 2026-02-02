import { Sparkles, MessageSquare, RefreshCw } from 'lucide-react'


interface PromptTemplatesProps {
    onSelect: (query: string) => void
    brandName: string
    suggestedQueries?: {
        query: string
        type: string
        priority: number
        description?: string
    }[]
    isLoading?: boolean
    onRefresh?: () => void
}

export function PromptTemplates({ onSelect, brandName, suggestedQueries, isLoading, onRefresh }: PromptTemplatesProps) {

    // Use suggested queries if available, otherwise fallback to static
    const activeTemplates = suggestedQueries && suggestedQueries.length > 0
        ? suggestedQueries.map((q, i) => ({
            id: `sota-${i}`,
            query: q.query,
            category: q.type.charAt(0).toUpperCase() + q.type.slice(1),
            description: q.description || 'Strategic Question'
        }))
        : []

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wider flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    {suggestedQueries?.length ? "Strategic Questions (AI Generated)" : "Quick Templates"}
                </h3>
                {onRefresh && (
                    <button
                        onClick={onRefresh}
                        className="p-1.5 rounded-lg hover:bg-surface text-text-secondary hover:text-text-primary transition-colors focus:outline-none"
                        disabled={isLoading}
                        title="Refresh Strategic Questions"
                    >
                        <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                    </button>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {isLoading ? (
                    // Loading Skeletons
                    Array.from({ length: 5 }).map((_, i) => (
                        <div key={i} className="flex flex-col gap-2 p-4 bg-surface/20 border border-border/50 rounded-xl animate-pulse">
                            <div className="w-8 h-8 bg-surface-highlight rounded-lg" />
                            <div className="space-y-2 mt-1">
                                <div className="h-4 w-24 bg-surface-highlight rounded" />
                                <div className="h-3 w-full bg-surface-highlight rounded opacity-50" />
                            </div>
                        </div>
                    ))
                ) : activeTemplates.length > 0 ? (
                    activeTemplates.map((template) => (
                        <button
                            key={template.id}
                            onClick={() => onSelect(template.query)}
                            className="group flex flex-col items-start gap-2 p-4 bg-surface/50 hover:bg-surface border border-border hover:border-primary/50 rounded-xl transition-all text-left shadow-sm"
                        >
                            <div className="p-2 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500/20 transition-colors">
                                <MessageSquare className="w-4 h-4 text-indigo-400" />
                            </div>

                            <div>
                                <div className="text-sm font-medium text-text-primary group-hover:text-primary transition-colors">
                                    {template.category} Check
                                </div>
                                <div className="text-xs text-text-secondary mt-1 line-clamp-2 group-hover:text-text-secondary/80">
                                    "{template.query}"
                                </div>
                            </div>
                        </button>
                    ))
                ) : (
                    <div className="col-span-full p-8 text-center bg-surface/20 border border-border border-dashed rounded-xl">
                        <Sparkles className="w-8 h-8 text-text-secondary mx-auto mb-3" />
                        <p className="text-text-secondary text-sm">
                            Running AI analysis to generate strategic questions for {brandName}...
                        </p>
                    </div>
                )}
            </div>
        </div>
    )
}
