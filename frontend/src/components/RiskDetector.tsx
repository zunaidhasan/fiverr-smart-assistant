import React, { useState } from 'react'
import { analyzeRisk } from '../api/client'
import { RiskDetectorResponse, RedFlag } from '../types'
import {
  AlertTriangle,
  Loader2,
  Shield,
  ShieldAlert,
  ShieldCheck,
  AlertCircle,
  TrendingUp,
  DollarSign,
  CheckCircle2,
  XCircle,
} from 'lucide-react'

export default function RiskDetector({ categories }: { categories: string[] }) {
  const [message, setMessage] = useState('')
  const [budget, setBudget] = useState('')
  const [category, setCategory] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<RiskDetectorResponse | null>(null)

  const handleAnalyze = async () => {
    if (!message.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await analyzeRisk({
        buyer_message: message,
        budget: budget ? Number(budget) : undefined,
        category: category || undefined,
      })
      setResult(res)
    } catch (err) {
      setError('Risk analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevel = (score: number) => {
    if (score >= 0.7) return { label: 'High Risk', color: 'text-danger-600', bg: 'bg-danger-50', icon: ShieldAlert }
    if (score >= 0.4) return { label: 'Medium Risk', color: 'text-warning-600', bg: 'bg-warning-50', icon: Shield }
    return { label: 'Low Risk', color: 'text-accent-600', bg: 'bg-accent-50', icon: ShieldCheck }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return { badge: 'badge-danger', bg: 'bg-danger-50 border-danger-200', text: 'text-danger-800' }
      case 'medium': return { badge: 'badge-warning', bg: 'bg-warning-50 border-warning-200', text: 'text-warning-800' }
      default: return { badge: 'badge-info', bg: 'bg-gray-50 border-gray-200', text: 'text-gray-700' }
    }
  }

  const riskLevel = result ? getRiskLevel(result.risk_score) : null
  const RiskIcon = riskLevel?.icon || Shield

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header flex items-center gap-2">
          <AlertTriangle size={20} className="text-danger-600" />
          <h2 className="font-semibold text-gray-900">Risk Detector</h2>
        </div>
        <div className="card-body space-y-4">
          <p className="text-sm text-gray-500">
            Analyze a buyer's message for red flags, scope creep signals, and risk factors.
          </p>

          <textarea
            placeholder="Paste the buyer's message for risk analysis..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={5}
            className="input-field resize-none"
          />

          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs font-medium text-gray-500 mb-1">Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="select-field">
                <option value="">Not specified</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            <div className="flex-1 min-w-[150px]">
              <label className="block text-xs font-medium text-gray-500 mb-1">Budget (optional)</label>
              <input
                type="number"
                placeholder="$"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="input-field"
              />
            </div>
          </div>

          <button onClick={handleAnalyze} className="btn-primary" disabled={!message.trim() || loading}>
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Shield size={16} />}
            {loading ? 'Analyzing...' : 'Analyze Risk'}
          </button>

          {error && (
            <div className="flex items-center gap-2 text-sm text-danger-600 bg-danger-50 px-3 py-2 rounded-lg">
              <AlertCircle size={14} />
              {error}
            </div>
          )}
        </div>
      </div>

      {result && (
        <div className="space-y-4 animate-slide-up">
          {/* Risk Score Overview */}
          <div className="card">
            <div className="card-body">
              <div className="flex items-center gap-4">
                <div className={`w-16 h-16 rounded-2xl ${riskLevel?.bg} flex items-center justify-center`}>
                  <RiskIcon size={32} className={riskLevel?.color} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-bold text-lg text-gray-900">{riskLevel?.label}</h3>
                    <span className={`badge ${result.risk_score >= 0.7 ? 'badge-danger' : result.risk_score >= 0.4 ? 'badge-warning' : 'badge-success'}`}>
                      Score: {(result.risk_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        result.risk_score >= 0.7 ? 'bg-danger-500' : result.risk_score >= 0.4 ? 'bg-warning-500' : 'bg-accent-500'
                      }`}
                      style={{ width: `${result.risk_score * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-4 mt-6">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-sm font-medium text-gray-700">
                    <TrendingUp size={14} />
                    Scope Creep
                  </div>
                  <p className="text-lg font-bold text-gray-900">{(result.scope_creep_probability * 100).toFixed(0)}%</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-sm font-medium text-gray-700">
                    {result.vague_requirements ? <XCircle size={14} className="text-danger-500" /> : <CheckCircle2 size={14} className="text-accent-500" />}
                    Vague
                  </div>
                  <p className="text-lg font-bold text-gray-900">{result.vague_requirements ? 'Yes' : 'No'}</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-sm font-medium text-gray-700">
                    {result.urgency_signals ? <AlertTriangle size={14} className="text-danger-500" /> : <CheckCircle2 size={14} className="text-accent-500" />}
                    Urgent
                  </div>
                  <p className="text-lg font-bold text-gray-900">{result.urgency_signals ? 'Yes' : 'No'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Budget Mismatch */}
          {result.budget_mismatch && (
            <div className={`card border-2 ${result.budget_mismatch.severity === 'high' ? 'border-danger-200' : 'border-warning-200'}`}>
              <div className="card-body">
                <div className="flex items-center gap-2 mb-3">
                  <DollarSign size={18} className="text-danger-600" />
                  <h3 className="font-semibold text-gray-900">Budget Mismatch Detected</h3>
                </div>
                <p className="text-sm text-gray-700 mb-2">{result.budget_mismatch.description}</p>
                <div className="flex gap-4 text-sm">
                  <span className="text-gray-500">Client budget: <strong>${result.budget_mismatch.client_budget}</strong></span>
                  <span className="text-gray-500">Category average: <strong>${result.budget_mismatch.category_average}</strong></span>
                  <span className="text-gray-500">Ratio: <strong>{result.budget_mismatch.ratio}x</strong></span>
                </div>
              </div>
            </div>
          )}

          {/* Red Flags */}
          {result.red_flags.length > 0 && (
            <div className="card">
              <div className="card-header flex items-center gap-2">
                <AlertCircle size={18} className="text-danger-600" />
                <h3 className="font-semibold text-gray-900">
                  Red Flags ({result.red_flags.length})
                </h3>
              </div>
              <div className="card-body space-y-3">
                {result.red_flags.map((flag, i) => {
                  const severity = getSeverityColor(flag.severity)
                  return (
                    <div key={i} className={`p-4 rounded-xl border ${severity.bg}`}>
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="text-sm font-semibold text-gray-900">{flag.description}</h4>
                        <span className={severity.badge}>{flag.severity.toUpperCase()}</span>
                      </div>
                      <p className="text-xs text-gray-600">{flag.details}</p>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Recommendations */}
          <div className="card">
            <div className="card-header flex items-center gap-2">
              <Shield size={18} className="text-accent-600" />
              <h3 className="font-semibold text-gray-900">Recommendations</h3>
            </div>
            <div className="card-body">
              <ul className="space-y-2">
                {result.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="w-5 h-5 bg-accent-50 text-accent-700 rounded-full flex items-center justify-center text-xs font-medium shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
