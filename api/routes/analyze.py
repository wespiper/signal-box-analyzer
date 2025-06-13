"""
Analysis endpoint for Signal Box Cost Analyzer
Uses Signal Box core as dependency
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import uuid

# Import Signal Box core components
try:
    from signal_box.core.orchestration.coordinator import OrchestratorEngine
    from signal_box.core.routing.smart_model_router import SmartModelRouter
    from signal_box.core.engine import SignalBoxEngine
    SIGNAL_BOX_AVAILABLE = True
except ImportError:
    SIGNAL_BOX_AVAILABLE = False
    print("⚠️  Signal Box core not available. Using local analyzer components.")

# Import local analyzer components as fallback
from ..services.github import GitHubService
from ...analyzer.detectors.autogen import AutoGenDetector
from ...analyzer.detectors.langchain import LangChainDetector
from ...analyzer.optimizer import OptimizationEngine
from ...analyzer.report import ReportGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request model for analysis"""
    github_url: str
    include_detailed_calculations: bool = True
    include_recommendations: bool = True
    custom_assumptions: Optional[Dict[str, Any]] = None
    
    @validator('github_url')
    def validate_github_url(cls, v):
        """Validate GitHub URL format"""
        if not v.startswith(('https://github.com/', 'http://github.com/')):
            raise ValueError('Must be a valid GitHub URL')
        return v


class ComponentInfo(BaseModel):
    """Component information for response"""
    name: str
    type: str
    model: Optional[str]
    estimated_tokens: Optional[int]
    file_path: str
    line_number: int
    metadata: Dict[str, Any]


class OptimizationInfo(BaseModel):
    """Optimization information for response"""
    type: str
    original_cost: float
    optimized_cost: float
    savings: float
    savings_percent: float
    explanation: str


class AnalysisResponse(BaseModel):
    """Response model for analysis"""
    analysis_id: str
    timestamp: str
    
    # Detection results
    framework: str
    confidence: str
    confidence_score: float
    
    # Components
    components: List[ComponentInfo]
    
    # Cost analysis
    total_original_cost: float
    total_optimized_cost: float
    total_savings: float
    savings_percentage: float
    
    # Optimizations
    optimizations: List[OptimizationInfo]
    
    # Recommendations
    recommendations: List[str]
    
    # Reports
    html_report_url: Optional[str] = None
    json_report: Optional[Dict[str, Any]] = None


class AnalysisStatus(BaseModel):
    """Analysis status for long-running operations"""
    analysis_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: float  # 0-100
    message: str
    result: Optional[AnalysisResponse] = None
    error: Optional[str] = None


