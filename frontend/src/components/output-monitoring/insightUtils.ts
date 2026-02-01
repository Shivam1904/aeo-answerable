
import { QueryResult } from './types'

export interface InsightData {
    sentimentScore: number // 0 to 100
    sentimentLabel: 'Positive' | 'Neutral' | 'Negative' | 'Mixed'
    competitors: string[]
    keyThemes: string[]
}

const POSITIVE_WORDS = ['best', 'good', 'great', 'excellent', 'top', 'leading', 'reliable', 'recommended', 'trustworthy', 'popular', 'highly', 'benefit', 'advantage']
const NEGATIVE_WORDS = ['avoid', 'bad', 'poor', 'expensive', 'slow', 'unreliable', 'issue', 'problem', 'flaw', 'worst', 'complaint']

export function analyzeSentiment(text: string): { score: number; label: InsightData['sentimentLabel'] } {
    const lower = text.toLowerCase()
    let score = 50 // Start neutral

    POSITIVE_WORDS.forEach(w => {
        if (lower.includes(w)) score += 5
    })

    NEGATIVE_WORDS.forEach(w => {
        if (lower.includes(w)) score -= 5
    })

    // Clamp
    score = Math.max(0, Math.min(100, score))

    let label: InsightData['sentimentLabel'] = 'Neutral'
    if (score > 60) label = 'Positive'
    else if (score < 40) label = 'Negative'
    else label = 'Mixed'

    return { score, label }
}

export function extractCompetitors(text: string): string[] {
    // Very naive extraction: looks for Capitalized words after "vs", "like", "alternative to"
    // In a real app, this would be backend NLP.
    const lower = text.toLowerCase()
    const competitors = new Set<string>()

    // Mock list of common tech competitors to check for
    const COMMON_BRANDS = ['Salesforce', 'HubSpot', 'Zoho', 'Microsoft', 'Google', 'Slack', 'Teams', 'Zoom', 'Notion', 'Asana', 'Monday', 'Trello', 'Jira', 'Linear']

    COMMON_BRANDS.forEach(brand => {
        if (text.includes(brand)) {
            competitors.add(brand)
        }
    })

    return Array.from(competitors).slice(0, 5) // Limit to 5
}

export function extractThemes(text: string): string[] {
    const themes = new Set<string>()
    const lower = text.toLowerCase()

    if (lower.includes('price') || lower.includes('cost') || lower.includes('expensive') || lower.includes('cheap')) themes.add('Pricing')
    if (lower.includes('feature') || lower.includes('capabilities')) themes.add('Features')
    if (lower.includes('support') || lower.includes('service')) themes.add('Support')
    if (lower.includes('easy') || lower.includes('ui') || lower.includes('ux') || lower.includes('user friendly')) themes.add('Usability')
    if (lower.includes('integrate') || lower.includes('api')) themes.add('Integration')

    return Array.from(themes)
}

export function aggregateInsights(results: QueryResult[]): InsightData {
    let totalScore = 0
    const allCompetitors = new Set<string>()
    const allThemes = new Set<string>()

    results.forEach(r => {
        const sentiment = analyzeSentiment(r.response)
        totalScore += sentiment.score

        extractCompetitors(r.response).forEach(c => allCompetitors.add(c))
        extractThemes(r.response).forEach(t => allThemes.add(t))
    })

    const avgScore = results.length > 0 ? Math.round(totalScore / results.length) : 50

    let label: InsightData['sentimentLabel'] = 'Neutral'
    if (avgScore > 65) label = 'Positive'
    else if (avgScore < 35) label = 'Negative'
    else label = 'Neutral' // Simplification for aggregate

    return {
        sentimentScore: avgScore,
        sentimentLabel: label,
        competitors: Array.from(allCompetitors),
        keyThemes: Array.from(allThemes)
    }
}
