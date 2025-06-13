"""
FastAPI application for Signal Box Cost Analyzer
Time estimate: 1 hour
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Signal Box Cost Analyzer API")
    yield
    logger.info("Shutting down Signal Box Cost Analyzer API")


# Create FastAPI app
app = FastAPI(
    title="Signal Box Cost Analyzer",
    description="Analyze and optimize AI workflow costs with full transparency",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Vite dev server
        "http://localhost:5173",  # Alternative Vite port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://signalbox.ai",   # Production domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Import routes
from .routes import analyze, examples


# Register routes
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(examples.router, prefix="/api", tags=["Examples"])


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Signal Box Cost Analyzer API</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 40px;
            }
            h1 { font-size: 2.5rem; margin-bottom: 20px; }
            .endpoint { 
                background: rgba(255,255,255,0.2); 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 8px;
                border-left: 4px solid #48bb78;
            }
            a { color: #90cdf4; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Signal Box Cost Analyzer API</h1>
            <p>Analyze and optimize AI workflow costs with full transparency.</p>
            
            <h2>Available Endpoints:</h2>
            
            <div class="endpoint">
                <strong>POST /api/analyze</strong><br>
                Analyze a GitHub repository for AI workflow costs
            </div>
            
            <div class="endpoint">
                <strong>GET /api/examples</strong><br>
                Get example analyses for popular frameworks
            </div>
            
            <div class="endpoint">
                <strong>GET /api/health</strong><br>
                Health check endpoint
            </div>
            
            <h2>Documentation:</h2>
            <p>
                📖 <a href="/docs">Interactive API Documentation (Swagger)</a><br>
                📋 <a href="/redoc">Alternative Documentation (ReDoc)</a>
            </p>
            
            <h2>Features:</h2>
            <ul>
                <li>🔍 Automatic framework detection (AutoGen, LangChain, etc.)</li>
                <li>💰 Transparent cost calculations</li>
                <li>🎯 Smart optimization recommendations</li>
                <li>📊 Beautiful HTML reports</li>
                <li>🔄 JSON API for integration</li>
            </ul>
        </div>
    </body>
    </html>
    """


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Signal Box Cost Analyzer",
        "version": "0.1.0"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again.",
            "type": "internal_error"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "type": "http_error",
            "status_code": exc.status_code
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )