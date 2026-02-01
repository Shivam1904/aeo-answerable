export interface SmartPrompt {
    id: string
    query: string
    category: string
    description: string
}

export interface HistoryItem {
    query_text: string
    last_run: string
    engine_count: number
    citation_count: number
}

// From EngineResponseCard/types
export interface Citation {
    url: string
    snippet?: string
    title?: string
}

export interface QueryResult {
    engine: string
    response: string
    citations: Citation[]
    error?: string
    latencyMs?: number
}

export interface EngineInfo {
    id: string
    name: string
    provider: string
    model: string
    enabled: boolean
}

export interface CostEstimate {
    inputTokens: number
    outputTokens: number
    cost: number
}

export const ENGINE_CONFIG: Record<string, { name: string; color: string; bgColor: string }> = {
    openai: { name: 'OpenAI (GPT-4)', color: 'text-green-500', bgColor: 'bg-green-500/10' },
    anthropic: { name: 'Claude 3.5', color: 'text-amber-500', bgColor: 'bg-amber-500/10' },
    gemini: { name: 'Gemini Pro', color: 'text-blue-500', bgColor: 'bg-blue-500/10' },
    perplexity: { name: 'Perplexity', color: 'text-teal-500', bgColor: 'bg-teal-500/10' },
    google: { name: 'Google SGE', color: 'text-blue-600', bgColor: 'bg-blue-600/10' },
    bing: { name: 'Bing Chat', color: 'text-sky-500', bgColor: 'bg-sky-500/10' }
}
