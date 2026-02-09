
import { useEffect, useState } from 'react'
import { Building2, Sparkles, ExternalLink, HelpCircle, RefreshCw } from 'lucide-react'
import { api } from '../../api'

interface Company {
    name: string
    domain: string
    reason: string
}

interface CompetitorAnalysisProps {
    productId: string | number
}

export function CompetitorAnalysis({ productId }: CompetitorAnalysisProps) {
    const [companies, setCompanies] = useState<Company[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [isRefreshing, setIsRefreshing] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleRefresh = async () => {
        setIsRefreshing(true)
        setError(null)
        try {
            const data = await api.monitoring.refreshCompetitors(productId)
            if (data.companies) {
                setCompanies(data.companies)
            }
        } catch (err: any) {
            console.error(err)
            setError('Failed to refresh analysis.')
        } finally {
            setIsRefreshing(false)
        }
    }

    useEffect(() => {
        const fetchCompetitors = async () => {
            try {
                // Determine if we need to fetch? 
                // Since this might cost money/tokens, maybe we should cache it or trigger it manually?
                // For now, auto-fetch on mount.
                const data = await api.monitoring.getSimilarCompanies(productId)
                if (data.companies) {
                    setCompanies(data.companies)
                }
            } catch (err: any) {
                console.error(err)
                setError('Failed to load competitor analysis.')
            } finally {
                setIsLoading(false)
            }
        }

        if (productId) {
            fetchCompetitors()
        }
    }, [productId])

    if (error) {
        return (
            <div className="rounded-xl border border-red-200 bg-red-50 p-6 animate-in fade-in slide-in-from-bottom-4">
                <div className="flex items-center gap-3 text-red-600 mb-2">
                    <HelpCircle className="w-5 h-5" />
                    <h3 className="font-bold">Analysis Failed</h3>
                </div>
                <p className="text-sm text-red-500">{error}</p>
                <button onClick={() => window.location.reload()} className="mt-4 text-xs bg-white border border-red-200 px-3 py-1.5 rounded hover:bg-gray-50 text-red-600 font-medium">
                    Retry
                </button>
            </div>
        )
    }

    return (
        <div className="rounded-xl border border-border bg-surface/50 overflow-hidden shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="p-6 border-b border-border flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-500/10 rounded-lg">
                        <Building2 className="w-5 h-5 text-indigo-400" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-text-primary">Similar Companies</h3>
                        <p className="text-xs text-text-secondary">Competitors likely to be cited alongside you.</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleRefresh}
                        disabled={isRefreshing}
                        className="px-2 py-1 hover:bg-surface-highlight border border-transparent hover:border-border rounded text-[10px] font-medium text-text-secondary flex items-center gap-1.5 transition-colors"
                        title="Refresh analysis based on latest product bio"
                    >
                        <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
                        Refresh
                    </button>
                    <div className="px-2 py-1 bg-surface-highlight border border-border rounded text-[10px] font-medium text-text-secondary flex items-center gap-1.5">
                        <Sparkles className="w-3 h-3 text-indigo-400" />
                        AI Analysis
                    </div>
                </div>
            </div>

            <div className="p-6">
                {isLoading ? (
                    <div className="space-y-3">
                        {Array.from({ length: 3 }).map((_, i) => (
                            <div key={i} className="h-16 rounded-xl bg-surface/30 animate-pulse border border-border/50" />
                        ))}
                    </div>
                ) : companies.length === 0 ? (
                    <div className="text-center py-8 text-text-secondary">
                        <HelpCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No similar companies identified yet.</p>
                    </div>
                ) : (
                    <div className="grid gap-3">
                        {companies.map((company, idx) => (
                            <div
                                key={idx}
                                className="group p-4 bg-surface/30 border border-border/50 hover:border-indigo-500/30 hover:bg-surface/60 rounded-xl transition-all"
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div>
                                        <h4 className="font-bold text-text-primary text-sm flex items-center gap-2">
                                            {company.name}
                                            <a
                                                href={`https://${company.domain}`}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="text-text-secondary hover:text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                                onClick={(e) => e.stopPropagation()}
                                            >
                                                <ExternalLink className="w-3 h-3" />
                                            </a>
                                        </h4>
                                        <p className="text-xs text-text-secondary font-mono mt-0.5">{company.domain}</p>
                                    </div>
                                </div>
                                <p className="mt-2 text-xs text-text-secondary leading-relaxed border-t border-border/30 pt-2 opacity-80 group-hover:opacity-100">
                                    {company.reason}
                                </p>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
