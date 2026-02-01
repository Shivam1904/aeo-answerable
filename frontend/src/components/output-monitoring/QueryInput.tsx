
import { useState, useEffect } from 'react'
import { Search, Zap, DollarSign, Type, Check } from 'lucide-react'
import { EngineInfo, CostEstimate, ENGINE_CONFIG } from './types'

interface QueryInputProps {
    targetUrl: string
    onSubmit: (query: string, engines: string[]) => Promise<void>
    isLoading: boolean
    // Exposed so parent can set query from templates
    query: string
    setQuery: (q: string) => void
    selectedEngines: string[]
    setSelectedEngines: (engines: string[]) => void
}

export function QueryInput({
    targetUrl,
    onSubmit,
    isLoading,
    query,
    setQuery,
    selectedEngines,
    setSelectedEngines
}: QueryInputProps) {
    const [availableEngines, setAvailableEngines] = useState<EngineInfo[]>([])
    const [loadingEngines, setLoadingEngines] = useState(true)

    // Fetch available engines on mount
    useEffect(() => {
        fetch('/api/output-monitoring/available-engines')
            .then(res => res.json())
            .then(data => {
                setAvailableEngines(data.engines || [])
                // Pre-select all available engines by default
                if (data.engines && data.engines.length > 0 && selectedEngines.length === 0) {
                    setSelectedEngines(data.engines.map((e: any) => e.id))
                }
            })
            .catch(console.error)
            .finally(() => setLoadingEngines(false))
    }, [])

    const handleEngineToggle = (engineId: string) => {
        setSelectedEngines(
            selectedEngines.includes(engineId)
                ? selectedEngines.filter(e => e !== engineId)
                : [...selectedEngines, engineId]
        )
    }

    const handleSubmit = async (e?: React.FormEvent) => {
        if (e) e.preventDefault()
        if (!query.trim() || selectedEngines.length === 0) return
        await onSubmit(query, selectedEngines)
    }

    const wordCount = query.trim().split(/\s+/).filter(Boolean).length

    return (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-sm">
            {/* Header / Title Area */}
            <div className="px-6 py-4 border-b border-zinc-800 bg-zinc-900/50 flex items-center justify-between">
                <div>
                    <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                        <Search className="w-5 h-5 text-indigo-400" />
                        Test Your Content against AI
                    </h2>
                    <p className="text-xs text-zinc-500 mt-1">
                        Analyzing against: <span className="text-indigo-400 font-mono">{targetUrl}</span>
                    </p>
                </div>
            </div>

            <div className="p-6 space-y-4">
                {/* Main Textarea */}
                <div className="relative">
                    <textarea
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && e.metaKey) {
                                handleSubmit()
                            }
                        }}
                        placeholder="Type your question here (e.g., 'What is [Your Brand] doing in AI space?')..."
                        className="w-full min-h-[140px] p-4 bg-zinc-950/50 border border-zinc-700 rounded-xl text-zinc-100 text-lg placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-y"
                    />

                    {/* Bottom Right Indicators */}
                    <div className="absolute bottom-4 right-4 flex items-center gap-4 text-xs text-zinc-500 pointer-events-none">
                        <div className="flex items-center gap-1.5 p-1.5 bg-zinc-900/80 rounded backdrop-blur-sm border border-zinc-800">
                            <Type className="w-3 h-3" />
                            <span>{wordCount} words</span>
                        </div>
                    </div>
                </div>

                {/* Footer Controls */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mt-2">

                    {/* Left: Model Selector Chips */}
                    <div className="flex flex-wrap gap-2">
                        {loadingEngines ? (
                            <span className="text-xs text-zinc-600">Loading models...</span>
                        ) : (
                            availableEngines.map((engine) => {
                                const config = ENGINE_CONFIG[engine.id] || { name: engine.name, color: 'text-zinc-400', bgColor: 'bg-zinc-800' }
                                const isSelected = selectedEngines.includes(engine.id)

                                return (
                                    <button
                                        key={engine.id}
                                        type="button"
                                        onClick={() => handleEngineToggle(engine.id)}
                                        className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all flex items-center gap-2 ${isSelected
                                            ? `${config.bgColor} border-transparent ${config.color} ring-1 ring-inset ring-current`
                                            : 'bg-zinc-900 border-zinc-700 text-zinc-500 hover:border-zinc-600'
                                            }`}
                                    >
                                        {isSelected && <Check className="w-3 h-3" />}
                                        {config.name}
                                    </button>
                                )
                            })
                        )}
                    </div>

                    {/* Right: Submit */}
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => handleSubmit()}
                            disabled={isLoading || !query.trim() || selectedEngines.length === 0}
                            className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-all shadow-lg shadow-indigo-500/10"
                        >
                            {isLoading ? (
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <Zap className="w-4 h-4 fill-current" />
                            )}
                            {isLoading ? 'Running...' : 'Run Analysis'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
