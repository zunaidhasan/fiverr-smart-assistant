import React, { useState } from 'react'
import { searchSimilar } from '../api/client'
import { SimilaritySearchResponse } from '../types'
import {
  Search,
  Loader2,
  AlertCircle,
  TrendingUp,
  Globe,
  Zap,
  Award,
  Tag,
  Target,
  Layers,
  ChevronRight,
  ExternalLink,
} from 'lucide-react'

export default function SimilaritySearch() {
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SimilaritySearchResponse | null>(null)

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await searchSimilar({ client_brief: query, top_k: topK })
      setResult(res)
    } catch (err) {
      setError('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getQualityBadge = (quality: string) => {
    switch (quality?.toLowerCase()) {
      case 'high':
        return <span className="badge-success"><Award size={12} /> High Quality</span>
      case 'medium':
        return <span className="badge-warning"><Award size={12} /> Medium</span>
      default:
        return <span className="badge-info">{quality}</span>
    }
  }

  return (
    <div className="space-y-6">
      {/* Search Input */}
      <div className="card">
        <div className="card-header flex items-center gap-2">
          <Search size={20} className="text-primary-600" />
          <h2 className="font-semibold text-gray-900">Portfolio Similarity Search</h2>
        </div>
        <div className="card-body space-y-4">
          <p className="text-sm text-gray-500">
            Describe the project you need — find similar projects from the SardarIT portfolio database of 566+ web development projects.
          </p>

          <textarea
            placeholder="Describe the project or paste the buyer's brief..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={5}
            className="input-field resize-none"
          />

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-xs text-gray-500">Top results:</label>
              <select
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="select-field w-20"
              >
                {[3, 5, 10, 15].map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </div>

            <button onClick={handleSearch} className="btn-primary" disabled={!query.trim() || loading}>
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
              {loading ? 'Searching...' : 'Search Similar Projects'}
            </button>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-sm text-danger-600 bg-danger-50 px-3 py-2 rounded-lg">
              <AlertCircle size={14} />
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {result && (
        <>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">{result.query_summary}</p>
          </div>

          {result.similar_projects.length === 0 ? (
            <div className="card p-12 text-center">
              <Search size={40} className="mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500">No similar projects found. Try a different description.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {result.similar_projects.map((proj) => (
                <div key={proj.project_id} className="card hover:shadow-md transition-all duration-200 animate-slide-up">
                  <div className="card-body">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <Globe size={16} className="text-primary-500" />
                          <h3 className="font-semibold text-gray-900">{proj.title}</h3>
                          {proj.url && (
                            <a
                              href={proj.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-gray-300 hover:text-primary-500 transition-colors"
                            >
                              <ExternalLink size={14} />
                            </a>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {proj.category}
                          {proj.use_case ? ` › ${proj.use_case}` : ''}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {proj.quality && getQualityBadge(proj.quality)}
                        <span className="text-xs font-semibold text-primary-600 bg-primary-50 px-2 py-1 rounded-full">
                          {(proj.similarity_score * 100).toFixed(0)}% match
                        </span>
                      </div>
                    </div>

                    {proj.description && (
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">{proj.description}</p>
                    )}

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      {proj.technology && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Zap size={14} className="text-gray-400" />
                          <span className="truncate">{proj.technology}</span>
                        </div>
                      )}
                      {proj.stack_used && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Layers size={14} className="text-gray-400" />
                          <span className="truncate">{proj.stack_used}</span>
                        </div>
                      )}
                      {proj.match_score > 0 && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Target size={14} className="text-gray-400" />
                          <span>Score: {proj.match_score}</span>
                        </div>
                      )}
                      {proj.strengths && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <TrendingUp size={14} className="text-gray-400" />
                          <span className="truncate">{proj.strengths.slice(0, 30)}</span>
                        </div>
                      )}
                    </div>

                    {proj.features && (
                      <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-gray-100">
                        <Tag size={12} className="text-gray-400 mt-0.5" />
                        {proj.features.split(',').slice(0, 4).map((feat, i) => (
                          <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                            {feat.trim()}
                          </span>
                        ))}
                        {proj.features.split(',').length > 4 && (
                          <span className="text-xs text-gray-400">+{proj.features.split(',').length - 4} more</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
