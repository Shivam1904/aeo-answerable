import { Product, MultiEngineResponse } from './types'

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
        login: (username: string): Promise<{ user_id: number; username: string }> =>
            fetchClient('/auth/login', { method: 'POST', body: JSON.stringify({ username }) })
    },
    products: {
        list: (userId: string | number): Promise<Product[]> =>
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
        ): Promise<Product> => fetchClient('/products', {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                name,
                domain,
                default_mode: defaultMode,
                ...profile
            })
        }),

        get: (productId: string | number): Promise<Product> =>
            fetchClient(`/products/${productId}`),

        update: (productId: string | number, data: any): Promise<Product> =>
            fetchClient(`/products/${productId}`, { method: 'PUT', body: JSON.stringify(data) }),

        getLatestScan: (productId: string | number): Promise<{ found: boolean; status?: string; job_id?: string; result?: any; timestamp?: string }> =>
            fetchClient(`/products/${productId}/latest-scan`),

        delete: (productId: string | number): Promise<{ success: boolean }> =>
            fetchClient(`/products/${productId}`, { method: 'DELETE' })
    },
    scan: {
        start: (url: string, productId: string | number, mode: 'fast' | 'rendered' = 'fast'): Promise<{ job_id: string }> =>
            fetchClient('/scan', {
                method: 'POST',
                body: JSON.stringify({ url, product_id: productId, mode })
            }),

        getStatus: (jobId: string): Promise<{ status: string; result?: any; error?: string; timestamp?: string }> =>
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

        getHistory: (productId?: string | number): Promise<any> =>
            fetchClient(`/output-monitoring/history${productId ? `?product_id=${productId}` : ''}`),

        getHistoryDetails: (query: string): Promise<any> =>
            fetchClient(`/output-monitoring/history/details?query=${encodeURIComponent(query)}`),

        deleteHistory: (query: string): Promise<any> =>
            fetchClient(`/output-monitoring/history/delete?query=${encodeURIComponent(query)}`, { method: 'DELETE' }),

        getBudget: (): Promise<any> =>
            fetchClient('/output-monitoring/budget'),

        getEngines: (): Promise<any> =>
            fetchClient('/output-monitoring/engines'),

        getSimilarCompanies: (productId: string | number): Promise<any> =>
            fetchClient(`/output-monitoring/competitors?product_id=${productId}`),

        refreshCompetitors: (productId: string | number): Promise<any> =>
            fetchClient('/output-monitoring/competitors/refresh', {
                method: 'POST',
                body: JSON.stringify({ product_id: productId })
            }),

        refreshQueries: (productId: string | number): Promise<any> =>
            fetchClient('/output-monitoring/queries/refresh', {
                method: 'POST',
                body: JSON.stringify({ product_id: productId })
            }),

        competitiveQuery: (query: string, targetUrls: string[], engines: string[], productId?: string | number): Promise<CompetitiveResponse> =>
            fetchClient('/output-monitoring/competitive-query', {
                method: 'POST',
                body: JSON.stringify({
                    query,
                    target_urls: targetUrls,
                    engines,
                    product_id: productId
                })
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

export interface CompetitiveResponse {
    query: string
    comparison: Array<{
        url: string
        results: any[]
        engines_cited: number
        citation_rate: number
        share_of_voice: number
    }>
    total_engines: number
    action_plan?: Array<{
        type: string
        priority: 'high' | 'medium' | 'low'
        title: string
        description: string
        fix_action: string
    }>
}
