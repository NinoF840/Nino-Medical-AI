#!/usr/bin/env python3
"""
Nino Medical AI - Visitor Analytics Dashboard
Professional Medical AI Platform for Italian Healthcare

Copyright (C) 2025 Nino Medical AI. All Rights Reserved.
Author: NinoF840
Founder & Chief AI Officer
Date: June 2025

This script generates comprehensive analytics reports for your published project visitors.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from analytics_system import NinoMedicalAnalytics
import webbrowser

def generate_html_dashboard():
    """Generate an HTML dashboard for visitor analytics"""
    analytics = NinoMedicalAnalytics()
    
    # Get insights for different time periods
    insights_7d = analytics.get_visitor_insights(7)
    insights_30d = analytics.get_visitor_insights(30)
    model_insights_7d = analytics.get_model_performance_insights(7)
    feedback_insights_7d = analytics.get_user_feedback_insights(7)
    
    # Generate daily report
    daily_report = analytics.generate_daily_report()
    
    # Create HTML dashboard
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nino Medical AI - Visitor Analytics Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 1.1rem;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .card-icon {{
            font-size: 2rem;
            margin-right: 15px;
        }}
        
        .card-title {{
            font-size: 1.4rem;
            color: #2c3e50;
            font-weight: 600;
        }}
        
        .stat-value {{
            font-size: 2.2rem;
            font-weight: 700;
            color: #3498db;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .report-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .report-content {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 25px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            line-height: 1.4;
            white-space: pre-wrap;
            overflow-x: auto;
        }}
        
        .charts-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .chart-item {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .chart-item img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .insights-list {{
            list-style: none;
            padding: 0;
        }}
        
        .insights-list li {{
            padding: 12px 0;
            border-bottom: 1px solid #ecf0f1;
            display: flex;
            align-items: center;
        }}
        
        .insights-list li:last-child {{
            border-bottom: none;
        }}
        
        .insight-icon {{
            margin-right: 10px;
            font-size: 1.2rem;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }}
        
        .footer a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        .refresh-btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s ease;
            margin: 10px 5px;
        }}
        
        .refresh-btn:hover {{
            background: #2980b9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎆 Nino Medical AI</h1>
            <p>Visitor Analytics Dashboard - Italian Medical NER Platform</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh Data</button>
            <button class="refresh-btn" onclick="window.open('http://localhost:8000/docs')">📖 API Docs</button>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">👥</span>
                    <h3 class="card-title">Visitor Statistics (7 Days)</h3>
                </div>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-value">{insights_7d['visitor_stats'].get('unique_visitors', 0)}</div>
                        <div class="stat-label">Unique Visitors</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{insights_7d['visitor_stats'].get('total_visits', 0)}</div>
                        <div class="stat-label">Total Visits</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">📊</span>
                    <h3 class="card-title">API Usage (7 Days)</h3>
                </div>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-value">{sum(api['usage_count'] for api in insights_7d['api_usage'])}</div>
                        <div class="stat-label">Total API Calls</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{len(insights_7d['api_usage'])}</div>
                        <div class="stat-label">Active Endpoints</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">🤖</span>
                    <h3 class="card-title">Model Performance</h3>
                </div>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-value">{model_insights_7d['performance_metrics'].get('overall_avg_confidence', 0):.3f}</div>
                        <div class="stat-label">Avg Confidence</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{model_insights_7d['total_entities']}</div>
                        <div class="stat-label">Entities Detected</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">⭐</span>
                    <h3 class="card-title">User Satisfaction</h3>
                </div>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-value">{feedback_insights_7d['feedback_summary'].get('avg_rating', 0):.1f}/5.0</div>
                        <div class="stat-label">Average Rating</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{feedback_insights_7d['feedback_summary'].get('total_feedback', 0)}</div>
                        <div class="stat-label">Total Feedback</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="card-header">
                <span class="card-icon">📈</span>
                <h3 class="card-title">Analytics Charts</h3>
            </div>
            <div class="chart-grid">
                <div class="chart-item">
                    <h4>Daily Visitors Trend</h4>
                    <img src="analytics_charts/daily_visitors.png" alt="Daily Visitors Chart" onerror="this.style.display='none'">
                </div>
                <div class="chart-item">
                    <h4>API Endpoint Usage</h4>
                    <img src="analytics_charts/api_usage.png" alt="API Usage Chart" onerror="this.style.display='none'">
                </div>
                <div class="chart-item">
                    <h4>Model Performance Trends</h4>
                    <img src="analytics_charts/model_performance.png" alt="Model Performance Chart" onerror="this.style.display='none'">
                </div>
            </div>
        </div>
        
        <div class="report-section">
            <div class="card-header">
                <span class="card-icon">📋</span>
                <h3 class="card-title">Daily Analytics Report</h3>
            </div>
            <div class="report-content">{daily_report}</div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <span class="card-icon">💡</span>
                <h3 class="card-title">Key Insights & Recommendations</h3>
            </div>
            <ul class="insights-list">
                <li><span class="insight-icon">📈</span> Monitor daily visitor trends to identify growth patterns</li>
                <li><span class="insight-icon">🔍</span> Analyze API usage to understand which endpoints are most popular</li>
                <li><span class="insight-icon">⚡</span> Optimize processing time for frequently used endpoints</li>
                <li><span class="insight-icon">🎯</span> Focus marketing efforts on days with lower visitor counts</li>
                <li><span class="insight-icon">📊</span> Use confidence scores to identify areas for model improvement</li>
                <li><span class="insight-icon">💬</span> Respond to user feedback to improve satisfaction scores</li>
                <li><span class="insight-icon">🚀</span> Consider premium features based on usage patterns</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>🚀 <strong>Nino Medical AI</strong> - Democratizing Italian Medical AI for Healthcare</p>
            <p>© 2025 Nino Medical AI. All Rights Reserved.</p>
            <p>Founded by NinoF840 | <a href="https://ninomedical.ai">ninomedical.ai</a> | <a href="mailto:contact@ninomedical.ai">contact@ninomedical.ai</a></p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML dashboard
    dashboard_path = "visitor_analytics_dashboard.html"
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return dashboard_path

def run_analytics_report():
    """Run comprehensive analytics and generate reports"""
    print("🎆 Nino Medical AI - Visitor Analytics Report")
    print("="*50)
    
    analytics = NinoMedicalAnalytics()
    
    # Generate visualizations
    print("📊 Creating analytics visualizations...")
    analytics.create_visualizations(30)
    
    # Generate daily report
    print("📋 Generating daily report...")
    daily_report = analytics.generate_daily_report()
    
    # Save daily report to file
    report_filename = f"daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(daily_report)
    
    print(f"✅ Daily report saved: {report_filename}")
    
    # Export analytics data
    print("💾 Exporting analytics data...")
    export_file = analytics.export_analytics_data(
        f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    # Generate HTML dashboard
    print("🌐 Generating HTML dashboard...")
    dashboard_path = generate_html_dashboard()
    
    print(f"""
✅ Analytics Report Complete!

Generated Files:
📋 Daily Report: {report_filename}
💾 Data Export: {export_file}
🌐 HTML Dashboard: {dashboard_path}
📊 Charts: analytics_charts/ folder

🚀 Next Steps:
1. Open {dashboard_path} in your browser
2. Review daily reports for insights
3. Share charts with stakeholders
4. Monitor visitor trends regularly

© 2025 Nino Medical AI - Italian Medical AI for Healthcare
""")
    
    # Automatically open dashboard in browser
    try:
        webbrowser.open(f'file:///{os.path.abspath(dashboard_path)}')
    except Exception as e:
        print(f"Note: Could not auto-open browser. Please manually open {dashboard_path}")

if __name__ == "__main__":
    run_analytics_report()

