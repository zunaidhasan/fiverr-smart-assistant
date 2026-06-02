import React, { useState, useEffect } from 'react'
import { Tab } from './types'
import SmartReply from './components/SmartReply'
import SimilaritySearch from './components/SimilaritySearch'
import ProposalOptimizer from './components/ProposalOptimizer'
import RiskDetector from './components/RiskDetector'
import Dashboard from './components/Dashboard'
import CRMView from './components/CRMView'
import { checkCsvStatus, uploadCsv } from './api/client'
import {
  MessageSquare,
  Search,
  FileText,
  AlertTriangle,
  BarChart3,
  Users,
  Upload,
  CheckCircle2,
  Loader2,
  Sparkles,
} from 'lucide-react'

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: 'smart-reply', label: 'Smart Reply', icon: <MessageSquare size={18} /> },
  { id: 'similarity', label: 'Similarity Search', icon: <Search size={18} /> },
  { id: 'proposal', label: 'Proposal Optimizer', icon: <FileText size={18} /> },
  { id: 'risk', label: 'Risk Detector', icon: <AlertTriangle size={18} /> },
  { id: 'dashboard', label: 'Dashboard', icon: <BarChart3 size={18} /> },
  { id: 'crm', label: 'Portfolio CRM', icon: <Users size={18} /> },
]

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('smart-reply')
  const [csvLoaded, setCsvLoaded] = useState(false)
  const [projectCount, setProjectCount] = useState(0)
  const [categories, setCategories] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    loadStatus()
  }, [])

  const loadStatus = async () => {
    try {
      setLoading(true)
      setError(null)
      const status = await checkCsvStatus()
      setCsvLoaded(status.loaded)
      setProjectCount(status.project_count)
      setCategories(status.categories)
    } catch (err) {
      const apiBase = import.meta.env.VITE_API_URL || '/api'
      setError(
        `Could not connect to backend at ${apiBase}. ` +
        (apiBase === '/api'
          ? 'Set the VITE_API_URL environment variable to your backend URL (e.g. https://your-app.onrender.com).'
          : 'Check that the backend is running and the URL is correct.')
      )
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      setUploading(true)
      setError(null)
      const result = await uploadCsv(file)
      setCsvLoaded(true)
      setProjectCount(result.project_count)
      setCategories(result.categories)
    } catch (err) {
      setError('Failed to upload CSV file.')
    } finally {
      setUploading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="text-center animate-fade-in">
          <Loader2 size={40} className="animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-500 text-sm">Loading Portfolio Intelligence...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-sm">
                <Sparkles size={20} className="text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">SardarIT Portfolio Intelligence</h1>
                <p className="text-xs text-gray-500">Internal OS — 566+ Web Development Projects Reference</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {csvLoaded ? (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-accent-50 text-accent-700 rounded-lg text-xs font-medium">
                  <CheckCircle2 size={14} />
                  <span>{projectCount} projects loaded</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-warning-50 text-warning-700 rounded-lg text-xs font-medium">
                  <AlertTriangle size={14} />
                  <span>No data loaded</span>
                </div>
              )}

              <label className="btn-primary cursor-pointer text-xs">
                <Upload size={16} />
                {uploading ? 'Uploading...' : 'Upload CSV'}
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleUpload}
                  className="hidden"
                  disabled={uploading}
                />
              </label>
            </div>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <div className="bg-danger-50 border border-danger-200 text-danger-800 px-4 py-3 rounded-xl text-sm flex items-center gap-2">
            <AlertTriangle size={16} />
            {error}
            <button onClick={() => setError(null)} className="ml-auto text-danger-600 hover:text-danger-800">Dismiss</button>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <nav className="flex gap-1 border-b border-gray-200 overflow-x-auto pb-px">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-all duration-200 whitespace-nowrap
                ${activeTab === tab.id
                  ? 'tab-active border-b-2'
                  : 'tab-inactive'
                }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 animate-fade-in">
        {!csvLoaded ? (
          <div className="card p-12 text-center">
            <Upload size={48} className="mx-auto text-gray-300 mb-4" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">Welcome to Portfolio Intelligence</h2>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              Upload a SardarIT project database CSV (or use the default one) to start. The system will
              help you match buyer requests to your portfolio, generate proposals, and detect risks.
            </p>
            <label className="btn-primary cursor-pointer inline-flex">
              <Upload size={18} />
              Upload Your CSV File
              <input
                type="file"
                accept=".csv"
                onChange={handleUpload}
                className="hidden"
              />
            </label>
            <p className="text-xs text-gray-400 mt-3">
              CSV should contain columns: Website URL, Category, Used Stack, Brief Description, etc.
            </p>
          </div>
        ) : (
          <>
            {activeTab === 'smart-reply' && <SmartReply categories={categories} />}
            {activeTab === 'similarity' && <SimilaritySearch />}
            {activeTab === 'proposal' && <ProposalOptimizer categories={categories} />}
            {activeTab === 'risk' && <RiskDetector categories={categories} />}
            {activeTab === 'dashboard' && <Dashboard />}
            {activeTab === 'crm' && <CRMView />}
          </>
        )}
      </main>
    </div>
  )
}
