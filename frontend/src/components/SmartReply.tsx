import React, { useState } from 'react'
import { SmartReplyRequest, SmartReplyResponse } from '../types'
import { generateReply, detectSituation } from '../api/client'
import {
  Send,
  Sparkles,
  AlertCircle,
  DollarSign,
  Clock,
  TrendingUp,
  MessageSquare,
  Copy,
  CheckCheck,
  Loader2,
  Globe,
  Zap,
  Award,
} from 'lucide-react'

const SITUATION_OPTIONS = [
  { value: '', label: 'Auto-detect' },
  { value: 'technical_project', label: 'Technical Project' },
  { value: 'creative_project', label: 'Creative Project' },
  { value: 'urgent_fix', label: 'Urgent Fix' },
  { value: 'data_entry', label: 'Data Entry' },
  { value: 'consulting', label: 'Consulting' },
  { value: 'ongoing_support', label: 'Ongoing Support' },
  { value: 'general', label: 'General' },
]

export default function SmartReply({ categories }: { categories: string[] }) {
  const [clientMessage, setClientMessage] = useState('')
  const [situationType, setSituationType] = useState('')
  const [category, setCategory] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SmartReplyResponse | null>(null)
  const [detectedSituation, setDetectedSituation] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const handleDetect = async () => {
    if (!clientMessage.trim()) return
    try {
      const res = await detectSituation(clientMessage)
      setDetectedSituation(res.situation_type)
      setSituationType(res.situation_type)
    } catch {
      // silent
    }
  }

  const handleGenerate = async () => {
    if (!clientMessage.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const req: SmartReplyRequest = {
        client_message: clientMessage,
        situation_type: situationType || undefined,
        category: category || undefined,
      }
      const res = await generateReply(req)
      setResult(res)
    } catch (err) {
      setError('Failed to generate reply. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (!result?.draft_reply) return
    navigator.clipboard.writeText(result.draft_reply)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getRiskColor = (score: number) => {
    if (score >= 0.7) return 'text-accent-600 bg-accent-50'
    if (score >= 0.4) return 'text-warning-600 bg-warning-50'
    return 'text-gray-500 bg-gray-50'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 0.7) return 'High Confidence'
    if (score >= 0.4) return 'Medium Confidence'
    return 'Low Confidence'
  }

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="card">
        <div className="card-header flex items-center gap-2">
          <MessageSquare size={20} className="text-primary-600" />
          <h2 className="font-semibold text-gray-900">Client Message</h2>
        </div>
        <div className="card-body space-y-4">
          <textarea
            placeholder="Paste the buyer's message here..."
            value={clientMessage}
            onChange={(e) => setClientMessage(e.target.value)}
            rows={6}
            className="input-field resize-none"
          />

          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs font-medium text-gray-500 mb-1">Situation Type</label>
              <select
                value={situationType}
                onChange={(e) => setSituationType(e.target.value)}
                className="select-field"
              >
                {SITUATION_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs font-medium text-gray-500 mb-1">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="select-field"
              >
                <option value="">Auto-detect</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex gap-3">
            <button onClick={handleDetect} className="btn-secondary text-xs" disabled={!clientMessage.trim()}>
              <Sparkles size={14} />
              Auto-Detect Type
            </button>
            <button onClick={handleGenerate} className="btn-primary" disabled={!clientMessage.trim() || loading}>
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              {loading ? 'Generating...' : 'Generate Reply'}
            </button>
          </div>

          {detectedSituation && (
            <p className="text-xs text-gray-500">
              Detected: <span className="font-medium text-primary-600">{detectedSituation.replace(/_/g, ' ')}</span>
            </p>
          )}

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
          {/* Draft Reply */}
          <div className="card animate-slide-up">
            <div className="card-header flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Send size={18} className="text-primary-600" />
                <h3 className="font-semibold text-gray-900">Draft Reply</h3>
              </div>
              <button onClick={handleCopy} className="btn-secondary text-xs">
                {copied ? <CheckCheck size={14} /> : <Copy size={14} />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <div className="card-body">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">
                {result.draft_reply}
              </pre>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
            <div className="card p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                <TrendingUp size={16} />
                Confidence
              </div>
              <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${getRiskColor(result.confidence_score)}`}>
                {getScoreLabel(result.confidence_score)}
                <span className="font-bold">{(result.confidence_score * 100).toFixed(0)}%</span>
              </div>
            </div>

            <div className="card p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                <DollarSign size={16} />
                Quote Range
              </div>
              <p className="text-lg font-bold text-gray-900">
                ${result.estimated_quote_range.min} - ${result.estimated_quote_range.max}
              </p>
              <p className="text-xs text-gray-400">{result.estimated_quote_range.currency}</p>
            </div>

            <div className="card p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                <MessageSquare size={16} />
                Suggested Tone
              </div>
              <p className="text-sm font-medium text-gray-800">
                {result.suggested_tone}
              </p>
            </div>

            <div className="card p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                <Clock size={16} />
                Past References
              </div>
              <p className="text-lg font-bold text-gray-900">
                {result.relevant_past_projects.length}
              </p>
              <p className="text-xs text-gray-400">similar projects found</p>
            </div>
          </div>

          {/* Questions to Ask */}
          <div className="card animate-slide-up">
            <div className="card-header flex items-center gap-2">
              <AlertCircle size={18} className="text-warning-600" />
              <h3 className="font-semibold text-gray-900">Questions to Ask the Buyer</h3>
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

          {/* Relevant Past Projects */}
          {result.relevant_past_projects.length > 0 && (
            <div className="card animate-slide-up">
              <div className="card-header flex items-center gap-2">
                <Sparkles size={18} className="text-accent-600" />
                <h3 className="font-semibold text-gray-900">Relevant Portfolio Projects</h3>
              </div>
              <div className="card-body">
                <div className="space-y-3">
                  {result.relevant_past_projects.map((proj) => (
                    <div key={proj.project_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <Globe size={14} className="text-gray-400 shrink-0" />
                          <p className="text-sm font-medium text-gray-900 truncate">{proj.title}</p>
                        </div>
                        <div className="flex items-center gap-3 mt-1">
                          <span className="text-xs text-gray-500">{proj.category}</span>
                          <span className="text-xs text-gray-400">•</span>
                          <span className="text-xs text-gray-500 flex items-center gap-1">
                            <Zap size={10} />
                            {proj.technology || proj.stack_used}
                          </span>
                          {proj.quality && (
                            <>
                              <span className="text-xs text-gray-400">•</span>
                              <span className={`text-xs font-medium ${proj.quality.toLowerCase() === 'high' ? 'text-accent-600' : 'text-warning-600'}`}>
                                <Award size={10} className="inline mr-0.5" />
                                {proj.quality}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-3 ml-4 shrink-0">
                        {proj.match_score > 0 && (
                          <span className="badge-info text-xs">Score: {proj.match_score}</span>
                        )}
                        <span className="text-xs font-semibold text-primary-600 bg-primary-50 px-2 py-1 rounded-full">
                          {(proj.similarity_score * 100).toFixed(0)}% match
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
