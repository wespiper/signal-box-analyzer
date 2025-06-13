"""
Report Generator for Signal Box Cost Analysis
Time estimate: 2 hours
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from .optimizer import OptimizedWorkflow
from .calculator import CostCalculation, OptimizationResult
from .detectors.base import DetectionResult, Component


@dataclass
class ReportConfig:
    """Configuration for report generation"""
    include_assumptions: bool = True
    include_calculations: bool = True
    include_recommendations: bool = True
    show_confidence_scores: bool = True
    format_currency: str = "USD"


class ReportGenerator:
    """Generates various report formats for cost analysis"""
    
    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
    
    def generate_html_report(self, 
                           detection_result: DetectionResult,
                           optimized_workflow: OptimizedWorkflow) -> str:
        """Generate a comprehensive HTML report"""
        
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Signal Box Cost Analysis Report</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="report-header">
            <h1>🚀 Signal Box Cost Analysis Report</h1>
            <div class="meta-info">
                <span class="timestamp">Generated: {timestamp}</span>
                <span class="framework">Framework: <strong>{detection_result.framework.upper()}</strong></span>
                <span class="confidence">Detection Confidence: <strong>{detection_result.confidence.value.title()}</strong></span>
            </div>
        </header>

        {self._generate_executive_summary(optimized_workflow)}
        
        {self._generate_cost_breakdown(optimized_workflow)}
        
        {self._generate_optimization_details(optimized_workflow)}
        
        {self._generate_component_analysis(detection_result.components, optimized_workflow)}
        
        {self._generate_recommendations(optimized_workflow)}
        
        {self._generate_assumptions_section(optimized_workflow)}
        
        <footer class="report-footer">
            <p>This report is fully auditable. All calculations, assumptions, and optimizations are transparent.</p>
            <p><strong>Signal Box</strong> - Enterprise AI Cost Optimization</p>
        </footer>
    </div>
</body>
</html>
        """
        
        return html
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .report-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .report-header h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            font-weight: 700;
        }
        
        .meta-info {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            font-size: 1.1rem;
        }
        
        .meta-info span {
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .section {
            padding: 40px;
        }
        
        .section h2 {
            color: #2d3748;
            font-size: 1.8rem;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .executive-summary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            text-align: center;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .metric-card {
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .savings-highlight {
            color: #48bb78;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e2e8f0;
        }
        
        tr:hover {
            background: #f7fafc;
        }
        
        .calculation-box {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 10px;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
            margin: 5px 0;
        }
        
        .optimization-badge {
            background: #48bb78;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
            display: inline-block;
        }
        
        .confidence-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
            display: inline-block;
        }
        
        .confidence-high { background: #48bb78; color: white; }
        .confidence-medium { background: #ed8936; color: white; }
        .confidence-low { background: #e53e3e; color: white; }
        
        .assumptions {
            background: #fffbeb;
            border: 1px solid #f6e05e;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .assumptions h3 {
            color: #92400e;
            margin-bottom: 15px;
        }
        
        .recommendations {
            background: #f0fff4;
            border: 1px solid #68d391;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .recommendations h3 {
            color: #2f855a;
            margin-bottom: 15px;
        }
        
        .recommendation-item {
            background: white;
            border-left: 4px solid #48bb78;
            padding: 15px;
            margin: 10px 0;
            border-radius: 0 8px 8px 0;
        }
        
        .report-footer {
            background: #2d3748;
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .component-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .component-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .component-header {
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        
        .component-meta {
            font-size: 0.9rem;
            color: #718096;
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .meta-info {
                flex-direction: column;
                align-items: center;
            }
            
            .metrics-grid {
                grid-template-columns: 1fr;
            }
            
            .component-grid {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def _generate_executive_summary(self, workflow: OptimizedWorkflow) -> str:
        """Generate executive summary section"""
        return f"""
        <section class="section executive-summary">
            <h2>Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-value savings-highlight">{workflow.savings_percentage:.1f}%</span>
                    <span class="metric-label">Cost Reduction</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">${workflow.total_original_cost:.4f}</span>
                    <span class="metric-label">Baseline Cost</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">${workflow.total_optimized_cost:.4f}</span>
                    <span class="metric-label">Optimized Cost</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value savings-highlight">${workflow.total_savings:.4f}</span>
                    <span class="metric-label">Savings per Run</span>
                </div>
            </div>
            <p style="margin-top: 30px; font-size: 1.2rem;">
                Signal Box can reduce your AI costs by <strong>{workflow.savings_percentage:.1f}%</strong>, 
                saving <strong>${workflow.total_savings:.4f}</strong> per workflow execution.
            </p>
        </section>
        """
    
    def _generate_cost_breakdown(self, workflow: OptimizedWorkflow) -> str:
        """Generate detailed cost breakdown"""
        baseline_table = self._generate_baseline_table(workflow.original_calculations)
        optimized_table = self._generate_optimized_table(workflow.optimized_calculations, workflow.optimization_results)
        
        return f"""
        <section class="section">
            <h2>💰 Cost Breakdown</h2>
            
            <h3>Baseline Execution</h3>
            {baseline_table}
            
            <h3>Optimized Execution</h3>
            {optimized_table}
        </section>
        """
    
    def _generate_baseline_table(self, calculations: List[CostCalculation]) -> str:
        """Generate baseline cost table"""
        rows = ""
        total_cost = 0
        total_tokens = 0
        
        for i, calc in enumerate(calculations, 1):
            total_cost += calc.total_cost
            total_tokens += calc.input_tokens + calc.output_tokens
            
            rows += f"""
            <tr>
                <td>{i}</td>
                <td>{calc.description}</td>
                <td>{calc.model}</td>
                <td>{calc.input_tokens + calc.output_tokens:,}</td>
                <td><div class="calculation-box">{calc.total_calculation}</div></td>
                <td>${calc.total_cost:.4f}</td>
            </tr>
            """
        
        # Total row
        rows += f"""
        <tr style="font-weight: bold; background: #f7fafc;">
            <td colspan="3">TOTAL</td>
            <td>{total_tokens:,}</td>
            <td></td>
            <td>${total_cost:.4f}</td>
        </tr>
        """
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Step</th>
                    <th>Component</th>
                    <th>Model</th>
                    <th>Tokens</th>
                    <th>Calculation</th>
                    <th>Cost</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """
    
    def _generate_optimized_table(self, calculations: List[CostCalculation], optimizations: List[OptimizationResult]) -> str:
        """Generate optimized cost table"""
        rows = ""
        total_cost = 0
        total_tokens = 0
        total_savings = 0
        
        for i, calc in enumerate(calculations, 1):
            total_cost += calc.total_cost
            total_tokens += calc.input_tokens + calc.output_tokens
            
            # Find corresponding optimization
            optimization = None
            if i <= len(optimizations):
                optimization = optimizations[i-1]
                total_savings += optimization.savings if optimization else 0
            
            optimization_badge = ""
            savings_display = "-"
            
            if optimization:
                optimization_badge = f'<span class="optimization-badge">{optimization.optimization_type.replace("_", " ").title()}</span>'
                savings_display = f'<span class="savings-highlight">${optimization.savings:.4f}</span>'
            
            rows += f"""
            <tr>
                <td>{i}</td>
                <td>{calc.description}</td>
                <td>{optimization_badge}</td>
                <td>{calc.input_tokens + calc.output_tokens:,}</td>
                <td><div class="calculation-box">{calc.total_calculation}</div></td>
                <td>${calc.total_cost:.4f}</td>
                <td>{savings_display}</td>
            </tr>
            """
        
        # Total row
        rows += f"""
        <tr style="font-weight: bold; background: #f7fafc;">
            <td colspan="3">TOTAL</td>
            <td>{total_tokens:,}</td>
            <td></td>
            <td>${total_cost:.4f}</td>
            <td class="savings-highlight">${total_savings:.4f}</td>
        </tr>
        """
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Step</th>
                    <th>Component</th>
                    <th>Optimization</th>
                    <th>Tokens</th>
                    <th>Calculation</th>
                    <th>Cost</th>
                    <th>Savings</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """
    
    def _generate_optimization_details(self, workflow: OptimizedWorkflow) -> str:
        """Generate optimization details section"""
        if not workflow.optimization_results:
            return ""
        
        details = ""
        for opt in workflow.optimization_results:
            details += f"""
            <div class="optimization-detail">
                <h4>{opt.optimization_type.replace('_', ' ').title()}</h4>
                <p><strong>Savings:</strong> ${opt.savings:.4f} ({opt.savings_percent:.1f}%)</p>
                <p><strong>Explanation:</strong> {opt.explanation}</p>
                <div class="calculation-box">{opt.calculation_details}</div>
            </div>
            """
        
        return f"""
        <section class="section">
            <h2>🎯 Optimization Details</h2>
            {details}
        </section>
        """
    
    def _generate_component_analysis(self, components: List[Component], workflow: OptimizedWorkflow) -> str:
        """Generate component analysis section"""
        component_cards = ""
        
        for component in components:
            # Find corresponding calculation
            calc = next((c for c in workflow.original_calculations if component.name in c.description), None)
            
            model_info = component.model or "Not specified"
            tokens_info = f"{component.estimated_tokens:,}" if component.estimated_tokens else "Estimated"
            cost_info = f"${calc.total_cost:.4f}" if calc else "Calculated"
            
            component_cards += f"""
            <div class="component-card">
                <div class="component-header">{component.name}</div>
                <div class="component-meta">
                    <strong>Type:</strong> {component.type.title()}<br>
                    <strong>Model:</strong> {model_info}<br>
                    <strong>Tokens:</strong> {tokens_info}<br>
                    <strong>Cost:</strong> {cost_info}
                </div>
                {self._format_component_metadata(component.metadata)}
            </div>
            """
        
        return f"""
        <section class="section">
            <h2>🔧 Component Analysis</h2>
            <div class="component-grid">
                {component_cards}
            </div>
        </section>
        """
    
    def _format_component_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format component metadata for display"""
        if not metadata:
            return ""
        
        formatted = "<div style='margin-top: 10px; font-size: 0.85rem;'>"
        
        for key, value in metadata.items():
            if key in ['system_message', 'template'] and value:
                # Truncate long text
                display_value = value[:100] + "..." if len(str(value)) > 100 else value
                formatted += f"<strong>{key.replace('_', ' ').title()}:</strong> {display_value}<br>"
            elif key not in ['system_message', 'template'] and value:
                formatted += f"<strong>{key.replace('_', ' ').title()}:</strong> {value}<br>"
        
        formatted += "</div>"
        return formatted
    
    def _generate_recommendations(self, workflow: OptimizedWorkflow) -> str:
        """Generate recommendations section"""
        if not workflow.recommendations:
            return ""
        
        rec_items = ""
        for rec in workflow.recommendations:
            rec_items += f'<div class="recommendation-item">{rec}</div>'
        
        return f"""
        <section class="section">
            <div class="recommendations">
                <h3>💡 Implementation Recommendations</h3>
                {rec_items}
            </div>
        </section>
        """
    
    def _generate_assumptions_section(self, workflow: OptimizedWorkflow) -> str:
        """Generate assumptions and methodology section"""
        if not self.config.include_assumptions:
            return ""
        
        # Get pricing info from first calculation
        pricing_table = ""
        if workflow.original_calculations:
            calc = workflow.original_calculations[0]
            if hasattr(calc, 'assumptions') and calc.assumptions:
                pricing_table = "<table><tr><th>Model</th><th>Input (per 1K)</th><th>Output (per 1K)</th></tr>"
                # This would need access to calculator's pricing data
                pricing_table += "</table>"
        
        return f"""
        <section class="section">
            <div class="assumptions">
                <h3>⚠️ Assumptions & Methodology</h3>
                <p>All calculations are based on transparent, conservative assumptions:</p>
                
                <h4>Key Assumptions</h4>
                <ul>
                    <li><strong>Token Estimation:</strong> ~4 characters per token with operation-specific adjustments</li>
                    <li><strong>Cache Hit Rate:</strong> Conservative 15% for semantic caching</li>
                    <li><strong>Model Pricing:</strong> Current published rates from providers</li>
                    <li><strong>Output Ratio:</strong> 30% of input tokens for typical operations</li>
                </ul>
                
                <h4>Optimization Strategies</h4>
                <ul>
                    <li><strong>Smart Model Routing:</strong> Use efficient models for simple tasks</li>
                    <li><strong>Semantic Caching:</strong> Cache similar queries based on vector similarity</li>
                    <li><strong>Token Optimization:</strong> Compress prompts and reduce redundancy</li>
                    <li><strong>Parallel Execution:</strong> Run independent operations concurrently</li>
                </ul>
                
                <p><strong>Note:</strong> Real-world savings may be higher with:</p>
                <ul>
                    <li>Higher cache hit rates (we assume only 15%)</li>
                    <li>More aggressive model substitution</li>
                    <li>Workflow-specific optimizations</li>
                    <li>Better prompt engineering</li>
                </ul>
            </div>
        </section>
        """
    
    def generate_json_report(self, 
                           detection_result: DetectionResult,
                           optimized_workflow: OptimizedWorkflow) -> str:
        """Generate JSON report for API consumption"""
        
        report_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "framework": detection_result.framework,
                "confidence": detection_result.confidence.value,
                "confidence_score": detection_result.confidence_score
            },
            "summary": {
                "total_original_cost": optimized_workflow.total_original_cost,
                "total_optimized_cost": optimized_workflow.total_optimized_cost,
                "total_savings": optimized_workflow.total_savings,
                "savings_percentage": optimized_workflow.savings_percentage,
                "components_analyzed": len(optimized_workflow.original_components)
            },
            "components": [
                {
                    "name": comp.name,
                    "type": comp.type,
                    "model": comp.model,
                    "estimated_tokens": comp.estimated_tokens,
                    "file_path": comp.file_path,
                    "line_number": comp.line_number,
                    "metadata": comp.metadata
                }
                for comp in optimized_workflow.original_components
            ],
            "optimizations": [
                {
                    "type": opt.optimization_type,
                    "original_cost": opt.original_cost,
                    "optimized_cost": opt.optimized_cost,
                    "savings": opt.savings,
                    "savings_percent": opt.savings_percent,
                    "explanation": opt.explanation
                }
                for opt in optimized_workflow.optimization_results
            ],
            "calculations": {
                "baseline": [
                    {
                        "description": calc.description,
                        "model": calc.model,
                        "input_tokens": calc.input_tokens,
                        "output_tokens": calc.output_tokens,
                        "total_cost": calc.total_cost,
                        "calculation": calc.total_calculation
                    }
                    for calc in optimized_workflow.original_calculations
                ],
                "optimized": [
                    {
                        "description": calc.description,
                        "model": calc.model,
                        "input_tokens": calc.input_tokens,
                        "output_tokens": calc.output_tokens,
                        "total_cost": calc.total_cost,
                        "calculation": calc.total_calculation
                    }
                    for calc in optimized_workflow.optimized_calculations
                ]
            },
            "recommendations": optimized_workflow.recommendations,
            "execution_optimizations": {
                "parallel_opportunities": optimized_workflow.parallel_opportunities,
                "cache_opportunities": optimized_workflow.cache_opportunities
            }
        }
        
        return json.dumps(report_data, indent=2)
    
    def save_report(self, 
                   html_content: str,
                   filename: Optional[str] = None,
                   output_dir: str = ".") -> str:
        """Save HTML report to file"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"signal_box_analysis_{timestamp}.html"
        
        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)