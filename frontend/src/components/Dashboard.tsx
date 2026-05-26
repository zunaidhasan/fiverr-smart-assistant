import React, { useState, useEffect } from 'react'
import { getDashboardMetrics } from '../api/client'
import { DashboardMetrics } from '../types'
import {
  BarChart3,
  Loader2,
  AlertCircle,
  RefreshCw,
  PieChart,
  Activity,
  Globe,
  Zap,
  Award,
  Layers,
  Target,
  Tag,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart as RePieChart, Pie, Cell,
} from 'recharts'

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#6366f1', '#14b8a6', '#d946ef']

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadMetrics()
  }, [])

  const loadMetrics = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getDashboardMetrics()
      setMetrics(data)
    } catch (err) {
      setError('Failed to load dashboard metrics.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="card p-12 text-center">
        <Loader2 size={40} className="animate-spin text-primary-600 mx-auto mb-4" />
        <p className="text-gray-500 text-sm">Loading dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card p-12 text-center">
        <AlertCircle size={40} className="text-danger-500 mx-auto mb-4" />
        <p className="text-gray-500">{error}</p>
        <button onClick={loadMetrics} className="btn-primary mt-4">
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    )
  }

  if (!metrics) return null

  // Prepare pie chart data
  const categoryPieData = metrics.projects_by_category.map((c) => ({
    name: c.category,
    value: c.count,
  }))

  const formatCurrency = (val: number) => `$${val.toLocaleString()}`

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Portfolio Intelligence Dashboard</h2>
          <p className="text-sm text-gray-500">
            Analytics from {metrics.total_projects} projects across {metrics.categories.length} categories
          </p>
        </div>
        <button onClick={loadMetrics} className="btn-secondary text-xs">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Globe size={16} className="text-primary-500" />
            Total Projects
          </div>
          <p className="text-2xl font-bold text-gray-900">{metrics.total_projects}</p>
          <p className="text-xs text-gray-400">in portfolio database</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Layers size={16} className="text-accent-500" />
            Categories
          </div>
          <p className="text-2xl font-bold text-gray-900">{metrics.categories.length}</p>
          <p className="text-xs text-gray-400">project categories</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Award size={16} className="text-warning-500" />
            High Quality
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {metrics.quality_distribution.find((q) => q.quality.toLowerCase() === 'high')?.count || 0}
          </p>
          <p className="text-xs text-gray-400">
            {metrics.quality_distribution.length > 0
              ? `${((metrics.quality_distribution.find((q) => q.quality.toLowerCase() === 'high')?.count || 0) / metrics.total_projects * 100).toFixed(0)}% of total`
              : 'projects'}
          </p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Target size={16} className="text-violet-500" />
            Avg Match Score
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {metrics.match_score_distribution.length > 0
              ? (metrics.match_score_distribution.reduce((a, s) => a + s.score * s.count, 0) / metrics.total_projects).toFixed(0)
              : 'N/A'}
          </p>
          <p className="text-xs text-gray-400">out of 100</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Zap size={16} className="text-cyan-500" />
            Technologies
          </div>
          <p className="text-2xl font-bold text-gray-900">{metrics.technology_distribution.length}</p>
          <p className="text-xs text-gray-400">unique tech stacks</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Tag size={16} className="text-orange-500" />
            Features
          </div>
          <p className="text-2xl font-bold text-gray-900">{metrics.feature_popularity.length}</p>
          <p className="text-xs text-gray-400">unique features</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Activity size={16} className="text-primary-500" />
            Best Niche
          </div>
          <p className="text-lg font-bold text-gray-900 truncate">
            {metrics.best_paying_niches[0]?.category || 'N/A'}
          </p>
          <p className="text-xs text-gray-400">
            {metrics.best_paying_niches[0]
              ? `${metrics.best_paying_niches[0].count} projects`
              : ''}
          </p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <BarChart3 size={16} className="text-accent-500" />
            Largest Category
          </div>
          <p className="text-lg font-bold text-gray-900 truncate">
            {metrics.projects_by_category[0]?.category || 'N/A'}
          </p>
          <p className="text-xs text-gray-400">
            {metrics.projects_by_category[0]
              ? `${metrics.projects_by_category[0].count} projects`
              : ''}
          </p>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Projects by Category */}
        <div className="card">
          <div className="card-header flex items-center gap-2">
            <BarChart3 size={18} className="text-primary-600" />
            <h3 className="font-semibold text-gray-900">Projects by Category</h3>
          </div>
          <div className="card-body">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics.projects_by_category}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="category" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v: number) => [v, 'Projects']} />
                  <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Category Distribution */}
        <div className="card">
          <div className="card-header flex items-center gap-2">
            <PieChart size={18} className="text-primary-600" />
            <h3 className="font-semibold text-gray-900">Category Distribution</h3>
          </div>
          <div className="card-body">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <RePieChart>
                  <Pie
                    data={categoryPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {categoryPieData.map((_, idx) => (
                      <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => [v, 'Projects']} />
                </RePieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Technology Distribution */}
        <div className="card">
          <div className="card-header flex items-center gap-2">
            <Zap size={18} className="text-accent-600" />
            <h3 className="font-semibold text-gray-900">Top Technologies</h3>
          </div>
          <div className="card-body">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={metrics.technology_distribution.slice(0, 10)}
                  layout="vertical"
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis
                    dataKey="technology"
                    type="category"
                    tick={{ fontSize: 10 }}
                    width={100}
                  />
                  <Tooltip formatter={(v: number) => [v, 'Projects']} />
                  <Bar dataKey="count" fill="#22c55e" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Quality Distribution */}
        <div className="card">
          <div className="card-header flex items-center gap-2">
            <Award size={18} className="text-primary-600" />
            <h3 className="font-semibold text-gray-900">Quality Distribution</h3>
          </div>
          <div className="card-body">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics.quality_distribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="quality" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v: number) => [v, 'Projects']} />
                  <Bar
                    dataKey="count"
                    radius={[6, 6, 0, 0]}
                    fill="#8b5cf6"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Best Paying Niches & Match Score Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header flex items-center gap-2">
            <Target size={18} className="text-accent-600" />
            <h3 className="font-semibold text-gray-900">Best Paying Niches (by Category)</h3>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              {metrics.best_paying_niches.map((n, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-xs font-bold">
                      {i + 1}
                    </span>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{n.category}</p>
                      <p className="text-xs text-gray-500">{n.count} projects</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-gray-900">
                      {n.estimated_budget_range ? formatCurrency(n.estimated_budget_range.average) : 'N/A'}
                    </p>
                    <p className="text-xs text-gray-400">avg budget</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header flex items-center gap-2">
            <Layers size={18} className="text-primary-600" />
            <h3 className="font-semibold text-gray-900">Technologies per Category</h3>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              {metrics.projects_by_category.slice(0, 6).map((cat, i) => (
                <div key={i} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-gray-900">{cat.category}</p>
                    <span className="text-xs text-gray-500">{cat.count} projects</span>
                  </div>
                  {cat.technologies && cat.technologies.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {cat.technologies.map((tech, j) => (
                        <span key={j} className="px-2 py-0.5 bg-white border border-gray-200 text-gray-600 rounded text-xs">
                          {tech}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Feature Popularity */}
      <div className="card">
        <div className="card-header flex items-center gap-2">
          <Tag size={18} className="text-accent-600" />
          <h3 className="font-semibold text-gray-900">Most Popular Features</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {metrics.feature_popularity.slice(0, 12).map((feat, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2 min-w-0">
                  <Tag size={12} className="text-gray-400 shrink-0" />
                  <span className="text-sm text-gray-700 truncate">{feat.feature}</span>
                </div>
                <div className="flex items-center gap-2 shrink-0 ml-2">
                  <span className="text-sm font-bold text-gray-900">{feat.count}</span>
                  <span className="text-xs text-gray-400">({feat.percentage}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
