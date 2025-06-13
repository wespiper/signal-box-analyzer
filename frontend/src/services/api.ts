/**
 * API service for Signal Box Cost Analyzer
 * Time estimate: 2 hours
 */

import axios from 'axios'

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for analysis
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types for API responses
export interface ComponentInfo {
  name: string
  type: string
  model?: string
  estimated_tokens?: number
  file_path: string
  line_number: number
  metadata: Record<string, any>
}

export interface OptimizationInfo {
  type: string
  original_cost: number
  optimized_cost: number
  savings: number
  savings_percent: number
  explanation: string
}

export interface AnalysisResponse {
  analysis_id: string
  timestamp: string
  framework: string
  confidence: string
  confidence_score: number
  components: ComponentInfo[]
  total_original_cost: number
  total_optimized_cost: number
  total_savings: number
  savings_percentage: number
  optimizations: OptimizationInfo[]
  recommendations: string[]
  html_report_url?: string
  json_report?: Record<string, any>
}

export interface AnalysisStatus {
  analysis_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  result?: AnalysisResponse
  error?: string
}

export interface ExampleInfo {
  id: string
  name: string
  framework: string
  description: string
  savings_percentage: number
  total_savings: number
  components_count: number
  github_url: string
}

export interface ExamplesResponse {
  examples: ExampleInfo[]
  total_examples: number
  note: string
}

// Error handling
class APIError extends Error {
  status?: number
  code?: string
  
  constructor(
    message: string,
    status?: number,
    code?: string
  ) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.code = code
  }
}

export { APIError }

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message)
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response
      const message = data?.error || data?.detail || `HTTP ${status} Error`
      throw new APIError(message, status, data?.type)
    } else if (error.request) {
      // Network error
      throw new APIError('Network error. Please check your connection.')
    } else {
      // Other error
      throw new APIError(error.message)
    }
  }
)

/**
 * Start analysis of a GitHub repository
 */
export const analyzeRepository = async (githubUrl: string): Promise<AnalysisResponse> => {
  try {
    const response = await api.post<AnalysisResponse>('/api/analyze', {
      github_url: githubUrl,
      include_detailed_calculations: true,
      include_recommendations: true,
    })
    
    return response.data
  } catch (error) {
    console.error('Analysis failed:', error)
    throw error
  }
}

/**
 * Get analysis status by ID
 */
export const getAnalysisStatus = async (analysisId: string): Promise<AnalysisStatus> => {
  try {
    const response = await api.get<AnalysisStatus>(`/api/analyze/${analysisId}/status`)
    return response.data
  } catch (error) {
    console.error('Failed to get analysis status:', error)
    throw error
  }
}

/**
 * Get analysis report by ID
 */
export const getAnalysisReport = async (
  analysisId: string, 
  format: 'html' | 'json' = 'json'
): Promise<string | Record<string, any>> => {
  try {
    const response = await api.get(`/api/analyze/${analysisId}/report`, {
      params: { format },
      responseType: format === 'html' ? 'text' : 'json'
    })
    
    return response.data
  } catch (error) {
    console.error('Failed to get analysis report:', error)
    throw error
  }
}

/**
 * Delete analysis by ID
 */
export const deleteAnalysis = async (analysisId: string): Promise<void> => {
  try {
    await api.delete(`/api/analyze/${analysisId}`)
  } catch (error) {
    console.error('Failed to delete analysis:', error)
    throw error
  }
}

/**
 * Get all available examples
 */
export const getExamples = async (): Promise<ExamplesResponse> => {
  try {
    const response = await api.get<ExamplesResponse>('/api/examples')
    return response.data
  } catch (error) {
    console.error('Failed to get examples:', error)
    throw error
  }
}

/**
 * Get specific example analysis
 */
export const getExampleAnalysis = async (framework: string): Promise<AnalysisResponse> => {
  try {
    const response = await api.get<AnalysisResponse>(`/api/examples/${framework}`)
    return response.data
  } catch (error) {
    console.error('Failed to get example analysis:', error)
    throw error
  }
}

/**
 * Get example report (HTML or JSON)
 */
export const getExampleReport = async (
  framework: string,
  format: 'html' | 'json' = 'json'
): Promise<string | Record<string, any>> => {
  try {
    const response = await api.get(`/api/examples/${framework}/report`, {
      params: { format },
      responseType: format === 'html' ? 'text' : 'json'
    })
    
    return response.data
  } catch (error) {
    console.error('Failed to get example report:', error)
    throw error
  }
}

/**
 * Health check
 */
export const healthCheck = async (): Promise<{ status: string; service: string; version: string }> => {
  try {
    const response = await api.get('/api/health')
    return response.data
  } catch (error) {
    console.error('Health check failed:', error)
    throw error
  }
}

/**
 * Utility function for polling analysis status
 */
export const pollAnalysisStatus = async (
  analysisId: string,
  onUpdate?: (status: AnalysisStatus) => void,
  intervalMs: number = 2000,
  maxAttempts: number = 60
): Promise<AnalysisResponse> => {
  let attempts = 0
  
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        attempts++
        
        if (attempts > maxAttempts) {
          reject(new APIError('Analysis timeout. Please try again.'))
          return
        }
        
        const status = await getAnalysisStatus(analysisId)
        onUpdate?.(status)
        
        switch (status.status) {
          case 'completed':
            if (status.result) {
              resolve(status.result)
            } else {
              reject(new APIError('Analysis completed but no result available'))
            }
            break
            
          case 'failed':
            reject(new APIError(status.error || 'Analysis failed'))
            break
            
          case 'pending':
          case 'processing':
            setTimeout(poll, intervalMs)
            break
            
          default:
            reject(new APIError(`Unknown status: ${status.status}`))
        }
      } catch (error) {
        reject(error)
      }
    }
    
    poll()
  })
}

/**
 * Validate GitHub URL format
 */
export const validateGitHubUrl = (url: string): boolean => {
  const pattern = /^https?:\/\/(www\.)?github\.com\/[\w\-\.]+\/[\w\-\.]+\/?$/
  return pattern.test(url.trim())
}

/**
 * Format cost values for display
 */
export const formatCost = (cost: number, decimals: number = 4): string => {
  return `$${cost.toFixed(decimals)}`
}

/**
 * Format percentage values for display
 */
export const formatPercentage = (percentage: number, decimals: number = 1): string => {
  return `${percentage.toFixed(decimals)}%`
}

/**
 * Calculate savings information
 */
export const calculateSavings = (originalCost: number, optimizedCost: number) => {
  const savings = originalCost - optimizedCost
  const percentage = originalCost > 0 ? (savings / originalCost) * 100 : 0
  
  return {
    amount: savings,
    percentage,
    formatted: {
      amount: formatCost(savings),
      percentage: formatPercentage(percentage),
      originalCost: formatCost(originalCost),
      optimizedCost: formatCost(optimizedCost)
    }
  }
}

// Export the configured axios instance for custom requests
export { api }