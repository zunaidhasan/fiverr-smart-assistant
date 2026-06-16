// In dev, Vite proxies /api to localhost:8000.
// In production (Vercel), set VITE_API_URL to the Render backend URL, e.g.:
//   VITE_API_URL=https://sardarit-portfolio-api.onrender.com
const VITE_API = import.meta.env.VITE_API_URL;
const API_BASE = VITE_API ? (VITE_API.endsWith('/api') ? VITE_API : `${VITE_API.replace(/\/$/, '')}/api`) : '/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const isFormData = options?.body instanceof FormData
  const { headers: customHeaders, ...restOptions } = options || {}

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...restOptions,
    headers: {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...customHeaders,
    },
  })

  if (!res.ok) {
    const error = await res.text()
    throw new Error(error || `Request failed: ${res.statusText}`)
  }

  return res.json()
}

// CSV
export const checkCsvStatus = () =>
  request<{
    loaded: boolean
    project_count: number
    categories: string[]
    total_in_database: number
    high_quality: number
    top_recommended: string[]
  }>('/csv/status')

export const uploadCsv = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request<{
    message: string
    project_count: number
    categories: string[]
    total_projects_in_database: number
  }>('/csv/upload', {
    method: 'POST',
    body: formData,
  })
}

// Smart Reply
export const generateReply = (data: {
  client_message: string
  situation_type?: string
  category?: string
}) =>
  request<import('../types').SmartReplyResponse>('/reply/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  })

export const listTemplates = () =>
  request<{
    templates: import('../types').Template[]
    situation_types: string[]
    tones: Record<string, string>
  }>('/reply/templates')

export const detectSituation = (message: string) =>
  request<{ situation_type: string }>(
    `/reply/detect-situation?message=${encodeURIComponent(message)}`
  )

// Similarity
export const searchSimilar = (data: {
  client_brief: string
  top_k?: number
}) =>
  request<import('../types').SimilaritySearchResponse>(
    '/similarity/search',
    { method: 'POST', body: JSON.stringify(data) }
  )

// Proposal Optimizer
export const optimizeProposal = (data: {
  client_brief: string
  category?: string
  budget?: number
}) =>
  request<import('../types').ProposalOptimizerResponse>(
    '/proposal/optimize',
    { method: 'POST', body: JSON.stringify(data) }
  )

// Risk Detector
export const analyzeRisk = (data: {
  buyer_message: string
  budget?: number
  category?: string
}) =>
  request<import('../types').RiskDetectorResponse>('/risk/analyze', {
    method: 'POST',
    body: JSON.stringify(data),
  })

// Dashboard
export const getDashboardMetrics = () =>
  request<import('../types').DashboardMetrics>('/dashboard/metrics')

// CRM
export const getCRM = () =>
  request<import('../types').CRMResponse>('/crm')

// Projects
export const listProjects = (params?: {
  category?: string
  technology?: string
  min_match_score?: number
  limit?: number
}) => {
  const searchParams = new URLSearchParams()
  if (params?.category) searchParams.set('category', params.category)
  if (params?.technology) searchParams.set('technology', params.technology)
  if (params?.min_match_score !== undefined)
    searchParams.set('min_match_score', String(params.min_match_score))
  if (params?.limit) searchParams.set('limit', String(params.limit))
  const query = searchParams.toString()
  return request<{
    projects: import('../types').SardarProject[]
    total: number
    returned: number
  }>(`/projects${query ? `?${query}` : ''}`)
}

export const getProjectCategories = () =>
  request<{
    categories: {
      category: string
      count: number
      technologies: string[]
      high_quality_count: number
    }[]
  }>('/projects/categories')

// Health
export const healthCheck = () =>
  request<{
    status: string
    csv_loaded: boolean
    project_count: number
    version: string
  }>('/health')
