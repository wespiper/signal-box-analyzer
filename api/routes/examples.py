"""
Examples endpoint for Signal Box Cost Analyzer
Time estimate: 1 hour
"""

from fastapi import APIRouter
from typing import Dict, List, Any
from datetime import datetime

router = APIRouter()


# Pre-computed example analyses
EXAMPLE_ANALYSES = {
    "autogen": {
        "analysis_id": "example_autogen_001",
        "timestamp": "2024-01-15T10:30:00Z",
        "framework": "autogen",
        "confidence": "high",
        "confidence_score": 92.5,
        "github_url": "https://github.com/microsoft/autogen/examples/research_assistant",
        "repository": {
            "owner": "microsoft",
            "name": "autogen-example",
            "description": "Multi-agent research assistant using AutoGen",
            "language": "Python"
        },
        "components": [
            {
                "name": "coordinator",
                "type": "agent",
                "model": "gpt-4",
                "estimated_tokens": 1500,
                "file_path": "research_assistant.py",
                "line_number": 15,
                "metadata": {
                    "agent_type": "AssistantAgent",
                    "system_message": "You coordinate the research process and delegate tasks to other agents.",
                    "max_consecutive_auto_reply": 10
                }
            },
            {
                "name": "researcher",
                "type": "agent", 
                "model": "gpt-4",
                "estimated_tokens": 2800,
                "file_path": "research_assistant.py",
                "line_number": 25,
                "metadata": {
                    "agent_type": "AssistantAgent",
                    "system_message": "You conduct detailed research on given topics using available tools.",
                    "tools": ["web_search", "document_analysis"]
                }
            },
            {
                "name": "analyst",
                "type": "agent",
                "model": "gpt-4", 
                "estimated_tokens": 2000,
                "file_path": "research_assistant.py",
                "line_number": 35,
                "metadata": {
                    "agent_type": "AssistantAgent",
                    "system_message": "You analyze research findings and provide insights."
                }
            },
            {
                "name": "web_searcher",
                "type": "agent",
                "model": "gpt-3.5-turbo",
                "estimated_tokens": 700,
                "file_path": "research_assistant.py", 
                "line_number": 45,
                "metadata": {
                    "agent_type": "UserProxyAgent",
                    "code_execution_config": {"last_n_messages": 2}
                }
            }
        ],
        "total_original_cost": 0.1927,
        "total_optimized_cost": 0.0424,
        "total_savings": 0.1503,
        "savings_percentage": 78.0,
        "optimizations": [
            {
                "type": "model_substitution",
                "original_cost": 0.0450,
                "optimized_cost": 0.0004,
                "savings": 0.0446,
                "savings_percent": 99.1,
                "explanation": "Substituted GPT-4 with Claude-3-Haiku for coordination tasks"
            },
            {
                "type": "model_substitution", 
                "original_cost": 0.0007,
                "optimized_cost": 0.0002,
                "savings": 0.0005,
                "savings_percent": 71.4,
                "explanation": "Used more efficient model for web search agent"
            },
            {
                "type": "semantic_caching",
                "original_cost": 0.1470,
                "optimized_cost": 0.0418,
                "savings": 0.1052,
                "savings_percent": 71.6,
                "explanation": "Applied 15% semantic caching for research queries"
            }
        ],
        "recommendations": [
            "Implement smart model routing to save $0.15 per run. Use Claude-3-Haiku for simple coordination tasks.",
            "Enable semantic caching for research queries with 15-30% expected hit rate.",
            "Parallelize independent research tasks to reduce execution time by ~40%.",
            "Implement loop detection to prevent circular agent calls in complex conversations."
        ],
        "execution_optimizations": {
            "parallel_opportunities": [
                {
                    "type": "parallel_agents",
                    "agents": ["researcher", "analyst"],
                    "estimated_time_savings": 0.3
                }
            ],
            "cache_opportunities": [
                {
                    "component": "researcher",
                    "cache_potential": "high",
                    "estimated_hit_rate": 0.25
                },
                {
                    "component": "coordinator", 
                    "cache_potential": "medium",
                    "estimated_hit_rate": 0.15
                }
            ]
        }
    },
    
    "langchain": {
        "analysis_id": "example_langchain_001",
        "timestamp": "2024-01-15T11:00:00Z",
        "framework": "langchain",
        "confidence": "high",
        "confidence_score": 89.2,
        "github_url": "https://github.com/langchain-ai/langchain/examples/customer_support",
        "repository": {
            "owner": "langchain-ai",
            "name": "langchain-example",
            "description": "Customer support chatbot using LangChain",
            "language": "Python"
        },
        "components": [
            {
                "name": "intent_classifier",
                "type": "chain",
                "model": "gpt-3.5-turbo",
                "estimated_tokens": 800,
                "file_path": "customer_support.py",
                "line_number": 12,
                "metadata": {
                    "chain_type": "LLMChain",
                    "prompt_template": "Classify the customer intent from: {query}"
                }
            },
            {
                "name": "query_router",
                "type": "chain",
                "model": "gpt-3.5-turbo",
                "estimated_tokens": 600,
                "file_path": "customer_support.py", 
                "line_number": 20,
                "metadata": {
                    "chain_type": "LLMChain",
                    "routing_options": ["billing", "technical", "general"]
                }
            },
            {
                "name": "response_generator",
                "type": "chain",
                "model": "gpt-4",
                "estimated_tokens": 2000,
                "file_path": "customer_support.py",
                "line_number": 30,
                "metadata": {
                    "chain_type": "LLMChain",
                    "uses_context": True,
                    "max_tokens": 500
                }
            },
            {
                "name": "embeddings",
                "type": "llm",
                "model": "text-embedding-ada-002",
                "estimated_tokens": 200,
                "file_path": "customer_support.py",
                "line_number": 8,
                "metadata": {
                    "embedding_dimension": 1536,
                    "purpose": "semantic_search"
                }
            }
        ],
        "total_original_cost": 0.0713,
        "total_optimized_cost": 0.0189,
        "total_savings": 0.0524,
        "savings_percentage": 73.5,
        "optimizations": [
            {
                "type": "model_substitution",
                "original_cost": 0.0004,
                "optimized_cost": 0.0001,
                "savings": 0.0003,
                "savings_percent": 75.0,
                "explanation": "Used Claude-3-Haiku for intent classification"
            },
            {
                "type": "model_substitution",
                "original_cost": 0.0003,
                "optimized_cost": 0.0001,
                "savings": 0.0002,
                "savings_percent": 66.7,
                "explanation": "Used Claude-3-Haiku for query routing"
            },
            {
                "type": "semantic_caching",
                "original_cost": 0.0706,
                "optimized_cost": 0.0187,
                "savings": 0.0519,
                "savings_percent": 73.5,
                "explanation": "Applied semantic caching with 20% hit rate for customer support queries"
            }
        ],
        "recommendations": [
            "Implement smart model routing to save $0.05 per conversation. Use Claude-3-Haiku for classification and routing.",
            "Enable semantic caching for common customer queries with 20-30% expected hit rate.",
            "Parallelize intent classification and embedding generation to reduce latency by ~50%.",
            "Optimize prompt templates to reduce token usage by 15-20%."
        ],
        "execution_optimizations": {
            "parallel_opportunities": [
                {
                    "type": "parallel_chains",
                    "chains": ["intent_classifier", "embeddings"],
                    "estimated_time_savings": 0.5
                }
            ],
            "cache_opportunities": [
                {
                    "component": "intent_classifier",
                    "cache_potential": "high",
                    "estimated_hit_rate": 0.35
                },
                {
                    "component": "query_router",
                    "cache_potential": "high", 
                    "estimated_hit_rate": 0.30
                },
                {
                    "component": "embeddings",
                    "cache_potential": "medium",
                    "estimated_hit_rate": 0.20
                }
            ]
        }
    },

    "crewai": {
        "analysis_id": "example_crewai_001", 
        "timestamp": "2024-01-15T11:30:00Z",
        "framework": "crewai",
        "confidence": "medium",
        "confidence_score": 78.5,
        "github_url": "https://github.com/joaomdmoura/crewAI/examples/content_creation",
        "repository": {
            "owner": "joaomdmoura",
            "name": "crewai-example",
            "description": "Content creation crew using CrewAI",
            "language": "Python"
        },
        "components": [
            {
                "name": "researcher_agent",
                "type": "agent",
                "model": "gpt-4",
                "estimated_tokens": 1800,
                "file_path": "content_crew.py",
                "line_number": 15,
                "metadata": {
                    "role": "Content Researcher",
                    "goal": "Research trending topics and gather relevant information"
                }
            },
            {
                "name": "writer_agent", 
                "type": "agent",
                "model": "gpt-4",
                "estimated_tokens": 2500,
                "file_path": "content_crew.py",
                "line_number": 25,
                "metadata": {
                    "role": "Content Writer",
                    "goal": "Create engaging content based on research findings"
                }
            },
            {
                "name": "editor_agent",
                "type": "agent",
                "model": "gpt-4",
                "estimated_tokens": 1200,
                "file_path": "content_crew.py",
                "line_number": 35,
                "metadata": {
                    "role": "Content Editor",
                    "goal": "Review and polish content for publication"
                }
            }
        ],
        "total_original_cost": 0.1650,
        "total_optimized_cost": 0.0495,
        "total_savings": 0.1155,
        "savings_percentage": 70.0,
        "optimizations": [
            {
                "type": "model_substitution",
                "original_cost": 0.0540,
                "optimized_cost": 0.0135,
                "savings": 0.0405,
                "savings_percent": 75.0,
                "explanation": "Used Claude-3-Sonnet for research tasks"
            },
            {
                "type": "model_substitution",
                "original_cost": 0.0360,
                "optimized_cost": 0.0030,
                "savings": 0.0330,
                "savings_percent": 91.7,
                "explanation": "Used Claude-3-Haiku for editing tasks"
            },
            {
                "type": "semantic_caching", 
                "original_cost": 0.0750,
                "optimized_cost": 0.0330,
                "savings": 0.0420,
                "savings_percent": 56.0,
                "explanation": "Applied caching for research queries and common editing patterns"
            }
        ],
        "recommendations": [
            "Implement tiered model routing: Claude-3-Sonnet for research, Claude-3-Haiku for editing.",
            "Enable semantic caching for research queries and common editing patterns.",
            "Use sequential workflow optimization to reduce redundant context passing.",
            "Implement content templates to reduce token usage in writing tasks."
        ],
        "execution_optimizations": {
            "parallel_opportunities": [
                {
                    "type": "sequential_optimization",
                    "description": "Optimize handoffs between agents",
                    "estimated_time_savings": 0.2
                }
            ],
            "cache_opportunities": [
                {
                    "component": "researcher_agent",
                    "cache_potential": "medium",
                    "estimated_hit_rate": 0.20
                },
                {
                    "component": "editor_agent",
                    "cache_potential": "high",
                    "estimated_hit_rate": 0.35
                }
            ]
        }
    }
}


