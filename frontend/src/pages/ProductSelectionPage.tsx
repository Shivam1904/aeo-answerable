import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createPortal } from 'react-dom'
import { Navbar } from '../components/common/Navbar'
import { Plus } from 'lucide-react'
import { ProductForm, ProductFormData } from '../components/products/ProductForm'
import { ProductCard } from '../components/products/ProductCard'
import { useProducts } from '../hooks/useProducts'
import { Product } from '../types'

export default function ProductSelectionPage() {
    const [user, setUser] = useState<any>(null)
    const navigate = useNavigate()

    // User Session Management
    useEffect(() => {
        const storedUser = localStorage.getItem('aeo_user')
        if (!storedUser) {
            navigate('/')
            return
        }
        setUser(JSON.parse(storedUser))
    }, [navigate])

    const { products, isLoading, createProduct, updateProduct, deleteProduct, loadProducts } = useProducts(user?.user_id)

    // Edit Mode State
    const [editingProduct, setEditingProduct] = useState<Product | null>(null)
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)

    // Initial load
    useEffect(() => {
        if (user) loadProducts()
    }, [user, loadProducts])

    // Handlers
    const handleCreateOrUpdate = async (formData: ProductFormData) => {
        setIsSubmitting(true)

        if (editingProduct) {
            const success = await updateProduct(editingProduct.id, {
                name: formData.name,
                domain: formData.domain,
                default_mode: formData.default_mode,
                business_bio: formData.profile.business_bio,
                target_region: formData.profile.target_region,
                target_audience_age: formData.profile.target_audience_age,
                gender_preference: formData.profile.gender_preference
            })
            if (success) {
                setEditingProduct(null)
                setIsCreateModalOpen(false)
            }
        } else {
            const newProduct = await createProduct(
                formData.name,
                formData.domain,
                formData.default_mode,
                formData.profile
            )

            if (newProduct) {
                // Navigate to the dashboard of the new product
                // We use 'as any' here because useProducts return type inference might need adjustment, 
                // but at runtime `newProduct` is the object with an id.
                navigate(`/dashboard/${(newProduct as any).id}`)
            }
        }

        setIsSubmitting(false)
    }

    const handleDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this product?')) return
        await deleteProduct(id)
        if (editingProduct?.id === id) {
            setEditingProduct(null)
        }
    }

    return (
        <div className="min-h-screen bg-background">
            <Navbar user={user} />

            <div className="p-6 lg:p-12 pt-24 lg:pt-32 max-w-6xl mx-auto space-y-8">
                <div className="flex items-center justify-between border-b border-border pb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-text-primary mb-2">Your Products</h1>
                        <p className="text-text-secondary">Select a website to monitor or add a new one.</p>
                    </div>
                    <button
                        onClick={() => setIsCreateModalOpen(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 text-white font-medium rounded-lg transition-colors shadow-sm"
                    >
                        <Plus className="w-4 h-4" />
                        Create Product
                    </button>
                </div>

                {/* Product List */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {isLoading ? (
                        [1, 2, 3].map((n) => (
                            <div key={n} className="h-64 rounded-xl bg-surface/50 border border-border animate-pulse" />
                        ))
                    ) : products.length === 0 ? (
                        <div className="col-span-full text-center py-20 bg-surface/30 rounded-2xl border border-dashed border-border">
                            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Plus className="w-8 h-8 text-primary" />
                            </div>
                            <h3 className="text-lg font-semibold text-text-primary mb-2">No Products Yet</h3>
                            <p className="text-text-secondary mb-6 max-w-sm mx-auto">
                                Get started by adding your first product to monitor its Answer Engine Optimization performance.
                            </p>
                            <button
                                onClick={() => setIsCreateModalOpen(true)}
                                className="px-6 py-2.5 bg-primary hover:bg-primary/90 text-white font-medium rounded-lg transition-colors"
                            >
                                Create Your First Product
                            </button>
                        </div>
                    ) : (
                        products.map((product) => (
                            <ProductCard
                                key={product.id}
                                product={product}
                                isEditing={editingProduct?.id === product.id}
                                onEdit={setEditingProduct}
                                onDelete={handleDelete}
                                onNavigate={(id) => navigate(`/dashboard/${id}`)}
                            />
                        ))
                    )}
                </div>

                {/* Create/Edit Modal Overlay */}
                {(isCreateModalOpen || editingProduct) && createPortal(
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
                        <div className="w-full max-w-2xl bg-surface rounded-2xl shadow-2xl overflow-hidden scale-100 animate-in zoom-in-95 duration-200 border border-border">
                            <ProductForm
                                initialData={editingProduct || undefined}
                                onSubmit={handleCreateOrUpdate}
                                onCancel={() => {
                                    setIsCreateModalOpen(false)
                                    setEditingProduct(null)
                                }}
                                isSubmitting={isSubmitting}
                            />
                        </div>
                    </div>,
                    document.body
                )}
            </div>
        </div>
    )
}
