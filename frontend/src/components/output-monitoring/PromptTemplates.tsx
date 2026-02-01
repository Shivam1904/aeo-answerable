
import { Sparkles, MessageSquare, ArrowRight } from 'lucide-react'

export interface SmartPrompt {
    id: string
    query: string
    category: string
    description: string
}

interface PromptTemplatesProps {
    onSelect: (query: string) => void
    brandName: string
}

export function PromptTemplates({ onSelect, brandName }: PromptTemplatesProps) {
    const brand = brandName.charAt(0).toUpperCase() + brandName.slice(1).toLowerCase()

    const templates: SmartPrompt[] = [
        {
            id: 'brand-awareness',
            query: `What is ${brand}?`,
            category: 'Brand',
            description: 'Check if AI knows your brand exists'
        },
        {
            id: 'reviews',
            query: `Is ${brand} legit?`,
            category: 'Trust',
            description: 'Check sentiment and reputation'
        },
        {
            id: 'competitors',
            query: `${brand} vs competitors`,
            category: 'Comparison',
            description: 'See who you are compared against'
        },
        {
            id: 'pricing',
            query: `How much does ${brand} cost?`,
            category: 'Pricing',
            description: 'Check pricing accuracy'
        },
        {
            id: 'features',
            query: `What are the key features of ${brand}?`,
            category: 'Product',
            description: 'Check feature knowledge'
        }
    ]

    return (
        <div className="space-y-4">
            <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Quick Templates
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {templates.map((template) => (
                    <button
                        key={template.id}
                        onClick={() => onSelect(template.query)}
                        className="group flex flex-col items-start gap-2 p-4 bg-zinc-900/30 hover:bg-zinc-900 border border-zinc-800 hover:border-indigo-500/50 rounded-xl transition-all text-left"
                    >
                        <div className="p-2 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500/20 transition-colors">
                            <MessageSquare className="w-4 h-4 text-indigo-400" />
                        </div>

                        <div>
                            <div className="text-sm font-medium text-zinc-200 group-hover:text-indigo-300 transition-colors">
                                {template.category} Check
                            </div>
                            <div className="text-xs text-zinc-500 mt-1 line-clamp-2 group-hover:text-zinc-400">
                                "{template.query}"
                            </div>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    )
}
