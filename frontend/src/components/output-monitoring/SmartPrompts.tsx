import { useState, useEffect } from 'react'
import { Sparkles, Play, Loader2, Check, TrendingUp, Heart, Hash, ChevronRight, AlertCircle } from 'lucide-react'
import { MultiEngineResponse, ENGINE_CONFIG } from './types'

interface SmartPrompt {
    id: string
    query: string
    category: 'brand' | 'product' | 'comparison' | 'how-to' | 'reviews' | 'pricing'
    priority: 'high' | 'medium' | 'low'
    description: string
    expectedInsight: string
}

interface PromptResult {
    prompt: SmartPrompt
    result: MultiEngineResponse | null
    isLoading: boolean
    error?: string
}

interface SmartPromptsProps {
    targetUrl: string
    brandName: string
    productKeywords?: string[]
    selectedEngines: string[]
    onResultsUpdate?: (results: PromptResult[]) => void
}

// Category styling
const CATEGORY_CONFIG: Record<string, { label: string; color: string; bgColor: string }> = {
    'brand': { label: 'Brand Awareness', color: 'text-purple-400', bgColor: 'bg-purple-500/10' },
    'product': { label: 'Product Discovery', color: 'text-blue-400', bgColor: 'bg-blue-500/10' },
    'comparison': { label: 'Competitive', color: 'text-orange-400', bgColor: 'bg-orange-500/10' },
    'how-to': { label: 'How-To', color: 'text-emerald-400', bgColor: 'bg-emerald-500/10' },
    'reviews': { label: 'Reviews & Trust', color: 'text-amber-400', bgColor: 'bg-amber-500/10' },
    'pricing': { label: 'Pricing', color: 'text-pink-400', bgColor: 'bg-pink-500/10' },
}

const PRIORITY_CONFIG: Record<string, { label: string; color: string }> = {
    'high': { label: 'High Impact', color: 'text-red-400' },
    'medium': { label: 'Medium Impact', color: 'text-yellow-400' },
    'low': { label: 'Low Impact', color: 'text-zinc-400' },
}

function generateSmartPrompts(brandName: string, productKeywords: string[] = []): SmartPrompt[] {
    const brand = brandName.charAt(0).toUpperCase() + brandName.slice(1).toLowerCase()
    const keywords = productKeywords.length > 0 ? productKeywords : ['product', 'service', 'solution']
    const mainKeyword = keywords[0]

    return [
        {
            id: 'brand-awareness',
            query: `What is ${brand}?`,
            category: 'brand',
            priority: 'high',
            description: 'Tests if AI knows your brand exists',
            expectedInsight: 'Brand visibility & recognition'
        },
        {
            id: 'brand-reputation',
            query: `Is ${brand} a good company?`,
            category: 'reviews',
            priority: 'high',
            description: 'Tests sentiment and reputation',
            expectedInsight: 'Brand sentiment score'
        },
        {
            id: 'product-discovery',
            query: `Best ${mainKeyword} tools in 2025`,
            category: 'product',
            priority: 'high',
            description: 'Tests if you appear in category searches',
            expectedInsight: 'Position in category rankings'
        },
        {
            id: 'comparison',
            query: `${brand} alternatives`,
            category: 'comparison',
            priority: 'medium',
            description: 'Tests how you compare to competitors',
            expectedInsight: 'Competitive positioning'
        },
        {
            id: 'how-to',
            query: `How to use ${brand}?`,
            category: 'how-to',
            priority: 'medium',
            description: 'Tests content discovery for your product',
            expectedInsight: 'Content citation rate'
        },
        {
            id: 'pricing',
            query: `${brand} pricing`,
            category: 'pricing',
            priority: 'low',
            description: 'Tests if pricing info is discoverable',
            expectedInsight: 'Information accuracy'
        },
    ]
}

