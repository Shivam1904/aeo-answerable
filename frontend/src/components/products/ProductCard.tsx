import { Globe, Pencil, Trash2, Sparkles } from 'lucide-react'
import { Product } from '../../types'

interface ProductCardProps {
    product: Product
    isEditing: boolean
    onEdit: (product: Product) => void
    onDelete: (id: number) => void
    onNavigate: (id: number) => void
}

export function ProductCard({ product, isEditing, onEdit, onDelete, onNavigate }: ProductCardProps) {
    return (
        <div className={`bg-surface border rounded-xl p-6 flex flex-col justify-between transition-colors shadow-sm group ${isEditing ? 'border-primary/50 ring-1 ring-primary/30' : 'border-border hover:border-text-secondary/30'}`}>
            <div className="mb-6">
                <div className="flex justify-between items-start mb-4">
                    <div className="w-10 h-10 rounded-lg bg-surface-highlight flex items-center justify-center text-text-secondary group-hover:text-primary transition-colors">
                        <Globe className="w-5 h-5" />
                    </div>
                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                            onClick={() => onEdit(product)}
                            className="p-1.5 rounded hover:bg-surface-highlight text-text-secondary hover:text-primary transition-colors"
                            title="Edit"
                        >
                            <Pencil className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                <h3 className="text-xl font-bold text-text-primary mb-1">{product.name}</h3>
                <p className="text-sm text-text-secondary font-mono truncate mb-2">{product.domain}</p>

                {/* Bio / AI Badge */}
                {product.is_bio_ai_generated && (
                    <span className="inline-flex items-center gap-1 text-[10px] text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full border border-indigo-500/20">
                        <Sparkles className="w-3 h-3" />
                        AI Profile
                    </span>
                )}

                {/* Detail Badges */}
                <div className="mt-4 flex flex-wrap gap-2">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium uppercase tracking-wide border ${product.default_mode === 'rendered'
                        ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                        : 'bg-green-500/10 text-green-400 border-green-500/20'
                        }`}>
                        {product.default_mode || 'fast'}
                    </span>
                    {product.target_region && product.target_region !== 'Global' && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-surface-highlight text-text-secondary border border-border">
                            {product.target_region}
                        </span>
                    )}
                </div>
            </div>
            <div className="flex gap-3">
                <button
                    onClick={() => onNavigate(product.id)}
                    className="flex-1 py-2 rounded-lg bg-surface-highlight hover:bg-primary hover:text-white text-text-primary text-sm font-medium transition-colors"
                >
                    Go to Dashboard
                </button>
                <button
                    onClick={() => onDelete(product.id)}
                    className="px-3 py-2 rounded-lg bg-surface-highlight hover:bg-red-500/10 hover:text-red-500 text-text-secondary transition-colors"
                    title="Delete product"
                >
                    <Trash2 className="w-4 h-4" />
                </button>
            </div>
        </div>
    )
}
