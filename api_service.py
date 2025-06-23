#!/usr/bin/env python3
"""
Nino Medical AI - Italian Medical NER API Service
Professional Medical AI Platform for Italian Healthcare

Copyright (C) 2025 Nino Medical AI. All Rights Reserved.
Author: NinoF840
Founder & Chief AI Officer
Date: June 2025

This software is proprietary and confidential. Unauthorized copying, 
transferring or reproduction of the contents of this file, via any medium 
is strictly prohibited without the express written permission of Nino Medical AI.
"""

from fastapi import FastAPI, HTTPException, Depends, Security
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
from improved_inference import ImprovedItalianMedicalNER
from analytics_system import NinoMedicalAnalytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Nino Medical AI - Italian Medical NER API",
    description="⚠️ RESEARCH USE ONLY - NOT A MEDICAL DEVICE\n\nProfessional Medical AI Platform for Italian Healthcare - Enhanced with Multi-Source Detection\n\n🚫 NOT for clinical diagnosis or treatment decisions\n✅ For research, education, and text analysis only",
    version="1.0.0",
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

# CORS middleware for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# API Models
class TextInput(BaseModel):
    text: str = Field(..., description="Italian medical text to analyze", max_length=10000)
    confidence_threshold: Optional[float] = Field(0.6, description="Confidence threshold for entity detection (0.0-1.0)")
    include_source: Optional[bool] = Field(True, description="Include source information (model/pattern/dictionary)")

class EntityResult(BaseModel):
    text: str = Field(..., description="Entity text")
    label: str = Field(..., description="Entity type (PROBLEM/TREATMENT/TEST)")
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    source: Optional[str] = Field(None, description="Detection source (model/pattern/dictionary)")

class AnalysisResult(BaseModel):
    success: bool = Field(..., description="Analysis success status")
    text: str = Field(..., description="Original input text")
    entities: List[EntityResult] = Field(..., description="Detected medical entities")
    total_entities: int = Field(..., description="Total number of entities found")
    processing_time: float = Field(..., description="Processing time in seconds")
    model_version: str = Field(..., description="Model version used")
    timestamp: str = Field(..., description="Analysis timestamp")

class BatchInput(BaseModel):
    texts: List[str] = Field(..., description="List of texts to analyze", max_items=100)
    confidence_threshold: Optional[float] = Field(0.6, description="Confidence threshold for entity detection")
    include_source: Optional[bool] = Field(True, description="Include source information")

class BatchResult(BaseModel):
    success: bool = Field(..., description="Batch analysis success status")
    results: List[AnalysisResult] = Field(..., description="Individual analysis results")
    total_texts: int = Field(..., description="Total number of texts processed")
    total_entities: int = Field(..., description="Total entities found across all texts")
    total_processing_time: float = Field(..., description="Total processing time")
    timestamp: str = Field(..., description="Batch analysis timestamp")

class HealthCheck(BaseModel):
    status: str = Field(..., description="Service health status")
    model_loaded: bool = Field(..., description="Model loading status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Health check timestamp")

# Global model instance
ner_model = None
analytics = None

# Simple API key validation (expand this for production)
VALID_API_KEYS = {
    "demo-key-123": {"tier": "demo", "daily_limit": 100},
    "pro-key-456": {"tier": "professional", "daily_limit": 10000},
    "enterprise-key-789": {"tier": "enterprise", "daily_limit": 100000}
}

# Usage tracking (use database in production)
usage_tracking = {}

