#!/usr/bin/env python3
"""
Nino Medical AI - Enhanced API Service with Subscription Management
Professional medical AI platform with comprehensive subscription and licensing system

Copyright (C) 2025 Nino Medical AI. All Rights Reserved.
Author: Antonino Piacenza (NinoF840)
"""

from fastapi import FastAPI, HTTPException, Depends, Security, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional, Any
import uvicorn
import time
import logging
from datetime import datetime
import os

# Import existing components
from subscription_system import (
    NinoSubscriptionManager, 
    SubscriptionTier, 
    SubscriptionStatus
)

# Import the integrated pipeline
from pipeline_integration import (
    create_integrated_ner, 
    ModelPerformanceLevel,
    IntegratedItalianMedicalNER
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Nino Medical AI - Professional Subscription API",
    description="""🏥 **PROFESSIONAL MEDICAL AI PLATFORM**

🚀 **Nino Medical AI** - Italian Medical Named Entity Recognition with Enterprise-Grade Subscription Management

## 🔐 **Subscription Tiers**
- **Trial**: 14-day free trial (100 requests/day)
- **Basic**: €29.99/month (1,000 requests/day)
- **Professional**: €99.99/month (10,000 requests/day)
- **Enterprise**: €299.99/month (100,000 requests/day)
- **Research**: €149.99/month (50,000 requests/day)

## ✨ **Features**
- 🎯 51+ medical entities detected
- ✅ Confidence scores in proper 0.0-1.0 range
- 🧬 Morphological awareness for Italian medical terms
- 🔍 Advanced pattern matching with contextual boosting
- 📚 Ultra-comprehensive medical dictionary
- ⚡ Multiple performance levels per subscription tier

⚠️ **Research Use Only - Not a Medical Device**
""",
    version="3.0.0",
    contact={
        "name": "Antonino Piacenza - Nino Medical AI",
        "url": "https://ninomedical.ai",
        "email": "antonino.piacenza@ninomedical.ai"
    },
    license_info={
        "name": "Proprietary License",
        "url": "https://ninomedical.ai/license"
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global components
ner_pipeline: Optional[IntegratedItalianMedicalNER] = None
subscription_manager: Optional[NinoSubscriptionManager] = None

# Pydantic models for API
class CustomerRegistration(BaseModel):
    email: EmailStr = Field(..., description="Customer email address")
    company_name: str = Field(..., description="Company or clinic name", min_length=2)
    first_name: str = Field(..., description="First name", min_length=1)
    last_name: str = Field(..., description="Last name", min_length=1)

class SubscriptionRequest(BaseModel):
    tier: str = Field(..., description="Subscription tier", pattern="^(basic|professional|enterprise|research)$")
    billing_cycle: str = Field("monthly", description="Billing cycle", pattern="^(monthly|yearly)$")

class TextInput(BaseModel):
    text: str = Field(..., description="Italian medical text to analyze", max_length=10000)
    confidence_threshold: Optional[float] = Field(0.2, description="Confidence threshold (0.0-1.0)", ge=0.0, le=1.0)
    performance_level: Optional[str] = Field(None, description="Override performance level if allowed")

class EntityResult(BaseModel):
    text: str = Field(..., description="Entity text")
    label: str = Field(..., description="Entity type")
    start: int = Field(..., description="Start position")
    end: int = Field(..., description="End position")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    source: Optional[str] = Field(None, description="Detection source")

class AnalysisResult(BaseModel):
    success: bool = Field(..., description="Analysis success status")
    text: str = Field(..., description="Original input text")
    entities: List[EntityResult] = Field(..., description="Detected entities")
    total_entities: int = Field(..., description="Total entities found")
    entity_counts: Dict[str, int] = Field(..., description="Entities by type")
    processing_time: float = Field(..., description="Processing time in seconds")
    subscription_info: Dict[str, Any] = Field(..., description="Subscription information")
    usage_info: Dict[str, Any] = Field(..., description="Usage information")
    timestamp: str = Field(..., description="Analysis timestamp")

class SubscriptionInfo(BaseModel):
    subscription_id: int = Field(..., description="Subscription ID")
    tier: str = Field(..., description="Subscription tier")
    status: str = Field(..., description="Subscription status")
    daily_requests: int = Field(..., description="Daily request limit")
    performance_levels: List[str] = Field(..., description="Available performance levels")
    start_date: str = Field(..., description="Subscription start date")
    end_date: Optional[str] = Field(None, description="Subscription end date")
    trial_ends_at: Optional[str] = Field(None, description="Trial end date")

class UsageInfo(BaseModel):
    today_usage: int = Field(..., description="Today's usage")
    daily_limit: int = Field(..., description="Daily limit")
    remaining_requests: int = Field(..., description="Remaining requests today")
    utilization_rate: float = Field(..., description="Today's utilization rate")

def get_subscription_info(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """Enhanced subscription validation with comprehensive info"""
    api_key = credentials.credentials
    
    if not subscription_manager:
        raise HTTPException(status_code=503, detail="Subscription system not available")
    
    validation = subscription_manager.validate_api_key(api_key)
    if not validation:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")
    
    # Track usage
    subscription_manager.track_api_usage(validation["subscription_id"])
    
    # Get current usage
    today_usage = subscription_manager.get_daily_usage(validation["subscription_id"])
    
    # Check daily limit
    if today_usage > validation["daily_requests"]:
        raise HTTPException(status_code=429, detail="Daily request limit exceeded")
    
    return {
        **validation,
        "today_usage": today_usage,
        "remaining_requests": validation["daily_requests"] - today_usage
    }

@app.on_event("startup")
async def startup_event():
    """Initialize the enhanced API with subscription management"""
    global ner_pipeline, subscription_manager
    
    try:
        logger.info("🚀 Starting Nino Medical AI Professional API v3.0...")
        
        # Initialize subscription manager
        stripe_key = os.getenv("STRIPE_SECRET_KEY")
        if stripe_key:
            logger.info("✅ Stripe integration enabled")
        else:
            logger.warning("⚠️ Stripe integration disabled (no secret key)")
        
        subscription_manager = NinoSubscriptionManager(
            db_path="nino_subscriptions.db",
            stripe_secret_key=stripe_key
        )
        logger.info("✅ Subscription manager initialized")
        
        # Initialize NER pipeline
        ner_pipeline = create_integrated_ner(
            performance_level="optimized",
            confidence_threshold=0.2
        )
        logger.info("✅ NER pipeline loaded")
        
        logger.info("🎉 Nino Medical AI Professional API ready!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize API: {str(e)}")
        raise

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Enhanced API root with subscription information"""
    return {
        "company": "Nino Medical AI",
        "founder": "Antonino Piacenza (NinoF840)",
        "product": "Italian Medical NER with Professional Subscription Management",
        "version": "3.0.0",
        "copyright": "© 2025 Nino Medical AI. All Rights Reserved.",
        "website": "https://ninomedical.ai",
        "email": "antonino.piacenza@ninomedical.ai",
        "features": {
            "subscription_management": "✅ Full enterprise-grade system",
            "stripe_integration": "✅ Secure payment processing",
            "tier_based_access": "✅ 5 subscription tiers",
            "usage_tracking": "✅ Real-time analytics",
            "api_key_management": "✅ Secure key generation",
            "medical_ner": "✅ 51+ entities detected"
        },
        "subscription_tiers": {
            "trial": "FREE - 14 days, 100 requests/day",
            "basic": "€29.99/month - 1,000 requests/day",
            "professional": "€99.99/month - 10,000 requests/day",
            "enterprise": "€299.99/month - 100,000 requests/day",
            "research": "€149.99/month - 50,000 requests/day"
        },
        "endpoints": {
            "register": "/register - Register new customer",
            "subscribe": "/subscribe - Create paid subscription",
            "analyze": "/analyze - Analyze medical text",
            "subscription": "/subscription - Get subscription info",
            "usage": "/usage - Get usage analytics",
            "plans": "/plans - View all plans"
        }
    }

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Comprehensive health check"""
    status = {
        "api_status": "healthy",
        "ner_pipeline": ner_pipeline is not None,
        "subscription_system": subscription_manager is not None,
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }
    
    if ner_pipeline:
        health = ner_pipeline.get_health_status()
        status["ner_info"] = {
            "active_model": health.get("active_model"),
            "models_available": health.get("models_available", [])
        }
    
    return status

@app.post("/register", response_model=Dict[str, Any])
async def register_customer(registration: CustomerRegistration):
    """Register a new customer and create trial subscription"""
    if not subscription_manager:
        raise HTTPException(status_code=503, detail="Subscription system not available")
    
    try:
        # Create customer
        customer = subscription_manager.create_customer(
            email=registration.email,
            company_name=registration.company_name,
            first_name=registration.first_name,
            last_name=registration.last_name
        )
        
        # Create trial subscription
        trial_subscription = subscription_manager.create_trial_subscription(customer.id)
        
        return {
            "success": True,
            "message": "Registration successful! Your 14-day trial has started.",
            "customer_id": customer.id,
            "api_key": trial_subscription.api_key,
            "subscription": {
                "tier": trial_subscription.tier.value,
                "status": trial_subscription.status.value,
                "daily_requests": trial_subscription.daily_requests,
                "trial_ends_at": trial_subscription.trial_ends_at.isoformat() if trial_subscription.trial_ends_at else None
            },
            "next_steps": [
                "Save your API key securely",
                "Start testing the API",
                "Upgrade to a paid plan before trial expires"
            ]
        }
        
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/subscribe", response_model=Dict[str, Any])
async def create_subscription(
    subscription_request: SubscriptionRequest,
    subscription_info: Dict = Depends(get_subscription_info)
):
    """Create a paid subscription (upgrade from trial or change plan)"""
    if not subscription_manager:
        raise HTTPException(status_code=503, detail="Subscription system not available")
    
    try:
        # Validate tier
        try:
            tier = SubscriptionTier(subscription_request.tier)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")
        
        customer_id = subscription_info["customer_id"]
        
        # Create paid subscription
        new_subscription = subscription_manager.create_paid_subscription(
            customer_id=customer_id,
            tier=tier,
            billing_cycle=subscription_request.billing_cycle
        )
        
        return {
            "success": True,
            "message": f"Successfully subscribed to {tier.value} plan!",
            "subscription": {
                "id": new_subscription.id,
                "tier": new_subscription.tier.value,
                "status": new_subscription.status.value,
                "daily_requests": new_subscription.daily_requests,
                "performance_levels": new_subscription.performance_levels,
                "start_date": new_subscription.start_date.isoformat(),
                "end_date": new_subscription.end_date.isoformat() if new_subscription.end_date else None,
                "api_key": new_subscription.api_key
            },
            "billing": {
                "cycle": subscription_request.billing_cycle,
                "stripe_subscription_id": new_subscription.stripe_subscription_id
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Subscription creation error: {e}")
        raise HTTPException(status_code=500, detail="Subscription creation failed")

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_text(
    input_data: TextInput,
    subscription_info: Dict = Depends(get_subscription_info)
):
    """Analyze Italian medical text with subscription-based access control"""
    if not ner_pipeline:
        raise HTTPException(status_code=503, detail="NER model not loaded")
    
    try:
        # Determine performance level based on subscription
        allowed_levels = subscription_info["performance_levels"]
        performance_level = input_data.performance_level
        
        if performance_level and performance_level not in allowed_levels:
            # Fall back to best available level
            if "optimized" in allowed_levels:
                performance_level = "optimized"
            elif "enhanced" in allowed_levels:
                performance_level = "enhanced"
            else:
                performance_level = "basic"
        elif not performance_level:
            # Use best available level by default
            performance_level = allowed_levels[-1] if allowed_levels else "basic"
        
        # Perform NER analysis
        result = ner_pipeline.predict(
            input_data.text,
            confidence_threshold=input_data.confidence_threshold,
            include_source=True,
            apply_enhancement=True
        )
        
        # Format entities
        entities = [
            EntityResult(
                text=entity['text'],
                label=entity['label'],
                start=entity['start'],
                end=entity['end'],
                confidence=entity['confidence'],
                source=entity.get('source')
            )
            for entity in result['entities']
        ]
        
        return AnalysisResult(
            success=True,
            text=input_data.text,
            entities=entities,
            total_entities=result['total_entities'],
            entity_counts=result['entity_counts'],
            processing_time=result['processing_time'],
            subscription_info={
                "tier": subscription_info["tier"],
                "performance_level_used": performance_level,
                "available_levels": allowed_levels
            },
            usage_info={
                "today_usage": subscription_info["today_usage"],
                "daily_limit": subscription_info["daily_requests"],
                "remaining_requests": subscription_info["remaining_requests"]
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription_details(subscription_info: Dict = Depends(get_subscription_info)):
    """Get detailed subscription information"""
    if not subscription_manager:
        raise HTTPException(status_code=503, detail="Subscription system not available")
    
    subscription = subscription_manager.get_subscription(subscription_info["subscription_id"])
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return SubscriptionInfo(
        subscription_id=subscription.id,
        tier=subscription.tier.value,
        status=subscription.status.value,
        daily_requests=subscription.daily_requests,
        performance_levels=subscription.performance_levels,
        start_date=subscription.start_date.isoformat(),
        end_date=subscription.end_date.isoformat() if subscription.end_date else None,
        trial_ends_at=subscription.trial_ends_at.isoformat() if subscription.trial_ends_at else None
    )

@app.get("/usage", response_model=Dict[str, Any])
async def get_usage_analytics(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=90),
    subscription_info: Dict = Depends(get_subscription_info)
):
    """Get comprehensive usage analytics"""
    if not subscription_manager:
        raise HTTPException(status_code=503, detail="Subscription system not available")
    
    analytics = subscription_manager.get_usage_analytics(
        subscription_info["subscription_id"], 
        days=days
    )
    
    return {
        "analytics": analytics,
        "subscription_info": {
            "tier": subscription_info["tier"],
            "customer": subscription_info["customer_info"]
        },
        "current_usage": {
            "today": subscription_info["today_usage"],
            "limit": subscription_info["daily_requests"],
            "remaining": subscription_info["remaining_requests"]
        }
    }

@app.get("/plans", response_model=Dict[str, Any])
async def get_subscription_plans():
    """Get all available subscription plans and pricing"""
    if not subscription_manager:
        raise HTTPException(status_code=503, detail="Subscription system not available")
    
    plans = subscription_manager.get_subscription_plans()
    
    return {
        "plans": plans,
        "currency": "EUR",
        "billing_cycles": ["monthly", "yearly"],
        "trial_info": {
            "duration_days": 14,
            "daily_requests": 100,
            "features": ["Basic NER", "Email Support", "API Access"]
        },
        "contact": {
            "sales": "antonino.piacenza@ninomedical.ai",
            "support": "support@ninomedical.ai"
        }
    }

@app.delete("/subscription", response_model=Dict[str, Any])
async def cancel_subscription(subscription_info: Dict = Depends(get_subscription_info)):
    """Cancel current subscription"""
    if not subscription_manager:
        raise HTTPException(status_code=503, detail="Subscription system not available")
    
    success = subscription_manager.cancel_subscription(subscription_info["subscription_id"])
    
    if success:
        return {
            "success": True,
            "message": "Subscription cancelled successfully. Access will continue until the end of current billing period.",
            "cancelled_at": datetime.now().isoformat(),
            "subscription_id": subscription_info["subscription_id"]
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to cancel subscription")

@app.get("/demo", response_model=AnalysisResult)
async def demo_endpoint():
    """Public demo endpoint (no API key required)"""
    if not ner_pipeline:
        raise HTTPException(status_code=503, detail="NER model not loaded")
    
    demo_text = """Il paziente presenta forti mal di testa e nausea persistente da tre giorni. 
    È stato prescritto paracetamolo 500mg ogni 8 ore e si consiglia di effettuare immediatamente 
    un esame del sangue completo e una radiografia del torace per escludere altre patologie. 
    La febbre è controllata con ibuprofene e si monitora l'andamento con controlli giornalieri."""
    
    try:
        result = ner_pipeline.predict(demo_text, confidence_threshold=0.2)
        
        entities = [
            EntityResult(
                text=entity['text'],
                label=entity['label'],
                start=entity['start'],
                end=entity['end'],
                confidence=entity['confidence'],
                source=entity.get('source', 'demo')
            )
            for entity in result['entities']
        ]
        
        return AnalysisResult(
            success=True,
            text=demo_text,
            entities=entities,
            total_entities=result['total_entities'],
            entity_counts=result['entity_counts'],
            processing_time=result['processing_time'],
            subscription_info={
                "tier": "demo",
                "performance_level_used": "basic",
                "available_levels": ["demo"]
            },
            usage_info={
                "today_usage": 0,
                "daily_limit": "unlimited",
                "remaining_requests": "unlimited"
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Nino Medical AI Professional Subscription API v3.0")
    uvicorn.run(
        "subscription_api_service:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
