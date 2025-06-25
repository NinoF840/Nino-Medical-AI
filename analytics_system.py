#!/usr/bin/env python3
"""
Nino Medical AI - Analytics and Visitor Tracking System
Professional Medical AI Platform for Italian Healthcare

Copyright (C) 2025 Nino Medical AI. All Rights Reserved.
Author: NinoF840
Founder & Chief AI Officer
Date: June 2025

This software is proprietary and confidential. Unauthorized copying, 
transferring or reproduction of the contents of this file, via any medium 
is strictly prohibited without the express written permission of Nino Medical AI.
"""

import sqlite3
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional
import hashlib
from collections import Counter
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NinoMedicalAnalytics:
    """
    Comprehensive analytics system for Nino Medical AI
    Tracks visitors, API usage, model performance, and generates insights
    """
    
    def __init__(self, db_path: str = "nino_medical_analytics.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database with analytics tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Visitor tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visitor_id TEXT UNIQUE,
                first_visit TIMESTAMP,
                last_visit TIMESTAMP,
                total_visits INTEGER DEFAULT 1,
                user_agent TEXT,
                ip_hash TEXT
            )
        """)
        
        # API usage tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visitor_id TEXT,
                endpoint TEXT,
                text_length INTEGER,
                entities_found INTEGER,
                confidence_threshold REAL,
                processing_time REAL,
                success BOOLEAN,
                api_key_tier TEXT
            )
        """)
        
        # Model performance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                text_sample TEXT,
                entities_detected INTEGER,
                avg_confidence REAL,
                source_breakdown TEXT,  -- JSON: {"model": 3, "pattern": 1, "dictionary": 1}
                entity_types TEXT,     -- JSON: {"PROBLEM": 2, "TREATMENT": 2, "TEST": 1}
                processing_time REAL
            )
        """)
        
        # User feedback tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visitor_id TEXT,
                rating INTEGER,  -- 1-5 stars
                feedback_text TEXT,
                improvement_suggestions TEXT,
                contact_email TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Analytics database initialized successfully")
    
    def track_visitor(self, visitor_id: str, user_agent: str = "", ip_address: str = ""):
        """Track visitor with privacy-preserving approach"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hash IP address for privacy
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16] if ip_address else ""
        
        # Check if visitor exists
        cursor.execute("SELECT total_visits FROM visitors WHERE visitor_id = ?", (visitor_id,))
        result = cursor.fetchone()
        
        if result:
            # Update existing visitor
            cursor.execute("""
                UPDATE visitors 
                SET last_visit = CURRENT_TIMESTAMP, total_visits = total_visits + 1
                WHERE visitor_id = ?
            """, (visitor_id,))
        else:
            # New visitor
            cursor.execute("""
                INSERT INTO visitors (visitor_id, first_visit, last_visit, user_agent, ip_hash)
                VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?)
            """, (visitor_id, user_agent, ip_hash))
        
        conn.commit()
        conn.close()
    
    def track_api_usage(self, visitor_id: str, endpoint: str, text_length: int, 
                       entities_found: int, confidence_threshold: float, 
                       processing_time: float, success: bool, api_key_tier: str = "demo"):
        """Track API endpoint usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO api_usage 
            (visitor_id, endpoint, text_length, entities_found, confidence_threshold, 
             processing_time, success, api_key_tier)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (visitor_id, endpoint, text_length, entities_found, confidence_threshold, 
              processing_time, success, api_key_tier))
        
        conn.commit()
        conn.close()
    
    def track_model_performance(self, text_sample: str, entities: List[Dict], processing_time: float):
        """Track model performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyze entities
        entities_count = len(entities)
        avg_confidence = sum(e['confidence'] for e in entities) / max(1, entities_count)
        
        # Source breakdown
        source_breakdown = Counter(e.get('source', 'model') for e in entities)
        entity_types = Counter(e['label'] for e in entities)
        
        cursor.execute("""
            INSERT INTO model_performance 
            (text_sample, entities_detected, avg_confidence, source_breakdown, 
             entity_types, processing_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (text_sample[:500], entities_count, avg_confidence, 
              json.dumps(dict(source_breakdown)), json.dumps(dict(entity_types)), processing_time))
        
        conn.commit()
        conn.close()
    
    def add_user_feedback(self, visitor_id: str, rating: int, feedback_text: str = "", 
                         improvement_suggestions: str = "", contact_email: str = ""):
        """Add user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_feedback 
            (visitor_id, rating, feedback_text, improvement_suggestions, contact_email)
            VALUES (?, ?, ?, ?, ?)
        """, (visitor_id, rating, feedback_text, improvement_suggestions, contact_email))
        
        conn.commit()
        conn.close()
        logger.info(f"User feedback added: {rating} stars from {visitor_id}")
    
    def get_visitor_insights(self, days: int = 30) -> Dict[str, Any]:
        """Generate visitor insights for the last N days"""
        conn = sqlite3.connect(self.db_path)
        
        # Basic visitor stats
        query = """
            SELECT 
                COUNT(DISTINCT visitor_id) as unique_visitors,
                SUM(total_visits) as total_visits,
                AVG(total_visits) as avg_visits_per_user,
                MIN(first_visit) as first_user_date,
                MAX(last_visit) as latest_visit
            FROM visitors 
            WHERE last_visit >= datetime('now', '-{} days')
        """.format(days)
        
        df_visitors = pd.read_sql(query, conn)
        
        # Daily visitor trend
        trend_query = """
            SELECT 
                DATE(last_visit) as visit_date,
                COUNT(DISTINCT visitor_id) as unique_visitors,
                COUNT(*) as total_visits
            FROM visitors 
            WHERE last_visit >= datetime('now', '-{} days')
            GROUP BY DATE(last_visit)
            ORDER BY visit_date
        """.format(days)
        
        df_trend = pd.read_sql(trend_query, conn)
        
        # API usage stats
        api_query = """
            SELECT 
                endpoint,
                COUNT(*) as usage_count,
                AVG(processing_time) as avg_processing_time,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_calls,
                AVG(entities_found) as avg_entities_found
            FROM api_usage 
            WHERE timestamp >= datetime('now', '-{} days')
            GROUP BY endpoint
        """.format(days)
        
        df_api = pd.read_sql(api_query, conn)
        
        conn.close()
        
        return {
            'period_days': days,
            'visitor_stats': df_visitors.to_dict('records')[0] if not df_visitors.empty else {},
            'daily_trend': df_trend.to_dict('records'),
            'api_usage': df_api.to_dict('records'),
            'generated_at': datetime.now().isoformat()
        }
    
    def get_model_performance_insights(self, days: int = 30) -> Dict[str, Any]:
        """Generate model performance insights"""
        conn = sqlite3.connect(self.db_path)
        
        # Performance metrics
        perf_query = """
            SELECT 
                COUNT(*) as total_predictions,
                AVG(entities_detected) as avg_entities_per_text,
                AVG(avg_confidence) as overall_avg_confidence,
                AVG(processing_time) as avg_processing_time,
                MIN(processing_time) as min_processing_time,
                MAX(processing_time) as max_processing_time
            FROM model_performance 
            WHERE timestamp >= datetime('now', '-{} days')
        """.format(days)
        
        df_perf = pd.read_sql(perf_query, conn)
        
        # Source breakdown analysis
        source_query = """
            SELECT source_breakdown, entity_types, entities_detected, avg_confidence
            FROM model_performance 
            WHERE timestamp >= datetime('now', '-{} days')
        """.format(days)
        
        df_sources = pd.read_sql(source_query, conn)
        
        # Aggregate source and entity type statistics
        source_stats = {'model': 0, 'pattern': 0, 'dictionary': 0}
        entity_stats = {'PROBLEM': 0, 'TREATMENT': 0, 'TEST': 0}
        
        for _, row in df_sources.iterrows():
            if row['source_breakdown']:
                try:
                    sources = json.loads(row['source_breakdown'])
                    for source, count in sources.items():
                        if source in source_stats:
                            source_stats[source] += count
                except json.JSONDecodeError:
                    pass
            
            if row['entity_types']:
                try:
                    entities = json.loads(row['entity_types'])
                    for entity_type, count in entities.items():
                        if entity_type in entity_stats:
                            entity_stats[entity_type] += count
                except json.JSONDecodeError:
                    pass
        
        conn.close()
        
        return {
            'period_days': days,
            'performance_metrics': df_perf.to_dict('records')[0] if not df_perf.empty else {},
            'source_breakdown': source_stats,
            'entity_type_distribution': entity_stats,
            'total_sources': sum(source_stats.values()),
            'total_entities': sum(entity_stats.values()),
            'generated_at': datetime.now().isoformat()
        }
    
    def get_user_feedback_insights(self, days: int = 30) -> Dict[str, Any]:
        """Generate user feedback insights"""
        conn = sqlite3.connect(self.db_path)
        
        feedback_query = """
            SELECT 
                AVG(rating) as avg_rating,
                COUNT(*) as total_feedback,
                COUNT(DISTINCT visitor_id) as unique_feedback_users,
                SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as positive_feedback,
                SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) as negative_feedback
            FROM user_feedback 
            WHERE timestamp >= datetime('now', '-{} days')
        """.format(days)
        
        df_feedback = pd.read_sql(feedback_query, conn)
        
        # Recent feedback with text
        recent_query = """
            SELECT rating, feedback_text, improvement_suggestions, timestamp
            FROM user_feedback 
            WHERE timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp DESC
            LIMIT 10
        """.format(days)
        
        df_recent = pd.read_sql(recent_query, conn)
        
        conn.close()
        
        return {
            'period_days': days,
            'feedback_summary': df_feedback.to_dict('records')[0] if not df_feedback.empty else {},
            'recent_feedback': df_recent.to_dict('records'),
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_daily_report(self) -> str:
        """Generate a comprehensive daily analytics report"""
        visitor_insights = self.get_visitor_insights(1)
        model_insights = self.get_model_performance_insights(1)
        feedback_insights = self.get_user_feedback_insights(1)
        
        report = f"""