def get_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Validate API key and return key info"""
    api_key = credentials.credentials
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Simple daily usage tracking
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{api_key}_{today}"
    
    if key not in usage_tracking:
        usage_tracking[key] = 0
    
    if usage_tracking[key] >= VALID_API_KEYS[api_key]["daily_limit"]:
        raise HTTPException(status_code=429, detail="Daily API limit exceeded")
    
    usage_tracking[key] += 1
    return api_key

@app.on_event("startup")
async def startup_event():
    """Initialize the NER model and analytics on startup"""
    global ner_model, analytics
    try:
        logger.info("Loading Italian Medical NER model...")
        ner_model = ImprovedItalianMedicalNER(confidence_threshold=0.6)
        logger.info("Model loaded successfully!")
        
        logger.info("Initializing analytics system...")
        analytics = NinoMedicalAnalytics()
        logger.info("Analytics system initialized!")
    except Exception as e:
        logger.error(f"Failed to load model or analytics: {str(e)}")
        raise

@app.get("/", response_model=Dict[str, Any])
async def root():
    """API root endpoint with basic information"""
    return {
        "message": "Nino Medical AI - Italian Medical NER API",
        "version": "1.0.0",
        "description": "Professional Medical AI Platform for Italian Healthcare",
        "company": "Nino Medical AI",
        "founder": "NinoF840",
        "copyright": "© 2025 Nino Medical AI. All Rights Reserved.",
        "mission": "Democratizing Italian medical AI for healthcare",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "analyze": "/analyze",
            "batch": "/batch",
            "demo": "/demo",
            "stats": "/stats"
        }
    }

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy" if ner_model is not None else "unhealthy",
        model_loaded=ner_model is not None,
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_text(
    input_data: TextInput,
    api_key: str = Depends(get_api_key)
):
    """Analyze Italian medical text for named entities"""
    if ner_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        start_time = time.time()
        
        # Update model confidence threshold if provided
        if input_data.confidence_threshold != ner_model.confidence_threshold:
            ner_model.confidence_threshold = input_data.confidence_threshold
        
        # Perform NER analysis
        result = ner_model.predict(input_data.text)
        
        processing_time = time.time() - start_time
        
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
            
            entities.append(entity_result)
        
        return AnalysisResult(
            success=True,
            text=input_data.text,
            entities=entities,
            total_entities=len(entities),
            processing_time=round(processing_time, 4),
            model_version="italian_medical_ner_enhanced_v1.0",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/batch", response_model=BatchResult)
async def batch_analyze(
    input_data: BatchInput,
    api_key: str = Depends(get_api_key)
):
    """Batch analyze multiple Italian medical texts"""
    if ner_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(input_data.texts) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 texts per batch")
    
    try:
        start_time = time.time()
        results = []
        total_entities = 0
        
        # Update model confidence threshold
        if input_data.confidence_threshold != ner_model.confidence_threshold:
            ner_model.confidence_threshold = input_data.confidence_threshold
        
        for text in input_data.texts:
            text_start_time = time.time()
            result = ner_model.predict(text)
            text_processing_time = time.time() - text_start_time
            
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
                
                entities.append(entity_result)
            
            analysis_result = AnalysisResult(
                success=True,
                text=text,
                entities=entities,
                total_entities=len(entities),
                processing_time=round(text_processing_time, 4),
                model_version="italian_medical_ner_enhanced_v1.0",
                timestamp=datetime.now().isoformat()
            )
            
            results.append(analysis_result)
            total_entities += len(entities)
        
        total_processing_time = time.time() - start_time
        
        return BatchResult(
            success=True,
            results=results,
            total_texts=len(input_data.texts),
            total_entities=total_entities,
            total_processing_time=round(total_processing_time, 4),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@app.get("/demo", response_model=AnalysisResult)
async def demo_endpoint():
    """Demo endpoint with sample Italian medical text (no API key required)"""
    if ner_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Sample Italian medical text
    demo_text = "Il paziente presenta mal di testa persistente e nausea. È stato prescritto paracetamolo e si consiglia di effettuare un esame del sangue per escludere altre patologie."
    
    try:
        start_time = time.time()
        result = ner_model.predict(demo_text)
        processing_time = time.time() - start_time
        
        # Format entities
        entities = []
        for entity in result['entities']:
            entities.append(EntityResult(
                text=entity['text'],
                label=entity['label'],
                start=entity['start'],
                end=entity['end'],
                confidence=entity['confidence'],
                source=entity.get('source', None)
            ))
        
        return AnalysisResult(
            success=True,
            text=demo_text,
            entities=entities,
            total_entities=len(entities),
            processing_time=round(processing_time, 4),
            model_version="italian_medical_ner_enhanced_v1.0",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

@app.get("/stats", response_model=Dict[str, Any])
async def get_stats(api_key: str = Depends(get_api_key)):
    """Get API usage statistics"""
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{api_key}_{today}"
    
    current_usage = usage_tracking.get(key, 0)
    daily_limit = VALID_API_KEYS[api_key]["daily_limit"]
    tier = VALID_API_KEYS[api_key]["tier"]
    
    return {
        "api_key": api_key[:8] + "...",  # Masked for security
        "tier": tier,
        "daily_limit": daily_limit,
        "current_usage": current_usage,
        "remaining_requests": daily_limit - current_usage,
        "date": today
    }

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

