import { useState, useEffect } from 'react'
import { Wallet, AlertTriangle } from 'lucide-react'

interface BudgetStatus {
    total_spend: number
    budget_limit: number
    remaining: number
    currency: string
}

export function BudgetIndicator() {
    const [budget, setBudget] = useState<BudgetStatus | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchBudget = async () => {
            try {
                const response = await fetch('/api/output-monitoring/budget')
                if (response.ok) {
                    const data = await response.json()
                    setBudget(data)
                }
            } catch (e) {
                console.error('Failed to fetch budget:', e)
            } finally {
                setLoading(false)
            }
        }

        fetchBudget()
        // Refresh every minute
        const interval = setInterval(fetchBudget, 60000)
        return () => clearInterval(interval)
    }, [])

    if (loading || !budget) {
        return null
    }

    const usagePercent = (budget.total_spend / budget.budget_limit) * 100
    const isLow = usagePercent >= 80
    const isExhausted = budget.remaining <= 0

    return (
        <div className={`p-4 border rounded-lg ${isExhausted
                ? 'border-red-900/50 bg-red-900/10'
                : isLow
                    ? 'border-amber-900/50 bg-amber-900/10'
                    : 'border-zinc-800 bg-zinc-900/30'
            }`}>
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    <Wallet className={`w-4 h-4 ${isExhausted ? 'text-red-400' : isLow ? 'text-amber-400' : 'text-zinc-400'
                        }`} />
                    <span className="text-sm font-medium text-zinc-300">Daily Budget</span>
                </div>
                <span className={`text-xs ${isExhausted ? 'text-red-400' : isLow ? 'text-amber-400' : 'text-zinc-500'
                    }`}>
                    {/* Query count not yet in API */}
                    Budget Usage
                </span>
            </div>

            {/* Progress Bar */}
            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden mb-2">
                <div
                    className={`h-full rounded-full transition-all ${isExhausted ? 'bg-red-500' : isLow ? 'bg-amber-500' : 'bg-emerald-500'
                        }`}
                    style={{ width: `${Math.min(100, usagePercent)}%` }}
                />
            </div>

            <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-500">
                    ${budget.total_spend.toFixed(4)} / ${budget.budget_limit.toFixed(2)}
                </span>
                <span className={isLow ? 'text-amber-400' : 'text-zinc-400'}>
                    ${budget.remaining.toFixed(4)} remaining
                </span>
            </div>

            {isExhausted && (
                <div className="mt-3 flex items-center gap-2 text-xs text-red-400">
                    <AlertTriangle className="w-3 h-3" />
                    <span>Budget exhausted. Queries disabled until tomorrow.</span>
                </div>
            )}

            {isLow && !isExhausted && (
                <div className="mt-3 flex items-center gap-2 text-xs text-amber-400">
                    <AlertTriangle className="w-3 h-3" />
                    <span>Budget running low</span>
                </div>
            )}
        </div>
    )
}
