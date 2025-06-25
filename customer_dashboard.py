#!/usr/bin/env python3
"""
Nino Medical AI - Customer Dashboard
Professional web interface for subscription and usage management

Copyright (C) 2025 Nino Medical AI. All Rights Reserved.
Author: Antonino Piacenza (NinoF840)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, Any, Optional
import os

# Configure the page
st.set_page_config(
    page_title="Nino Medical AI - Customer Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-message {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .subscription-tier {
        font-weight: bold;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        color: white;
        margin: 0.2rem;
    }
    
    .tier-trial { background-color: #6c757d; }
    .tier-basic { background-color: #17a2b8; }
    .tier-professional { background-color: #28a745; }
    .tier-enterprise { background-color: #dc3545; }
    .tier-research { background-color: #6f42c1; }
</style>
""", unsafe_allow_html=True)

class NinoDashboard:
    """Nino Medical AI Customer Dashboard"""
    
    def __init__(self):
        self.api_base_url = os.getenv("NINO_API_URL", "http://localhost:8002")
        
    def make_api_request(self, endpoint: str, method: str = "GET", headers: Optional[Dict] = None, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            url = f"{self.api_base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                st.error(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                st.error("🔐 Invalid or expired API key. Please check your credentials.")
                return None
            elif response.status_code == 429:
                st.error("📊 Daily request limit exceeded. Please upgrade your plan or wait until tomorrow.")
                return None
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
            return None
    
    def get_subscription_info(self, api_key: str) -> Optional[Dict]:
        """Get subscription information"""
        headers = {"Authorization": f"Bearer {api_key}"}
        return self.make_api_request("/subscription", headers=headers)
    
    def get_usage_analytics(self, api_key: str, days: int = 7) -> Optional[Dict]:
        """Get usage analytics"""
        headers = {"Authorization": f"Bearer {api_key}"}
        return self.make_api_request(f"/usage?days={days}", headers=headers)
    
    def get_plans(self) -> Optional[Dict]:
        """Get available subscription plans"""
        return self.make_api_request("/plans")
    
    def analyze_text(self, api_key: str, text: str, confidence_threshold: float = 0.2) -> Optional[Dict]:
        """Analyze medical text"""
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {
            "text": text,
            "confidence_threshold": confidence_threshold
        }
        return self.make_api_request("/analyze", method="POST", headers=headers, data=data)
    
    def cancel_subscription(self, api_key: str) -> Optional[Dict]:
        """Cancel subscription"""
        headers = {"Authorization": f"Bearer {api_key}"}
        return self.make_api_request("/subscription", method="DELETE", headers=headers)

def main():
    dashboard = NinoDashboard()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Nino Medical AI</h1>
        <h3>Customer Dashboard & API Management</h3>
        <p>Professional Italian Medical Named Entity Recognition Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("🔐 Authentication")
    
    # API Key input
    api_key = st.sidebar.text_input(
        "Enter your API Key", 
        type="password", 
        help="Your Nino Medical AI API key. Get one by registering at our platform."
    )
    
    if not api_key:
        st.sidebar.warning("Please enter your API key to access the dashboard.")
        
        # Show public information
        st.markdown("## 🚀 Welcome to Nino Medical AI")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### ✨ Features
            - 🎯 **51+ Medical Entities** detected
            - 🇮🇹 **Italian Language** specialized
            - 🧬 **Morphological Analysis** for medical terms
            - 📚 **Comprehensive Dictionary** of medical terms
            - ⚡ **Multiple Performance Levels** available
            - 🔍 **Advanced Pattern Matching** with context
            """)
        
        with col2:
            st.markdown("""
            ### 💰 Subscription Plans
            - 🆓 **Trial**: 14 days free (100 requests/day)
            - 💙 **Basic**: €29.99/month (1,000 requests/day)
            - 💚 **Professional**: €99.99/month (10,000 requests/day)
            - ❤️ **Enterprise**: €299.99/month (100,000 requests/day)
            - 💜 **Research**: €149.99/month (50,000 requests/day)
            """)
        
        # Demo section
        st.markdown("## 🧪 Try Our Demo")
        demo_response = dashboard.make_api_request("/demo")
        
        if demo_response and demo_response.get("success"):
            st.success("✅ Demo analysis successful!")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Analyzed Text:**")
                st.text_area("Demo Text", demo_response["text"], height=100, disabled=True)
            
            with col2:
                st.metric("Entities Found", demo_response["total_entities"])
                st.metric("Processing Time", f"{demo_response['processing_time']:.3f}s")
            
            # Show entities
            if demo_response["entities"]:
                st.markdown("### 🎯 Detected Medical Entities")
                entities_df = pd.DataFrame(demo_response["entities"])
                st.dataframe(entities_df, use_container_width=True)
        
        # Registration info
        st.markdown("""
        ## 📝 Getting Started
        
        1. **Register** for a free trial at our API
        2. **Get your API key** instantly
        3. **Start analyzing** Italian medical texts
        4. **Upgrade** to a paid plan for more features
        
        **Contact:** antonino.piacenza@ninomedical.ai
        """)
        
        return
    
    # If API key is provided, show dashboard
    st.sidebar.success("🔑 API Key provided")
    
    # Navigation
    page = st.sidebar.selectbox(
        "📋 Navigation",
        ["Dashboard", "Text Analysis", "Usage Analytics", "Subscription Management", "API Testing"]
    )
    
    # Get subscription info
    subscription_info = dashboard.get_subscription_info(api_key)
    
    if not subscription_info:
        st.error("❌ Failed to load subscription information. Please check your API key.")
        return
    
    # Show subscription status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Your Subscription")
    
    tier = subscription_info.get("tier", "unknown")
    status = subscription_info.get("status", "unknown")
    
    # Tier styling
    tier_class = f"tier-{tier}"
    st.sidebar.markdown(f'<div class="subscription-tier {tier_class}">{tier.upper()}</div>', unsafe_allow_html=True)
    st.sidebar.text(f"Status: {status}")
    st.sidebar.text(f"Daily Limit: {subscription_info.get('daily_requests', 0):,}")
    
    # Page routing
    if page == "Dashboard":
        show_dashboard(dashboard, api_key, subscription_info)
    elif page == "Text Analysis":
        show_text_analysis(dashboard, api_key, subscription_info)
    elif page == "Usage Analytics":
        show_usage_analytics(dashboard, api_key, subscription_info)
    elif page == "Subscription Management":
        show_subscription_management(dashboard, api_key, subscription_info)
    elif page == "API Testing":
        show_api_testing(dashboard, api_key, subscription_info)

def show_dashboard(dashboard, api_key, subscription_info):
    """Show main dashboard"""
    st.markdown("## 📊 Dashboard Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Subscription Tier",
            subscription_info.get("tier", "N/A").title(),
            delta=None
        )
    
    with col2:
        st.metric(
            "Daily Limit",
            f"{subscription_info.get('daily_requests', 0):,}",
            delta=None
        )
    
    with col3:
        # Get today's usage
        usage_data = dashboard.get_usage_analytics(api_key, days=1)
        today_usage = 0
        if usage_data and usage_data.get("current_usage"):
            today_usage = usage_data["current_usage"].get("today", 0)
        
        remaining = subscription_info.get("daily_requests", 0) - today_usage
        st.metric(
            "Remaining Today",
            f"{remaining:,}",
            delta=f"-{today_usage}" if today_usage > 0 else None
        )
    
    with col4:
        utilization = 0
        if subscription_info.get("daily_requests", 0) > 0:
            utilization = (today_usage / subscription_info["daily_requests"]) * 100
        
        st.metric(
            "Utilization Rate",
            f"{utilization:.1f}%",
            delta=None
        )
    
    # Usage chart
    st.markdown("### 📈 Usage Trends (Last 7 Days)")
    
    usage_data = dashboard.get_usage_analytics(api_key, days=7)
    if usage_data and usage_data.get("analytics", {}).get("usage_by_date"):
        usage_by_date = usage_data["analytics"]["usage_by_date"]
        
        # Prepare data for chart
        dates = list(usage_by_date.keys())
        requests = list(usage_by_date.values())
        
        # Create DataFrame
        df = pd.DataFrame({
            "Date": pd.to_datetime(dates),
            "Requests": requests
        })
        
        # Create chart
        fig = px.line(
            df, 
            x="Date", 
            y="Requests",
            title="Daily API Usage",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Requests",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 No usage data available yet. Start making API calls to see analytics!")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧪 Test API", use_container_width=True):
            test_text = "Il paziente presenta mal di testa e febbre."
            result = dashboard.analyze_text(api_key, test_text)
            if result and result.get("success"):
                st.success(f"✅ API working! Found {result['total_entities']} entities.")
            else:
                st.error("❌ API test failed.")
    
    with col2:
        if st.button("📊 View Plans", use_container_width=True):
            st.session_state.show_plans = True
    
    with col3:
        if st.button("📧 Contact Support", use_container_width=True):
            st.info("📧 Contact: antonino.piacenza@ninomedical.ai")
    
    # Show plans if requested
    if st.session_state.get("show_plans", False):
        plans_data = dashboard.get_plans()
        if plans_data and plans_data.get("plans"):
            st.markdown("### 💰 Available Plans")
            
            plans = plans_data["plans"]
            for tier, plan in plans.items():
                if tier != "trial":  # Skip trial in plans display
                    with st.expander(f"{plan['name']} - €{plan['monthly_price']}/month"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Description:** {plan['description']}")
                            st.write(f"**Daily Requests:** {plan['daily_requests']:,}")
                            st.write(f"**Monthly Price:** €{plan['monthly_price']}")
                            st.write(f"**Yearly Price:** €{plan['yearly_price']}")
                        
                        with col2:
                            st.write("**Features:**")
                            for feature in plan['features']:
                                st.write(f"• {feature}")
                            
                            st.write("**Performance Levels:**")
                            for level in plan['performance_levels']:
                                st.write(f"• {level.title()}")

def show_text_analysis(dashboard, api_key, subscription_info):
    """Show text analysis interface"""
    st.markdown("## 🧬 Medical Text Analysis")
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        text_input = st.text_area(
            "Italian Medical Text",
            placeholder="Enter your Italian medical text here...",
            height=150,
            help="Enter any Italian medical text for NER analysis. Maximum 10,000 characters."
        )
    
    with col2:
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.05,
            help="Minimum confidence score for entity detection"
        )
        
        performance_levels = subscription_info.get("performance_levels", ["basic"])
        performance_level = st.selectbox(
            "Performance Level",
            performance_levels,
            index=len(performance_levels)-1,  # Default to best available
            help="Higher levels provide better accuracy"
        )
    
    # Analysis button
    if st.button("🔍 Analyze Text", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("⚠️ Please enter some text to analyze.")
            return
        
        with st.spinner("Analyzing text..."):
            result = dashboard.analyze_text(api_key, text_input, confidence_threshold)
            
            if result and result.get("success"):
                # Success message
                st.success("✅ Analysis completed successfully!")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Entities Found", result["total_entities"])
                
                with col2:
                    st.metric("Processing Time", f"{result['processing_time']:.3f}s")
                
                with col3:
                    usage_info = result.get("usage_info", {})
                    remaining = usage_info.get("remaining_requests", 0)
                    st.metric("Remaining Requests", remaining)
                
                with col4:
                    subscription_info_result = result.get("subscription_info", {})
                    level_used = subscription_info_result.get("performance_level_used", "unknown")
                    st.metric("Performance Level", level_used.title())
                
                # Entity breakdown
                if result["entity_counts"]:
                    st.markdown("### 📊 Entity Breakdown")
                    
                    # Create pie chart
                    entity_counts = result["entity_counts"]
                    labels = list(entity_counts.keys())
                    values = list(entity_counts.values())
                    
                    fig = px.pie(
                        values=values,
                        names=labels,
                        title="Distribution of Entity Types"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Detailed entities table
                if result["entities"]:
                    st.markdown("### 🎯 Detected Entities")
                    
                    entities_df = pd.DataFrame(result["entities"])
                    
                    # Format confidence as percentage
                    entities_df["confidence"] = entities_df["confidence"].apply(lambda x: f"{x:.1%}")
                    
                    # Rename columns for display
                    entities_df = entities_df.rename(columns={
                        "text": "Entity Text",
                        "label": "Type",
                        "confidence": "Confidence",
                        "start": "Start",
                        "end": "End",
                        "source": "Source"
                    })
                    
                    st.dataframe(entities_df, use_container_width=True)
                    
                    # Download option
                    csv = entities_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name=f"nino_medical_ner_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # Highlighted text
                st.markdown("### 📝 Annotated Text")
                highlighted_text = text_input
                
                # Sort entities by start position (reverse order for replacement)
                entities = sorted(result["entities"], key=lambda x: x["start"], reverse=True)
                
                for entity in entities:
                    start, end = entity["start"], entity["end"]
                    entity_text = entity["text"]
                    entity_type = entity["label"]
                    confidence = entity["confidence"]
                    
                    # Create highlighted span
                    highlighted_span = f'<mark style="background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;" title="{entity_type} (Confidence: {confidence:.1%})">{entity_text}</mark>'
                    
                    # Replace in text
                    highlighted_text = highlighted_text[:start] + highlighted_span + highlighted_text[end:]
                
                st.markdown(highlighted_text, unsafe_allow_html=True)
                
            else:
                st.error("❌ Analysis failed. Please check your input and try again.")

def show_usage_analytics(dashboard, api_key, subscription_info):
    """Show usage analytics"""
    st.markdown("## 📊 Usage Analytics")
    
    # Time period selector
    col1, col2 = st.columns([1, 3])
    
    with col1:
        days = st.selectbox(
            "Time Period",
            [7, 14, 30, 60, 90],
            index=2,  # Default to 30 days
            format_func=lambda x: f"Last {x} days"
        )
    
    # Get analytics data
    usage_data = dashboard.get_usage_analytics(api_key, days=days)
    
    if not usage_data:
        st.error("❌ Failed to load usage analytics.")
        return
    
    analytics = usage_data.get("analytics", {})
    current_usage = usage_data.get("current_usage", {})
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = analytics.get("total_requests_period", 0)
        st.metric("Total Requests", f"{total_requests:,}")
    
    with col2:
        avg_daily = analytics.get("average_daily_usage", 0)
        st.metric("Avg Daily Usage", f"{avg_daily:.1f}")
    
    with col3:
        utilization = analytics.get("utilization_rate", 0)
        st.metric("Utilization Rate", f"{utilization:.1f}%")
    
    with col4:
        today_usage = current_usage.get("today", 0)
        st.metric("Today's Usage", f"{today_usage:,}")
    
    # Usage trend chart
    usage_by_date = analytics.get("usage_by_date", {})
    
    if usage_by_date:
        st.markdown("### 📈 Usage Trends")
        
        # Prepare data
        dates = list(usage_by_date.keys())
        requests = list(usage_by_date.values())
        
        df = pd.DataFrame({
            "Date": pd.to_datetime(dates),
            "Requests": requests
        })
        
        # Line chart
        fig = px.line(
            df,
            x="Date",
            y="Requests",
            title=f"API Usage Over Last {days} Days",
            markers=True
        )
        
        # Add daily limit line
        daily_limit = subscription_info.get("daily_requests", 0)
        if daily_limit > 0:
            fig.add_hline(
                y=daily_limit,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Daily Limit ({daily_limit:,})"
            )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Requests",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Usage distribution
        st.markdown("### 📊 Usage Distribution")
        
        # Create histogram
        fig2 = px.histogram(
            df,
            x="Requests",
            nbins=20,
            title="Distribution of Daily Usage",
            labels={"count": "Number of Days", "Requests": "Requests per Day"}
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    else:
        st.info("📊 No usage data available for the selected period.")
    
    # Usage recommendations
    st.markdown("### 💡 Usage Recommendations")
    
    if utilization < 25:
        st.info("💡 **Low Usage**: You're using less than 25% of your daily limit. Consider downgrading to save costs.")
    elif utilization > 80:
        st.warning("⚠️ **High Usage**: You're using over 80% of your daily limit. Consider upgrading for better performance.")
    else:
        st.success("✅ **Optimal Usage**: Your usage pattern looks good for your current plan.")

def show_subscription_management(dashboard, api_key, subscription_info):
    """Show subscription management"""
    st.markdown("## 🔐 Subscription Management")
    
    # Current subscription info
    st.markdown("### 📋 Current Subscription")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Tier:** {subscription_info.get('tier', 'N/A').title()}
        
        **Status:** {subscription_info.get('status', 'N/A').title()}
        
        **Daily Requests:** {subscription_info.get('daily_requests', 0):,}
        
        **Performance Levels:** {', '.join(subscription_info.get('performance_levels', []))}
        """)
    
    with col2:
        start_date = subscription_info.get('start_date', 'N/A')
        end_date = subscription_info.get('end_date', 'N/A')
        trial_ends = subscription_info.get('trial_ends_at', 'N/A')
        
        st.info(f"""
        **Start Date:** {start_date[:10] if start_date != 'N/A' else 'N/A'}
        
        **End Date:** {end_date[:10] if end_date != 'N/A' else 'N/A'}
        
        **Trial Ends:** {trial_ends[:10] if trial_ends != 'N/A' else 'N/A'}
        
        **Subscription ID:** {subscription_info.get('subscription_id', 'N/A')}
        """)
    
    # Available plans
    st.markdown("### 💰 Available Plans")
    
    plans_data = dashboard.get_plans()
    if plans_data and plans_data.get("plans"):
        plans = plans_data["plans"]
        
        current_tier = subscription_info.get("tier", "")
        
        for tier, plan in plans.items():
            if tier == "trial":
                continue  # Skip trial in upgrade options
            
            is_current = (tier == current_tier)
            
            with st.expander(f"{'⭐ ' if is_current else ''}{plan['name']} - €{plan['monthly_price']}/month"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Monthly:** €{plan['monthly_price']}")
                    st.write(f"**Yearly:** €{plan['yearly_price']}")
                    if plan['yearly_price'] > 0:
                        savings = (plan['monthly_price'] * 12) - plan['yearly_price']
                        st.write(f"**Yearly Savings:** €{savings:.2f}")
                
                with col2:
                    st.write(f"**Daily Requests:** {plan['daily_requests']:,}")
                    st.write("**Performance Levels:**")
                    for level in plan['performance_levels']:
                        st.write(f"• {level.title()}")
                
                with col3:
                    st.write("**Features:**")
                    for feature in plan['features']:
                        st.write(f"• {feature}")
                
                if is_current:
                    st.success("✅ This is your current plan")
                else:
                    if st.button(f"Upgrade to {plan['name']}", key=f"upgrade_{tier}"):
                        st.info("🔄 Upgrade functionality would redirect to payment processor.")
    
    # Subscription actions
    st.markdown("### ⚙️ Subscription Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📧 Contact Sales", use_container_width=True):
            st.info("""
            📧 **Sales Contact:**
            antonino.piacenza@ninomedical.ai
            
            💬 **Subject:** Subscription Inquiry - {subscription_info.get('subscription_id', 'N/A')}
            """)
    
    with col2:
        if st.button("❌ Cancel Subscription", use_container_width=True, type="secondary"):
            st.warning("⚠️ Are you sure you want to cancel your subscription?")
            
            if st.button("⚠️ Yes, Cancel My Subscription", type="secondary"):
                result = dashboard.cancel_subscription(api_key)
                if result and result.get("success"):
                    st.success("✅ Subscription cancelled successfully.")
                    st.info("ℹ️ Your access will continue until the end of your current billing period.")
                    st.rerun()
                else:
                    st.error("❌ Failed to cancel subscription. Please contact support.")

def show_api_testing(dashboard, api_key, subscription_info):
    """Show API testing interface"""
    st.markdown("## 🧪 API Testing")
    
    # Test endpoint selector
    endpoint = st.selectbox(
        "Test Endpoint",
        ["/analyze", "/subscription", "/usage", "/plans", "/demo"],
        help="Select which API endpoint to test"
    )
    
    if endpoint == "/analyze":
        st.markdown("### 🧬 Test Text Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            test_text = st.text_area(
                "Test Text",
                value="Il paziente presenta mal di testa persistente e nausea. È stata prescritta una TAC del cranio.",
                height=100
            )
        
        with col2:
            confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.2, 0.05)
        
        if st.button("🔍 Test Analysis", type="primary"):
            with st.spinner("Testing..."):
                result = dashboard.analyze_text(api_key, test_text, confidence)
                
                if result:
                    st.success("✅ API call successful!")
                    st.json(result)
                else:
                    st.error("❌ API call failed.")
    
    elif endpoint == "/subscription":
        st.markdown("### 📋 Test Subscription Info")
        
        if st.button("📋 Get Subscription Info", type="primary"):
            with st.spinner("Testing..."):
                result = dashboard.get_subscription_info(api_key)
                
                if result:
                    st.success("✅ API call successful!")
                    st.json(result)
                else:
                    st.error("❌ API call failed.")
    
    elif endpoint == "/usage":
        st.markdown("### 📊 Test Usage Analytics")
        
        days = st.slider("Days to analyze", 1, 90, 7)
        
        if st.button("📊 Get Usage Analytics", type="primary"):
            with st.spinner("Testing..."):
                result = dashboard.get_usage_analytics(api_key, days)
                
                if result:
                    st.success("✅ API call successful!")
                    st.json(result)
                else:
                    st.error("❌ API call failed.")
    
    elif endpoint == "/plans":
        st.markdown("### 💰 Test Plans Endpoint")
        
        if st.button("💰 Get Plans", type="primary"):
            with st.spinner("Testing..."):
                result = dashboard.get_plans()
                
                if result:
                    st.success("✅ API call successful!")
                    st.json(result)
                else:
                    st.error("❌ API call failed.")
    
    elif endpoint == "/demo":
        st.markdown("### 🧪 Test Demo Endpoint")
        
        if st.button("🧪 Test Demo", type="primary"):
            with st.spinner("Testing..."):
                result = dashboard.make_api_request("/demo")
                
                if result:
                    st.success("✅ API call successful!")
                    st.json(result)
                else:
                    st.error("❌ API call failed.")
    
    # Raw API testing
    st.markdown("### 🔧 Raw API Testing")
    
    with st.expander("Advanced API Testing"):
        col1, col2 = st.columns(2)
        
        with col1:
            custom_endpoint = st.text_input("Custom Endpoint", value="/health")
            method = st.selectbox("HTTP Method", ["GET", "POST", "DELETE"])
        
        with col2:
            if method == "POST":
                custom_data = st.text_area("Request Data (JSON)", value="{}")
            else:
                custom_data = "{}"
        
        if st.button("🚀 Send Request", type="secondary"):
            try:
                headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                data = json.loads(custom_data) if custom_data.strip() else None
                
                result = dashboard.make_api_request(custom_endpoint, method, headers, data)
                
                if result:
                    st.success("✅ Request successful!")
                    st.json(result)
                else:
                    st.error("❌ Request failed.")
                    
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON in request data.")

if __name__ == "__main__":
    main()
