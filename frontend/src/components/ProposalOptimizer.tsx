import React, { useState } from 'react'
import { optimizeProposal } from '../api/client'
import { ProposalOptimizerResponse } from '../types'
import {
  FileText,
  Loader2,
  AlertCircle,
  Sparkles,
  DollarSign,
  Clock,
  Star,
  Lightbulb,
  AlertTriangle,
  HelpCircle,
  ListChecks,
  Globe,
  Zap,
  Award,
  Target,
  Layers,
} from 'lucide-react'

export default function ProposalOptimizer({ categories }: { categories: string[] }) {
  const [clientBrief, setClientBrief] = useState('')
  const [category, setCategory] = useState('')
  const [budget, setBudget] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ProposalOptimizerResponse | null>(null)

  const handleOptimize = async () => {
    if (!clientBrief.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await optimizeProposal({
        client_brief: clientBrief,
        category: category || undefined,
        budget: budget ? Number(budget) : undefined,
      })
      setResult(res)
    } catch (err) {
      setError('Failed to optimize proposal. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header flex items-center gap-2">
          <FileText size={20} className="text-primary-600" />
          <h2 className="font-semibold text-gray-900">Proposal Optimizer</h2>
        </div>
        <div className="card-body space-y-4">
          <p className="text-sm text-gray-500">
            Paste the client's brief and get a fully optimized proposal structure with relevant portfolio examples,
            risk signals, and recommended approach drawn from 566+ web development projects.
          </p>

          <textarea
            placeholder="Paste the client's full brief here..."
            value={clientBrief}
            onChange={(e) => setClientBrief(e.target.value)}
            rows={6}
            className="input-field resize-none"
          />

          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs font-medium text-gray-500 mb-1">Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="select-field">
                <option value="">Auto-detect</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            <div className="flex-1 min-w-[150px]">
              <label className="block text-xs font-medium text-gray-500 mb-1">Client Budget (optional)</label>
              <input
                type="number"
                placeholder="$"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="input-field"
              />
            </div>
          </div>

          <button onClick={handleOptimize} className="btn-primary" disabled={!clientBrief.trim() || loading}>
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
            {loading ? 'Optimizing...' : 'Optimize Proposal'}
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
          {/* Quote & Timeline Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="card p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                <DollarSign size={16} />
                Suggested Quote Range
              </div>
              <p className="text-2xl font-bold text-gray-900">
                ${result.suggested_quote_range.min} - ${result.suggested_quote_range.max}
              </p>
              <p className="text-xs text-gray-400">{result.suggested_quote_range.currency}</p>
            </div>
            <div className="card p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                <Clock size={16} />
                Estimated Timeline
              </div>
              <p className="text-lg font-semibold text-gray-900">{result.estimated_timeline}</p>
            </div>
          </div>

          {/* Recommended Structure */}
          <div className="card">
            <div className="card-header flex items-center gap-2">
              <ListChecks size={18} className="text-primary-600" />
              <h3 className="font-semibold text-gray-900">Recommended Proposal Structure</h3>
            </div>
            <div className="card-body">
              <ol className="space-y-2">
                {result.recommended_structure.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="w-6 h-6 bg-primary-50 text-primary-700 rounded-full flex items-center justify-center text-xs font-medium shrink-0">
                      {i + 1}
                    </span>
                    {item}
                  </li>
                ))}
              </ol>
            </div>
          </div>

          {/* Portfolio Examples */}
          {result.portfolio_examples.length > 0 && (
            <div className="card">
              <div className="card-header flex items-center gap-2">
                <Star size={18} className="text-warning-500" />
                <h3 className="font-semibold text-gray-900">Best Portfolio Examples to Mention</h3>
              </div>
              <div className="card-body">
                <div className="space-y-3">
                  {result.portfolio_examples.map((ex, i) => (
                    <div key={i} className="flex items-start justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <Globe size={14} className="text-gray-400 shrink-0" />
                          <p className="text-sm font-medium text-gray-900 truncate">{ex.title}</p>
                          {ex.match_score > 0 && (
                            <span className="badge-info text-xs shrink-0">Score: {ex.match_score}</span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 mt-1 text-xs text-gray-500 flex-wrap">
                          <span>{ex.category}</span>
                          {ex.technology && (
                            <>
                              <span>•</span>
                              <span className="flex items-center gap-1">
                                <Zap size={10} /> {ex.technology}
                              </span>
                            </>
                          )}
                          {ex.stack && (
                            <>
                              <span>•</span>
                              <span className="flex items-center gap-1">
                                <Layers size={10} /> {ex.stack}
                              </span>
                            </>
                          )}
                        </div>
                        {ex.description && (
                          <p className="text-xs text-gray-400 mt-1 italic truncate">
                            "{ex.description.slice(0, 120)}"
                          </p>
                        )}
                      </div>
                      <div className="flex items-center gap-2 ml-4 shrink-0">
                        {ex.relevance_score && (
                          <span className="text-xs font-semibold text-primary-600 bg-primary-50 px-2 py-1 rounded-full">
                            {(ex.relevance_score * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Relevant Experience */}
          {result.relevant_experience.length > 0 && (
            <div className="card">
              <div className="card-header flex items-center gap-2">
                <Lightbulb size={18} className="text-accent-600" />
                <h3 className="font-semibold text-gray-900">Relevant Experience to Highlight</h3>
              </div>
              <div className="card-body">
                <ul className="space-y-2">
                  {result.relevant_experience.map((exp, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                      <span className="w-1.5 h-1.5 bg-accent-500 rounded-full shrink-0" />
                      {exp}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Risk Signals */}
          {result.risk_signals.length > 0 && (
            <div className="card">
              <div className="card-header flex items-center gap-2">
                <AlertTriangle size={18} className="text-danger-600" />
                <h3 className="font-semibold text-gray-900">Risk Signals</h3>
              </div>
              <div className="card-body">
                <ul className="space-y-2">
                  {result.risk_signals.map((signal, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-danger-700">
                      <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                      {signal}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Questions */}
          <div className="card">
            <div className="card-header flex items-center gap-2">
              <HelpCircle size={18} className="text-primary-600" />
              <h3 className="font-semibold text-gray-900">Questions to Ask</h3>
            </div>
            <div className="card-body">
              <ul className="space-y-2">
                {result.questions_to_ask.map((q, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="w-5 h-5 bg-primary-50 text-primary-700 rounded-full flex items-center justify-center text-xs font-medium shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    {q}
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
