
import { Sparkles } from 'lucide-react'
import { MultiEngineResponse } from './types'
import { EngineResponseCard } from './EngineResponseCard'
import { AnalysisSummary } from '../results/AnalysisSummary'
import { CompetitiveAnalysisCard } from '../results/CompetitiveAnalysisCard'

interface ResultsDisplayProps {
    results: MultiEngineResponse
}

export function ResultsDisplay({ results }: ResultsDisplayProps) {
    return (
        <div className="space-y-8 animation-fade-in">
            {/* Unified Analysis Summary Card */}
            <AnalysisSummary results={results} />

            {/* Competitive Intelligence (SOTA) */}
            {results.sota_insights && (
                <CompetitiveAnalysisCard sotaInsights={results.sota_insights} />
            )}

            {/* Engine Responses Header */}
            <div className="pt-4">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-gradient-to-br from-surface to-surface-highlight rounded-lg border border-border">
                        <Sparkles className="w-4 h-4 text-purple-400" />
                    </div>
                    <h3 className="text-xl font-bold text-text-primary">AI Engine Reponses</h3>
                </div>

                <div className="space-y-4">
                    {results.results.map((result, i) => (
                        <EngineResponseCard key={`${result.engine}-${i}`} result={result} brandName="Your Brand" />
                    ))}
                </div>
            </div>
        </div>
    )
}