🎆 NINO MEDICAL AI - DAILY ANALYTICS REPORT
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
👥 VISITOR ANALYTICS
{'='*60}

Unique Visitors Today: {visitor_insights['visitor_stats'].get('unique_visitors', 0)}
Total Visits Today: {visitor_insights['visitor_stats'].get('total_visits', 0)}
Avg Visits per User: {visitor_insights['visitor_stats'].get('avg_visits_per_user', 0):.1f}

📊 API Usage:
"""
        
        for api_stat in visitor_insights['api_usage']:
            report += f"  • {api_stat['endpoint']}: {api_stat['usage_count']} calls ({api_stat['avg_processing_time']:.3f}s avg)\n"
        
        report += f"""

{'='*60}
🤖 MODEL PERFORMANCE
{'='*60}

Total Predictions: {model_insights['performance_metrics'].get('total_predictions', 0)}
Avg Entities per Text: {model_insights['performance_metrics'].get('avg_entities_per_text', 0):.1f}
Overall Confidence: {model_insights['performance_metrics'].get('overall_avg_confidence', 0):.3f}
Avg Processing Time: {model_insights['performance_metrics'].get('avg_processing_time', 0):.3f}s

🔍 Detection Sources:
  • Model: {model_insights['source_breakdown']['model']} entities
  • Patterns: {model_insights['source_breakdown']['pattern']} entities  
  • Dictionary: {model_insights['source_breakdown']['dictionary']} entities

