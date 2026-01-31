import {
    Layers, FileText, BarChart2, FileCode2, ExternalLink,
    Check, TrendingUp, Hash, List, Clock, User, Link2,
    Shield, Search, type LucideIcon
} from 'lucide-react'

// --- Types ---
export interface MetricResult {
    metric: string
    score: number
    weight: number
    [key: string]: any
}

export interface MetricConfig {
    label: string
    icon: LucideIcon
    category: string
    description: string
}

export const CATEGORY_CONFIG = {
    structure: { label: 'Structure', icon: Layers, description: 'HTML hierarchy and DOM efficiency.' },
    content: { label: 'Content', icon: FileText, description: 'Relevance, clarity, and answerability.' },
    retrieval: { label: 'Retrieval', icon: Search, description: 'How easily engines parse chunks.' },
    schema: { label: 'Schema', icon: FileCode2, description: 'structured data entity mapping.' },
    trust: { label: 'Trust', icon: Shield, description: 'E-E-A-T signals and transparency.' },
} as const

export const METRIC_CONFIG: Record<string, MetricConfig> = {
    dom_to_token_ratio: {
        label: 'DOM Efficiency',
        icon: Hash,
        category: 'structure',
        description: 'Ratio of content to HTML tags. Higher is better for crawling budget.'
    },
    main_content_detectability: {
        label: 'Content Detection',
        icon: FileText,
        category: 'structure',
        description: 'How easily the main answer is identified amidst boilerplate.'
    },
    semantic_tree_depth: {
        label: 'Tree Depth',
        icon: Layers,
        category: 'structure',
        description: 'Logical nesting of HTML elements.'
    },
    heading_hierarchy_validity: {
        label: 'Heading Hierarchy',
        icon: List,
        category: 'structure',
        description: 'Correct use of H1-H6 tags for document outline.'
    },
    heading_predictive_power: {
        label: 'Heading Quality',
        icon: TrendingUp,
        category: 'content',
        description: 'Do headings accurately describe the content below them?'
    },
    liftable_units_density: {
        label: 'Liftable Units',
        icon: BarChart2,
        category: 'content',
        description: 'Sections of text that make sense independently.'
    },
    answer_first_compliance: {
        label: 'Answer-First',
        icon: Check,
        category: 'content',
        description: 'Is the answer provided immediately after the question?'
    },
    anaphora_resolution: {
        label: 'Pronoun Clarity',
        icon: User,
        category: 'content',
        description: 'Use of specific nouns instead of vague pronouns (it, they).'
    },
    chunk_boundary_integrity: {
        label: 'Chunk Quality',
        icon: Layers,
        category: 'retrieval',
        description: 'Do logical sections strictly respect sentence/paragraph boundaries?'
    },
    duplicate_boilerplate_rate: {
        label: 'Uniqueness',
        icon: FileText,
        category: 'retrieval',
        description: 'Percentage of non-unique, repetitive content.'
    },
    entity_schema_mapping: {
        label: 'Entity Mapping',
        icon: Link2,
        category: 'schema',
        description: 'Alignment between on-page entities and Schema.org types.'
    },
    schema_coverage_by_intent: {
        label: 'Schema Match',
        icon: FileCode2,
        category: 'schema',
        description: 'Coverage of expected schema types for the page intent.'
    },
    schema_quality_relationships: {
        label: 'Schema Depth',
        icon: Layers,
        category: 'schema',
        description: 'Use of @id to link related schema entities.'
    },
    citation_source_density: {
        label: 'Citations',
        icon: ExternalLink,
        category: 'trust',
        description: 'Presence of authoritative external links.'
    },
    freshness_signal_strength: {
        label: 'Freshness',
        icon: Clock,
        category: 'trust',
        description: 'Dates and update signals visible to crawlers.'
    },
    author_eeat_signals: {
        label: 'E-E-A-T',
        icon: User,
        category: 'trust',
        description: 'Clear authorship and expertise indicators.'
    },
}
