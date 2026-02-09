import { MultiEngineResponse as GlobalMultiEngineResponse, QueryResult as GlobalQueryResult, Citation as GlobalCitation } from '../../types'

export type Citation = GlobalCitation
export type QueryResult = GlobalQueryResult
export type MultiEngineResponse = GlobalMultiEngineResponse

export interface SOTAInsights {
    share_of_voice: Record<string, number>
    sentiment_profile: {
        brand_sentiment: number
        industry_benchmark: number
        label: string
    }
    key_takeaways: string[]
}

export interface EngineInfo {
    id: string
    name: string
    provider: string
}

export interface CostEstimate {
    estimated_cost_usd: number
    breakdown: Record<string, number>
}

// Engine display configuration
export const ENGINE_CONFIG: Record<string, { name: string; color: string; bgColor: string }> = {
    openai: {
        name: 'GPT-4o Mini',
        color: 'text-emerald-400',
        bgColor: 'bg-emerald-500/10'
    },
    anthropic: {
        name: 'Claude 3.5 Haiku',
        color: 'text-orange-400',
        bgColor: 'bg-orange-500/10'
    },
    gemini: {
        name: 'Gemini 2.0 Flash-Lite',
        color: 'text-blue-400',
        bgColor: 'bg-blue-500/10'
    },
    searchgpt: {
        name: 'SearchGPT',
        color: 'text-cyan-400',
        bgColor: 'bg-cyan-500/10'
    },
    bing_copilot: {
        name: 'Bing Copilot',
        color: 'text-sky-400',
        bgColor: 'bg-sky-500/10'
    }
}