@router.get("/examples")
async def get_examples():
    """
    Get example analyses for popular frameworks
    
    Returns a list of available example analyses that demonstrate
    Signal Box optimizations on real-world AI workflows.
    """
    return {
        "examples": [
            {
                "id": "autogen",
                "name": "AutoGen Multi-Agent Research Assistant",
                "framework": "autogen", 
                "description": "Multi-agent system with coordinator, researcher, analyst, and web search agents",
                "savings_percentage": EXAMPLE_ANALYSES["autogen"]["savings_percentage"],
                "total_savings": EXAMPLE_ANALYSES["autogen"]["total_savings"],
                "components_count": len(EXAMPLE_ANALYSES["autogen"]["components"]),
                "github_url": EXAMPLE_ANALYSES["autogen"]["github_url"]
            },
            {
                "id": "langchain",
                "name": "LangChain Customer Support Bot",
                "framework": "langchain",
                "description": "Customer support chatbot with intent classification, routing, and response generation",
                "savings_percentage": EXAMPLE_ANALYSES["langchain"]["savings_percentage"],
                "total_savings": EXAMPLE_ANALYSES["langchain"]["total_savings"], 
                "components_count": len(EXAMPLE_ANALYSES["langchain"]["components"]),
                "github_url": EXAMPLE_ANALYSES["langchain"]["github_url"]
            },
            {
                "id": "crewai",
                "name": "CrewAI Content Creation Team", 
                "framework": "crewai",
                "description": "Content creation crew with researcher, writer, and editor agents",
                "savings_percentage": EXAMPLE_ANALYSES["crewai"]["savings_percentage"],
                "total_savings": EXAMPLE_ANALYSES["crewai"]["total_savings"],
                "components_count": len(EXAMPLE_ANALYSES["crewai"]["components"]),
                "github_url": EXAMPLE_ANALYSES["crewai"]["github_url"]
            }
        ],
        "total_examples": 3,
        "note": "These are pre-computed examples demonstrating Signal Box optimizations on popular AI frameworks"
    }


