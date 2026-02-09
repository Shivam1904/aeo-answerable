import { useState, useMemo, useEffect } from 'react'
import { Radio } from 'lucide-react'
import {
    QueryInput,
    ResultsDisplay,
    PromptTemplates,
    MultiEngineResponse,
    HistorySidebar,
    CompetitorAnalysis,
    CompetitorSelector
} from '../../components/output-monitoring'
import { CompetitiveResultsDisplay } from '../../components/output-monitoring/CompetitiveResultsDisplay'
import { api } from '../../api'

interface OutputMonitoringProps {
    targetUrl: string
    pageContent?: string
    pageTitle?: string
    productId?: string | number
}

export function OutputMonitoring({ targetUrl, pageContent: _pageContent, pageTitle: _pageTitle, productId }: OutputMonitoringProps) {
    const [results, setResults] = useState<MultiEngineResponse | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [loadingStage, setLoadingStage] = useState<string>('')
    const [error, setError] = useState<string | null>(null)

    // Tab State
    const [activeTab, setActiveTab] = useState<'overview' | 'ask' | 'history'>('overview')

    // Unified State
    const [query, setQuery] = useState('')
    const [selectedEngines, setSelectedEngines] = useState<string[]>(['openai', 'anthropic', 'gemini'])
    const [selectedCompetitors, setSelectedCompetitors] = useState<string[]>([])
    const [competitiveResults, setCompetitiveResults] = useState<any | null>(null)

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

    // SOTA Analysis State
    const [analysisResult, setAnalysisResult] = useState<any>(null)
    const [isAnalyzing, setIsAnalyzing] = useState(false)

    // Trigger analysis on mount or url change
    useEffect(() => {
        const runAnalysis = async () => {
            if (!targetUrl || isAnalyzing || analysisResult) return
            setIsAnalyzing(true)
            try {
                // Pass page content if available to avoid re-scraping
                const data = await api.monitoring.analyze(targetUrl, _pageContent, productId)
                setAnalysisResult(data)
            } catch (e: any) {
                // 422 is expected if insufficient content.
                // Check status (if available from ApiError) or message text
                if (e.status === 422 || (e.message && e.message.includes('Unprocessable'))) {
                    console.warn("Analysis skipped (insufficient content to generate questions). Using default templates.")
                } else {
                    console.error("Analysis failed:", e)
                }
            } finally {
                setIsAnalyzing(false)
            }
        }
        runAnalysis()
    }, [targetUrl])

    const handleSubmit = async (queryText: string, engines: string[]) => {
        setIsLoading(true)
        setLoadingStage('Initializing analysis...')
        setError(null)
        setResults(null)
        setCompetitiveResults(null)

        try {
            // Competitive Flow
            if (selectedCompetitors.length > 0) {
                setLoadingStage('Running competitive analysis...')
                const targetUrls = [targetUrl, ...selectedCompetitors]
                const data = await api.monitoring.competitiveQuery(queryText, targetUrls, engines, productId)
                setCompetitiveResults(data)
            } else {
                // Standard Flow
                const profile = analysisResult?.profile
                setLoadingStage('Fetching AI responses...')
                const data = await api.monitoring.query(queryText, targetUrl, engines, profile, productId)
                setResults(data)
            }
        } catch (e: any) {
            setError(e.message)
        } finally {
            setIsLoading(false)
            setLoadingStage('')
        }
    }

    const handleTemplateSelect = (templateQuery: string) => {
        setActiveTab('ask') // Switch to ask tab
        setQuery(templateQuery)
        handleSubmit(templateQuery, selectedEngines)
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }



    return (
        <div className="max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div>
                <div className="flex items-start gap-4 mb-2">
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

                {/* Tabs */}
                <div className="sticky top-0 z-20 bg-background/95 backdrop-blur-md pt-4 -mx-4 px-4">
                    <div className="flex items-center gap-1 border-b border-border">
                        <button
                            onClick={() => setActiveTab('overview')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'overview'
                                ? 'border-indigo-500 text-text-primary'
                                : 'border-transparent text-text-secondary hover:text-text-primary hover:border-border'
                                }`}
                        >
                            Overview
                        </button>
                        <button
                            onClick={() => setActiveTab('ask')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'ask'
                                ? 'border-indigo-500 text-text-primary'
                                : 'border-transparent text-text-secondary hover:text-text-primary hover:border-border'
                                }`}
                        >
                            Ask LLMs
                        </button>
                        <button
                            onClick={() => setActiveTab('history')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'history'
                                ? 'border-indigo-500 text-text-primary'
                                : 'border-transparent text-text-secondary hover:text-text-primary hover:border-border'
                                }`}
                        >
                            History
                        </button>
                    </div>
                </div>
            </div>

            {/* Tab: Overview */}
            {activeTab === 'overview' && (
                <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
                    <div className="bg-surface rounded-xl">
                        {productId ? (
                            <CompetitorAnalysis productId={productId} />
                        ) : (
                            <div className="p-6 bg-surface border border-border rounded-xl text-center text-text-secondary">
                                Competitor analysis requires a saved product.
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Tab: Ask LLMs */}
            {activeTab === 'ask' && (
                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
                    {/* Input Area */}
                    <div className={results ? "sticky top-[60px] z-10 pt-2" : ""}>
                        <QueryInput
                            targetUrl={targetUrl}
                            onSubmit={handleSubmit}
                            isLoading={isLoading}
                            loadingStage={loadingStage}
                            query={query}
                            setQuery={setQuery}
                            selectedEngines={selectedEngines}
                            setSelectedEngines={setSelectedEngines}
                        />

                        {productId && (
                            <div className="mt-4 animate-in fade-in slide-in-from-top-2 duration-500">
                                <CompetitorSelector
                                    productId={productId}
                                    selectedCompetitors={selectedCompetitors}
                                    onToggle={(domain) => {
                                        setSelectedCompetitors(prev =>
                                            prev.includes(domain) ? prev.filter(d => d !== domain) : [...prev, domain]
                                        )
                                    }}
                                />
                            </div>
                        )}
                    </div>

                    {/* Error Display */}
                    {error && (
                        <div className="p-4 bg-red-900/10 border border-red-900/20 rounded-lg">
                            <p className="text-sm text-red-400">{error}</p>
                        </div>
                    )}

                    {/* Results Area */}
                    {competitiveResults ? (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <CompetitiveResultsDisplay
                                results={competitiveResults}
                                yourUrl={targetUrl}
                            />
                        </div>
                    ) : results ? (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <ResultsDisplay results={results} />
                        </div>
                    ) : (
                        /* Show Templates only if no results yet, as a helper */
                        <PromptTemplates
                            onSelect={handleTemplateSelect}
                            brandName={brandName}
                            suggestedQueries={analysisResult?.suggested_queries}
                            isLoading={isAnalyzing}
                            onRefresh={productId ? async () => {
                                setIsAnalyzing(true)
                                try {
                                    const data = await api.monitoring.refreshQueries(productId)
                                    // Update local state by merging
                                    setAnalysisResult((prev: any) => ({
                                        ...prev,
                                        suggested_queries: data.suggested_queries
                                    }))
                                } catch (e) {
                                    console.error("Refresh queries failed", e)
                                    alert("Failed to refresh queries.")
                                } finally {
                                    setIsAnalyzing(false)
                                }
                            } : undefined}
                        />
                    )}
                </div>
            )}

            {/* Tab: History */}
            {activeTab === 'history' && (
                <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
                    <HistorySidebar productId={productId} />
                </div>
            )}
        </div>
    )
}
