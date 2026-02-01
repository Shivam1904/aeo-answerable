import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Globe, Trash2 } from 'lucide-react'
import { Navbar } from '../components/common/Navbar'
import { api } from '../api'

interface Product {
    id: number
    name: string
    domain: string
    default_mode?: 'fast' | 'rendered'
    created_at: string
}

export default function ProductSelectionPage() {
    const [products, setProducts] = useState<Product[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [isCreating, setIsCreating] = useState(false)
    const [newProductName, setNewProductName] = useState('')
    const [newDomain, setNewDomain] = useState('')
    const [defaultMode, setDefaultMode] = useState<'fast' | 'rendered'>('fast')
    const [user, setUser] = useState<any>(null)
    const navigate = useNavigate()

    useEffect(() => {
        const storedUser = localStorage.getItem('aeo_user')
        if (!storedUser) {
            navigate('/')
            return
        }
        const parsedUser = JSON.parse(storedUser)
        setUser(parsedUser)
        loadProducts(parsedUser.user_id)
    }, [navigate])

    const loadProducts = async (userId: number) => {
        try {
            const data = await api.products.list(userId)
            setProducts(data)
        } catch (err) {
            console.error(err)
        } finally {
            setIsLoading(false)
        }
    }

    const handleCreateProduct = async () => {
        if (!newProductName || !newDomain) return

        setIsCreating(true)
        try {
            await api.products.create(user.user_id, newProductName, newDomain, defaultMode)
            setNewProductName('')
            setNewDomain('')
            loadProducts(user.user_id)
            setIsCreating(false)
        } catch (err) {
            console.error(err)
            setIsCreating(false)
        }
    }

    const deleteProduct = async (id: number) => {
        if (!confirm('Are you sure you want to delete this product?')) return
        try {
            await api.products.delete(id)
            loadProducts(user.user_id)
        } catch (err) {
            console.error(err)
        }
    }

    return (
        <div className="min-h-screen bg-background">
            <Navbar user={user} />

            <div className="p-6 lg:p-12 pt-40 lg:pt-48 max-w-6xl mx-auto space-y-12">
                <header className="border-b border-border pb-6">
                    <h1 className="text-3xl font-bold text-text-primary mb-2">Your Products</h1>
                    <p className="text-text-secondary">Select a website to monitor or add a new one.</p>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Create New Card */}
                    <div className="bg-surface border border-border rounded-xl p-6 flex flex-col justify-between hover:border-primary/50 transition-colors shadow-sm">
                        <div className="mb-6">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4 text-primary">
                                <Plus className="w-5 h-5" />
                            </div>
                            <h3 className="text-xl font-bold text-text-primary mb-2">Add New Product</h3>
                            {!isCreating ? (
                                <p className="text-sm text-text-secondary">Start monitoring a new domain and analyze its AEO readiness.</p>
                            ) : (
                                <div className="space-y-4 animate-fade-in">
                                    <div>
                                        <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5 block">Product Name</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., My Blog"
                                            value={newProductName}
                                            onChange={(e) => setNewProductName(e.target.value)}
                                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:border-primary transition-colors"
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5 block">Domain</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., example.com"
                                            value={newDomain}
                                            onChange={(e) => setNewDomain(e.target.value)}
                                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:border-primary transition-colors"
                                        />
                                    </div>

                                    {/* Mode Selection */}
                                    <div>
                                        <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2 block">Audit Mode</label>
                                        <div className="grid grid-cols-2 gap-2 p-1 bg-background border border-border rounded-lg">
                                            <button
                                                type="button"
                                                onClick={() => setDefaultMode('fast')}
                                                className={`py-1.5 text-xs font-medium rounded transition-colors ${defaultMode === 'fast'
                                                    ? 'bg-primary text-white shadow-sm'
                                                    : 'text-text-secondary hover:text-text-primary'
                                                    }`}
                                            >
                                                Fast Mode
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => setDefaultMode('rendered')}
                                                className={`py-1.5 text-xs font-medium rounded transition-colors ${defaultMode === 'rendered'
                                                    ? 'bg-primary text-white shadow-sm'
                                                    : 'text-text-secondary hover:text-text-primary'
                                                    }`}
                                            >
                                                Start with Rendered
                                            </button>
                                        </div>
                                        <p className="mt-1.5 text-[10px] text-text-secondary">
                                            {defaultMode === 'fast'
                                                ? 'HTML-only scan. Faster & cheaper.'
                                                : 'Full browser rendering. Captures JS content.'}
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                        <button
                            onClick={handleCreateProduct}
                            disabled={isCreating && (!newProductName || !newDomain)}
                            className={`w-full py-2.5 rounded-lg font-medium transition-all ${isCreating
                                ? 'bg-primary hover:bg-primary/90 text-white disabled:opacity-50 disabled:cursor-not-allowed'
                                : 'bg-surface-highlight hover:bg-border text-text-primary'
                                }`}
                        >
                            {isCreating ? 'Create Product' : 'Get Started'}
                        </button>
                    </div>

                    {/* Existing Products */}
                    {isLoading ? (
                        <div className="col-span-full text-center py-12 text-text-secondary">Loading your products...</div>
                    ) : (
                        products.map((product) => (
                            <div key={product.id} className="bg-surface border border-border rounded-xl p-6 flex flex-col justify-between hover:border-text-secondary/30 transition-colors shadow-sm group">
                                <div className="mb-6">
                                    <div className="w-10 h-10 rounded-lg bg-surface-highlight flex items-center justify-center mb-4 text-text-secondary group-hover:text-primary transition-colors">
                                        <Globe className="w-5 h-5" />
                                    </div>
                                    <h3 className="text-xl font-bold text-text-primary mb-1">{product.name}</h3>
                                    <p className="text-sm text-text-secondary font-mono truncate">{product.domain}</p>
                                    {/* Mode Badge */}
                                    <div className="mt-3">
                                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium uppercase tracking-wide border ${product.default_mode === 'rendered'
                                            ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                                            : 'bg-green-500/10 text-green-400 border-green-500/20'
                                            }`}>
                                            {product.default_mode || 'fast'}
                                        </span>
                                    </div>
                                </div>
                                <div className="flex gap-3">
                                    <button
                                        onClick={() => navigate(`/dashboard/${product.id}`)}
                                        className="flex-1 py-2 rounded-lg bg-surface-highlight hover:bg-primary hover:text-white text-text-primary text-sm font-medium transition-colors"
                                    >
                                        Go to Dashboard
                                    </button>
                                    <button
                                        onClick={() => deleteProduct(product.id)}
                                        className="px-3 py-2 rounded-lg bg-surface-highlight hover:bg-red-500/10 hover:text-red-500 text-text-secondary transition-colors"
                                        title="Delete product"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}
