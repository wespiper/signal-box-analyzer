"""
Cost Calculator with transparent calculations and audit trail
Time estimate: 2 hours
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


@dataclass
class ModelPricing:
    """Pricing information for a model"""
    model_id: str
    provider: str
    input_cost_per_1k: float  # Cost per 1K input tokens
    output_cost_per_1k: float  # Cost per 1K output tokens
    context_window: int
    notes: str = ""


@dataclass
class TokenEstimate:
    """Token estimate with breakdown"""
    input_tokens: int
    output_tokens: int
    reasoning: str
    confidence: float = 0.8  # 0-1 confidence in estimate


@dataclass
class CostCalculation:
    """Single cost calculation with full transparency"""
    step_id: str
    description: str
    
    # Input values
    input_tokens: int
    output_tokens: int
    model: str
    input_price_per_1k: float
    output_price_per_1k: float
    
    # Calculations
    input_calculation: str  # e.g., "1500 × $0.03/1K = $0.045"
    output_calculation: str  # e.g., "500 × $0.06/1K = $0.030"
    total_calculation: str  # e.g., "$0.045 + $0.030 = $0.075"
    
    # Results
    input_cost: float
    output_cost: float
    total_cost: float
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    assumptions: Dict[str, any] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Result of applying an optimization"""
    optimization_type: str
    original_cost: float
    optimized_cost: float
    savings: float
    savings_percent: float
    explanation: str
    calculation_details: str


