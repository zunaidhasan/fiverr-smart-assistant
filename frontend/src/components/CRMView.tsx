import React, { useState, useEffect } from 'react'
import { getCRM } from '../api/client'
import { CRMResponse } from '../types'
import {
  Users,
  Loader2,
  AlertCircle,
  RefreshCw,
  Globe,
  Search,
  Filter,
  Zap,
  Award,
  Target,
  AlertTriangle,
  ExternalLink,
  Layers,
} from 'lucide-react'

export default function CRMView() {
  const [crmData, setCrmData] = useState<CRMResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')

  useEffect(() => {
    loadCRM()
  }, [])

  const loadCRM = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getCRM()
      setCrmData(data)
    } catch (err) {
      setError('Failed to load CRM data.')
    } finally {
      setLoading(false)
    }
  }

  const getQualityBadge = (matchScore: number) => {
    if (matchScore >= 80) return <span className="badge-success"><Award size={12} /> Top Match</span>
    if (matchScore >= 60) return <span className="badge-warning">Good Match</span>
    return <span className="badge-info">Standard</span>
  }

  const filteredEntries = (crmData?.entries || []).filter((entry) => {
    const matchesSearch =
      searchTerm === '' ||
      entry.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.main_technology.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.use_case.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.best_for.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.id.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesCategory = categoryFilter === 'all' || entry.category === categoryFilter

    return matchesSearch && matchesCategory
  })

  if (loading) {
    return (
      <div className="card p-12 text-center">
        <Loader2 size={40} className="animate-spin text-primary-600 mx-auto mb-4" />
        <p className="text-gray-500 text-sm">Loading portfolio CRM...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card p-12 text-center">
        <AlertCircle size={40} className="text-danger-500 mx-auto mb-4" />
        <p className="text-gray-500">{error}</p>
        <button onClick={loadCRM} className="btn-primary mt-4">
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    )
  }

  if (!crmData) return null

  return (
    <div className="space-y-6">
      {/* Summary Header */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <Globe size={16} className="text-primary-500" />
            Total Projects
          </div>
          <p className="text-2xl font-bold text-gray-900">{crmData.total_count}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <Layers size={16} className="text-warning-500" />
            Categories
          </div>
          <p className="text-2xl font-bold text-gray-900">{crmData.categories.length}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <Zap size={16} className="text-accent-500" />
            Tech Diversity
          </div>
          <p className="text-2xl font-bold text-gray-900">{crmData.technology_diversity}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <Target size={16} className="text-violet-500" />
            Avg Match Score
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {crmData.entries.length > 0
              ? `${(crmData.entries.reduce((a, e) => a + e.match_score, 0) / crmData.entries.length).toFixed(0)}`
              : 'N/A'}
          </p>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex-1 min-w-[250px] relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by category, technology, use case..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={16} className="text-gray-400" />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="select-field w-44"
          >
            <option value="all">All Categories</option>
            {crmData.categories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
        <button onClick={loadCRM} className="btn-secondary text-xs">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* CRM Table */}
      {filteredEntries.length === 0 ? (
        <div className="card p-12 text-center">
          <Users size={40} className="mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">No entries match your filters.</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Project URL</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Technology</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Match Score</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Use Case</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Best For</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Flags</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Strengths</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredEntries.slice(0, 100).map((entry) => (
                  <tr key={entry.id} className="hover:bg-gray-50 transition-colors duration-150">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        <Globe size={12} className="text-gray-400 shrink-0" />
                        <a
                          href={entry.project_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary-600 hover:text-primary-800 truncate max-w-[200px] block"
                          title={entry.project_url}
                        >
                          {entry.id.replace('https://', '').replace('http://', '').slice(0, 40)}
                        </a>
                        <ExternalLink size={10} className="text-gray-300 shrink-0" />
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="badge-info text-xs">{entry.category}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs text-gray-700">{entry.main_technology}</span>
                    </td>
                    <td className="px-4 py-3">
                      {getQualityBadge(entry.match_score)}
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-xs text-gray-600 max-w-[200px] truncate" title={entry.use_case}>
                        {entry.use_case || '-'}
                      </p>
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-xs text-gray-600 max-w-[150px] truncate" title={entry.best_for}>
                        {entry.best_for || '-'}
                      </p>
                    </td>
                    <td className="px-4 py-3">
                      {entry.risk_flags.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {entry.risk_flags.map((flag, i) => (
                            <span key={i} className="badge-danger text-xs flex items-center gap-1">
                              <AlertTriangle size={10} />
                              {flag}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">None</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-xs text-gray-500 max-w-[150px] truncate" title={entry.strengths}>
                        {entry.strengths || '-'}
                      </p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Footer */}
          <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
            <p className="text-xs text-gray-500">
              Showing {Math.min(filteredEntries.length, 100)} of {crmData.total_count} entries
              {filteredEntries.length > 100 ? ' (filter to see more)' : ''}
            </p>
            <div className="flex gap-4 text-xs text-gray-500">
              <span>Categories: <strong>{crmData.categories.length}</strong></span>
              <span>Tech stacks: <strong>{crmData.technology_diversity}</strong></span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
