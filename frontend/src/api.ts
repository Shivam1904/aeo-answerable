const API_BASE = '/api';

class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

async function fetchClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const { headers, ...customConfig } = options;

    const config: RequestInit = {
        method: options.method || 'GET',
        headers: {
            'Content-Type': 'application/json',
            ...(headers as Record<string, string>),
        },
        ...customConfig,
    };

    const response = await fetch(`${API_BASE}${endpoint}`, config);

    if (response.status === 404) {
        return null as unknown as T; // Handle 404s gracefully where expected
    }

    if (!response.ok) {
        throw new ApiError(response.status, `API Error: ${response.statusText}`);
    }

    // Handle empty responses (e.g. 204 No Content)
    if (response.status === 204) {
        return {} as T;
    }

    return response.json();
}

export const api = {
    auth: {
        login: (username: string) =>
            fetchClient('/auth/login', { method: 'POST', body: JSON.stringify({ username }) })
    },
    products: {
        list: (userId: string | number) =>
            fetchClient(`/products?user_id=${userId}`),

        create: (
            userId: string | number,
            name: string,
            domain: string,
            defaultMode: 'fast' | 'rendered' = 'fast',
            profile?: {
                business_bio?: string
                target_region?: string
                target_audience_age?: string
                gender_preference?: string
            }
        ) => fetchClient('/products', {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                name,
                domain,
                default_mode: defaultMode,
                ...profile
            })
        }),

        get: (productId: string | number) =>
            fetchClient(`/products/${productId}`),

        update: (productId: string | number, data: any) =>
            fetchClient(`/products/${productId}`, { method: 'PUT', body: JSON.stringify(data) }),

        getLatestScan: (productId: string | number) =>
            fetchClient(`/products/${productId}/latest-scan`),

        delete: (productId: string | number) =>
            fetchClient(`/products/${productId}`, { method: 'DELETE' })
    },
    scan: {
        start: (url: string, productId: string | number, mode: 'fast' | 'rendered' = 'fast') =>
            fetchClient('/scan', {
                method: 'POST',
                body: JSON.stringify({ url, product_id: productId, mode })
            }),

        getStatus: (jobId: string) =>
            fetchClient(`/scan/${jobId}`)
    },
    monitoring: {
        analyze: (targetUrl: string, pageContent?: string, productId?: string | number): Promise<AnalysisResponse> =>
            fetchClient('/output-monitoring/analyze', {
                method: 'POST',
                body: JSON.stringify({ target_url: targetUrl, page_content: pageContent, product_id: productId })
            }),

        query: (query: string, targetUrl: string, engines: string[], brandProfile?: any, productId?: string | number): Promise<MultiEngineResponse> =>
            fetchClient('/output-monitoring/query', {
                method: 'POST',
                body: JSON.stringify({
                    query,
                    target_url: targetUrl,
                    engines,
                    brand_profile: brandProfile,
                    product_id: productId
                })
            }),

        getHistory: (productId?: string | number) =>
            fetchClient(`/output-monitoring/history${productId ? `?product_id=${productId}` : ''}`),

        getHistoryDetails: (query: string) =>
            fetchClient(`/output-monitoring/history/details?query=${encodeURIComponent(query)}`),

        deleteHistory: (query: string) =>
            fetchClient(`/output-monitoring/history/delete?query=${encodeURIComponent(query)}`, { method: 'DELETE' }),

        getBudget: () =>
            fetchClient('/output-monitoring/budget'),

        getEngines: () =>
            fetchClient('/output-monitoring/engines'),

        getSimilarCompanies: (productId: string | number) =>
            fetchClient(`/output-monitoring/competitors?product_id=${productId}`),

        refreshCompetitors: (productId: string | number) =>
            fetchClient('/output-monitoring/competitors/refresh', {
                method: 'POST',
                body: JSON.stringify({ product_id: productId })
            }),

        refreshQueries: (productId: string | number) =>
            fetchClient('/output-monitoring/queries/refresh', {
                method: 'POST',
                body: JSON.stringify({ product_id: productId })
            })
    }
};


export interface BrandProfile {
    brand_name: string
    industry: string
    tagline?: string
    target_audience: string[]
    key_value_props: string[]
    primary_competitors: string[]
    industry_baseline_sentiment: number
}

export interface AnalysisResponse {
    profile: BrandProfile
    suggested_queries: {
        query: string
        type: string
        priority: number
        description?: string
    }[]
}

export interface Citation {
    url: string
    snippet: string
}

export interface EngineResult {
    engine: string
    response: string
    citations: Citation[]
    cost_usd: number
    latency_ms: number
    tokens_used: number
}

export interface MultiEngineResponse {
    query: string
    results: EngineResult[]
    total_cost_usd: number
    citation_rate: number
    sota_insights?: Record<string, any>
}

