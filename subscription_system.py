#!/usr/bin/env python3
"""
Nino Medical AI - Subscription and Licensing System
Professional subscription management with Stripe integration

Copyright (C) 2025 Nino Medical AI. All Rights Reserved.
Author: Antonino Piacenza (NinoF840)
"""

import sqlite3
import hashlib
import secrets
import json
import stripe
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubscriptionTier(Enum):
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    RESEARCH = "research"

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TRIAL = "trial"

class LicenseType(Enum):
    API_KEY = "api_key"
    ENTERPRISE = "enterprise"
    RESEARCH = "research"
    TRIAL = "trial"

@dataclass
class SubscriptionPlan:
    tier: SubscriptionTier
    name: str
    description: str
    monthly_price: float
    yearly_price: float
    daily_requests: int
    performance_levels: List[str]
    features: List[str]
    stripe_monthly_price_id: Optional[str] = None
    stripe_yearly_price_id: Optional[str] = None

@dataclass
class Customer:
    id: Optional[int]
    email: str
    company_name: str
    first_name: str
    last_name: str
    stripe_customer_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

@dataclass
class Subscription:
    id: Optional[int]
    customer_id: int
    tier: SubscriptionTier
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime]
    stripe_subscription_id: Optional[str]
    api_key: str
    daily_requests: int
    performance_levels: List[str]
    created_at: datetime
    updated_at: datetime
    trial_ends_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

@dataclass
class UsageRecord:
    id: Optional[int]
    subscription_id: int
    date: str  # YYYY-MM-DD format
    requests_made: int
    created_at: datetime

