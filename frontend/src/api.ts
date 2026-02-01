const API_BASE = '/api';

export const api = {
    auth: {
        login: async (username: string) => {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username })
            });
            if (!res.ok) throw new Error('Login failed');
            return res.json();
        }
    },
    products: {
        list: async (userId: string | number) => {
            const res = await fetch(`${API_BASE}/products?user_id=${userId}`);
            if (!res.ok) throw new Error('Failed to load products');
            return res.json();
        },
        create: async (userId: string | number, name: string, domain: string, defaultMode: 'fast' | 'rendered' = 'fast') => {
            const res = await fetch(`${API_BASE}/products`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, name, domain, default_mode: defaultMode })
            });
            if (!res.ok) throw new Error('Failed to create product');
            return res.json();
        },
        get: async (productId: string | number) => {
            const res = await fetch(`${API_BASE}/products/${productId}`);
            if (!res.ok) throw new Error('Failed to load product');
            return res.json();
        },
        getLatestScan: async (productId: string | number) => {
            const res = await fetch(`${API_BASE}/products/${productId}/latest-scan`);
            if (res.status === 404) return null;
            if (!res.ok) throw new Error('Failed to check for existing scans');
            return res.json();
        },
        delete: async (productId: string | number) => {
            const res = await fetch(`${API_BASE}/products/${productId}`, {
                method: 'DELETE'
            });
            if (!res.ok) throw new Error('Failed to delete product');
            return res.json();
        }
    },
    scan: {
        start: async (url: string, productId: string | number, mode: 'fast' | 'rendered' = 'fast') => {
            const res = await fetch(`${API_BASE}/scan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, product_id: productId, mode })
            });
            if (!res.ok) throw new Error('Scan failed to start');
            return res.json();
        },
        getStatus: async (jobId: string) => {
            const res = await fetch(`${API_BASE}/scan/${jobId}`);
            if (!res.ok) throw new Error('Failed to get status');
            return res.json();
        }
    }
};
