
import { Sparkles, MessageSquare } from 'lucide-react'
import { SmartPrompt } from '../../types'


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
            <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Quick Templates
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {templates.map((template) => (
                    <button
                        key={template.id}
                        onClick={() => onSelect(template.query)}
                        className="group flex flex-col items-start gap-2 p-4 bg-surface/50 hover:bg-surface border border-border hover:border-primary/50 rounded-xl transition-all text-left shadow-sm"
                    >
                        <div className="p-2 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500/20 transition-colors">
                            <MessageSquare className="w-4 h-4 text-indigo-400" />
                        </div>

                        <div>
                            <div className="text-sm font-medium text-text-primary group-hover:text-primary transition-colors">
                                {template.category} Check
                            </div>
                            <div className="text-xs text-text-secondary mt-1 line-clamp-2 group-hover:text-text-secondary/80">
                                "{template.query}"
                            </div>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    )
}