🏷️ Entity Types:
  • PROBLEM: {model_insights['entity_type_distribution']['PROBLEM']} entities
  • TREATMENT: {model_insights['entity_type_distribution']['TREATMENT']} entities
  • TEST: {model_insights['entity_type_distribution']['TEST']} entities

{'='*60}
⭐ USER FEEDBACK
{'='*60}

Total Feedback: {feedback_insights['feedback_summary'].get('total_feedback', 0)}
Average Rating: {feedback_insights['feedback_summary'].get('avg_rating', 0):.1f}/5.0
Positive Feedback: {feedback_insights['feedback_summary'].get('positive_feedback', 0)}
Negative Feedback: {feedback_insights['feedback_summary'].get('negative_feedback', 0)}
"""
        
        if feedback_insights['recent_feedback']:
            report += "\n📝 Recent Feedback:\n"
            for feedback in feedback_insights['recent_feedback'][:3]:
                report += f"  • {feedback['rating']}⭐ - {feedback['feedback_text'][:100]}...\n"
        
        report += f"""

{'='*60}
📈 INSIGHTS & RECOMMENDATIONS
{'='*60}

"""
        
        # Generate insights based on data
        unique_visitors = visitor_insights['visitor_stats'].get('unique_visitors', 0)
        avg_confidence = model_insights['performance_metrics'].get('overall_avg_confidence', 0)
        avg_rating = feedback_insights['feedback_summary'].get('avg_rating', 0)
        
        if unique_visitors > 10:
            report += "✅ Great visitor engagement today!\n"
        elif unique_visitors > 0:
            report += "📢 Consider promoting your API to attract more visitors\n"
        else:
            report += "🔍 No visitors today - time to increase marketing efforts\n"
        
        if avg_confidence > 0.8:
            report += "✅ Excellent model confidence scores!\n"
        elif avg_confidence > 0.6:
            report += "📊 Good model performance, consider fine-tuning for higher confidence\n"
        
        if avg_rating >= 4.0:
            report += "⭐ Outstanding user satisfaction!\n"
        elif avg_rating >= 3.0:
            report += "📈 Good user feedback, look for improvement opportunities\n"
        
        report += f"""

