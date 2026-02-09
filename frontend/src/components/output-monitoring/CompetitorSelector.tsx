import { useState, useEffect } from 'react'
import { Users, Check, Plus } from 'lucide-react'

interface Competitor {
    name: string
    domain: string
}

interface CompetitorSelectorProps {
    productId: string | number
    selectedCompetitors: string[]
    onToggle: (domain: string) => void
}

export function CompetitorSelector({ productId, selectedCompetitors, onToggle }: CompetitorSelectorProps) {
    const [competitors, setCompetitors] = useState<Competitor[]>([])
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        if (!productId) return

        fetch(`/api/output-monitoring/competitors?product_id=${productId}`)
            .then(res => res.json())
            .then(data => {
                if (data.companies) {
                    setCompetitors(data.companies)
                }
            })
            .catch(console.error)
            .finally(() => setIsLoading(false))
    }, [productId])

    if (isLoading) return <div className="text-xs text-text-secondary animate-pulse">Loading competitors...</div>
    if (competitors.length === 0) return null

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-text-secondary uppercase tracking-wider">
                <Users className="w-3.5 h-3.5" />
                Compare with Competitors
            </div>

            <div className="flex flex-wrap gap-2">
                {competitors.map((comp) => {
                    const isSelected = selectedCompetitors.includes(comp.domain)
                    return (
                        <button
                            key={comp.domain}
                            onClick={() => onToggle(comp.domain)}
                            className={`px-3 py-1.5 rounded-lg border text-xs transition-all flex items-center gap-2 ${isSelected
                                    ? 'bg-indigo-500/10 border-indigo-500/50 text-indigo-400'
                                    : 'bg-surface border-border text-text-secondary hover:border-text-secondary/50'
                                }`}
                        >
                            {isSelected ? <Check className="w-3 h-3" /> : <Plus className="w-3 h-3" />}
                            <span className="font-medium">{comp.name}</span>
                            <span className="opacity-50 font-mono text-[10px]">{comp.domain}</span>
                        </button>
                    )
                })}
            </div>
        </div>
    )
}
