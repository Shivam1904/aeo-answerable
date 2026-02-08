
export interface SmartPrompt {
    id: string
    query: string
    category: 'brand' | 'product' | 'comparison' | 'how-to' | 'reviews' | 'pricing'
    priority: 'high' | 'medium' | 'low'
    description: string
    expectedInsight: string
}

export interface PromptResult {
    prompt: SmartPrompt
    result: MultiEngineResponse | null
    isLoading: boolean
    error?: string
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
    position?: number
}

export interface SOTAInsights {
    share_of_voice: Record<string, number>
    sentiment_profile: {
        brand_sentiment: number
        industry_benchmark: number
        label: string
    }
    key_takeaways: string[]
}

export interface MultiEngineResponse {
    query: string
    results: QueryResult[]
    total_cost_usd: number
    citation_rate: number
    sota_insights?: SOTAInsights
}


export interface AnalysisData {
    share_of_voice?: number
    sentiment_score?: number
    recommendation?: string
    rank?: number
    key_attributes?: { name: string; sentiment: string }[]
    hallucinations?: string[]
}

export interface QueryResult {
    engine: string
    response: string
    citations: Citation[]
    error?: string | null
    latency_ms?: number
    cost_usd?: number
    tokens_used?: number
    analysis?: AnalysisData
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

export interface Product {
    id: number
    name: string
    domain: string
    default_mode?: 'fast' | 'rendered'
    created_at: string
    business_bio?: string
    is_bio_ai_generated?: boolean
    target_region?: string
    target_audience_age?: string
    gender_preference?: string
    stats?: {
        avg_citation_rate: number
        trend: number[]
        total_queries: number
        last_scan_status: string
    }
}
