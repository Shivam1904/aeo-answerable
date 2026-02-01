
import { useState, useMemo } from 'react'
import { Radio } from 'lucide-react'
import {
    QueryInput,
    ResultsDisplay,
    PromptTemplates,
    MultiEngineResponse,
    HistorySidebar
} from '../../components/output-monitoring'

interface OutputMonitoringProps {
    targetUrl: string
    pageContent?: string
    pageTitle?: string
}

export function OutputMonitoring({ targetUrl, pageContent: _pageContent, pageTitle: _pageTitle }: OutputMonitoringProps) {
    const [results, setResults] = useState<MultiEngineResponse | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Unified State
    const [query, setQuery] = useState('')
    const [selectedEngines, setSelectedEngines] = useState<string[]>(['openai', 'anthropic', 'gemini'])

    // Extract brand name from URL
    const brandName = useMemo(() => {
        try {
            const hostname = new URL(targetUrl).hostname
            const domain = hostname.startsWith('www.') ? hostname.slice(4) : hostname
            return domain.split('.')[0]
        } catch {
            return 'brand'
        }
    }, [targetUrl])

    const handleSubmit = async (queryText: string, engines: string[]) => {
        setIsLoading(true)
        setError(null)
        setResults(null)

        try {
            const response = await fetch('/api/output-monitoring/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: queryText,
                    target_url: targetUrl,
                    engines
                })
            })

            if (!response.ok) {
                const err = await response.json()
                throw new Error(err.detail || 'Failed to run query')
            }

            const data = await response.json()
            setResults(data)
        } catch (e: any) {
            setError(e.message)
        } finally {
            setIsLoading(false)
        }
    }

    const handleTemplateSelect = (templateQuery: string) => {
        setQuery(templateQuery)
        handleSubmit(templateQuery, selectedEngines)
    }

    const handleHistorySelect = async (historyQuery: string) => {
        setQuery(historyQuery)
        setIsLoading(true)
        setError(null)
        setResults(null)

        try {
            // Use the new history details endpoint
            const response = await fetch(`/api/output-monitoring/history/details?query=${encodeURIComponent(historyQuery)}`)

            if (!response.ok) {
                throw new Error('Failed to load history')
            }

            const data = await response.json()
            setResults(data)
        } catch (e: any) {
            setError(e.message)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-start gap-4 mb-8">
                <div className="p-3 bg-indigo-500/10 rounded-xl">
                    <Radio className="w-6 h-6 text-indigo-400" />
                </div>
                <div>
                    <h2 className="text-2xl font-bold text-text-primary">Agent Output</h2>
                    <p className="text-text-secondary mt-1">
                        See how AI models answer questions about your brand.
                    </p>
                </div>
            </div>

            <div className="flex flex-col lg:flex-row gap-8 items-start">
                {/* Main Content */}
                <div className="flex-1 w-full space-y-8">
                    {/* 1. Main Input Area (Hero) */}
                    <QueryInput
                        targetUrl={targetUrl}
                        onSubmit={handleSubmit}
                        isLoading={isLoading}
                        query={query}
                        setQuery={setQuery}
                        selectedEngines={selectedEngines}
                        setSelectedEngines={setSelectedEngines}
                    />

                    {/* Error Display */}
                    {error && (
                        <div className="p-4 bg-red-900/10 border border-red-900/20 rounded-lg animate-in fade-in slide-in-from-top-2">
                            <p className="text-sm text-red-400">{error}</p>
                        </div>
                    )}

                    {/* 2. Templates */}
                    <PromptTemplates
                        onSelect={handleTemplateSelect}
                        brandName={brandName}
                    />

                    {/* 3. Results Area */}
                    {results && (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <ResultsDisplay results={results} />
                        </div>
                    )}
                </div>

                {/* Sidebar (History) */}
                <HistorySidebar
                    onSelect={handleHistorySelect}
                    currentQuery={query}
                />
            </div>
        </div>
    )
}
