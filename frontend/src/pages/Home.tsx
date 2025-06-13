import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Rocket, Github, Zap, BarChart3, Shield, Clock } from 'lucide-react'
import URLInput from '../components/URLInput'

const Home = () => {
  const navigate = useNavigate()
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleAnalyze = async (githubUrl: string) => {
    setIsAnalyzing(true)
    
    // Navigate to analysis page with URL as query param
    const params = new URLSearchParams({ url: githubUrl })
    navigate(`/analysis?${params.toString()}`)
  }

  const handleTryExample = (framework: string) => {
    navigate(`/analysis?example=${framework}`)
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Signal Box</h1>
                <p className="text-sm text-gray-500">AI Cost Analyzer</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <a href="#features" className="text-gray-600 hover:text-primary-600 transition-colors">
                Features
              </a>
              <a href="#examples" className="text-gray-600 hover:text-primary-600 transition-colors">
                Examples
              </a>
              <a href="https://docs.signalbox.ai" className="text-gray-600 hover:text-primary-600 transition-colors">
                Docs
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-500/10 to-secondary-500/10"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              See exactly how much your
              <span className="bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent"> AI agents cost</span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Analyze any GitHub repository and get a transparent, auditable report showing 
              exactly how much your AI workflows cost - and how to optimize them.
            </p>

            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <div className="flex items-center bg-white rounded-full px-4 py-2 shadow-sm border border-gray-200">
                <span className="text-green-500 text-sm font-semibold">✓</span>
                <span className="ml-2 text-sm text-gray-700">100% Transparent</span>
              </div>
              <div className="flex items-center bg-white rounded-full px-4 py-2 shadow-sm border border-gray-200">
                <span className="text-green-500 text-sm font-semibold">✓</span>
                <span className="ml-2 text-sm text-gray-700">Fully Auditable</span>
              </div>
              <div className="flex items-center bg-white rounded-full px-4 py-2 shadow-sm border border-gray-200">
                <span className="text-green-500 text-sm font-semibold">✓</span>
                <span className="ml-2 text-sm text-gray-700">Real Savings</span>
              </div>
            </div>

            {/* URL Input */}
            <div className="max-w-2xl mx-auto">
              <URLInput onAnalyze={handleAnalyze} isLoading={isAnalyzing} />
            </div>

            <p className="text-sm text-gray-500 mt-4">
              Or try our examples below ↓
            </p>
          </div>
        </div>
      </section>

      {/* Examples Section */}
      <section id="examples" className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Try Signal Box with Popular Frameworks
            </h2>
            <p className="text-lg text-gray-600">
              See real cost optimizations on production AI workflows
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* AutoGen Example */}
            <div className="card hover:shadow-xl transition-all duration-300 group cursor-pointer"
                 onClick={() => handleTryExample('autogen')}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">AG</span>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold text-green-600">78%</span>
                  <p className="text-sm text-gray-500">Cost Reduction</p>
                </div>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                AutoGen Research Assistant
              </h3>
              <p className="text-gray-600 mb-4">
                Multi-agent system with coordinator, researcher, analyst, and web search agents.
              </p>
              
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>4 agents analyzed</span>
                <span className="font-semibold text-green-600">$0.15 saved per run</span>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-100">
                <button className="text-primary-600 font-semibold group-hover:text-primary-700 transition-colors">
                  Analyze Example →
                </button>
              </div>
            </div>

            {/* LangChain Example */}
            <div className="card hover:shadow-xl transition-all duration-300 group cursor-pointer"
                 onClick={() => handleTryExample('langchain')}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">LC</span>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold text-green-600">74%</span>
                  <p className="text-sm text-gray-500">Cost Reduction</p>
                </div>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Customer Support Bot
              </h3>
              <p className="text-gray-600 mb-4">
                Intent classification, query routing, and response generation with semantic search.
              </p>
              
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>4 chains analyzed</span>
                <span className="font-semibold text-green-600">$0.05 saved per chat</span>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-100">
                <button className="text-primary-600 font-semibold group-hover:text-primary-700 transition-colors">
                  Analyze Example →
                </button>
              </div>
            </div>

            {/* CrewAI Example */}
            <div className="card hover:shadow-xl transition-all duration-300 group cursor-pointer"
                 onClick={() => handleTryExample('crewai')}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">CA</span>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold text-green-600">70%</span>
                  <p className="text-sm text-gray-500">Cost Reduction</p>
                </div>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Content Creation Crew
              </h3>
              <p className="text-gray-600 mb-4">
                Research, writing, and editing crew working together to create content.
              </p>
              
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>3 agents analyzed</span>
                <span className="font-semibold text-green-600">$0.12 saved per run</span>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-100">
                <button className="text-primary-600 font-semibold group-hover:text-primary-700 transition-colors">
                  Analyze Example →
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Signal Box?
            </h2>
            <p className="text-lg text-gray-600">
              The only AI cost analyzer that shows you exactly how the numbers work
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                100% Transparent
              </h3>
              <p className="text-gray-600">
                Every calculation is shown step-by-step. No black boxes, no hidden assumptions.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Real Optimizations
              </h3>
              <p className="text-gray-600">
                Smart model routing, semantic caching, and token optimization that actually work.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Instant Analysis
              </h3>
              <p className="text-gray-600">
                Paste any GitHub URL and get a complete cost analysis in under 30 seconds.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Github className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Any Framework
              </h3>
              <p className="text-gray-600">
                Supports AutoGen, LangChain, CrewAI, and custom LLM implementations.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Actionable Insights
              </h3>
              <p className="text-gray-600">
                Get specific recommendations you can implement immediately to reduce costs.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Shareable Reports
              </h3>
              <p className="text-gray-600">
                Beautiful HTML reports you can share with your team or stakeholders.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-primary-500 to-secondary-500">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to optimize your AI costs?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Get started with a free analysis of your GitHub repository
          </p>
          
          <div className="max-w-xl mx-auto">
            <URLInput 
              onAnalyze={handleAnalyze} 
              isLoading={isAnalyzing}
              placeholder="Paste your GitHub URL here..."
              theme="dark"
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
                  <Rocket className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">Signal Box</span>
              </div>
              <p className="text-gray-400 mb-4">
                The transparent AI cost analyzer that shows you exactly how to optimize your workflows.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#examples" className="hover:text-white transition-colors">Examples</a></li>
                <li><a href="/docs" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="/api" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="/about" className="hover:text-white transition-colors">About</a></li>
                <li><a href="/contact" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="/privacy" className="hover:text-white transition-colors">Privacy</a></li>
                <li><a href="/terms" className="hover:text-white transition-colors">Terms</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Signal Box. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Home