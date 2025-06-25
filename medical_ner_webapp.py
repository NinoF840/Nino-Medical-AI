import streamlit as st
import requests
import json
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import subprocess
import threading
import time
import os

# Configure Streamlit page
st.set_page_config(
    page_title="Italian Medical NER - Live Demo",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for medical theme
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
.medical-header {
    background: linear-gradient(90deg, #4CAF50, #45a049);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.entity-box {
    padding: 0.5rem;
    margin: 0.2rem;
    border-radius: 5px;
    display: inline-block;
    color: white;
    font-weight: bold;
}
.medication { background-color: #FF6B6B; }
.symptom { background-color: #4ECDC4; }
.disease { background-color: #45B7D1; }
.anatomy { background-color: #96CEB4; }
.procedure { background-color: #FFEAA7; color: black; }
</style>
""", unsafe_allow_html=True)

class MedicalNERWebApp:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.db_path = "nino_medical_analytics.db"
        
    def check_api_status(self):
        """Check if API server is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_api_server(self):
        """Start the API server in background"""
        if not self.check_api_status():
            try:
                subprocess.Popen(["python", "api_service.py"], 
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(3)  # Give server time to start
                return True
            except:
                return False
        return True
    
    def process_text(self, text):
        """Process text through NER API"""
        try:
            response = requests.post(
                f"{self.api_url}/process",
                json={"text": text},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
        except Exception as e:
            return {"error": f"Connection Error: {str(e)}"}
    
    def get_analytics_data(self):
        """Get analytics data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get recent processing statistics
            query = """
            SELECT 
                COUNT(*) as total_requests,
                AVG(processing_time) as avg_processing_time,
                DATE(timestamp) as date
            FROM processing_logs 
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except:
            return pd.DataFrame()
    
    def render_entities(self, entities):
        """Render entities with color coding"""
        if not entities:
            return "No medical entities detected."
        
        html_content = ""
        entity_colors = {
            'MEDICATION': 'medication',
            'SYMPTOM': 'symptom', 
            'DISEASE': 'disease',
            'ANATOMY': 'anatomy',
            'PROCEDURE': 'procedure'
        }
        
        for entity in entities:
            entity_type = entity.get('label', 'UNKNOWN')
            entity_text = entity.get('text', '')
            confidence = entity.get('confidence', 0)
            
            css_class = entity_colors.get(entity_type, 'entity-box')
            html_content += f'<span class="entity-box {css_class}">{entity_text} ({entity_type}: {confidence:.2f})</span> '
        
        return html_content

def main():
    app = MedicalNERWebApp()
    
    # Header
    st.markdown('<div class="medical-header"><h1>🏥 Italian Medical NER - Live Demo</h1><p>Advanced Named Entity Recognition for Medical Texts</p></div>', unsafe_allow_html=True)
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🔧 Control Panel")
        
        # API Status
        api_status = app.check_api_status()
        if api_status:
            st.success("✅ API Server Online")
        else:
            st.error("❌ API Server Offline")
            if st.button("🚀 Start API Server"):
                with st.spinner("Starting API server..."):
                    if app.start_api_server():
                        st.success("Server started!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to start server")
        
        st.markdown("---")
        
        # Example texts
        st.subheader("📝 Example Texts")
        examples = [
            "Il paziente presenta febbre alta e mal di testa.",
            "Prescrizione: ibuprofene 200mg tre volte al giorno.",
            "Radiografia del torace normale, nessuna anomalia rilevata.",
            "Sintomi: nausea, vomito e dolore addominale acuto."
        ]
        
        selected_example = st.selectbox("Choose an example:", [""] + examples)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Text Analysis")
        
        # Text input
        if selected_example:
            default_text = selected_example
        else:
            default_text = ""
            
        user_text = st.text_area(
            "Enter Italian medical text:",
            value=default_text,
            height=150,
            placeholder="Inserisci qui il testo medico in italiano..."
        )
        
        # Process button
        if st.button("🔍 Analyze Text", type="primary") and user_text.strip():
            if not api_status:
                st.error("❌ API server is not running. Please start it first.")
            else:
                with st.spinner("Processing text..."):
                    result = app.process_text(user_text)
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        # Display results
                        st.success("✅ Analysis Complete!")
                        
                        # Show entities
                        entities = result.get('entities', [])
                        if entities:
                            st.subheader("🏷️ Detected Medical Entities")
                            entity_html = app.render_entities(entities)
                            st.markdown(entity_html, unsafe_allow_html=True)
                            
                            # Entity statistics
                            entity_counts = {}
                            for entity in entities:
                                label = entity.get('label', 'UNKNOWN')
                                entity_counts[label] = entity_counts.get(label, 0) + 1
                            
                            if entity_counts:
                                st.subheader("📊 Entity Distribution")
                                fig = px.pie(
                                    values=list(entity_counts.values()),
                                    names=list(entity_counts.keys()),
                                    title="Medical Entity Types"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No medical entities detected in the text.")
                        
                        # Show processing details
                        processing_time = result.get('processing_time', 0)
                        confidence_avg = sum([e.get('confidence', 0) for e in entities]) / len(entities) if entities else 0
                        
                        col1_stats, col2_stats, col3_stats = st.columns(3)
                        with col1_stats:
                            st.metric("Processing Time", f"{processing_time:.3f}s")
                        with col2_stats:
                            st.metric("Entities Found", len(entities))
                        with col3_stats:
                            st.metric("Avg Confidence", f"{confidence_avg:.3f}")
    
    with col2:
        st.subheader("📈 Analytics Dashboard")
        
        # Get analytics data
        analytics_df = app.get_analytics_data()
        
        if not analytics_df.empty:
            # Processing trends
            fig_trend = px.line(
                analytics_df, 
                x='date', 
                y='total_requests',
                title='Daily Processing Requests'
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Performance metrics
            fig_perf = px.bar(
                analytics_df,
                x='date',
                y='avg_processing_time',
                title='Average Processing Time'
            )
            st.plotly_chart(fig_perf, use_container_width=True)
        else:
            st.info("No analytics data available yet.")
        
        # System status
        st.subheader("🖥️ System Status")
        
        # Check model files
        model_files = ['model.safetensors', 'pytorch_model.bin']
        for file in model_files:
            if os.path.exists(file):
                size_mb = os.path.getsize(file) / (1024 * 1024)
                st.success(f"✅ {file} ({size_mb:.1f} MB)")
            else:
                st.error(f"❌ {file} missing")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        🏥 Italian Medical NER System | Built with ❤️ using Streamlit & Transformers
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

