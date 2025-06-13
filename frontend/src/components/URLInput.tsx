import { useState } from 'react'
import { Github, Loader2, AlertCircle } from 'lucide-react'

interface URLInputProps {
  onAnalyze: (url: string) => void
  isLoading?: boolean
  placeholder?: string
  theme?: 'light' | 'dark'
}

const URLInput = ({ 
  onAnalyze, 
  isLoading = false, 
  placeholder = "https://github.com/username/repository",
  theme = 'light'
}: URLInputProps) => {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')

  const validateGitHubUrl = (url: string): boolean => {
    const githubPattern = /^https?:\/\/(www\.)?github\.com\/[\w\-\.]+\/[\w\-\.]+\/?$/
    return githubPattern.test(url.trim())
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!url.trim()) {
      setError('Please enter a GitHub URL')
      return
    }

    if (!validateGitHubUrl(url)) {
      setError('Please enter a valid GitHub repository URL')
      return
    }

    setError('')
    onAnalyze(url.trim())
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value)
    if (error) setError('')
  }

  const isDark = theme === 'dark'
  
  const inputClasses = `
    w-full px-4 py-4 pl-12 pr-32 rounded-xl border-2 text-lg
    transition-all duration-300 focus:outline-none focus:ring-4
    ${isDark 
      ? 'bg-white/10 border-white/20 text-white placeholder-white/60 focus:border-white/40 focus:ring-white/20 backdrop-blur-sm'
      : 'bg-white border-gray-200 text-gray-900 placeholder-gray-500 focus:border-primary-500 focus:ring-primary-500/20'
    }
    ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
  `

  const buttonClasses = `
    absolute right-2 top-2 bottom-2 px-6 rounded-lg font-semibold
    transition-all duration-300 flex items-center space-x-2
    ${isDark
      ? 'bg-white text-primary-600 hover:bg-white/90'
      : 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white hover:shadow-lg hover:scale-105'
    }
    disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
  `

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <Github className={`absolute left-4 top-1/2 transform -translate-y-1/2 w-6 h-6 ${
            isDark ? 'text-white/60' : 'text-gray-400'
          }`} />
          
          <input
            type="url"
            value={url}
            onChange={handleInputChange}
            placeholder={placeholder}
            className={inputClasses}
            disabled={isLoading}
          />
          
          <button
            type="submit"
            disabled={isLoading || !url.trim()}
            className={buttonClasses}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <span>Analyze</span>
              </>
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="mt-3 flex items-center space-x-2 text-red-600">
          <AlertCircle className="w-4 h-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      <div className={`mt-4 text-sm ${isDark ? 'text-white/60' : 'text-gray-500'}`}>
        <p className="mb-2">
          <strong>Supported frameworks:</strong> AutoGen, LangChain, CrewAI, and custom LLM implementations
        </p>
        <p>
          <strong>Example URLs:</strong>
        </p>
        <ul className="mt-1 space-y-1 text-xs">
          <li>• https://github.com/microsoft/autogen</li>
          <li>• https://github.com/langchain-ai/langchain</li>
          <li>• https://github.com/joaomdmoura/crewAI</li>
        </ul>
      </div>
    </div>
  )
}

export default URLInput