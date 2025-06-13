"""
Optimization Engine for Signal Box
Time estimate: 3 hours
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import re

from .calculator import CostCalculator, CostCalculation, OptimizationResult
from .detectors.base import Component, DetectionResult


class OptimizationType(Enum):
    """Types of optimizations available"""
    MODEL_SUBSTITUTION = "model_substitution"
    SEMANTIC_CACHING = "semantic_caching"
    TOKEN_REDUCTION = "token_reduction"
    PARALLEL_EXECUTION = "parallel_execution"
    LOOP_PREVENTION = "loop_prevention"
    BATCH_PROCESSING = "batch_processing"


@dataclass
class OptimizationStrategy:
    """A specific optimization strategy"""
    type: OptimizationType
    name: str
    description: str
    applicable_to: List[str]  # Component types this applies to
    estimated_savings: float  # 0-1 percentage
    implementation_notes: str
    priority: int = 1  # Higher = apply first


@dataclass
class OptimizedWorkflow:
    """Result of optimizing an entire workflow"""
    original_components: List[Component]
    optimized_components: List[Component]
    
    # Cost analysis
    original_calculations: List[CostCalculation]
    optimized_calculations: List[CostCalculation]
    optimization_results: List[OptimizationResult]
    
    # Summary
    total_original_cost: float
    total_optimized_cost: float
    total_savings: float
    savings_percentage: float
    
    # Applied strategies
    strategies_applied: List[OptimizationStrategy]
    
    # Execution optimizations
    parallel_opportunities: List[Dict[str, Any]]
    cache_opportunities: List[Dict[str, Any]]
    
    # Recommendations
    recommendations: List[str]


class OptimizationEngine:
    """Engine for applying Signal Box optimizations"""
    
    def __init__(self):
        self.calculator = CostCalculator()
        self.strategies = self._initialize_strategies()
        
        # Task classification rules
        self.task_classifiers = {
            'classification': ['classify', 'categorize', 'filter', 'route', 'check'],
            'formatting': ['format', 'template', 'structure', 'parse', 'convert'],
            'validation': ['validate', 'verify', 'check', 'ensure', 'confirm'],
            'extraction': ['extract', 'find', 'search', 'locate', 'identify'],
            'summarization': ['summarize', 'tldr', 'brief', 'overview', 'synopsis'],
            'generation': ['generate', 'create', 'write', 'produce', 'compose'],
            'analysis': ['analyze', 'examine', 'investigate', 'study', 'evaluate'],
            'qa': ['question', 'answer', 'ask', 'respond', 'query']
        }
        
        # Model substitution rules
        self.model_substitutions = {
            'gpt-4': {
                'classification': 'claude-3-haiku',
                'formatting': 'claude-3-haiku',
                'validation': 'gpt-3.5-turbo',
                'extraction': 'gpt-3.5-turbo',
                'summarization': 'claude-3-sonnet'
            },
            'gpt-3.5-turbo': {
                'classification': 'claude-3-haiku',
                'formatting': 'claude-3-haiku'
            },
            'claude-3-opus': {
                'classification': 'claude-3-haiku',
                'formatting': 'claude-3-haiku',
                'validation': 'claude-3-haiku',
                'extraction': 'claude-3-sonnet'
            }
        }
    
    def _initialize_strategies(self) -> List[OptimizationStrategy]:
        """Initialize optimization strategies"""
        return [
            OptimizationStrategy(
                type=OptimizationType.MODEL_SUBSTITUTION,
                name="Smart Model Routing",
                description="Use cheaper models for simple tasks",
                applicable_to=['agent', 'chain', 'llm'],
                estimated_savings=0.7,
                implementation_notes="Analyze task complexity and route to appropriate model",
                priority=1
            ),
            OptimizationStrategy(
                type=OptimizationType.SEMANTIC_CACHING,
                name="Intelligent Caching",
                description="Cache similar queries and responses",
                applicable_to=['agent', 'chain', 'llm'],
                estimated_savings=0.15,
                implementation_notes="Use vector similarity for semantic matching",
                priority=2
            ),
            OptimizationStrategy(
                type=OptimizationType.TOKEN_REDUCTION,
                name="Prompt Optimization",
                description="Reduce tokens through better prompting",
                applicable_to=['agent', 'chain', 'prompt'],
                estimated_savings=0.2,
                implementation_notes="Compress prompts, remove redundancy",
                priority=3
            ),
            OptimizationStrategy(
                type=OptimizationType.PARALLEL_EXECUTION,
                name="Parallel Processing",
                description="Execute independent operations in parallel",
                applicable_to=['agent', 'chain'],
                estimated_savings=0.0,  # Time savings, not cost
                implementation_notes="Identify independent operations for parallel execution",
                priority=4
            ),
            OptimizationStrategy(
                type=OptimizationType.LOOP_PREVENTION,
                name="Circular Call Prevention",
                description="Prevent agent communication loops",
                applicable_to=['agent', 'groupchat'],
                estimated_savings=0.25,
                implementation_notes="Detect and break circular dependencies",
                priority=5
            ),
            OptimizationStrategy(
                type=OptimizationType.BATCH_PROCESSING,
                name="Request Batching",
                description="Batch multiple requests together",
                applicable_to=['llm', 'chain'],
                estimated_savings=0.1,
                implementation_notes="Combine multiple small requests",
                priority=6
            )
        ]
    
    def classify_task(self, component: Component) -> str:
        """Classify the task type based on component information"""
        # Check component name
        comp_name = component.name.lower()
        
        for task_type, keywords in self.task_classifiers.items():
            if any(keyword in comp_name for keyword in keywords):
                return task_type
        
        # Check metadata
        if component.metadata:
            # Check system message for AutoGen agents
            system_msg = component.metadata.get('system_message', '').lower()
            for task_type, keywords in self.task_classifiers.items():
                if any(keyword in system_msg for keyword in keywords):
                    return task_type
            
            # Check prompt templates for LangChain
            template = component.metadata.get('template', '').lower()
            for task_type, keywords in self.task_classifiers.items():
                if any(keyword in template for keyword in keywords):
                    return task_type
        
        return 'general'
    
    def suggest_model_substitution(self, component: Component, task_type: str) -> Optional[str]:
        """Suggest a more efficient model for the task"""
        current_model = component.model
        
        if not current_model:
            return None
        
        # Check substitution rules
        if current_model in self.model_substitutions:
            substitutions = self.model_substitutions[current_model]
            if task_type in substitutions:
                return substitutions[task_type]
        
        # General rules
        if task_type in ['classification', 'formatting', 'validation']:
            if current_model in ['gpt-4', 'claude-3-opus']:
                return 'claude-3-haiku'
            elif current_model == 'gpt-3.5-turbo':
                return 'claude-3-haiku'
        
        return None
    
    def identify_parallel_opportunities(self, 
                                      components: List[Component],
                                      workflow_patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify operations that can run in parallel"""
        opportunities = []
        
        # For AutoGen: Find agents that don't depend on each other
        agent_components = [c for c in components if c.type == 'agent']
        if len(agent_components) > 1:
            # Simple heuristic: agents with no direct calls between them
            independent_groups = []
            
            # Analyze workflow patterns for dependencies
            dependencies = {}
            for pattern in workflow_patterns:
                if pattern.get('type') == 'chat':
                    from_agent = pattern.get('from')
                    to_agent = pattern.get('to')
                    if from_agent not in dependencies:
                        dependencies[from_agent] = []
                    dependencies[from_agent].append(to_agent)
            
            # Find independent agents
            for agent in agent_components:
                agent_name = agent.name
                if agent_name not in dependencies:
                    # This agent doesn't call others
                    for group in independent_groups:
                        # Check if it's called by any in the group
                        if not any(agent_name in dependencies.get(g.name, []) for g in group):
                            group.append(agent)
                            break
                    else:
                        independent_groups.append([agent])
            
            # Report parallel opportunities
            for group in independent_groups:
                if len(group) > 1:
                    opportunities.append({
                        'type': 'parallel_agents',
                        'agents': [a.name for a in group],
                        'estimated_time_savings': 0.3
                    })
        
        # For LangChain: Find independent chains
        chain_components = [c for c in components if c.type == 'chain']
        if len(chain_components) > 1:
            # Look for chains not in sequential flows
            sequential_chains = []
            for pattern in workflow_patterns:
                if pattern.get('type') == 'sequential':
                    sequential_chains.extend(pattern.get('chains', []))
            
            independent_chains = [
                c for c in chain_components 
                if c.name not in sequential_chains
            ]
            
            if len(independent_chains) > 1:
                opportunities.append({
                    'type': 'parallel_chains',
                    'chains': [c.name for c in independent_chains],
                    'estimated_time_savings': 0.4
                })
        
        return opportunities
    
    def identify_cache_opportunities(self, components: List[Component]) -> List[Dict[str, Any]]:
        """Identify caching opportunities"""
        opportunities = []
        
        # Components with static or semi-static outputs
        for component in components:
            task_type = self.classify_task(component)
            
            # High cache potential
            if task_type in ['classification', 'validation', 'formatting']:
                opportunities.append({
                    'component': component.name,
                    'type': component.type,
                    'task_type': task_type,
                    'cache_potential': 'high',
                    'estimated_hit_rate': 0.3
                })
            # Medium cache potential
            elif task_type in ['extraction', 'qa']:
                opportunities.append({
                    'component': component.name,
                    'type': component.type,
                    'task_type': task_type,
                    'cache_potential': 'medium',
                    'estimated_hit_rate': 0.15
                })
            # Low cache potential
            elif task_type in ['generation', 'analysis']:
                opportunities.append({
                    'component': component.name,
                    'type': component.type,
                    'task_type': task_type,
                    'cache_potential': 'low',
                    'estimated_hit_rate': 0.05
                })
        
        return opportunities
    
    def optimize_workflow(self, 
                         detection_result: DetectionResult,
                         detailed: bool = True) -> OptimizedWorkflow:
        """
        Optimize an entire workflow
        
        Args:
            detection_result: Detection result with components
            detailed: Whether to include detailed calculations
            
        Returns:
            OptimizedWorkflow with full analysis
        """
        components = detection_result.components
        workflow_patterns = detection_result.workflow_patterns
        
        # Calculate baseline costs
        original_calculations = []
        total_original_cost = 0
        
        for component in components:
            # Estimate tokens if not provided
            if not component.estimated_tokens:
                # Default estimation based on component type
                if component.type == 'agent':
                    component.estimated_tokens = 1500  # Typical agent interaction
                elif component.type == 'chain':
                    component.estimated_tokens = 1000
                else:
                    component.estimated_tokens = 500
            
            # Use component's model or default
            model = component.model or 'gpt-3.5-turbo'
            
            # Calculate cost
            calc = self.calculator.calculate_cost(
                component.estimated_tokens,
                int(component.estimated_tokens * 0.3),  # Output estimate
                model,
                f"Component: {component.name}"
            )
            
            original_calculations.append(calc)
            total_original_cost += calc.total_cost
        
        # Apply optimizations
        optimized_calculations = []
        optimization_results = []
        strategies_applied = []
        total_optimized_cost = 0
        
        for i, component in enumerate(components):
            original_calc = original_calculations[i]
            best_calc = original_calc
            best_result = None
            
            # Try different optimizations
            applied_optimizations = []
            
            # 1. Model substitution
            task_type = self.classify_task(component)
            suggested_model = self.suggest_model_substitution(component, task_type)
            
            if suggested_model:
                opt_calc, opt_result = self.calculator.apply_optimization(
                    original_calc,
                    'model_substitution',
                    target_model=suggested_model,
                    reason=f"Task type '{task_type}' can use more efficient model"
                )
                
                if opt_calc.total_cost < best_calc.total_cost:
                    best_calc = opt_calc
                    best_result = opt_result
                    applied_optimizations.append(self.strategies[0])
            
            # 2. Caching (if applicable)
            cache_opps = self.identify_cache_opportunities([component])
            if cache_opps and cache_opps[0]['cache_potential'] in ['high', 'medium']:
                cache_rate = cache_opps[0]['estimated_hit_rate']
                
                opt_calc, opt_result = self.calculator.apply_optimization(
                    best_calc,
                    'caching',
                    cache_hit_rate=cache_rate
                )
                
                if opt_calc.total_cost < best_calc.total_cost:
                    best_calc = opt_calc
                    if best_result:
                        # Combine optimizations
                        best_result.savings += opt_result.savings
                        best_result.explanation += f" + {opt_result.explanation}"
                    else:
                        best_result = opt_result
                    applied_optimizations.append(self.strategies[1])
            
            # 3. Token reduction (for certain tasks)
            if task_type in ['summarization', 'extraction']:
                opt_calc, opt_result = self.calculator.apply_optimization(
                    best_calc,
                    'token_reduction',
                    reduction_rate=0.2
                )
                
                if opt_calc.total_cost < best_calc.total_cost:
                    best_calc = opt_calc
                    if best_result:
                        best_result.savings += opt_result.savings
                        best_result.explanation += f" + {opt_result.explanation}"
                    else:
                        best_result = opt_result
                    applied_optimizations.append(self.strategies[2])
            
            optimized_calculations.append(best_calc)
            if best_result:
                optimization_results.append(best_result)
            
            strategies_applied.extend(applied_optimizations)
            total_optimized_cost += best_calc.total_cost
        
        # Remove duplicate strategies
        unique_strategies = []
        seen = set()
        for strategy in strategies_applied:
            if strategy.name not in seen:
                seen.add(strategy.name)
                unique_strategies.append(strategy)
        
        # Identify execution optimizations
        parallel_opportunities = self.identify_parallel_opportunities(components, workflow_patterns)
        cache_opportunities = self.identify_cache_opportunities(components)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            components,
            optimization_results,
            parallel_opportunities,
            cache_opportunities
        )
        
        # Calculate summary
        total_savings = total_original_cost - total_optimized_cost
        savings_percentage = (total_savings / total_original_cost * 100) if total_original_cost > 0 else 0
        
        return OptimizedWorkflow(
            original_components=components,
            optimized_components=components,  # Components with updated models
            original_calculations=original_calculations,
            optimized_calculations=optimized_calculations,
            optimization_results=optimization_results,
            total_original_cost=total_original_cost,
            total_optimized_cost=total_optimized_cost,
            total_savings=total_savings,
            savings_percentage=savings_percentage,
            strategies_applied=unique_strategies,
            parallel_opportunities=parallel_opportunities,
            cache_opportunities=cache_opportunities,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self,
                                components: List[Component],
                                optimization_results: List[OptimizationResult],
                                parallel_opportunities: List[Dict[str, Any]],
                                cache_opportunities: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Model substitution recommendations
        model_savings = sum(r.savings for r in optimization_results 
                          if r.optimization_type == 'model_substitution')
        if model_savings > 0:
            recommendations.append(
                f"Implement smart model routing to save ${model_savings:.2f} per run. "
                "Use Claude-3-Haiku for simple tasks like classification and formatting."
            )
        
        # Caching recommendations
        high_cache = [c for c in cache_opportunities if c['cache_potential'] == 'high']
        if high_cache:
            recommendations.append(
                f"Enable semantic caching for {len(high_cache)} components with high cache potential. "
                "Expected 15-30% hit rate for classification and validation tasks."
            )
        
        # Parallel execution
        if parallel_opportunities:
            time_savings = sum(p.get('estimated_time_savings', 0) for p in parallel_opportunities)
            recommendations.append(
                f"Parallelize {len(parallel_opportunities)} independent operations to reduce "
                f"execution time by ~{time_savings*100:.0f}%."
            )
        
        # Loop prevention (for multi-agent systems)
        if any(c.type == 'agent' for c in components) and len(components) > 3:
            recommendations.append(
                "Implement loop detection to prevent circular agent calls. "
                "This can reduce costs by 25% in complex multi-agent conversations."
            )
        
        # Token optimization
        total_tokens = sum(c.estimated_tokens or 0 for c in components)
        if total_tokens > 5000:
            recommendations.append(
                "Optimize prompts to reduce token usage by 20%. "
                "Focus on system prompts and repeated templates."
            )
        
        return recommendations