export function SmartPrompts({ 
    targetUrl, 
    brandName, 
    productKeywords = [],
    selectedEngines,
    onResultsUpdate 
}: SmartPromptsProps) {
    const [prompts] = useState<SmartPrompt[]>(() => 
        generateSmartPrompts(brandName, productKeywords)
    )
    const [promptResults, setPromptResults] = useState<Map<string, PromptResult>>(new Map())
    const [runningAll, setRunningAll] = useState(false)

    // Notify parent of results changes
    useEffect(() => {
        if (onResultsUpdate) {
            onResultsUpdate(Array.from(promptResults.values()))
        }
    }, [promptResults, onResultsUpdate])

    const runPrompt = async (prompt: SmartPrompt) => {
        // Set loading state
        setPromptResults(prev => new Map(prev).set(prompt.id, {
            prompt,
            result: null,
            isLoading: true
        }))

        try {
            const response = await fetch('/api/output-monitoring/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: prompt.query,
                    target_url: targetUrl,
                    engines: selectedEngines
                })
            })

            if (!response.ok) {
                throw new Error('Failed to get response')
            }

            const data: MultiEngineResponse = await response.json()
            
            setPromptResults(prev => new Map(prev).set(prompt.id, {
                prompt,
                result: data,
                isLoading: false
            }))
        } catch (error: any) {
            setPromptResults(prev => new Map(prev).set(prompt.id, {
                prompt,
                result: null,
                isLoading: false,
                error: error.message
            }))
        }
    }

    const runAllPrompts = async () => {
        setRunningAll(true)
        
        // Run prompts sequentially to avoid rate limits
        for (const prompt of prompts) {
            if (!promptResults.get(prompt.id)?.result) {
                await runPrompt(prompt)
                // Small delay between requests
                await new Promise(resolve => setTimeout(resolve, 500))
            }
        }
        
        setRunningAll(false)
    }

    const getPromptStatus = (promptId: string) => {
        const result = promptResults.get(promptId)
        if (!result) return 'pending'
        if (result.isLoading) return 'loading'
        if (result.error) return 'error'
        if (result.result) return 'complete'
        return 'pending'
    }

    const completedCount = Array.from(promptResults.values()).filter(r => r.result).length

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                    <div className="p-3 bg-purple-500/10 rounded-xl">
                        <Sparkles className="w-6 h-6 text-purple-400" />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-zinc-100">AI Visibility Check</h3>
                        <p className="text-zinc-500 mt-1">
                            Test how AI engines see your brand with these targeted prompts
                        </p>
                    </div>
                </div>
                
                {/* Run All Button */}
                <button
                    onClick={runAllPrompts}
                    disabled={runningAll || completedCount === prompts.length}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
                >
                    {runningAll ? (
                        <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Running...
                        </>
                    ) : completedCount === prompts.length ? (
                        <>
                            <Check className="w-4 h-4" />
                            All Complete
                        </>
                    ) : (
                        <>
                            <Play className="w-4 h-4" />
                            Run All ({completedCount}/{prompts.length})
                        </>
                    )}
                </button>
            </div>

            {/* Progress Bar */}
            {completedCount > 0 && (
                <div className="w-full bg-zinc-800 rounded-full h-2">
                    <div 
                        className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${(completedCount / prompts.length) * 100}%` }}
                    />
                </div>
            )}

            {/* Prompts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {prompts.map((prompt) => {
                    const status = getPromptStatus(prompt.id)
                    const result = promptResults.get(prompt.id)
                    const categoryStyle = CATEGORY_CONFIG[prompt.category]
                    const priorityStyle = PRIORITY_CONFIG[prompt.priority]

                    return (
                        <div
                            key={prompt.id}
                            className={`p-5 border rounded-xl transition-all ${
                                status === 'complete' 
                                    ? 'border-emerald-500/30 bg-emerald-900/10' 
                                    : status === 'error'
                                    ? 'border-red-500/30 bg-red-900/10'
                                    : 'border-zinc-800 bg-zinc-900/30 hover:border-zinc-700'
                            }`}
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <span className={`text-xs px-2 py-1 rounded-full ${categoryStyle.bgColor} ${categoryStyle.color}`}>
                                        {categoryStyle.label}
                                    </span>
                                    <span className={`text-xs ${priorityStyle.color}`}>
                                        • {priorityStyle.label}
                                    </span>
                                </div>
                                {status === 'complete' && (
                                    <Check className="w-5 h-5 text-emerald-400" />
                                )}
                                {status === 'error' && (
                                    <AlertCircle className="w-5 h-5 text-red-400" />
                                )}
                            </div>

                            {/* Query */}
                            <p className="text-zinc-200 font-medium mb-2">"{prompt.query}"</p>
                            <p className="text-xs text-zinc-500 mb-4">{prompt.description}</p>

                            {/* Result Preview or Get Answers Button */}
                            {status === 'complete' && result?.result ? (
                                <PromptResultPreview result={result.result} prompt={prompt} />
                            ) : status === 'loading' ? (
                                <div className="flex items-center gap-2 text-zinc-400">
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span className="text-sm">Querying AI engines...</span>
                                </div>
                            ) : status === 'error' ? (
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-red-400">{result?.error || 'Failed'}</span>
                                    <button
                                        onClick={() => runPrompt(prompt)}
                                        className="text-sm text-indigo-400 hover:text-indigo-300"
                                    >
                                        Retry
                                    </button>
                                </div>
                            ) : (
                                <button
                                    onClick={() => runPrompt(prompt)}
                                    disabled={runningAll}
                                    className="flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300 transition-colors group"
                                >
                                    <Play className="w-4 h-4" />
                                    Get Answers
                                    <ChevronRight className="w-3 h-3 opacity-0 -ml-1 group-hover:opacity-100 group-hover:ml-0 transition-all" />
                                </button>
                            )}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

// Sub-component for result preview
function PromptResultPreview({ result, prompt }: { result: MultiEngineResponse; prompt: SmartPrompt }) {
    const citedEngines = result.results.filter(r => r.citations.length > 0)
    const avgSentiment = calculateSentiment(result.results.map(r => r.response).join(' '))
    
    return (
        <div className="space-y-3">
            {/* Quick Metrics */}
            <div className="grid grid-cols-3 gap-2">
                <div className="text-center p-2 bg-zinc-800/50 rounded-lg">
                    <div className="flex items-center justify-center gap-1 mb-1">
                        <TrendingUp className="w-3 h-3 text-emerald-400" />
                    </div>
                    <div className="text-lg font-bold text-zinc-100">
                        {Math.round(result.citation_rate * 100)}%
                    </div>
                    <div className="text-[10px] text-zinc-500 uppercase">Visibility</div>
                </div>
                <div className="text-center p-2 bg-zinc-800/50 rounded-lg">
                    <div className="flex items-center justify-center gap-1 mb-1">
                        <Heart className="w-3 h-3 text-pink-400" />
                    </div>
                    <div className="text-lg font-bold text-zinc-100">{avgSentiment}</div>
                    <div className="text-[10px] text-zinc-500 uppercase">Sentiment</div>
                </div>
                <div className="text-center p-2 bg-zinc-800/50 rounded-lg">
                    <div className="flex items-center justify-center gap-1 mb-1">
                        <Hash className="w-3 h-3 text-blue-400" />
                    </div>
                    <div className="text-lg font-bold text-zinc-100">
                        {citedEngines.length > 0 ? calculatePosition(result) : '-'}
                    </div>
                    <div className="text-[10px] text-zinc-500 uppercase">Position</div>
                </div>
            </div>

            {/* Engine breakdown */}
            <div className="flex flex-wrap gap-2">
                {result.results.map(r => {
                    const config = ENGINE_CONFIG[r.engine] || { name: r.engine, color: 'text-zinc-400', bgColor: 'bg-zinc-500/10' }
                    const cited = r.citations.length > 0
                    return (
                        <span
                            key={r.engine}
                            className={`text-xs px-2 py-1 rounded-full flex items-center gap-1 ${
                                cited ? 'bg-emerald-500/10 text-emerald-400' : 'bg-zinc-800 text-zinc-500'
                            }`}
                        >
                            {cited ? <Check className="w-3 h-3" /> : null}
                            {config.name}
                        </span>
                    )
                })}
            </div>
        </div>
    )
}

// Simple sentiment calculation (positive/negative word count)
function calculateSentiment(text: string): number {
    const positiveWords = ['great', 'excellent', 'good', 'best', 'amazing', 'love', 'recommend', 'helpful', 'powerful', 'innovative', 'reliable', 'trusted', 'leading', 'popular']
    const negativeWords = ['bad', 'poor', 'worst', 'terrible', 'hate', 'avoid', 'expensive', 'complicated', 'difficult', 'limited', 'outdated', 'issues', 'problems']
    
    const words = text.toLowerCase().split(/\s+/)
    let positive = 0
    let negative = 0
    
    words.forEach(word => {
        if (positiveWords.some(pw => word.includes(pw))) positive++
        if (negativeWords.some(nw => word.includes(nw))) negative++
    })
    
    const total = positive + negative
    if (total === 0) return 50
    
    return Math.round((positive / total) * 100)
}

// Calculate average citation position
function calculatePosition(result: MultiEngineResponse): string {
    const positions = result.results
        .filter(r => r.citations.length > 0)
        .flatMap(r => r.citations.map(c => c.position))
    
    if (positions.length === 0) return '-'
    
    const avg = positions.reduce((a, b) => a + b, 0) / positions.length
    return avg.toFixed(1)
}