class NinoSubscriptionManager:
    """Professional subscription and licensing management system"""
    
    def __init__(self, db_path: str = "nino_subscriptions.db", stripe_secret_key: Optional[str] = None):
        self.db_path = db_path
        self.stripe_secret_key = stripe_secret_key
        
        if stripe_secret_key:
            stripe.api_key = stripe_secret_key
        
        self.subscription_plans = {
            SubscriptionTier.TRIAL: SubscriptionPlan(
                tier=SubscriptionTier.TRIAL,
                name="Free Trial",
                description="14-day free trial with basic features",
                monthly_price=0.0,
                yearly_price=0.0,
                daily_requests=100,
                performance_levels=["basic"],
                features=["Basic NER", "Email Support", "API Access"]
            ),
            SubscriptionTier.BASIC: SubscriptionPlan(
                tier=SubscriptionTier.BASIC,
                name="Basic Plan",
                description="Perfect for small clinics and individual practitioners",
                monthly_price=29.99,
                yearly_price=299.99,
                daily_requests=1000,
                performance_levels=["basic", "enhanced"],
                features=["Enhanced NER", "Priority Support", "API Access", "Batch Processing"],
                stripe_monthly_price_id="price_basic_monthly",
                stripe_yearly_price_id="price_basic_yearly"
            ),
            SubscriptionTier.PROFESSIONAL: SubscriptionPlan(
                tier=SubscriptionTier.PROFESSIONAL,
                name="Professional Plan",
                description="Advanced features for growing medical practices",
                monthly_price=99.99,
                yearly_price=999.99,
                daily_requests=10000,
                performance_levels=["basic", "enhanced", "optimized"],
                features=["Optimized NER", "Advanced Analytics", "Custom Integration", "Phone Support"],
                stripe_monthly_price_id="price_professional_monthly",
                stripe_yearly_price_id="price_professional_yearly"
            ),
            SubscriptionTier.ENTERPRISE: SubscriptionPlan(
                tier=SubscriptionTier.ENTERPRISE,
                name="Enterprise Plan",
                description="Full-scale solution for hospitals and large organizations",
                monthly_price=299.99,
                yearly_price=2999.99,
                daily_requests=100000,
                performance_levels=["basic", "enhanced", "optimized", "auto"],
                features=["All Performance Levels", "Custom Models", "Dedicated Support", "SLA", "White-labeling"],
                stripe_monthly_price_id="price_enterprise_monthly",
                stripe_yearly_price_id="price_enterprise_yearly"
            ),
            SubscriptionTier.RESEARCH: SubscriptionPlan(
                tier=SubscriptionTier.RESEARCH,
                name="Research Plan",
                description="Special pricing for academic and research institutions",
                monthly_price=149.99,
                yearly_price=1499.99,
                daily_requests=50000,
                performance_levels=["basic", "enhanced", "optimized", "auto"],
                features=["Research License", "Publication Rights", "Academic Support", "Custom Training"],
                stripe_monthly_price_id="price_research_monthly",
                stripe_yearly_price_id="price_research_yearly"
            )
        }
        
        self._init_database()
    
    @contextmanager
    def get_db_connection(self):
        """Get database connection with proper error handling"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize the subscription database"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    company_name TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    stripe_customer_id TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Subscriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    tier TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_date TIMESTAMP NOT NULL,
                    end_date TIMESTAMP,
                    stripe_subscription_id TEXT UNIQUE,
                    api_key TEXT UNIQUE NOT NULL,
                    daily_requests INTEGER NOT NULL,
                    performance_levels TEXT NOT NULL,
                    trial_ends_at TIMESTAMP,
                    cancelled_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """)
            
            # Usage records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subscription_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    requests_made INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(subscription_id, date),
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
                )
            """)
            
            # API keys table (for additional security)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subscription_id INTEGER NOT NULL,
                    key_hash TEXT UNIQUE NOT NULL,
                    key_prefix TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    last_used TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
                )
            """)
            
            conn.commit()
            logger.info("✅ Subscription database initialized successfully")
    
    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"nino_{secrets.token_urlsafe(32)}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def create_customer(self, email: str, company_name: str, first_name: str, last_name: str) -> Customer:
        """Create a new customer"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if customer already exists
            cursor.execute("SELECT id FROM customers WHERE email = ?", (email,))
            if cursor.fetchone():
                raise ValueError(f"Customer with email {email} already exists")
            
            # Create Stripe customer if configured
            stripe_customer_id = None
            if self.stripe_secret_key:
                try:
                    stripe_customer = stripe.Customer.create(
                        email=email,
                        name=f"{first_name} {last_name}",
                        metadata={"company": company_name}
                    )
                    stripe_customer_id = stripe_customer.id
                    logger.info(f"✅ Created Stripe customer: {stripe_customer_id}")
                except Exception as e:
                    logger.warning(f"Failed to create Stripe customer: {e}")
            
            # Insert customer
            cursor.execute("""
                INSERT INTO customers (email, company_name, first_name, last_name, stripe_customer_id)
                VALUES (?, ?, ?, ?, ?)
            """, (email, company_name, first_name, last_name, stripe_customer_id))
            
            customer_id = cursor.lastrowid
            conn.commit()
            
            # Fetch and return the created customer
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            
            return Customer(
                id=row['id'],
                email=row['email'],
                company_name=row['company_name'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                stripe_customer_id=row['stripe_customer_id'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                is_active=bool(row['is_active'])
            )
    
    def create_trial_subscription(self, customer_id: int) -> Subscription:
        """Create a 14-day trial subscription"""
        plan = self.subscription_plans[SubscriptionTier.TRIAL]
        api_key = self.generate_api_key()
        
        start_date = datetime.now(timezone.utc)
        trial_ends_at = start_date + timedelta(days=14)
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO subscriptions 
                (customer_id, tier, status, start_date, api_key, daily_requests, 
                 performance_levels, trial_ends_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer_id,
                plan.tier.value,
                SubscriptionStatus.TRIAL.value,
                start_date,
                api_key,
                plan.daily_requests,
                json.dumps(plan.performance_levels),
                trial_ends_at
            ))
            
            subscription_id = cursor.lastrowid
            
            # Store API key hash
            cursor.execute("""
                INSERT INTO api_keys (subscription_id, key_hash, key_prefix)
                VALUES (?, ?, ?)
            """, (subscription_id, self.hash_api_key(api_key), api_key[:12]))
            
            conn.commit()
            
            logger.info(f"✅ Created trial subscription for customer {customer_id}")
            
            return self.get_subscription(subscription_id)
    
    def create_paid_subscription(self, customer_id: int, tier: SubscriptionTier, 
                               billing_cycle: str = "monthly") -> Subscription:
        """Create a paid subscription with Stripe integration"""
        plan = self.subscription_plans[tier]
        api_key = self.generate_api_key()
        
        if not self.stripe_secret_key:
            raise ValueError("Stripe integration not configured")
        
        # Get customer
        customer = self.get_customer(customer_id)
        if not customer or not customer.stripe_customer_id:
            raise ValueError("Customer not found or missing Stripe ID")
        
        # Create Stripe subscription
        price_id = (plan.stripe_monthly_price_id if billing_cycle == "monthly" 
                   else plan.stripe_yearly_price_id)
        
        if not price_id:
            raise ValueError(f"Price ID not configured for {tier.value} {billing_cycle}")
        
        try:
            stripe_subscription = stripe.Subscription.create(
                customer=customer.stripe_customer_id,
                items=[{"price": price_id}],
                metadata={
                    "tier": tier.value,
                    "billing_cycle": billing_cycle,
                    "customer_id": str(customer_id)
                }
            )
            
            start_date = datetime.fromtimestamp(stripe_subscription.current_period_start, timezone.utc)
            end_date = datetime.fromtimestamp(stripe_subscription.current_period_end, timezone.utc)
            
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO subscriptions 
                    (customer_id, tier, status, start_date, end_date, stripe_subscription_id,
                     api_key, daily_requests, performance_levels)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer_id,
                    tier.value,
                    SubscriptionStatus.ACTIVE.value,
                    start_date,
                    end_date,
                    stripe_subscription.id,
                    api_key,
                    plan.daily_requests,
                    json.dumps(plan.performance_levels)
                ))
                
                subscription_id = cursor.lastrowid
                
                # Store API key hash
                cursor.execute("""
                    INSERT INTO api_keys (subscription_id, key_hash, key_prefix)
                    VALUES (?, ?, ?)
                """, (subscription_id, self.hash_api_key(api_key), api_key[:12]))
                
                conn.commit()
                
                logger.info(f"✅ Created paid subscription for customer {customer_id}")
                
                return self.get_subscription(subscription_id)
                
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {e}")
            raise ValueError(f"Payment processing failed: {e}")
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return subscription info"""
        key_hash = self.hash_api_key(api_key)
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.*, c.email, c.company_name, c.first_name, c.last_name
                FROM subscriptions s
                JOIN customers c ON s.customer_id = c.id
                JOIN api_keys ak ON s.id = ak.subscription_id
                WHERE ak.key_hash = ? AND ak.is_active = 1 AND s.status IN ('active', 'trial')
            """, (key_hash,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Check if subscription is expired
            now = datetime.now(timezone.utc)
            
            # Check trial expiration
            if row['status'] == 'trial' and row['trial_ends_at']:
                trial_end = datetime.fromisoformat(row['trial_ends_at'].replace('Z', '+00:00'))
                if now > trial_end:
                    self._update_subscription_status(row['id'], SubscriptionStatus.EXPIRED)
                    return None
            
            # Check subscription expiration
            if row['end_date']:
                end_date = datetime.fromisoformat(row['end_date'].replace('Z', '+00:00'))
                if now > end_date:
                    self._update_subscription_status(row['id'], SubscriptionStatus.EXPIRED)
                    return None
            
            # Update last used timestamp
            cursor.execute("""
                UPDATE api_keys SET last_used = CURRENT_TIMESTAMP 
                WHERE key_hash = ?
            """, (key_hash,))
            conn.commit()
            
            return {
                "subscription_id": row['id'],
                "customer_id": row['customer_id'],
                "tier": row['tier'],
                "status": row['status'],
                "daily_requests": row['daily_requests'],
                "performance_levels": json.loads(row['performance_levels']),
                "customer_info": {
                    "email": row['email'],
                    "company": row['company_name'],
                    "name": f"{row['first_name']} {row['last_name']}"
                }
            }
    
    def track_api_usage(self, subscription_id: int, requests_count: int = 1):
        """Track API usage for billing and limits"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO usage_records (subscription_id, date, requests_made)
                VALUES (?, ?, 0)
            """, (subscription_id, today))
            
            cursor.execute("""
                UPDATE usage_records 
                SET requests_made = requests_made + ?
                WHERE subscription_id = ? AND date = ?
            """, (requests_count, subscription_id, today))
            
            conn.commit()
    
    def get_daily_usage(self, subscription_id: int, date: Optional[str] = None) -> int:
        """Get daily usage for a subscription"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT requests_made FROM usage_records 
                WHERE subscription_id = ? AND date = ?
            """, (subscription_id, date))
            
            row = cursor.fetchone()
            return row['requests_made'] if row else 0
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return Customer(
                id=row['id'],
                email=row['email'],
                company_name=row['company_name'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                stripe_customer_id=row['stripe_customer_id'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                is_active=bool(row['is_active'])
            )
    
    def get_subscription(self, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return Subscription(
                id=row['id'],
                customer_id=row['customer_id'],
                tier=SubscriptionTier(row['tier']),
                status=SubscriptionStatus(row['status']),
                start_date=datetime.fromisoformat(row['start_date']),
                end_date=datetime.fromisoformat(row['end_date']) if row['end_date'] else None,
                stripe_subscription_id=row['stripe_subscription_id'],
                api_key=row['api_key'],
                daily_requests=row['daily_requests'],
                performance_levels=json.loads(row['performance_levels']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                trial_ends_at=datetime.fromisoformat(row['trial_ends_at']) if row['trial_ends_at'] else None,
                cancelled_at=datetime.fromisoformat(row['cancelled_at']) if row['cancelled_at'] else None
            )
    
    def _update_subscription_status(self, subscription_id: int, status: SubscriptionStatus):
        """Update subscription status"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE subscriptions 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (status.value, subscription_id))
            
            conn.commit()
    
    def cancel_subscription(self, subscription_id: int) -> bool:
        """Cancel a subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False
        
        # Cancel in Stripe if it's a paid subscription
        if subscription.stripe_subscription_id and self.stripe_secret_key:
            try:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                logger.info(f"✅ Cancelled Stripe subscription: {subscription.stripe_subscription_id}")
            except stripe.error.StripeError as e:
                logger.error(f"Failed to cancel Stripe subscription: {e}")
        
        # Update local database
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE subscriptions 
                SET status = ?, cancelled_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (SubscriptionStatus.CANCELLED.value, subscription_id))
            
            conn.commit()
        
        return True
    
    def get_subscription_plans(self) -> Dict[str, Dict[str, Any]]:
        """Get all available subscription plans"""
        return {
            tier.value: {
                "name": plan.name,
                "description": plan.description,
                "monthly_price": plan.monthly_price,
                "yearly_price": plan.yearly_price,
                "daily_requests": plan.daily_requests,
                "performance_levels": plan.performance_levels,
                "features": plan.features,
                "savings_yearly": (plan.monthly_price * 12) - plan.yearly_price if plan.yearly_price > 0 else 0
            }
            for tier, plan in self.subscription_plans.items()
        }
    
    def get_customer_subscriptions(self, customer_id: int) -> List[Subscription]:
        """Get all subscriptions for a customer"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM subscriptions 
                WHERE customer_id = ? 
                ORDER BY created_at DESC
            """, (customer_id,))
            
            subscriptions = []
            for row in cursor.fetchall():
                subscriptions.append(Subscription(
                    id=row['id'],
                    customer_id=row['customer_id'],
                    tier=SubscriptionTier(row['tier']),
                    status=SubscriptionStatus(row['status']),
                    start_date=datetime.fromisoformat(row['start_date']),
                    end_date=datetime.fromisoformat(row['end_date']) if row['end_date'] else None,
                    stripe_subscription_id=row['stripe_subscription_id'],
                    api_key=row['api_key'],
                    daily_requests=row['daily_requests'],
                    performance_levels=json.loads(row['performance_levels']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    trial_ends_at=datetime.fromisoformat(row['trial_ends_at']) if row['trial_ends_at'] else None,
                    cancelled_at=datetime.fromisoformat(row['cancelled_at']) if row['cancelled_at'] else None
                ))
            
            return subscriptions
    
    def get_usage_analytics(self, subscription_id: int, days: int = 30) -> Dict[str, Any]:
        """Get usage analytics for a subscription"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get usage for the last N days
            cursor.execute("""
                SELECT date, requests_made FROM usage_records 
                WHERE subscription_id = ? AND date >= date('now', '-{} days')
                ORDER BY date DESC
            """.format(days), (subscription_id,))
            
            usage_data = {}
            total_requests = 0
            
            for row in cursor.fetchall():
                usage_data[row['date']] = row['requests_made']
                total_requests += row['requests_made']
            
            # Get subscription info
            subscription = self.get_subscription(subscription_id)
            if not subscription:
                return {}
            
            avg_daily_usage = total_requests / days if days > 0 else 0
            utilization_rate = (avg_daily_usage / subscription.daily_requests) * 100 if subscription.daily_requests > 0 else 0
            
            return {
                "subscription_id": subscription_id,
                "tier": subscription.tier.value,
                "daily_limit": subscription.daily_requests,
                "total_requests_period": total_requests,
                "average_daily_usage": round(avg_daily_usage, 2),
                "utilization_rate": round(utilization_rate, 2),
                "usage_by_date": usage_data,
                "period_days": days
            }

if __name__ == "__main__":
    # Test the subscription system
    print("🧪 Testing Nino Medical AI Subscription System...")
    
    # Initialize system
    subscription_manager = NinoSubscriptionManager()
    
    # Create test customer
    try:
        customer = subscription_manager.create_customer(
            email="test@ninomedical.ai",
            company_name="Test Medical Clinic",
            first_name="Dr. Mario",
            last_name="Rossi"
        )
        print(f"✅ Created customer: {customer.email}")
        
        # Create trial subscription
        trial_sub = subscription_manager.create_trial_subscription(customer.id)
        print(f"✅ Created trial subscription with API key: {trial_sub.api_key[:20]}...")
        
        # Test API key validation
        validation = subscription_manager.validate_api_key(trial_sub.api_key)
        if validation:
            print(f"✅ API key validated successfully for tier: {validation['tier']}")
        
        # Track some usage
        subscription_manager.track_api_usage(trial_sub.id, 5)
        usage = subscription_manager.get_daily_usage(trial_sub.id)
        print(f"✅ Tracked usage: {usage} requests today")
        
        # Get subscription plans
        plans = subscription_manager.get_subscription_plans()
        print(f"✅ Available plans: {list(plans.keys())}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
