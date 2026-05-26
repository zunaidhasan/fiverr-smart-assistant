export interface SardarProject {
  id: string
  title: string
  url: string
  category: string
  technology: string
  stack: string
  features: string
  description: string
  match_score: number
  quality: string
}

export interface SmartReplyRequest {
  client_message: string
  situation_type?: string
  category?: string
}

export interface SmartReplyResponse {
  draft_reply: string
  relevant_past_projects: SimilarProject[]
  suggested_tone: string
  questions_to_ask: string[]
  estimated_quote_range: {
    min: number
    max: number
    currency: string
    confidence: boolean
  }
  confidence_score: number
}

export interface SimilarProject {
  project_id: string
  title: string
  url: string
  category: string
  technology: string
  stack_used: string
  description: string
  match_score: number
  similarity_score: number
  quality: string
}

export interface SimilaritySearchRequest {
  client_brief: string
  top_k?: number
}

export interface SimilaritySearchResponse {
  similar_projects: SimilarProjectDetailed[]
  query_summary: string
  total_matches: number
}

export interface SimilarProjectDetailed {
  project_id: string
  title: string
  url: string
  category: string
  technology: string
  stack_used: string
  description: string
  features: string
  use_case: string
  strengths: string
  match_score: number
  quality: string
  similarity_score: number
}

export interface ProposalOptimizerRequest {
  client_brief: string
  category?: string
  budget?: number
}

export interface ProposalOptimizerResponse {
  portfolio_examples: {
    title: string
    url: string
    category: string
    technology: string
    stack: string
    description: string
    strengths: string
    match_score: number
    relevance_score: number
  }[]
  relevant_experience: string[]
  risk_signals: string[]
  questions_to_ask: string[]
  recommended_structure: string[]
  suggested_quote_range: {
    min: number
    max: number
    currency: string
  }
  estimated_timeline: string
}

export interface RiskDetectorRequest {
  buyer_message: string
  budget?: number
  category?: string
}

export interface RiskDetectorResponse {
  risk_score: number
  red_flags: RedFlag[]
  scope_creep_probability: number
  vague_requirements: boolean
  urgency_signals: boolean
  budget_mismatch: BudgetMismatch | null
  recommendations: string[]
}

export interface RedFlag {
  type: string
  severity: 'high' | 'medium' | 'low'
  description: string
  details: string
}

export interface BudgetMismatch {
  client_budget: number
  category_average: number
  ratio: number
  severity: string
  description: string
}

export interface DashboardMetrics {
  total_projects: number
  categories: string[]
  projects_by_category: CategoryInfo[]
  technology_distribution: TechCount[]
  feature_popularity: FeatureCount[]
  best_paying_niches: CategoryInfo[]
  quality_distribution: QualityBucket[]
  match_score_distribution: ScoreBucket[]
}

export interface CategoryInfo {
  category: string
  count: number
  technologies: string[]
  estimated_budget_range: {
    min: number
    max: number
    average: number
  }
}

export interface TechCount {
  technology: string
  count: number
  percentage: number
}

export interface FeatureCount {
  feature: string
  count: number
  percentage: number
}

export interface QualityBucket {
  quality: string
  count: number
}

export interface ScoreBucket {
  score: number
  count: number
}

export interface CRMEntry {
  id: string
  project_url: string
  category: string
  main_technology: string
  use_case: string
  best_for: string
  match_score: number
  keywords: string
  strengths: string
  risk_flags: string[]
}

export interface CRMResponse {
  entries: CRMEntry[]
  total_count: number
  categories: string[]
  technology_diversity: number
}

export interface Template {
  name: string
  situation_type: string
  tone: string
  strength: number
}

export interface CsvStatus {
  loaded: boolean
  project_count: number
  categories: string[]
  total_in_database: number
  high_quality: number
  top_recommended: string[]
}

export type Tab = 'smart-reply' | 'similarity' | 'proposal' | 'risk' | 'dashboard' | 'crm'