💡 Action Items:
  • Check API endpoint performance and optimize slow endpoints
  • Review user feedback for improvement suggestions
  • Monitor model confidence and retrain if needed
  • Engage with users who provided contact information

🚀 Nino Medical AI - Democratizing Italian Medical AI
© 2025 Nino Medical AI. All Rights Reserved.
"""
        
        return report
    
    def create_visualizations(self, days: int = 30, output_dir: str = "analytics_charts"):
        """Create visualization charts for analytics data"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        conn = sqlite3.connect(self.db_path)
        
        # 1. Daily visitor trend
        trend_query = f"""
            SELECT 
                DATE(last_visit) as visit_date,
                COUNT(DISTINCT visitor_id) as unique_visitors
            FROM visitors 
            WHERE last_visit >= datetime('now', '-{days} days')
            GROUP BY DATE(last_visit)
            ORDER BY visit_date
        """
        
        df_trend = pd.read_sql(trend_query, conn)
        
        if not df_trend.empty:
            plt.figure(figsize=(12, 6))
            plt.plot(df_trend['visit_date'], df_trend['unique_visitors'], marker='o', linewidth=2)
            plt.title('Daily Unique Visitors - Nino Medical AI', fontsize=16, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Unique Visitors')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/daily_visitors.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. API Endpoint Usage
        api_query = f"""
            SELECT endpoint, COUNT(*) as usage_count
            FROM api_usage 
            WHERE timestamp >= datetime('now', '-{days} days')
            GROUP BY endpoint
        """
        
        df_api = pd.read_sql(api_query, conn)
        
        if not df_api.empty:
            plt.figure(figsize=(10, 6))
            plt.bar(df_api['endpoint'], df_api['usage_count'], color='steelblue')
            plt.title('API Endpoint Usage - Nino Medical AI', fontsize=16, fontweight='bold')
            plt.xlabel('Endpoint')
            plt.ylabel('Usage Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/api_usage.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Model Performance Over Time
        perf_query = f"""
            SELECT 
                DATE(timestamp) as date,
                AVG(avg_confidence) as daily_avg_confidence,
                AVG(entities_detected) as daily_avg_entities
            FROM model_performance 
            WHERE timestamp >= datetime('now', '-{days} days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        """
        
        df_perf = pd.read_sql(perf_query, conn)
        
        if not df_perf.empty:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Confidence over time
            ax1.plot(df_perf['date'], df_perf['daily_avg_confidence'], marker='o', color='green', linewidth=2)
            ax1.set_title('Daily Average Confidence Score', fontweight='bold')
            ax1.set_ylabel('Confidence Score')
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)
            
            # Entities detected over time
            ax2.plot(df_perf['date'], df_perf['daily_avg_entities'], marker='s', color='orange', linewidth=2)
            ax2.set_title('Daily Average Entities Detected', fontweight='bold')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Entities per Text')
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            plt.suptitle('Model Performance Trends - Nino Medical AI', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(f'{output_dir}/model_performance.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        conn.close()
        logger.info(f"Visualizations saved to {output_dir}/")
    
    def export_analytics_data(self, output_file: str = "nino_medical_analytics_export.json"):
        """Export all analytics data to JSON file"""
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'visitor_insights_7d': self.get_visitor_insights(7),
            'visitor_insights_30d': self.get_visitor_insights(30),
            'model_performance_7d': self.get_model_performance_insights(7),
            'model_performance_30d': self.get_model_performance_insights(30),
            'user_feedback_7d': self.get_user_feedback_insights(7),
            'user_feedback_30d': self.get_user_feedback_insights(30)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analytics data exported to {output_file}")
        return output_file


def demo_analytics_system():
    """Demonstrate the analytics system with sample data"""
    print("🎆 Nino Medical AI - Analytics System Demo")
    print("="*50)
    
    # Initialize analytics
    analytics = NinoMedicalAnalytics()
    
    # Add sample data
    print("📊 Adding sample analytics data...")
    
    # Sample visitors
    analytics.track_visitor("user_001", "Mozilla/5.0 Chrome", "192.168.1.1")
    analytics.track_visitor("user_002", "Mozilla/5.0 Firefox", "192.168.1.2")
    analytics.track_visitor("user_003", "Mozilla/5.0 Safari", "192.168.1.3")
    
    # Sample API usage
    analytics.track_api_usage("user_001", "/analyze", 150, 3, 0.7, 0.234, True, "demo")
    analytics.track_api_usage("user_002", "/batch", 300, 7, 0.6, 0.456, True, "professional")
    analytics.track_api_usage("user_003", "/analyze", 80, 1, 0.8, 0.123, True, "demo")
    
    # Sample model performance
    sample_entities = [
        {'text': 'febbre', 'label': 'PROBLEM', 'confidence': 0.95, 'source': 'model'},
        {'text': 'paracetamolo', 'label': 'TREATMENT', 'confidence': 0.88, 'source': 'model'},
        {'text': 'mal di testa', 'label': 'PROBLEM', 'confidence': 0.82, 'source': 'pattern'}
    ]
    
    analytics.track_model_performance("Il paziente ha febbre e prende paracetamolo per il mal di testa.", 
                                    sample_entities, 0.234)
    
    # Sample feedback
    analytics.add_user_feedback("user_001", 5, "Excellent API! Very accurate for Italian medical texts.")
    analytics.add_user_feedback("user_002", 4, "Good performance, could be faster.")
    
    print("✅ Sample data added successfully!")
    
    # Generate report
    print("\n📋 Generating daily report...")
    report = analytics.generate_daily_report()
    print(report)
    
    # Create visualizations
    print("\n📊 Creating visualizations...")
    analytics.create_visualizations(7)
    
    # Export data
    print("\n💾 Exporting analytics data...")
    export_file = analytics.export_analytics_data()
    
    print(f"\n🎉 Demo completed! Check {export_file} and analytics_charts/ folder")


if __name__ == "__main__":
    demo_analytics_system()

