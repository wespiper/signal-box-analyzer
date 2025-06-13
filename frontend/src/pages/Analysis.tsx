import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Rocket, ArrowLeft, Github, ExternalLink } from 'lucide-react'
import { getExampleAnalysis, analyzeRepository, APIError, type AnalysisResponse } from '../services/api'

const Analysis = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const githubUrl = searchParams.get('url')
  const exampleFramework = searchParams.get('example')

  useEffect(() => {
    const loadAnalysis = async () => {
      try {
        if (exampleFramework) {
          // Load example analysis
          const data = await getExampleAnalysis(exampleFramework)
          setAnalysisData(data)
        } else if (githubUrl) {
          // Start real analysis
          const data = await analyzeRepository(githubUrl)
          setAnalysisData(data)
        } else {
          setError('No URL or example specified')
        }
      } catch (err) {
        if (err instanceof APIError) {
          setError(err.message)
        } else {
          setError('Failed to load analysis')
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadAnalysis()
  }, [githubUrl, exampleFramework])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Rocket className="w-8 h-8 text-white animate-pulse" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Analyzing Repository</h2>
          <p className="text-gray-600">This might take a few seconds...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-red-100 rounded-xl flex items-center justify-center mx-auto mb-4">
            <span className="text-red-600 text-2xl">⚠️</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Analysis Failed</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button 
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!analysisData) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => navigate('/')}
                className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Home</span>
              </button>
              
              <div className="h-6 border-l border-gray-300"></div>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
                  <Rocket className="w-4 h-4 text-white" />
                </div>
                <span className="font-semibold text-gray-900">Signal Box Analysis</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {githubUrl && (
                <a 
                  href={githubUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
                >
                  <Github className="w-4 h-4" />
                  <span>View Repository</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Results */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="metric-card">
            <div className="text-3xl font-bold mb-2">
              {analysisData.savings_percentage.toFixed(1)}%
            </div>
            <div className="text-blue-100">Cost Reduction</div>
          </div>
          
          <div className="card">
            <div className="text-2xl font-bold text-gray-900 mb-2">
              ${analysisData.total_original_cost.toFixed(4)}
            </div>
            <div className="text-gray-600">Original Cost</div>
          </div>
          
          <div className="card">
            <div className="text-2xl font-bold text-gray-900 mb-2">
              ${analysisData.total_optimized_cost.toFixed(4)}
            </div>
            <div className="text-gray-600">Optimized Cost</div>
          </div>
          
          <div className="card">
            <div className="text-2xl font-bold text-green-600 mb-2">
              ${analysisData.total_savings.toFixed(4)}
            </div>
            <div className="text-gray-600">Savings per Run</div>
          </div>
        </div>

        {/* Framework Info */}
        <div className="card mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Framework Detected: {analysisData.framework.toUpperCase()}
              </h2>
              <p className="text-gray-600">
                Detection confidence: <span className="font-semibold">{analysisData.confidence}</span>
              </p>
            </div>
            <div className="text-right">
              <div className="text-lg font-semibold text-gray-900">
                {analysisData.components.length} Components Analyzed
              </div>
              <div className="text-sm text-gray-500">
                {analysisData.optimizations.length} Optimizations Applied
              </div>
            </div>
          </div>
        </div>

        {/* Components */}
        <div className="card mb-8">
          <h3 className="section-header">Components Analyzed</h3>
          <div className="space-y-4">
            {analysisData.components.map((component, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">{component.name}</h4>
                  <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    {component.type}
                  </span>
                </div>
                <div className="grid md:grid-cols-3 gap-4 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">Model:</span> {component.model || 'Not specified'}
                  </div>
                  <div>
                    <span className="font-medium">Tokens:</span> {component.estimated_tokens || 'Estimated'}
                  </div>
                  <div>
                    <span className="font-medium">File:</span> {component.file_path}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Optimizations */}
        <div className="card mb-8">
          <h3 className="section-header">Optimizations Applied</h3>
          <div className="space-y-4">
            {analysisData.optimizations.map((optimization, index) => (
              <div key={index} className="border-l-4 border-green-500 bg-green-50 p-4 rounded-r-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">
                    {optimization.type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                  </h4>
                  <div className="text-right">
                    <span className="text-lg font-bold text-green-600">
                      ${optimization.savings.toFixed(4)}
                    </span>
                    <span className="text-sm text-gray-500 ml-2">
                      ({optimization.savings_percent.toFixed(1)}% saved)
                    </span>
                  </div>
                </div>
                <p className="text-gray-700">{optimization.explanation}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="card">
          <h3 className="section-header">Implementation Recommendations</h3>
          <div className="space-y-3">
            {analysisData.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-white text-xs font-bold">{index + 1}</span>
                </div>
                <p className="text-gray-700">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}

export default Analysis