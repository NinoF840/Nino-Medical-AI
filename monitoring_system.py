"""
Monitoring and Scaling System for Italian Medical NER API
Author: Nino Medical AI Platform
Email: nino58150@gmail.com

This module provides comprehensive monitoring, alerting, and scaling capabilities
for the Italian Medical NER API service.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psutil
import sqlite3
import threading
from pathlib import Path

# Third-party imports
import numpy as np
from fastapi import BackgroundTasks
import asyncpg
import redis

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    response_time: float
    cpu_usage: float
    memory_usage: float
    gpu_usage: Optional[float]
    active_requests: int
    queue_size: int
    error_rate: float
    throughput: float
    model_inference_time: float

@dataclass
class AlertConfig:
    """Alert configuration"""
    metric_name: str
    threshold: float
    severity: str  # 'warning', 'critical'
    enabled: bool = True
    cooldown_minutes: int = 15

@dataclass
class ScalingRecommendation:
    """Scaling recommendation"""
    action: str  # 'scale_up', 'scale_down', 'maintain'
    reason: str
    confidence: float
    recommended_instances: int
    estimated_cost_impact: float

class MetricsCollector:
    """Collects system and application metrics"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics
        self.request_times = deque(maxlen=100)
        self.error_count = 0
        self.total_requests = 0
        self.active_requests = 0
        self.queue_size = 0
        
    def record_request_start(self):
        """Record when a request starts"""
        self.active_requests += 1
        self.total_requests += 1
        
    def record_request_end(self, response_time: float, success: bool = True):
        """Record when a request ends"""
        self.active_requests = max(0, self.active_requests - 1)
        self.request_times.append(response_time)
        if not success:
            self.error_count += 1
            
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current system metrics"""
        # System metrics
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # GPU usage (if available)
        gpu_usage = None
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_usage = gpus[0].load * 100
        except ImportError:
            pass
            
        # Application metrics
        avg_response_time = np.mean(self.request_times) if self.request_times else 0
        error_rate = (self.error_count / max(1, self.total_requests)) * 100
        throughput = len(self.request_times) / 60  # Requests per minute
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            response_time=avg_response_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            gpu_usage=gpu_usage,
            active_requests=self.active_requests,
            queue_size=self.queue_size,
            error_rate=error_rate,
            throughput=throughput,
            model_inference_time=avg_response_time * 0.7  # Estimate
        )
        
        self.metrics_history.append(metrics)
        return metrics

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, email_config: Dict):
        self.email_config = email_config
        self.alert_history = {}
        self.alert_configs = [
            AlertConfig("cpu_usage", 80.0, "warning"),
            AlertConfig("cpu_usage", 95.0, "critical"),
            AlertConfig("memory_usage", 85.0, "warning"),
            AlertConfig("memory_usage", 95.0, "critical"),
            AlertConfig("response_time", 5.0, "warning"),
            AlertConfig("response_time", 10.0, "critical"),
            AlertConfig("error_rate", 5.0, "warning"),
            AlertConfig("error_rate", 10.0, "critical"),
        ]
        
    def check_alerts(self, metrics: PerformanceMetrics):
        """Check if any alerts should be triggered"""
        current_time = datetime.now()
        
        for config in self.alert_configs:
            if not config.enabled:
                continue
                
            metric_value = getattr(metrics, config.metric_name)
            if metric_value is None:
                continue
                
            # Check if threshold is exceeded
            if metric_value > config.threshold:
                alert_key = f"{config.metric_name}_{config.severity}"
                
                # Check cooldown
                last_alert = self.alert_history.get(alert_key)
                if last_alert:
                    time_since_last = (current_time - last_alert).total_seconds() / 60
                    if time_since_last < config.cooldown_minutes:
                        continue
                
                # Trigger alert
                self._send_alert(config, metric_value, metrics)
                self.alert_history[alert_key] = current_time
                
    def _send_alert(self, config: AlertConfig, value: float, metrics: PerformanceMetrics):
        """Send alert notification"""
        subject = f"[{config.severity.upper()}] Italian Medical NER API Alert"
        
        body = f"""
        Alert: {config.metric_name} threshold exceeded
        
        Current Value: {value:.2f}
        Threshold: {config.threshold}
        Severity: {config.severity}
        
        System Status:
        - CPU Usage: {metrics.cpu_usage:.1f}%
        - Memory Usage: {metrics.memory_usage:.1f}%
        - Response Time: {metrics.response_time:.2f}s
        - Error Rate: {metrics.error_rate:.2f}%
        - Active Requests: {metrics.active_requests}
        - Throughput: {metrics.throughput:.1f} req/min
        
        Time: {metrics.timestamp}
        
        Please check the system immediately.
        
        Best regards,
        Nino Medical AI Monitoring System
        """
        
        try:
            self._send_email(subject, body)
            logging.warning(f"Alert sent: {config.metric_name} = {value}")
        except Exception as e:
            logging.error(f"Failed to send alert: {e}")
            
    def _send_email(self, subject: str, body: str):
        """Send email notification"""
        msg = MIMEMultipart()
        msg['From'] = self.email_config['from_email']
        msg['To'] = self.email_config['to_email']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
        server.starttls()
        server.login(self.email_config['username'], self.email_config['password'])
        server.send_message(msg)
        server.quit()

class ScalingEngine:
    """Provides scaling recommendations and auto-scaling"""
    
    def __init__(self):
        self.current_instances = 1
        self.min_instances = 1
        self.max_instances = 10
        self.scale_up_threshold = 70  # CPU/Memory %
        self.scale_down_threshold = 30
        self.scale_cooldown = 300  # 5 minutes
        self.last_scale_action = datetime.now() - timedelta(minutes=10)
        
    def analyze_scaling_need(self, metrics_history: List[PerformanceMetrics]) -> ScalingRecommendation:
        """Analyze metrics and provide scaling recommendation"""
        if len(metrics_history) < 5:
            return ScalingRecommendation(
                action="maintain",
                reason="Insufficient data for scaling decision",
                confidence=0.0,
                recommended_instances=self.current_instances,
                estimated_cost_impact=0.0
            )
        
        # Analyze recent metrics (last 5 minutes)
        recent_metrics = metrics_history[-5:]
        avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
        avg_memory = np.mean([m.memory_usage for m in recent_metrics])
        avg_response_time = np.mean([m.response_time for m in recent_metrics])
        avg_throughput = np.mean([m.throughput for m in recent_metrics])
        
        # Check cooldown
        time_since_last_scale = (datetime.now() - self.last_scale_action).total_seconds()
        if time_since_last_scale < self.scale_cooldown:
            return ScalingRecommendation(
                action="maintain",
                reason=f"Scaling cooldown active ({int(self.scale_cooldown - time_since_last_scale)}s remaining)",
                confidence=0.0,
                recommended_instances=self.current_instances,
                estimated_cost_impact=0.0
            )
        
        # Scale up conditions
        if (avg_cpu > self.scale_up_threshold or 
            avg_memory > self.scale_up_threshold or 
            avg_response_time > 3.0):
            
            if self.current_instances < self.max_instances:
                confidence = min(0.9, (avg_cpu + avg_memory) / 200)
                return ScalingRecommendation(
                    action="scale_up",
                    reason=f"High resource usage: CPU {avg_cpu:.1f}%, Memory {avg_memory:.1f}%, Response Time {avg_response_time:.2f}s",
                    confidence=confidence,
                    recommended_instances=min(self.current_instances + 1, self.max_instances),
                    estimated_cost_impact=50.0  # Estimated monthly cost increase
                )
        
        # Scale down conditions
        elif (avg_cpu < self.scale_down_threshold and 
              avg_memory < self.scale_down_threshold and 
              avg_throughput < 10):  # Low traffic
            
            if self.current_instances > self.min_instances:
                confidence = min(0.8, (100 - avg_cpu + 100 - avg_memory) / 200)
                return ScalingRecommendation(
                    action="scale_down",
                    reason=f"Low resource usage: CPU {avg_cpu:.1f}%, Memory {avg_memory:.1f}%, Throughput {avg_throughput:.1f} req/min",
                    confidence=confidence,
                    recommended_instances=max(self.current_instances - 1, self.min_instances),
                    estimated_cost_impact=-50.0  # Estimated monthly cost savings
                )
        
        return ScalingRecommendation(
            action="maintain",
            reason="System operating within normal parameters",
            confidence=0.7,
            recommended_instances=self.current_instances,
            estimated_cost_impact=0.0
        )
        
    def execute_scaling(self, recommendation: ScalingRecommendation) -> bool:
        """Execute scaling action (placeholder for actual implementation)"""
        if recommendation.action == "maintain":
            return True
            
        # In a real implementation, this would:
        # 1. Call cloud provider APIs (AWS ECS, Kubernetes, etc.)
        # 2. Update load balancer configurations
        # 3. Handle graceful shutdown/startup
        
        logging.info(f"Scaling action: {recommendation.action} to {recommendation.recommended_instances} instances")
        logging.info(f"Reason: {recommendation.reason}")
        
        self.current_instances = recommendation.recommended_instances
        self.last_scale_action = datetime.now()
        
        return True

class DatabaseManager:
    """Manages metrics storage and retrieval"""
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize monitoring database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            response_time REAL,
            cpu_usage REAL,
            memory_usage REAL,
            gpu_usage REAL,
            active_requests INTEGER,
            queue_size INTEGER,
            error_rate REAL,
            throughput REAL,
            model_inference_time REAL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            metric_name TEXT,
            value REAL,
            threshold REAL,
            severity TEXT,
            message TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scaling_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            action TEXT,
            from_instances INTEGER,
            to_instances INTEGER,
            reason TEXT,
            confidence REAL
        )
        """)
        
        conn.commit()
        conn.close()
        
    def store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO metrics (
            timestamp, response_time, cpu_usage, memory_usage, gpu_usage,
            active_requests, queue_size, error_rate, throughput, model_inference_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.timestamp, metrics.response_time, metrics.cpu_usage,
            metrics.memory_usage, metrics.gpu_usage, metrics.active_requests,
            metrics.queue_size, metrics.error_rate, metrics.throughput,
            metrics.model_inference_time
        ))
        
        conn.commit()
        conn.close()
        
    def get_metrics_history(self, hours: int = 24) -> List[PerformanceMetrics]:
        """Get metrics history from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        cursor.execute("""
        SELECT * FROM metrics WHERE timestamp > ? ORDER BY timestamp DESC
        """, (since,))
        
        rows = cursor.fetchall()
        conn.close()
        
        metrics = []
        for row in rows:
            metrics.append(PerformanceMetrics(
                timestamp=datetime.fromisoformat(row[1]),
                response_time=row[2],
                cpu_usage=row[3],
                memory_usage=row[4],
                gpu_usage=row[5],
                active_requests=row[6],
                queue_size=row[7],
                error_rate=row[8],
                throughput=row[9],
                model_inference_time=row[10]
            ))
        
        return metrics

class MonitoringSystem:
    """Main monitoring system orchestrator"""
    
    def __init__(self, email_config: Dict):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(email_config)
        self.scaling_engine = ScalingEngine()
        self.db_manager = DatabaseManager()
        self.running = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: int = 60):
        """Start the monitoring system"""
        if self.running:
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logging.info("Monitoring system started")
        
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logging.info("Monitoring system stopped")
        
    def _monitoring_loop(self, interval: int):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect current metrics
                metrics = self.metrics_collector.get_current_metrics()
                
                # Store metrics
                self.db_manager.store_metrics(metrics)
                
                # Check alerts
                self.alert_manager.check_alerts(metrics)
                
                # Analyze scaling needs
                history = self.db_manager.get_metrics_history(hours=1)
                if history:
                    recommendation = self.scaling_engine.analyze_scaling_need(history)
                    
                    if recommendation.action != "maintain" and recommendation.confidence > 0.7:
                        logging.info(f"Scaling recommendation: {recommendation.action}")
                        # Auto-scaling can be enabled here
                        # self.scaling_engine.execute_scaling(recommendation)
                
                # Log current status
                logging.info(f"Monitoring: CPU {metrics.cpu_usage:.1f}%, "
                           f"Memory {metrics.memory_usage:.1f}%, "
                           f"Response Time {metrics.response_time:.2f}s, "
                           f"Active Requests {metrics.active_requests}")
                
            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                
            time.sleep(interval)
            
    def get_system_status(self) -> Dict:
        """Get current system status"""
        metrics = self.metrics_collector.get_current_metrics()
        history = self.db_manager.get_metrics_history(hours=24)
        
        # Calculate trends
        if len(history) > 1:
            cpu_trend = np.mean([m.cpu_usage for m in history[-10:]]) - np.mean([m.cpu_usage for m in history[-20:-10]])
            memory_trend = np.mean([m.memory_usage for m in history[-10:]]) - np.mean([m.memory_usage for m in history[-20:-10]])
            response_time_trend = np.mean([m.response_time for m in history[-10:]]) - np.mean([m.response_time for m in history[-20:-10]])
        else:
            cpu_trend = memory_trend = response_time_trend = 0
            
        return {
            "current_metrics": asdict(metrics),
            "trends": {
                "cpu_trend": cpu_trend,
                "memory_trend": memory_trend,
                "response_time_trend": response_time_trend
            },
            "scaling_info": {
                "current_instances": self.scaling_engine.current_instances,
                "min_instances": self.scaling_engine.min_instances,
                "max_instances": self.scaling_engine.max_instances
            },
            "system_health": self._calculate_health_score(metrics)
        }
        
    def _calculate_health_score(self, metrics: PerformanceMetrics) -> Dict:
        """Calculate overall system health score"""
        scores = []
        
        # CPU health (lower is better)
        cpu_score = max(0, 100 - metrics.cpu_usage)
        scores.append(cpu_score)
        
        # Memory health (lower is better)
        memory_score = max(0, 100 - metrics.memory_usage)
        scores.append(memory_score)
        
        # Response time health (lower is better)
        response_time_score = max(0, 100 - min(100, metrics.response_time * 20))
        scores.append(response_time_score)
        
        # Error rate health (lower is better)
        error_score = max(0, 100 - metrics.error_rate * 10)
        scores.append(error_score)
        
        overall_score = np.mean(scores)
        
        if overall_score >= 80:
            status = "Excellent"
        elif overall_score >= 60:
            status = "Good"
        elif overall_score >= 40:
            status = "Fair"
        else:
            status = "Poor"
            
        return {
            "score": overall_score,
            "status": status,
            "components": {
                "cpu": cpu_score,
                "memory": memory_score,
                "response_time": response_time_score,
                "error_rate": error_score
            }
        }

# Global monitoring instance
monitoring_system = None

def init_monitoring(email_config: Dict):
    """Initialize the global monitoring system"""
    global monitoring_system
    monitoring_system = MonitoringSystem(email_config)
    return monitoring_system

def get_monitoring_system():
    """Get the global monitoring system instance"""
    return monitoring_system

if __name__ == "__main__":
    # Example usage
    email_config = {
        'from_email': 'nino58150@gmail.com',
        'to_email': 'nino58150@gmail.com',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'nino58150@gmail.com',
        'password': 'your_app_password'  # Use app password for Gmail
    }
    
    # Initialize and start monitoring
    monitor = init_monitoring(email_config)
    monitor.start_monitoring(interval=30)  # Check every 30 seconds
    
    try:
        # Keep running
        while True:
            time.sleep(60)
            status = monitor.get_system_status()
            print(f"System Health: {status['system_health']['status']} ({status['system_health']['score']:.1f}/100)")
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("Monitoring stopped")
