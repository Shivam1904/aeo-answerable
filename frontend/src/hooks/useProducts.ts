import { useState, useCallback } from 'react'
import { api } from '../api'
import { Product } from '../types'

export function useProducts(userId: number | null) {
    const [products, setProducts] = useState<Product[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const loadProducts = useCallback(async () => {
        if (!userId) return
        try {
            setIsLoading(true)
            const data = await api.products.list(userId)
            setProducts(data)
            setError(null)
        } catch (err: any) {
            setError(err.message || 'Failed to load products')
            console.error(err)
        } finally {
            setIsLoading(false)
        }
    }, [userId])

    const createProduct = async (
        name: string,
        domain: string,
        defaultMode: 'fast' | 'rendered',
        profile: {
            business_bio?: string
            target_region?: string
            target_audience_age?: string
            gender_preference?: string
        }
    ) => {
        if (!userId) return null
        try {
            const data = await api.products.create(userId, name, domain, defaultMode, profile)
            await loadProducts()
            return data
        } catch (err: any) {
            setError(err.message || 'Failed to create product')
            console.error(err)
            return null
        }
    }

    const updateProduct = async (id: number, data: Partial<Product>) => {
        try {
            await api.products.update(id, data)
            await loadProducts()
            return true
        } catch (err: any) {
            setError(err.message || 'Failed to update product')
            console.error(err)
            return false
        }
    }

    const deleteProduct = async (id: number) => {
        try {
            await api.products.delete(id)
            setProducts(prev => prev.filter(p => p.id !== id))
            // Ensure we are fully synced, though local filter is fast
            await loadProducts()
            return true
        } catch (err: any) {
            setError(err.message || 'Failed to delete product')
            console.error(err)
            return false
        }
    }

    return {
        products,
        isLoading,
        error,
        loadProducts,
        createProduct,
        updateProduct,
        deleteProduct
    }
}
