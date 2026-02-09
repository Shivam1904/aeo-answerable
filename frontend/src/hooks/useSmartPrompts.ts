import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'
import { SmartPrompt, PromptResult } from '../types'

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

interface UseSmartPromptsProps {
    brandName: string
    productKeywords?: string[]
    targetUrl: string
    selectedEngines: string[]
    onResultsUpdate?: (results: PromptResult[]) => void
}

export function useSmartPrompts({
    brandName,
    productKeywords = [],
    targetUrl,
    selectedEngines,
    onResultsUpdate
}: UseSmartPromptsProps) {
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

    const runPrompt = useCallback(async (prompt: SmartPrompt) => {
        // Set loading state
        setPromptResults(prev => new Map(prev).set(prompt.id, {
            prompt,
            result: null,
            isLoading: true
        }))

        try {
            const data = await api.monitoring.query(
                prompt.query,
                targetUrl,
                selectedEngines
            )

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
    }, [targetUrl, selectedEngines])

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

    const getPromptStatus = useCallback((promptId: string) => {
        const result = promptResults.get(promptId)
        if (!result) return 'pending'
        if (result.isLoading) return 'loading'
        if (result.error) return 'error'
        if (result.result) return 'complete'
        return 'pending'
    }, [promptResults])

    const completedCount = Array.from(promptResults.values()).filter(r => r.result).length

    return {
        prompts,
        promptResults,
        runningAll,
        runPrompt,
        runAllPrompts,
        getPromptStatus,
        completedCount
    }
}