# In-memory storage for demo (would use Redis/DB in production)
analysis_cache: Dict[str, AnalysisStatus] = {}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_repository(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze a GitHub repository for AI workflow costs
    
    This endpoint:
    1. Fetches the repository content
    2. Detects the AI framework used
    3. Analyzes components and costs
    4. Applies optimizations
    5. Generates recommendations and reports
    """
    analysis_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Starting analysis {analysis_id} for {request.github_url}")
        
        # Initialize status
        analysis_cache[analysis_id] = AnalysisStatus(
            analysis_id=analysis_id,
            status="processing",
            progress=0,
            message="Fetching repository content..."
        )
        
        # Step 1: Fetch repository content (20% progress)
        github_service = GitHubService()
        
        try:
            repo_info = await github_service.fetch_repository(request.github_url)
            file_paths = list(repo_info['files'].keys())
            file_contents = repo_info['files']
            
        except Exception as e:
            logger.error(f"Failed to fetch repository: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch repository: {str(e)}"
            )
        
        analysis_cache[analysis_id].progress = 20
        analysis_cache[analysis_id].message = "Detecting AI framework..."
        
        # Step 2: Detect framework (40% progress)
        detectors = [
            AutoGenDetector(),
            LangChainDetector(),
        ]
        
        best_result = None
        best_score = 0
        
        for detector in detectors:
            try:
                result = detector.detect(file_paths, file_contents)
                if result.confidence_score > best_score:
                    best_result = result
                    best_score = result.confidence_score
            except Exception as e:
                logger.warning(f"Detector {detector.get_framework_name()} failed: {e}")
        
        if not best_result or best_score < 10:
            raise HTTPException(
                status_code=400,
                detail="No supported AI framework detected in the repository. "
                       "Currently supports AutoGen and LangChain."
            )
        
        analysis_cache[analysis_id].progress = 40
        analysis_cache[analysis_id].message = f"Analyzing {best_result.framework} workflow..."
        
        # Step 3: Optimize workflow (70% progress)
        optimizer = OptimizationEngine()
        optimized_workflow = optimizer.optimize_workflow(best_result)
        
        analysis_cache[analysis_id].progress = 70
        analysis_cache[analysis_id].message = "Generating reports..."
        
        # Step 4: Generate reports (90% progress)
        report_generator = ReportGenerator()
        html_report = report_generator.generate_html_report(best_result, optimized_workflow)
        json_report_str = report_generator.generate_json_report(best_result, optimized_workflow)
        
        # Save HTML report (in production, would save to cloud storage)
        html_filename = f"analysis_{analysis_id}.html"
        html_path = report_generator.save_report(html_report, html_filename, "reports")
        
        analysis_cache[analysis_id].progress = 90
        analysis_cache[analysis_id].message = "Finalizing analysis..."
        
        # Step 5: Prepare response (100% progress)
        response = AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=datetime.now().isoformat(),
            framework=best_result.framework,
            confidence=best_result.confidence.value,
            confidence_score=best_result.confidence_score,
            components=[
                ComponentInfo(
                    name=comp.name,
                    type=comp.type,
                    model=comp.model,
                    estimated_tokens=comp.estimated_tokens,
                    file_path=comp.file_path,
                    line_number=comp.line_number,
                    metadata=comp.metadata
                )
                for comp in best_result.components
            ],
            total_original_cost=optimized_workflow.total_original_cost,
            total_optimized_cost=optimized_workflow.total_optimized_cost,
            total_savings=optimized_workflow.total_savings,
            savings_percentage=optimized_workflow.savings_percentage,
            optimizations=[
                OptimizationInfo(
                    type=opt.optimization_type,
                    original_cost=opt.original_cost,
                    optimized_cost=opt.optimized_cost,
                    savings=opt.savings,
                    savings_percent=opt.savings_percent,
                    explanation=opt.explanation
                )
                for opt in optimized_workflow.optimization_results
            ],
            recommendations=optimized_workflow.recommendations,
            html_report_url=f"/reports/{html_filename}",
            json_report=eval(json_report_str) if request.include_detailed_calculations else None
        )
        
        # Update cache with completed status
        analysis_cache[analysis_id].status = "completed"
        analysis_cache[analysis_id].progress = 100
        analysis_cache[analysis_id].message = "Analysis completed successfully"
        analysis_cache[analysis_id].result = response
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        analysis_cache[analysis_id].status = "failed"
        analysis_cache[analysis_id].error = "Analysis failed"
        raise
    
    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {e}")
        analysis_cache[analysis_id].status = "failed"
        analysis_cache[analysis_id].error = str(e)
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/analyze/{analysis_id}/status", response_model=AnalysisStatus)
async def get_analysis_status(analysis_id: str):
    """Get the status of a running analysis"""
    
    if analysis_id not in analysis_cache:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )
    
    return analysis_cache[analysis_id]


@router.get("/analyze/{analysis_id}/report")
async def get_analysis_report(analysis_id: str, format: str = "html"):
    """Get the full report for a completed analysis"""
    
    if analysis_id not in analysis_cache:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )
    
    status = analysis_cache[analysis_id]
    
    if status.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis is {status.status}, report not available"
        )
    
    if format == "html":
        # Return HTML report
        html_filename = f"analysis_{analysis_id}.html"
        try:
            with open(f"reports/{html_filename}", "r") as f:
                html_content = f.read()
            
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=html_content)
            
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="Report file not found"
            )
    
    elif format == "json":
        if not status.result or not status.result.json_report:
            raise HTTPException(
                status_code=404,
                detail="JSON report not available"
            )
        
        return status.result.json_report
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Use 'html' or 'json'"
        )


@router.delete("/analyze/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis and its associated files"""
    
    if analysis_id not in analysis_cache:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )
    
    # Remove from cache
    del analysis_cache[analysis_id]
    
    # Remove files (in production, would clean up cloud storage)
    import os
    html_filename = f"analysis_{analysis_id}.html"
    html_path = f"reports/{html_filename}"
    
    if os.path.exists(html_path):
        os.remove(html_path)
    
    return {"message": "Analysis deleted successfully"}


@router.get("/analyze/list")
async def list_analyses():
    """List all analyses (for debugging/admin)"""
    
    return {
        "analyses": [
            {
                "analysis_id": analysis_id,
                "status": status.status,
                "progress": status.progress,
                "message": status.message
            }
            for analysis_id, status in analysis_cache.items()
        ]
    }