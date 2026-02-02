import { useState, useEffect } from 'react'
import { Sparkles, Pencil, Plus, X } from 'lucide-react'
import { Product } from '../../types'

interface ProductFormProps {
    initialData?: Product
    onSubmit: (data: ProductFormData) => Promise<void>
    onCancel: () => void
    isSubmitting: boolean
}

export interface ProductFormData {
    name: string
    domain: string
    default_mode: 'fast' | 'rendered'
    profile: {
        business_bio: string
        target_region: string
        target_audience_age: string
        gender_preference: string
    }
}

export function ProductForm({ initialData, onSubmit, onCancel, isSubmitting }: ProductFormProps) {
    const [formData, setFormData] = useState<ProductFormData>({
        name: '',
        domain: '',
        default_mode: 'rendered',
        profile: {
            business_bio: '',
            target_region: 'Global',
            target_audience_age: 'All',
            gender_preference: 'All'
        }
    })

    useEffect(() => {
        if (initialData) {
            setFormData({
                name: initialData.name,
                domain: initialData.domain,
                default_mode: initialData.default_mode || 'rendered',
                profile: {
                    business_bio: initialData.business_bio || '',
                    target_region: initialData.target_region || 'Global',
                    target_audience_age: initialData.target_audience_age || 'All',
                    gender_preference: initialData.gender_preference || 'All'
                }
            })
            window.scrollTo({ top: 0, behavior: 'smooth' })
        }
    }, [initialData])

    const handleSubmit = () => {
        if (!formData.name || !formData.domain) return
        onSubmit(formData)
    }

    const updateField = (field: keyof ProductFormData, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }))
    }

    const updateProfile = (field: keyof ProductFormData['profile'], value: string) => {
        setFormData(prev => ({
            ...prev,
            profile: { ...prev.profile, [field]: value }
        }))
    }

    const isEditMode = !!initialData

    return (
        <div className="flex flex-col h-full bg-surface">
            {/* Header */}
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isEditMode ? 'bg-primary text-white' : 'bg-primary/10 text-primary'}`}>
                        {isEditMode ? <Pencil className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
                    </div>
                    <h3 className="text-xl font-bold text-text-primary">
                        {isEditMode ? 'Edit Product' : 'Add New Product'}
                    </h3>
                </div>
                <button onClick={onCancel} className="text-text-secondary hover:text-red-400">
                    <X className="w-5 h-5" />
                </button>
            </div>

            {/* Scrollable Content */}
            <div className="p-6 space-y-4 overflow-y-auto custom-scrollbar flex-1 max-h-[60vh]">
                {/* Product Name */}
                <div>
                    <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5 block">Product Name</label>
                    <input
                        type="text"
                        placeholder="e.g., My Blog"
                        value={formData.name}
                        onChange={(e) => updateField('name', e.target.value)}
                        className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:border-primary transition-colors"
                    />
                </div>

                {/* Domain */}
                <div>
                    <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5 block">Domain</label>
                    <input
                        type="text"
                        placeholder="e.g., example.com"
                        value={formData.domain}
                        onChange={(e) => updateField('domain', e.target.value)}
                        className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:border-primary transition-colors"
                    />
                </div>

                {/* Region */}
                <div>
                    <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5 block">Target Region</label>
                    <input
                        type="text"
                        placeholder="e.g., USA, Europe, Global"
                        value={formData.profile.target_region}
                        onChange={(e) => updateProfile('target_region', e.target.value)}
                        className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:border-primary transition-colors"
                    />
                </div>

                {/* Business Bio */}
                <div>
                    <div className="flex items-center justify-between mb-1.5">
                        <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider block">Business Bio</label>
                        <span className="text-[10px] text-indigo-400 flex items-center gap-1">
                            <Sparkles className="w-3 h-3" />
                            AI Auto-fills if empty
                        </span>
                    </div>
                    <textarea
                        placeholder="Short description of what your business does..."
                        value={formData.profile.business_bio}
                        onChange={(e) => updateProfile('business_bio', e.target.value)}
                        className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:border-primary transition-colors h-24 resize-none"
                    />
                </div>

                {/* Audience & Gender (Row) */}
                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5 block">Audience Age</label>
                        <select
                            value={formData.profile.target_audience_age}
                            onChange={(e) => updateProfile('target_audience_age', e.target.value)}
                            className="w-full px-2 py-2 bg-background border border-border rounded-lg text-sm text-text-primary focus:outline-none focus:border-primary"
                        >
                            <option value="All">All Ages</option>
                            <option value="18-24">18-24</option>
                            <option value="25-34">25-34</option>
                            <option value="35-50">35-50</option>
                            <option value="50+">50+</option>
                        </select>
                    </div>
                    <div>
                        <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5 block">Gender</label>
                        <select
                            value={formData.profile.gender_preference}
                            onChange={(e) => updateProfile('gender_preference', e.target.value)}
                            className="w-full px-2 py-2 bg-background border border-border rounded-lg text-sm text-text-primary focus:outline-none focus:border-primary"
                        >
                            <option value="All">All</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                </div>

                {/* Mode Selection - DISABLED: Defaulting to Rendered mode as per user request (02/02/2026) */}
                {/* 
                <div>
                    <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2 block">Audit Mode</label>
                    <div className="grid grid-cols-2 gap-2 p-1 bg-background border border-border rounded-lg">
                        <button
                            type="button"
                            onClick={() => updateField('default_mode', 'fast')}
                            className={`py-1.5 text-xs font-medium rounded transition-colors ${formData.default_mode === 'fast'
                                ? 'bg-primary text-white shadow-sm'
                                : 'text-text-secondary hover:text-text-primary'
                                }`}
                        >
                            Fast Mode
                        </button>
                        <button
                            type="button"
                            onClick={() => updateField('default_mode', 'rendered')}
                            className={`py-1.5 text-xs font-medium rounded transition-colors ${formData.default_mode === 'rendered'
                                ? 'bg-primary text-white shadow-sm'
                                : 'text-text-secondary hover:text-text-primary'
                                }`}
                        >
                            Rendered
                        </button>
                    </div>
                </div>
                */}
            </div>

            {/* Sticky Footer */}
            <div className="p-6 border-t border-border bg-surface flex items-center gap-3">
                <button
                    onClick={onCancel}
                    className="flex-1 py-3 rounded-lg font-medium text-sm text-text-secondary bg-surface border border-border hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
                >
                    Cancel
                </button>
                <button
                    onClick={handleSubmit}
                    disabled={isSubmitting || !formData.name || !formData.domain}
                    className={`flex-[2] py-3 rounded-lg font-bold text-sm tracking-wide transition-all shadow-md active:scale-[0.99] ${isSubmitting || (!formData.name && !isEditMode)
                        ? 'bg-zinc-700 text-zinc-400 cursor-not-allowed'
                        : 'bg-primary hover:bg-primary/90 text-white hover:shadow-lg'
                        }`}
                >
                    {isSubmitting ? (
                        <span className="flex items-center justify-center gap-2">
                            <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                            Saving...
                        </span>
                    ) : (
                        isEditMode ? 'Update Product' : 'Create Product'
                    )}
                </button>
            </div>
        </div>
    )
}
