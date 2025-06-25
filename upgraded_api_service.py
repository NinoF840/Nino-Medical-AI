#!/usr/bin/env python3
"""
Upgraded Nino Medical AI - Italian Medical NER API Service
Integrated with Final Optimized Model while maintaining full backward compatibility

Copyright (C) 2025 Nino Medical AI. All Rights Reserved.
Author: NinoF840
"""

from fastapi import FastAPI, HTTPException, Depends, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uvicorn
import time
import hashlib
import json
from datetime import datetime
import logging

# Import the integrated pipeline
from pipeline_integration import (
    create_integrated_ner, 
    ModelPerformanceLevel,
    IntegratedItalianMedicalNER
)

# Analytics import (optional)
try:
    from analytics_system import NinoMedicalAnalytics
except ImportError:
    NinoMedicalAnalytics = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with enhanced documentation
app = FastAPI(
    title="Nino Medical AI - Italian Medical NER API (Optimized)",
    description="""⚠️ RESEARCH USE ONLY - NOT A MEDICAL DEVICE

🚀 **ENHANCED WITH FINAL OPTIMIZED MODEL**
Professional Medical AI Platform for Italian Healthcare with Maximum Performance

✨ **NEW FEATURES:**
- 🎯 51+ entities detected (vs 39 previous)
- ✅ Confidence scores in proper 0.0-1.0 range
- 🧬 Morphological awareness for Italian medical terms
- 🔍 Advanced pattern matching with contextual boosting
- 📚 Ultra-comprehensive medical dictionary
- ⚡ Multiple performance levels (basic/enhanced/optimized/auto)

🚫 NOT for clinical diagnosis or treatment decisions
✅ For research, education, and text analysis only""",
    version="2.0.0",
    contact={
        "name": "Nino Medical AI",
        "url": "https://ninomedical.ai",
        "email": "contact@ninomedical.ai"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://ninomedical.ai/license"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Enhanced API Models
class TextInput(BaseModel):
    text: str = Field(..., description="Italian medical text to analyze", max_length=10000)
    confidence_threshold: Optional[float] = Field(0.2, description="Confidence threshold (0.0-1.0)", ge=0.0, le=1.0)
    performance_level: Optional[str] = Field("optimized", description="Performance level: basic/enhanced/optimized/auto")
    include_source: Optional[bool] = Field(True, description="Include entity source information")
    include_contextual_boost: Optional[bool] = Field(True, description="Include contextual confidence boost info")

class EntityResult(BaseModel):
    text: str = Field(..., description="Entity text")
    label: str = Field(..., description="Entity type (PROBLEM/TREATMENT/TEST)")
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)", ge=0.0, le=1.0)
    source: Optional[str] = Field(None, description="Detection source (model/pattern/dictionary)")
    contextual_boost: Optional[float] = Field(None, description="Contextual confidence boost applied")

class AnalysisResult(BaseModel):
    success: bool = Field(..., description="Analysis success status")
    text: str = Field(..., description="Original input text")
    entities: List[EntityResult] = Field(..., description="Detected medical entities")
    total_entities: int = Field(..., description="Total number of entities found")
    entity_counts: Dict[str, int] = Field(..., description="Count of entities by type")
    processing_time: float = Field(..., description="Processing time in seconds")
    model_version: str = Field(..., description="Model version used")
    performance_level: str = Field(..., description="Performance level used")
    confidence_threshold: float = Field(..., description="Applied confidence threshold")
    enhancement_applied: bool = Field(..., description="Whether enhancements were applied")
    confidence_range_valid: bool = Field(..., description="Whether confidence scores are in valid range")
    performance_info: Dict[str, Any] = Field(..., description="Model performance information")
    timestamp: str = Field(..., description="Analysis timestamp")

class BatchInput(BaseModel):
    texts: List[str] = Field(..., description="List of texts to analyze", max_items=100)
    confidence_threshold: Optional[float] = Field(0.2, description="Confidence threshold", ge=0.0, le=1.0)
    performance_level: Optional[str] = Field("optimized", description="Performance level")
    include_source: Optional[bool] = Field(True, description="Include source information")
    include_contextual_boost: Optional[bool] = Field(True, description="Include boost information")

class BatchResult(BaseModel):
    success: bool = Field(..., description="Batch analysis success status")
    results: List[AnalysisResult] = Field(..., description="Individual analysis results")
    total_texts: int = Field(..., description="Total number of texts processed")
    total_entities: int = Field(..., description="Total entities found across all texts")
    total_processing_time: float = Field(..., description="Total processing time")
    performance_summary: Dict[str, Any] = Field(..., description="Performance summary statistics")
    timestamp: str = Field(..., description="Batch analysis timestamp")

class HealthCheck(BaseModel):
    status: str = Field(..., description="Service health status")
    model_loaded: bool = Field(..., description="Model loading status")
    active_model: str = Field(..., description="Currently active model")
    models_available: List[str] = Field(..., description="Available performance levels")
    version: str = Field(..., description="API version")
    features: Dict[str, bool] = Field(..., description="Available features")
    timestamp: str = Field(..., description="Health check timestamp")

class PerformanceLevel(BaseModel):
    level: str = Field(..., description="Performance level to switch to", pattern="^(basic|enhanced|optimized|auto)$")

# Global integrated NER pipeline
ner_pipeline: Optional[IntegratedItalianMedicalNER] = None
analytics = None

# Enhanced API key system
VALID_API_KEYS = {
    "demo-key-123": {"tier": "demo", "daily_limit": 100, "performance_levels": ["basic", "enhanced"]},
    "pro-key-456": {"tier": "professional", "daily_limit": 10000, "performance_levels": ["basic", "enhanced", "optimized"]},
    "enterprise-key-789": {"tier": "enterprise", "daily_limit": 100000, "performance_levels": ["basic", "enhanced", "optimized", "auto"]},
    "research-key-999": {"tier": "research", "daily_limit": 50000, "performance_levels": ["basic", "enhanced", "optimized", "auto"]}
}

# Usage tracking
usage_tracking = {}

def get_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """Enhanced API key validation with tier-based access"""
    api_key = credentials.credentials
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Daily usage tracking
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{api_key}_{today}"
    
    if key not in usage_tracking:
        usage_tracking[key] = 0
    
    key_info = VALID_API_KEYS[api_key]
    if usage_tracking[key] >= key_info["daily_limit"]:
        raise HTTPException(status_code=429, detail="Daily API limit exceeded")
    
    usage_tracking[key] += 1
    return {"api_key": api_key, "info": key_info}

def validate_performance_level(performance_level: str, api_key_info: Dict) -> str:
    """Validate that the requested performance level is allowed for the API key tier"""
    allowed_levels = api_key_info["info"]["performance_levels"]
    if performance_level not in allowed_levels:
        # Fall back to best available level
        if "optimized" in allowed_levels:
            return "optimized"
        elif "enhanced" in allowed_levels:
            return "enhanced"
        else:
            return "basic"
    return performance_level

@app.on_event("startup")
async def startup_event():
    """Initialize the integrated NER pipeline and analytics on startup"""
    global ner_pipeline, analytics
    try:
        logger.info("🚀 Starting Nino Medical AI API v2.0 with Final Optimized Model...")
        
        # Initialize integrated NER pipeline with optimized model
        logger.info("Loading integrated NER pipeline...")
        ner_pipeline = create_integrated_ner(
            performance_level="optimized",
            confidence_threshold=0.2
        )
        logger.info("✅ Integrated NER pipeline loaded successfully!")
        
        # Initialize analytics if available
        if NinoMedicalAnalytics is not None:
            try:
                logger.info("Initializing analytics system...")
                analytics = NinoMedicalAnalytics()
                logger.info("✅ Analytics system initialized!")
            except Exception as e:
                logger.warning(f"Analytics system initialization failed: {e}")
        
        # Log startup statistics
        health = ner_pipeline.get_health_status()
        logger.info(f"🎯 Active model: {health['active_model']}")
        logger.info(f"📊 Available models: {health['models_available']}")
        logger.info("🎉 Nino Medical AI API ready!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize API: {str(e)}")
        raise

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Enhanced API root endpoint with new features information"""
    return {
        "message": "Nino Medical AI - Italian Medical NER API v2.0",
        "version": "2.0.0",
        "description": "Professional Medical AI Platform with Final Optimized Model",
        "company": "Nino Medical AI",
        "founder": "NinoF840",
        "copyright": "© 2025 Nino Medical AI. All Rights Reserved.",
        "features": {
            "final_optimized_model": "✅ 51+ entities detected",
            "confidence_normalization": "✅ Proper 0.0-1.0 range",
            "morphological_analysis": "✅ Italian language specific",
            "contextual_boosting": "✅ Medical domain awareness",
            "performance_levels": "✅ Basic/Enhanced/Optimized/Auto",
            "source_attribution": "✅ Model/Pattern/Dictionary tracking"
        },
        "performance_comparison": {
            "previous_best": "50 entities",
            "current_optimized": "51 entities",
            "improvement": "+1 entity (+2%)"
        },
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "analyze": "/analyze",
            "batch": "/batch",
            "demo": "/demo",
            "stats": "/stats",
            "switch_model": "/switch-performance"
        }
    }

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Enhanced health check with detailed model information"""
    if ner_pipeline is None:
        return HealthCheck(
            status="unhealthy",
            model_loaded=False,
            active_model="none",
            models_available=[],
            version="2.0.0",
            features={},
            timestamp=datetime.now().isoformat()
        )
    
    health_status = ner_pipeline.get_health_status()
    
    return HealthCheck(
        status=health_status["status"],
        model_loaded=health_status["status"] == "healthy",
        active_model=health_status["active_model"],
        models_available=[str(model) for model in health_status["models_available"]],
        version="2.0.0",
        features=health_status["configuration"]["features_enabled"],
        timestamp=datetime.now().isoformat()
    )

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_text(
    input_data: TextInput,
    api_key_info: Dict = Depends(get_api_key)
):
    """Analyze Italian medical text with the integrated optimized model"""
    if ner_pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Validate and adjust performance level based on API key tier
        validated_level = validate_performance_level(input_data.performance_level, api_key_info)
        if validated_level != input_data.performance_level:
            logger.info(f"Performance level adjusted from {input_data.performance_level} to {validated_level} for tier {api_key_info['info']['tier']}")
        
        # Perform NER analysis with integrated pipeline
        result = ner_pipeline.predict(
            input_data.text,
            confidence_threshold=input_data.confidence_threshold,
            include_source=input_data.include_source,
            apply_enhancement=True
        )
        
        # Format entities for API response
        entities = []
        for entity in result['entities']:
            entity_result = EntityResult(
                text=entity['text'],
                label=entity['label'],
                start=entity['start'],
                end=entity['end'],
                confidence=entity['confidence']
            )
            
            if input_data.include_source and 'source' in entity:
                entity_result.source = entity['source']
            
            if input_data.include_contextual_boost and 'contextual_boost' in entity:
                entity_result.contextual_boost = entity['contextual_boost']
            
            entities.append(entity_result)
        
        # Create enhanced response
        analysis_result = AnalysisResult(
            success=True,
            text=input_data.text,
            entities=entities,
            total_entities=result['total_entities'],
            entity_counts=result['entity_counts'],
            processing_time=result['processing_time'],
            model_version=result['model_version'],
            performance_level=result['performance_level'],
            confidence_threshold=result['confidence_threshold'],
            enhancement_applied=result['enhancement_applied'],
            confidence_range_valid=result['confidence_range_valid'],
            performance_info=result['performance_info'],
            timestamp=datetime.now().isoformat()
        )
        
        # Log usage for analytics
        if analytics:
            try:
                analytics.log_request(api_key_info['api_key'], result)
            except Exception as e:
                logger.warning(f"Analytics logging failed: {e}")
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/batch", response_model=BatchResult)
async def batch_analyze(
    input_data: BatchInput,
    api_key_info: Dict = Depends(get_api_key)
):
    """Batch analyze multiple Italian medical texts"""
    if ner_pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(input_data.texts) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 texts per batch")
    
    try:
        start_time = time.time()
        
        # Validate performance level
        validated_level = validate_performance_level(input_data.performance_level, api_key_info)
        
        # Process all texts
        results = []
        total_entities = 0
        
        for i, text in enumerate(input_data.texts):
            try:
                # Analyze individual text
                result = ner_pipeline.predict(
                    text,
                    confidence_threshold=input_data.confidence_threshold,
                    include_source=input_data.include_source,
                    apply_enhancement=True
                )
                
                # Format entities
                entities = []
                for entity in result['entities']:
                    entity_result = EntityResult(
                        text=entity['text'],
                        label=entity['label'],
                        start=entity['start'],
                        end=entity['end'],
                        confidence=entity['confidence']
                    )
                    
                    if input_data.include_source and 'source' in entity:
                        entity_result.source = entity['source']
                    
                    if input_data.include_contextual_boost and 'contextual_boost' in entity:
                        entity_result.contextual_boost = entity['contextual_boost']
                    
                    entities.append(entity_result)
                
                # Create analysis result
                analysis_result = AnalysisResult(
                    success=True,
                    text=text,
                    entities=entities,
                    total_entities=result['total_entities'],
                    entity_counts=result['entity_counts'],
                    processing_time=result['processing_time'],
                    model_version=result['model_version'],
                    performance_level=result['performance_level'],
                    confidence_threshold=result['confidence_threshold'],
                    enhancement_applied=result['enhancement_applied'],
                    confidence_range_valid=result['confidence_range_valid'],
                    performance_info=result['performance_info'],
                    timestamp=datetime.now().isoformat()
                )
                
                results.append(analysis_result)
                total_entities += result['total_entities']
                
            except Exception as e:
                logger.error(f"Failed to process text {i+1}: {e}")
                # Add error result
                error_result = AnalysisResult(
                    success=False,
                    text=text,
                    entities=[],
                    total_entities=0,
                    entity_counts={},
                    processing_time=0.0,
                    model_version="error",
                    performance_level="error",
                    confidence_threshold=input_data.confidence_threshold,
                    enhancement_applied=False,
                    confidence_range_valid=False,
                    performance_info={},
                    timestamp=datetime.now().isoformat()
                )
                results.append(error_result)
        
        total_processing_time = time.time() - start_time
        
        # Calculate performance summary
        successful_results = [r for r in results if r.success]
        performance_summary = {
            "successful_analyses": len(successful_results),
            "failed_analyses": len(results) - len(successful_results),
            "average_entities_per_text": total_entities / len(successful_results) if successful_results else 0,
            "average_processing_time": sum(r.processing_time for r in successful_results) / len(successful_results) if successful_results else 0,
            "total_unique_entities": len(set(e.text for r in successful_results for e in r.entities))
        }
        
        return BatchResult(
            success=True,
            results=results,
            total_texts=len(input_data.texts),
            total_entities=total_entities,
            total_processing_time=round(total_processing_time, 4),
            performance_summary=performance_summary,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@app.get("/demo", response_model=AnalysisResult)
async def demo_endpoint():
    """Enhanced demo endpoint showcasing the optimized model (no API key required)"""
    if ner_pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Enhanced demo text showcasing more medical entities
    demo_text = """Il paziente presenta forti mal di testa e nausea persistente da tre giorni. 
    È stato prescritto paracetamolo 500mg ogni 8 ore e si consiglia di effettuare immediatamente 
    un esame del sangue completo e una radiografia del torace per escludere altre patologie. 
    La febbre è controllata con ibuprofene e si monitora l'andamento con controlli giornalieri."""
    
    try:
        result = ner_pipeline.predict(demo_text, confidence_threshold=0.2)
        
        # Format entities for demo
        entities = []
        for entity in result['entities']:
            entities.append(EntityResult(
                text=entity['text'],
                label=entity['label'],
                start=entity['start'],
                end=entity['end'],
                confidence=entity['confidence'],
                source=entity.get('source'),
                contextual_boost=entity.get('contextual_boost')
            ))
        
        return AnalysisResult(
            success=True,
            text=demo_text,
            entities=entities,
            total_entities=result['total_entities'],
            entity_counts=result['entity_counts'],
            processing_time=result['processing_time'],
            model_version=result['model_version'],
            performance_level=result['performance_level'],
            confidence_threshold=result['confidence_threshold'],
            enhancement_applied=result['enhancement_applied'],
            confidence_range_valid=result['confidence_range_valid'],
            performance_info=result['performance_info'],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

@app.post("/switch-performance", response_model=Dict[str, Any])
async def switch_performance_level(
    performance_data: PerformanceLevel,
    api_key_info: Dict = Depends(get_api_key)
):
    """Switch the active performance level (enterprise/research tier only)"""
    if ner_pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Check if tier allows performance switching
    tier = api_key_info["info"]["tier"]
    if tier not in ["enterprise", "research"]:
        raise HTTPException(status_code=403, detail="Performance switching requires enterprise or research tier")
    
    # Validate requested level is allowed for this tier
    validated_level = validate_performance_level(performance_data.level, api_key_info)
    if validated_level != performance_data.level:
        raise HTTPException(
            status_code=403, 
            detail=f"Performance level '{performance_data.level}' not available for tier '{tier}'"
        )
    
    try:
        # Attempt to switch performance level
        level_enum = ModelPerformanceLevel(performance_data.level.lower())
        success = ner_pipeline.switch_performance_level(level_enum)
        
        if success:
            return {
                "success": True,
                "message": f"Successfully switched to {performance_data.level} performance level",
                "active_model": performance_data.level,
                "tier": tier,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": f"Failed to switch to {performance_data.level} - model not available",
                "active_model": ner_pipeline.config.performance_level.value,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Performance switch error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance switch failed: {str(e)}")

@app.get("/stats", response_model=Dict[str, Any])
async def get_enhanced_stats(api_key_info: Dict = Depends(get_api_key)):
    """Get enhanced API usage and performance statistics"""
    today = datetime.now().strftime("%Y-%m-%d")
    api_key = api_key_info["api_key"]
    key = f"{api_key}_{today}"
    
    current_usage = usage_tracking.get(key, 0)
    key_info = api_key_info["info"]
    
    # Get pipeline health and performance stats
    health_status = ner_pipeline.get_health_status() if ner_pipeline else {}
    
    return {
        "api_usage": {
            "api_key": api_key[:8] + "...",
            "tier": key_info["tier"],
            "daily_limit": key_info["daily_limit"],
            "current_usage": current_usage,
            "remaining_requests": key_info["daily_limit"] - current_usage,
            "date": today,
            "allowed_performance_levels": key_info["performance_levels"]
        },
        "model_status": {
            "active_model": health_status.get("active_model", "unknown"),
            "models_available": health_status.get("models_available", []),
            "status": health_status.get("status", "unknown"),
            "features_enabled": health_status.get("configuration", {}).get("features_enabled", {})
        },
        "performance_statistics": health_status.get("performance_stats", {}),
        "api_version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Run the enhanced API server
    print("🚀 Starting Nino Medical AI API v2.0 with Final Optimized Model")
    uvicorn.run(
        "upgraded_api_service:app",
        host="0.0.0.0",
        port=8001,  # Different port to avoid conflicts
        reload=True,
        log_level="info"
    )