@router.get("/examples/{framework}")
async def get_example_analysis(framework: str):
    """
    Get detailed analysis for a specific framework example
    
    Args:
        framework: Framework name (autogen, langchain, crewai)
        
    Returns:
        Detailed analysis results showing costs, optimizations, and recommendations
    """
    if framework not in EXAMPLE_ANALYSES:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"Example not found for framework: {framework}. Available: {list(EXAMPLE_ANALYSES.keys())}"
        )
    
    # Add current timestamp to make it feel fresh
    example = EXAMPLE_ANALYSES[framework].copy()
    example["viewed_at"] = datetime.now().isoformat()
    example["note"] = "This is a pre-computed example analysis demonstrating Signal Box optimizations"
    
    return example


@router.get("/examples/{framework}/report")
async def get_example_report(framework: str, format: str = "html"):
    """
    Get the full report for an example analysis
    
    Args:
        framework: Framework name
        format: Report format (html or json)
        
    Returns:
        Full analysis report in requested format
    """
    if framework not in EXAMPLE_ANALYSES:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"Example not found for framework: {framework}"
        )
    
    example = EXAMPLE_ANALYSES[framework]
    
    if format == "json":
        return example
    
    elif format == "html":
        # Generate a simple HTML report for the example
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Signal Box Analysis: {framework.title()} Example</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 8px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .metric {{ 
                    display: inline-block; 
                    margin: 15px; 
                    text-align: center;
                    background: rgba(255,255,255,0.2);
                    padding: 20px;
                    border-radius: 8px;
                    min-width: 150px;
                }}
                .metric-value {{ 
                    font-size: 2rem; 
                    font-weight: bold; 
                    display: block;
                }}
                .savings {{ color: #48bb78; }}
                .component {{ 
                    background: #f7fafc; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 6px;
                    border-left: 4px solid #667eea;
                }}
                .optimization {{ 
                    background: #f0fff4; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 6px;
                    border-left: 4px solid #48bb78;
                }}
                .recommendation {{ 
                    background: #fffbeb; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 6px;
                    border-left: 4px solid #f6ad55;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Signal Box Analysis</h1>
                    <h2>{framework.title()} Example - {example['repository']['description']}</h2>
                    
                    <div class="metric">
                        <span class="metric-value savings">{example['savings_percentage']:.1f}%</span>
                        <span>Cost Reduction</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${example['total_original_cost']:.4f}</span>
                        <span>Original Cost</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${example['total_optimized_cost']:.4f}</span>
                        <span>Optimized Cost</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value savings">${example['total_savings']:.4f}</span>
                        <span>Savings per Run</span>
                    </div>
                </div>
                
                <h2>🔧 Components Analyzed</h2>
                {' '.join([f'<div class="component"><strong>{comp["name"]}</strong> ({comp["type"]}) - Model: {comp["model"] or "Not specified"}<br>Tokens: {comp["estimated_tokens"] or "Estimated"} | File: {comp["file_path"]}</div>' for comp in example['components']])}
                
                <h2>🎯 Optimizations Applied</h2>
                {' '.join([f'<div class="optimization"><strong>{opt["type"].replace("_", " ").title()}</strong><br>Savings: ${opt["savings"]:.4f} ({opt["savings_percent"]:.1f}%)<br>{opt["explanation"]}</div>' for opt in example['optimizations']])}
                
                <h2>💡 Recommendations</h2>
                {' '.join([f'<div class="recommendation">• {rec}</div>' for rec in example['recommendations']])}
                
                <div style="margin-top: 40px; padding: 20px; background: #f7fafc; border-radius: 8px; text-align: center;">
                    <p><strong>Note:</strong> This is a pre-computed example demonstrating Signal Box optimizations.</p>
                    <p>Ready to analyze your own repository? <a href="/docs">Try the API</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
    
    else:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Use 'html' or 'json'"
        )