class CostCalculator:
    """Transparent cost calculator with audit trail"""
    
    def __init__(self):
        # Initialize model pricing data
        self.model_pricing = self._initialize_pricing()
        
        # Default token ratios
        self.default_output_ratio = 0.3  # Output is typically 30% of input
        
        # Token estimation rules
        self.token_rules = {
            'system_prompt': 1.2,  # System prompts are token-dense
            'code_generation': 2.5,  # Code outputs are longer
            'summarization': 0.5,  # Summaries are shorter
            'qa': 0.8,  # Q&A is balanced
            'classification': 0.1,  # Classifications are short
        }
    
    def _initialize_pricing(self) -> Dict[str, ModelPricing]:
        """Initialize model pricing data"""
        return {
            # OpenAI Models
            'gpt-4': ModelPricing(
                'gpt-4', 'openai', 0.03, 0.06, 8192,
                "Most capable, best for complex tasks"
            ),
            'gpt-4-turbo': ModelPricing(
                'gpt-4-turbo', 'openai', 0.01, 0.03, 128000,
                "Faster, cheaper GPT-4 variant"
            ),
            'gpt-4-turbo-preview': ModelPricing(
                'gpt-4-turbo-preview', 'openai', 0.01, 0.03, 128000,
                "Preview version of GPT-4 Turbo"
            ),
            'gpt-3.5-turbo': ModelPricing(
                'gpt-3.5-turbo', 'openai', 0.0005, 0.0015, 16385,
                "Fast, good for simple tasks"
            ),
            'gpt-3.5-turbo-16k': ModelPricing(
                'gpt-3.5-turbo-16k', 'openai', 0.003, 0.004, 16385,
                "Extended context GPT-3.5"
            ),
            
            # Anthropic Models
            'claude-3-opus': ModelPricing(
                'claude-3-opus', 'anthropic', 0.015, 0.075, 200000,
                "Most capable Claude model"
            ),
            'claude-3-sonnet': ModelPricing(
                'claude-3-sonnet', 'anthropic', 0.003, 0.015, 200000,
                "Balanced performance and cost"
            ),
            'claude-3-haiku': ModelPricing(
                'claude-3-haiku', 'anthropic', 0.00025, 0.00125, 200000,
                "Fast, efficient for simple tasks"
            ),
            'claude-2.1': ModelPricing(
                'claude-2.1', 'anthropic', 0.008, 0.024, 200000,
                "Previous generation Claude"
            ),
            
            # Other Models
            'text-embedding-ada-002': ModelPricing(
                'text-embedding-ada-002', 'openai', 0.0001, 0.0001, 8191,
                "Embedding model"
            ),
            'text-davinci-003': ModelPricing(
                'text-davinci-003', 'openai', 0.02, 0.02, 4097,
                "Legacy completion model"
            ),
        }
    
    def estimate_tokens(self, text: str, operation_type: str = 'general') -> TokenEstimate:
        """
        Estimate tokens with transparent reasoning
        
        Args:
            text: The text to estimate tokens for
            operation_type: Type of operation (affects output estimation)
        
        Returns:
            TokenEstimate with breakdown
        """
        # Base calculation: ~4 characters per token
        base_tokens = len(text) // 4
        
        # Apply operation-specific adjustments
        multiplier = self.token_rules.get(operation_type, 1.0)
        input_tokens = int(base_tokens * multiplier)
        
        # Estimate output tokens based on operation
        output_ratio = {
            'code_generation': 2.5,
            'summarization': 0.3,
            'classification': 0.1,
            'qa': 0.8,
            'general': self.default_output_ratio
        }.get(operation_type, self.default_output_ratio)
        
        output_tokens = int(input_tokens * output_ratio)
        
        reasoning = (
            f"Text length: {len(text)} chars ≈ {base_tokens} base tokens\n"
            f"Operation type: {operation_type} (multiplier: {multiplier})\n"
            f"Input tokens: {base_tokens} × {multiplier} = {input_tokens}\n"
            f"Output tokens: {input_tokens} × {output_ratio} = {output_tokens}"
        )
        
        return TokenEstimate(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            reasoning=reasoning,
            confidence=0.8 if operation_type != 'general' else 0.6
        )
    
    def calculate_cost(self, 
                      input_tokens: int,
                      output_tokens: int,
                      model: str,
                      description: str = "") -> CostCalculation:
        """
        Calculate cost with full transparency
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier
            description: Description of this calculation
            
        Returns:
            CostCalculation with complete audit trail
        """
        # Get pricing
        pricing = self.model_pricing.get(model)
        if not pricing:
            # Default to GPT-3.5 pricing if model not found
            pricing = self.model_pricing['gpt-3.5-turbo']
            model = f"{model} (using gpt-3.5-turbo pricing)"
        
        # Calculate costs
        input_cost = (input_tokens / 1000) * pricing.input_cost_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_cost_per_1k
        total_cost = input_cost + output_cost
        
        # Create readable calculations
        input_calc = f"{input_tokens} tokens × ${pricing.input_cost_per_1k}/1K = ${input_cost:.4f}"
        output_calc = f"{output_tokens} tokens × ${pricing.output_cost_per_1k}/1K = ${output_cost:.4f}"
        total_calc = f"${input_cost:.4f} + ${output_cost:.4f} = ${total_cost:.4f}"
        
        return CostCalculation(
            step_id=f"calc_{datetime.now().timestamp()}",
            description=description or f"Cost calculation for {model}",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            input_price_per_1k=pricing.input_cost_per_1k,
            output_price_per_1k=pricing.output_cost_per_1k,
            input_calculation=input_calc,
            output_calculation=output_calc,
            total_calculation=total_calc,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            assumptions={
                'provider': pricing.provider,
                'context_window': pricing.context_window,
                'pricing_notes': pricing.notes
            }
        )
    
    def apply_optimization(self,
                         original_calc: CostCalculation,
                         optimization_type: str,
                         **kwargs) -> Tuple[CostCalculation, OptimizationResult]:
        """
        Apply optimization and show the impact
        
        Args:
            original_calc: Original cost calculation
            optimization_type: Type of optimization to apply
            **kwargs: Optimization-specific parameters
            
        Returns:
            Tuple of (optimized calculation, optimization result)
        """
        if optimization_type == 'model_substitution':
            return self._apply_model_substitution(original_calc, **kwargs)
        elif optimization_type == 'caching':
            return self._apply_caching(original_calc, **kwargs)
        elif optimization_type == 'token_reduction':
            return self._apply_token_reduction(original_calc, **kwargs)
        else:
            # No optimization
            return original_calc, OptimizationResult(
                optimization_type="none",
                original_cost=original_calc.total_cost,
                optimized_cost=original_calc.total_cost,
                savings=0,
                savings_percent=0,
                explanation="No optimization applied",
                calculation_details=""
            )
    
    def _apply_model_substitution(self, 
                                original_calc: CostCalculation,
                                target_model: str,
                                reason: str = "") -> Tuple[CostCalculation, OptimizationResult]:
        """Apply model substitution optimization"""
        
        # Calculate new cost with different model
        new_calc = self.calculate_cost(
            original_calc.input_tokens,
            original_calc.output_tokens,
            target_model,
            f"{original_calc.description} (optimized with {target_model})"
        )
        
        # Calculate savings
        savings = original_calc.total_cost - new_calc.total_cost
        savings_percent = (savings / original_calc.total_cost) * 100 if original_calc.total_cost > 0 else 0
        
        explanation = reason or f"Substituted {original_calc.model} with {target_model} for this task"
        
        calculation_details = (
            f"Original model: {original_calc.model}\n"
            f"Original cost: {original_calc.total_calculation}\n"
            f"Optimized model: {target_model}\n"
            f"Optimized cost: {new_calc.total_calculation}\n"
            f"Savings: ${savings:.4f} ({savings_percent:.1f}%)"
        )
        
        result = OptimizationResult(
            optimization_type="model_substitution",
            original_cost=original_calc.total_cost,
            optimized_cost=new_calc.total_cost,
            savings=savings,
            savings_percent=savings_percent,
            explanation=explanation,
            calculation_details=calculation_details
        )
        
        return new_calc, result
    
    def _apply_caching(self,
                      original_calc: CostCalculation,
                      cache_hit_rate: float = 0.15) -> Tuple[CostCalculation, OptimizationResult]:
        """Apply caching optimization"""
        
        # Calculate effective cost with caching
        cache_cost_per_hit = 0.0001  # Minimal cost for cache hit
        
        # Expected cost = (1 - hit_rate) * original_cost + hit_rate * cache_cost
        expected_cost = (1 - cache_hit_rate) * original_calc.total_cost + cache_hit_rate * cache_cost_per_hit
        
        # Create new calculation reflecting caching
        new_calc = CostCalculation(
            step_id=f"cached_{original_calc.step_id}",
            description=f"{original_calc.description} (with {cache_hit_rate*100:.0f}% caching)",
            input_tokens=int(original_calc.input_tokens * (1 - cache_hit_rate)),
            output_tokens=int(original_calc.output_tokens * (1 - cache_hit_rate)),
            model=original_calc.model,
            input_price_per_1k=original_calc.input_price_per_1k,
            output_price_per_1k=original_calc.output_price_per_1k,
            input_calculation=f"{cache_hit_rate*100:.0f}% cached, {(1-cache_hit_rate)*100:.0f}% computed",
            output_calculation=f"Effective cost with caching",
            total_calculation=f"${original_calc.total_cost:.4f} × {1-cache_hit_rate:.2f} + ${cache_cost_per_hit:.4f} × {cache_hit_rate:.2f} = ${expected_cost:.4f}",
            input_cost=expected_cost * 0.4,  # Approximate split
            output_cost=expected_cost * 0.6,
            total_cost=expected_cost,
            assumptions={
                'cache_hit_rate': cache_hit_rate,
                'cache_cost_per_hit': cache_cost_per_hit
            }
        )
        
        savings = original_calc.total_cost - expected_cost
        savings_percent = (savings / original_calc.total_cost) * 100
        
        calculation_details = (
            f"Cache hit rate: {cache_hit_rate*100:.0f}%\n"
            f"Original cost per call: ${original_calc.total_cost:.4f}\n"
            f"Cache cost per hit: ${cache_cost_per_hit:.4f}\n"
            f"Expected cost: {new_calc.total_calculation}\n"
            f"Savings: ${savings:.4f} ({savings_percent:.1f}%)"
        )
        
        result = OptimizationResult(
            optimization_type="caching",
            original_cost=original_calc.total_cost,
            optimized_cost=expected_cost,
            savings=savings,
            savings_percent=savings_percent,
            explanation=f"Applied {cache_hit_rate*100:.0f}% semantic caching",
            calculation_details=calculation_details
        )
        
        return new_calc, result
    
    def _apply_token_reduction(self,
                             original_calc: CostCalculation,
                             reduction_rate: float = 0.2) -> Tuple[CostCalculation, OptimizationResult]:
        """Apply token reduction optimization"""
        
        # Calculate reduced tokens
        reduced_input = int(original_calc.input_tokens * (1 - reduction_rate))
        reduced_output = int(original_calc.output_tokens * (1 - reduction_rate))
        
        # Calculate new cost
        new_calc = self.calculate_cost(
            reduced_input,
            reduced_output,
            original_calc.model,
            f"{original_calc.description} (token-optimized)"
        )
        
        savings = original_calc.total_cost - new_calc.total_cost
        savings_percent = (savings / original_calc.total_cost) * 100
        
        calculation_details = (
            f"Token reduction: {reduction_rate*100:.0f}%\n"
            f"Original tokens: {original_calc.input_tokens} in, {original_calc.output_tokens} out\n"
            f"Optimized tokens: {reduced_input} in, {reduced_output} out\n"
            f"Original cost: ${original_calc.total_cost:.4f}\n"
            f"Optimized cost: ${new_calc.total_cost:.4f}\n"
            f"Savings: ${savings:.4f} ({savings_percent:.1f}%)"
        )
        
        result = OptimizationResult(
            optimization_type="token_reduction",
            original_cost=original_calc.total_cost,
            optimized_cost=new_calc.total_cost,
            savings=savings,
            savings_percent=savings_percent,
            explanation=f"Reduced tokens by {reduction_rate*100:.0f}% through better prompting",
            calculation_details=calculation_details
        )
        
        return new_calc, result
    
    def get_model_suggestions(self, task_type: str) -> List[Dict[str, str]]:
        """Get model suggestions for different task types"""
        suggestions = {
            'classification': [
                {'model': 'claude-3-haiku', 'reason': 'Fast and efficient for simple classifications'},
                {'model': 'gpt-3.5-turbo', 'reason': 'Good balance of speed and accuracy'}
            ],
            'code_generation': [
                {'model': 'gpt-4-turbo', 'reason': 'Best for complex code generation'},
                {'model': 'claude-3-sonnet', 'reason': 'Good alternative with large context'}
            ],
            'analysis': [
                {'model': 'claude-3-opus', 'reason': 'Excellent for deep analysis'},
                {'model': 'gpt-4', 'reason': 'Strong analytical capabilities'}
            ],
            'summarization': [
                {'model': 'claude-3-haiku', 'reason': 'Efficient for straightforward summaries'},
                {'model': 'gpt-3.5-turbo', 'reason': 'Fast and capable for most summaries'}
            ],
            'general': [
                {'model': 'gpt-3.5-turbo', 'reason': 'Good default for most tasks'},
                {'model': 'claude-3-sonnet', 'reason': 'Balanced performance and cost'}
            ]
        }
        
        return suggestions.get(task_type, suggestions['general'])