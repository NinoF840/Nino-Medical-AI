"""
Operational Dashboard for Italian Medical NER API Monitoring
Author: Nino Medical AI Platform
Email: nino58150@gmail.com

This dashboard provides real-time monitoring, alerting, and scaling management
for the Italian Medical NER API service.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import time
from datetime import datetime, timedelta
import json
import sqlite3
from typing import Dict, List, Optional
import asyncio
import threading

# Local imports
from monitoring_system import (
    MonitoringSystem, init_monitoring, get_monitoring_system,
    PerformanceMetrics, ScalingRecommendation
)

# Dashboard configuration
st.set_page_config(
    page_title="Nino Medical AI - Operations Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-critical {
        background-color: #ffe6e6;
        border-left: 4px solid #ff4444;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .health-excellent {
        color: #28a745;
        font-weight: bold;
    }
    .health-good {
        color: #17a2b8;
        font-weight: bold;
    }
    .health-fair {
        color: #ffc107;
        font-weight: bold;
    }
    .health-poor {
        color: #dc3545;
        font-weight: bold;
    }
    .scaling-recommendation {
        background-color: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class OperationalDashboard:
    """Main operational dashboard class"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
        self.monitoring_system = None
        self.init_session_state()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
        if 'refresh_interval' not in st.session_state:
            st.session_state.refresh_interval = 30
        if 'alerts_enabled' not in st.session_state:
            st.session_state.alerts_enabled = True
        if 'auto_scaling_enabled' not in st.session_state:
            st.session_state.auto_scaling_enabled = False
            
    def setup_monitoring(self):
        """Setup monitoring system"""
        email_config = {
            'from_email': 'nino58150@gmail.com',
            'to_email': 'nino58150@gmail.com',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'nino58150@gmail.com',
            'password': st.secrets.get("email_password", "your_app_password")
        }
        
        if not self.monitoring_system:
            try:
                self.monitoring_system = init_monitoring(email_config)
                if st.session_state.monitoring_active:
                    self.monitoring_system.start_monitoring(interval=st.session_state.refresh_interval)
                return True
            except Exception as e:
                st.error(f"Failed to initialize monitoring: {e}")
                return False
        return True
        
    def render_header(self):
        """Render dashboard header"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("🏥 Nino Medical AI - Operations Dashboard")
            st.markdown("*Real-time monitoring and scaling for Italian Medical NER API*")
            
        with col2:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.metric("Current Time", current_time)
            
        with col3:
            if st.button("🔄 Refresh Data", type="primary"):
                st.rerun()
                
    def render_control_panel(self):
        """Render system control panel"""
        st.sidebar.header("🎛️ Control Panel")
        
        # Monitoring controls
        st.sidebar.subheader("Monitoring")
        monitoring_active = st.sidebar.toggle(
            "Enable Monitoring",
            value=st.session_state.monitoring_active,
            help="Start/stop system monitoring"
        )
        
        if monitoring_active != st.session_state.monitoring_active:
            st.session_state.monitoring_active = monitoring_active
            if self.monitoring_system:
                if monitoring_active:
                    self.monitoring_system.start_monitoring()
                    st.sidebar.success("Monitoring started")
                else:
                    self.monitoring_system.stop_monitoring()
                    st.sidebar.info("Monitoring stopped")
                    
        # Refresh settings
        st.session_state.auto_refresh = st.sidebar.toggle(
            "Auto Refresh",
            value=st.session_state.auto_refresh,
            help="Automatically refresh dashboard"
        )
        
        if st.session_state.auto_refresh:
            st.session_state.refresh_interval = st.sidebar.slider(
                "Refresh Interval (seconds)",
                min_value=10,
                max_value=300,
                value=st.session_state.refresh_interval,
                step=10
            )
            
        # Alert settings
        st.sidebar.subheader("Alerts")
        st.session_state.alerts_enabled = st.sidebar.toggle(
            "Enable Alerts",
            value=st.session_state.alerts_enabled,
            help="Enable email alerts for system issues"
        )
        
        # Scaling settings
        st.sidebar.subheader("Auto-Scaling")
        st.session_state.auto_scaling_enabled = st.sidebar.toggle(
            "Enable Auto-Scaling",
            value=st.session_state.auto_scaling_enabled,
            help="Enable automatic scaling based on system metrics"
        )
        
        # System actions
        st.sidebar.subheader("System Actions")
        if st.sidebar.button("🔄 Restart API Service"):
            self.restart_api_service()
            
        if st.sidebar.button("📊 Export Metrics"):
            self.export_metrics()
            
        if st.sidebar.button("🧹 Clear Logs"):
            self.clear_logs()
            
    def render_system_overview(self):
        """Render system overview metrics"""
        st.header("📊 System Overview")
        
        if not self.monitoring_system:
            if not self.setup_monitoring():
                st.error("Monitoring system not available")
                return
                
        try:
            status = self.monitoring_system.get_system_status()
            current_metrics = status['current_metrics']
            health = status['system_health']
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                cpu_color = "normal" if current_metrics['cpu_usage'] < 70 else "inverse"
                st.metric(
                    "CPU Usage",
                    f"{current_metrics['cpu_usage']:.1f}%",
                    delta=f"{status['trends']['cpu_trend']:.1f}%",
                    delta_color=cpu_color
                )
                
            with col2:
                memory_color = "normal" if current_metrics['memory_usage'] < 70 else "inverse"
                st.metric(
                    "Memory Usage",
                    f"{current_metrics['memory_usage']:.1f}%",
                    delta=f"{status['trends']['memory_trend']:.1f}%",
                    delta_color=memory_color
                )
                
            with col3:
                response_color = "normal" if current_metrics['response_time'] < 2.0 else "inverse"
                st.metric(
                    "Response Time",
                    f"{current_metrics['response_time']:.2f}s",
                    delta=f"{status['trends']['response_time_trend']:.2f}s",
                    delta_color=response_color
                )
                
            with col4:
                st.metric(
                    "Active Requests",
                    current_metrics['active_requests'],
                    delta=None
                )
                
            # Health status
            col1, col2, col3 = st.columns(3)
            
            with col1:
                health_class = f"health-{health['status'].lower()}"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>System Health</h4>
                    <h2 class="{health_class}">{health['status']}</h2>
                    <p>Score: {health['score']:.1f}/100</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Throughput</h4>
                    <h2>{current_metrics['throughput']:.1f}</h2>
                    <p>Requests per minute</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col3:
                error_rate = current_metrics['error_rate']
                error_color = "#28a745" if error_rate < 1 else "#dc3545" if error_rate > 5 else "#ffc107"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Error Rate</h4>
                    <h2 style="color: {error_color}">{error_rate:.2f}%</h2>
                    <p>Failed requests</p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error fetching system status: {e}")
            
    def render_performance_charts(self):
        """Render performance charts"""
        st.header("📈 Performance Metrics")
        
        if not self.monitoring_system:
            st.info("Monitoring system not initialized")
            return
            
        try:
            # Get metrics history
            history = self.monitoring_system.db_manager.get_metrics_history(hours=24)
            
            if not history:
                st.info("No metrics data available yet")
                return
                
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'timestamp': m.timestamp,
                    'cpu_usage': m.cpu_usage,
                    'memory_usage': m.memory_usage,
                    'response_time': m.response_time,
                    'throughput': m.throughput,
                    'error_rate': m.error_rate,
                    'active_requests': m.active_requests
                }
                for m in history[-100:]  # Last 100 data points
            ])
            
            # Create subplots
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=[
                    'CPU & Memory Usage (%)',
                    'Response Time (seconds)',
                    'Throughput (req/min)',
                    'Error Rate (%)',
                    'Active Requests',
                    'System Load'
                ],
                vertical_spacing=0.08
            )
            
            # CPU and Memory
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['cpu_usage'], name='CPU Usage', line=dict(color='#ff7f0e')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['memory_usage'], name='Memory Usage', line=dict(color='#2ca02c')),
                row=1, col=1
            )
            
            # Response Time
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['response_time'], name='Response Time', line=dict(color='#d62728')),
                row=1, col=2
            )
            
            # Throughput
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['throughput'], name='Throughput', line=dict(color='#9467bd')),
                row=2, col=1
            )
            
            # Error Rate
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['error_rate'], name='Error Rate', line=dict(color='#8c564b')),
                row=2, col=2
            )
            
            # Active Requests
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['active_requests'], name='Active Requests', line=dict(color='#e377c2')),
                row=3, col=1
            )
            
            # System Load (combination metric)
            system_load = (df['cpu_usage'] + df['memory_usage']) / 2
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=system_load, name='System Load', line=dict(color='#7f7f7f')),
                row=3, col=2
            )
            
            fig.update_layout(height=800, showlegend=True, title_text="System Performance Metrics")
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error rendering performance charts: {e}")
            
    def render_scaling_recommendations(self):
        """Render scaling recommendations"""
        st.header("🔄 Scaling Recommendations")
        
        if not self.monitoring_system:
            st.info("Monitoring system not initialized")
            return
            
        try:
            # Get recent metrics for scaling analysis
            history = self.monitoring_system.db_manager.get_metrics_history(hours=1)
            
            if len(history) < 5:
                st.info("Insufficient data for scaling recommendations")
                return
                
            recommendation = self.monitoring_system.scaling_engine.analyze_scaling_need(history)
            
            # Display recommendation
            if recommendation.action == "scale_up":
                icon = "📈"
                color = "#ff9800"
            elif recommendation.action == "scale_down":
                icon = "📉"
                color = "#4caf50"
            else:
                icon = "➡️"
                color = "#2196f3"
                
            st.markdown(f"""
            <div class="scaling-recommendation" style="border-color: {color}">
                <h3>{icon} Scaling Recommendation: {recommendation.action.replace('_', ' ').title()}</h3>
                <p><strong>Reason:</strong> {recommendation.reason}</p>
                <p><strong>Confidence:</strong> {recommendation.confidence:.1%}</p>
                <p><strong>Recommended Instances:</strong> {recommendation.recommended_instances}</p>
                <p><strong>Cost Impact:</strong> ${recommendation.estimated_cost_impact:.2f}/month</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Scaling controls
            col1, col2, col3 = st.columns(3)
            
            with col1:
                current_instances = self.monitoring_system.scaling_engine.current_instances
                st.metric("Current Instances", current_instances)
                
            with col2:
                if st.button("Execute Scaling", disabled=(recommendation.action == "maintain")):
                    if self.execute_scaling_action(recommendation):
                        st.success("Scaling action executed successfully")
                    else:
                        st.error("Failed to execute scaling action")
                        
            with col3:
                auto_scale_status = "Enabled" if st.session_state.auto_scaling_enabled else "Disabled"
                st.info(f"Auto-scaling: {auto_scale_status}")
                
        except Exception as e:
            st.error(f"Error generating scaling recommendations: {e}")
            
    def render_active_alerts(self):
        """Render active alerts"""
        st.header("🚨 Active Alerts")
        
        if not self.monitoring_system:
            st.info("Monitoring system not initialized")
            return
            
        try:
            # Get current metrics to check for alert conditions
            status = self.monitoring_system.get_system_status()
            current_metrics = status['current_metrics']
            
            alerts = []
            
            # Check alert conditions
            if current_metrics['cpu_usage'] > 95:
                alerts.append({
                    'severity': 'critical',
                    'message': f"Critical CPU usage: {current_metrics['cpu_usage']:.1f}%",
                    'timestamp': datetime.now()
                })
            elif current_metrics['cpu_usage'] > 80:
                alerts.append({
                    'severity': 'warning',
                    'message': f"High CPU usage: {current_metrics['cpu_usage']:.1f}%",
                    'timestamp': datetime.now()
                })
                
            if current_metrics['memory_usage'] > 95:
                alerts.append({
                    'severity': 'critical',
                    'message': f"Critical memory usage: {current_metrics['memory_usage']:.1f}%",
                    'timestamp': datetime.now()
                })
            elif current_metrics['memory_usage'] > 85:
                alerts.append({
                    'severity': 'warning',
                    'message': f"High memory usage: {current_metrics['memory_usage']:.1f}%",
                    'timestamp': datetime.now()
                })
                
            if current_metrics['response_time'] > 10:
                alerts.append({
                    'severity': 'critical',
                    'message': f"Critical response time: {current_metrics['response_time']:.2f}s",
                    'timestamp': datetime.now()
                })
            elif current_metrics['response_time'] > 5:
                alerts.append({
                    'severity': 'warning',
                    'message': f"High response time: {current_metrics['response_time']:.2f}s",
                    'timestamp': datetime.now()
                })
                
            # Display alerts
            if alerts:
                for alert in alerts:
                    alert_class = f"alert-{alert['severity']}"
                    st.markdown(f"""
                    <div class="{alert_class}">
                        <strong>{alert['severity'].upper()}:</strong> {alert['message']}
                        <br><small>Time: {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No active alerts - System operating normally")
                
        except Exception as e:
            st.error(f"Error checking alerts: {e}")
            
    def render_api_health_check(self):
        """Render API health check"""
        st.header("🔍 API Health Check")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Test API Health"):
                self.test_api_health()
                
        with col2:
            if st.button("Test API Performance"):
                self.test_api_performance()
                
    def test_api_health(self):
        """Test API health endpoints"""
        try:
            # Test main health endpoint
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API Health: OK")
                health_data = response.json()
                st.json(health_data)
            else:
                st.error(f"❌ API Health: Failed ({response.status_code})")
                
        except requests.RequestException as e:
            st.error(f"❌ API Health: Connection failed - {e}")
            
    def test_api_performance(self):
        """Test API performance with sample request"""
        try:
            sample_text = "Il paziente presenta sintomi di febbre e mal di testa."
            
            start_time = time.time()
            response = requests.post(
                f"{self.api_base_url}/analyze_demo",
                json={"text": sample_text},
                timeout=10
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                st.success(f"✅ API Performance: OK ({response_time:.2f}s)")
                result = response.json()
                st.write(f"Entities found: {len(result.get('entities', []))}")
            else:
                st.error(f"❌ API Performance: Failed ({response.status_code})")
                
        except requests.RequestException as e:
            st.error(f"❌ API Performance: Connection failed - {e}")
            
    def execute_scaling_action(self, recommendation: ScalingRecommendation) -> bool:
        """Execute scaling action"""
        try:
            return self.monitoring_system.scaling_engine.execute_scaling(recommendation)
        except Exception as e:
            st.error(f"Scaling execution failed: {e}")
            return False
            
    def restart_api_service(self):
        """Restart API service (placeholder)"""
        st.info("API service restart initiated (placeholder)")
        # In production, this would call actual restart commands
        
    def export_metrics(self):
        """Export metrics to file"""
        try:
            if not self.monitoring_system:
                st.error("Monitoring system not initialized")
                return
                
            history = self.monitoring_system.db_manager.get_metrics_history(hours=24)
            if history:
                df = pd.DataFrame([
                    {
                        'timestamp': m.timestamp,
                        'cpu_usage': m.cpu_usage,
                        'memory_usage': m.memory_usage,
                        'response_time': m.response_time,
                        'throughput': m.throughput,
                        'error_rate': m.error_rate,
                        'active_requests': m.active_requests
                    }
                    for m in history
                ])
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Metrics CSV",
                    data=csv,
                    file_name=f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No metrics data available to export")
                
        except Exception as e:
            st.error(f"Export failed: {e}")
            
    def clear_logs(self):
        """Clear system logs (placeholder)"""
        st.info("System logs cleared (placeholder)")
        
    def run(self):
        """Run the dashboard"""
        self.render_header()
        self.render_control_panel()
        
        # Auto-refresh logic
        if st.session_state.auto_refresh:
            time.sleep(1)  # Small delay to prevent excessive refreshing
            st.rerun()
            
        # Main content
        self.render_system_overview()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.render_performance_charts()
            
        with col2:
            self.render_active_alerts()
            
        self.render_scaling_recommendations()
        self.render_api_health_check()
        
        # Footer
        st.markdown("---")
        st.markdown("*Nino Medical AI Platform - Operations Dashboard*")
        st.markdown("*Contact: nino58150@gmail.com*")

# Main execution
if __name__ == "__main__":
    dashboard = OperationalDashboard()
    dashboard.run()
