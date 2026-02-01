import { createContext, useContext, ReactNode } from 'react'
import { MetricResult } from '../components/results/config'

// --- Types (Reused) ---
export interface PageData {
    url: string
    title: string
    page_score?: number
    metrics?: Record<string, MetricResult>
    audits: {
        structure: { score: number }
        clarity: { score: number }
    }
}

export interface ReportData {
    summary: {
        scanned_count: number
        errors: number
    }
    pages: PageData[]
}

interface ReportContextType {
    data: ReportData | null
    status: 'loading' | 'complete' | 'error'
    error: string
    hostname: string
}

const ReportContext = createContext<ReportContextType | undefined>(undefined)

export function useReport() {
    const context = useContext(ReportContext)
    if (!context) {
        throw new Error('useReport must be used within a ReportProvider')
    }
    return context
}

export function ReportProvider({
    children,
    value
}: {
    children: ReactNode,
    value: ReportContextType
}) {
    return (
        <ReportContext.Provider value={value}>
            {children}
        </ReportContext.Provider>
    )
}
