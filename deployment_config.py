"""
Deployment Configuration and Scaling Setup for Italian Medical NER API
Author: Nino Medical AI Platform
Email: nino58150@gmail.com

This module provides deployment configurations, Docker setup, and scaling
configurations for production deployment of the Italian Medical NER API.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "nino_medical_ner"
    user: str = "api_user"
    password: str = "secure_password"
    ssl_mode: str = "require"
    max_connections: int = 20

@dataclass
class RedisConfig:
    """Redis configuration for caching and rate limiting"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 10

@dataclass
class MonitoringConfig:
    """Monitoring system configuration"""
    enabled: bool = True
    metrics_interval: int = 60
    alert_email: str = "nino58150@gmail.com"
    slack_webhook: Optional[str] = None
    prometheus_port: int = 9090
    grafana_port: int = 3000

@dataclass
class ScalingConfig:
    """Auto-scaling configuration"""
    enabled: bool = True
    min_instances: int = 2
    max_instances: int = 20
    target_cpu_percent: int = 70
    target_memory_percent: int = 80
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    cors_origins: List[str] = None
    rate_limit_per_minute: int = 100
    max_request_size: str = "10MB"

@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    worker_class: str = "uvicorn.workers.UvicornWorker"
    timeout: int = 120
    max_requests: int = 1000
    max_requests_jitter: int = 100

class DeploymentManager:
    """Manages deployment configurations and scripts"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_name = "nino-medical-ner"
        self.project_root = Path(__file__).parent
        
    def generate_docker_compose(self) -> str:
        """Generate Docker Compose configuration"""
        
        compose_config = {
            'version': '3.8',
            'services': {
                'api': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile'
                    },
                    'ports': ['8000:8000'],
                    'environment': [
                        'ENVIRONMENT=production',
                        'DATABASE_URL=postgresql://api_user:secure_password@postgres:5432/nino_medical_ner',
                        'REDIS_URL=redis://redis:6379/0',
                        'JWT_SECRET_KEY=${JWT_SECRET_KEY}',
                        'STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}',
                        'EMAIL_PASSWORD=${EMAIL_PASSWORD}'
                    ],
                    'depends_on': ['postgres', 'redis'],
                    'volumes': [
                        './models:/app/models',
                        './logs:/app/logs'
                    ],
                    'restart': 'unless-stopped',
                    'deploy': {
                        'replicas': 2,
                        'resources': {
                            'limits': {
                                'cpus': '1.0',
                                'memory': '2G'
                            },
                            'reservations': {
                                'cpus': '0.5',
                                'memory': '1G'
                            }
                        }
                    }
                },
                'postgres': {
                    'image': 'postgres:15-alpine',
                    'environment': [
                        'POSTGRES_DB=nino_medical_ner',
                        'POSTGRES_USER=api_user',
                        'POSTGRES_PASSWORD=secure_password'
                    ],
                    'volumes': [
                        'postgres_data:/var/lib/postgresql/data',
                        './init.sql:/docker-entrypoint-initdb.d/init.sql'
                    ],
                    'ports': ['5432:5432'],
                    'restart': 'unless-stopped'
                },
                'redis': {
                    'image': 'redis:7-alpine',
                    'ports': ['6379:6379'],
                    'volumes': ['redis_data:/data'],
                    'restart': 'unless-stopped',
                    'command': 'redis-server --appendonly yes'
                },
                'nginx': {
                    'image': 'nginx:alpine',
                    'ports': ['80:80', '443:443'],
                    'volumes': [
                        './nginx.conf:/etc/nginx/nginx.conf',
                        './ssl:/etc/nginx/ssl'
                    ],
                    'depends_on': ['api'],
                    'restart': 'unless-stopped'
                },
                'monitoring': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile.monitoring'
                    },
                    'ports': ['8501:8501'],
                    'environment': [
                        'API_BASE_URL=http://api:8000'
                    ],
                    'depends_on': ['api'],
                    'restart': 'unless-stopped'
                },
                'prometheus': {
                    'image': 'prom/prometheus:latest',
                    'ports': ['9090:9090'],
                    'volumes': [
                        './prometheus.yml:/etc/prometheus/prometheus.yml'
                    ],
                    'restart': 'unless-stopped'
                },
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'ports': ['3000:3000'],
                    'environment': [
                        'GF_SECURITY_ADMIN_PASSWORD=admin123'
                    ],
                    'volumes': [
                        'grafana_data:/var/lib/grafana',
                        './grafana/dashboards:/etc/grafana/provisioning/dashboards',
                        './grafana/datasources:/etc/grafana/provisioning/datasources'
                    ],
                    'restart': 'unless-stopped'
                }
            },
            'volumes': {
                'postgres_data': {},
                'redis_data': {},
                'grafana_data': {}
            },
            'networks': {
                'default': {
                    'driver': 'bridge'
                }
            }
        }
        
        return yaml.dump(compose_config, default_flow_style=False)
    
    def generate_dockerfile(self) -> str:
        """Generate Dockerfile for the API"""
        
        dockerfile_content = """
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs models data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["gunicorn", "subscription_api_service:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
"""
        return dockerfile_content.strip()
    
    def generate_monitoring_dockerfile(self) -> str:
        """Generate Dockerfile for monitoring dashboard"""
        
        dockerfile_content = """
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements for monitoring
COPY monitoring_requirements.txt .
RUN pip install --no-cache-dir -r monitoring_requirements.txt

# Copy monitoring application
COPY operational_dashboard.py .
COPY monitoring_system.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8501

# Run Streamlit dashboard
CMD ["streamlit", "run", "operational_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
        return dockerfile_content.strip()
    
    def generate_nginx_config(self) -> str:
        """Generate Nginx configuration for load balancing"""
        
        nginx_config = """
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        least_conn;
        server api:8000 max_fails=3 fail_timeout=30s;
        # Add more API instances here for scaling
        # server api2:8000 max_fails=3 fail_timeout=30s;
        # server api3:8000 max_fails=3 fail_timeout=30s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # API endpoints
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://api_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Buffer settings
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # Authentication endpoints with stricter rate limiting
        location /auth/ {
            limit_req zone=auth_limit burst=10 nodelay;
            
            proxy_pass http://api_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://api_backend/health;
            access_log off;
        }

        # Monitoring dashboard
        location /monitoring/ {
            proxy_pass http://monitoring:8501/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Static files
        location /static/ {
            root /var/www;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
"""
        return nginx_config.strip()
    
    def generate_kubernetes_config(self) -> Dict:
        """Generate Kubernetes deployment configuration"""
        
        k8s_config = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'nino-medical-ner-api',
                'labels': {
                    'app': 'nino-medical-ner'
                }
            },
            'spec': {
                'replicas': 3,
                'selector': {
                    'matchLabels': {
                        'app': 'nino-medical-ner'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'nino-medical-ner'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'api',
                            'image': 'nino-medical-ner:latest',
                            'ports': [{
                                'containerPort': 8000
                            }],
                            'env': [
                                {'name': 'ENVIRONMENT', 'value': 'production'},
                                {'name': 'DATABASE_URL', 'valueFrom': {'secretKeyRef': {'name': 'api-secrets', 'key': 'database-url'}}},
                                {'name': 'REDIS_URL', 'valueFrom': {'secretKeyRef': {'name': 'api-secrets', 'key': 'redis-url'}}},
                                {'name': 'JWT_SECRET_KEY', 'valueFrom': {'secretKeyRef': {'name': 'api-secrets', 'key': 'jwt-secret'}}},
                                {'name': 'STRIPE_SECRET_KEY', 'valueFrom': {'secretKeyRef': {'name': 'api-secrets', 'key': 'stripe-secret'}}},
                            ],
                            'resources': {
                                'requests': {
                                    'cpu': '500m',
                                    'memory': '1Gi'
                                },
                                'limits': {
                                    'cpu': '1000m',
                                    'memory': '2Gi'
                                }
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': 8000
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': 8000
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }]
                    }
                }
            }
        }
        
        return k8s_config
    
    def generate_hpa_config(self) -> Dict:
        """Generate Horizontal Pod Autoscaler configuration"""
        
        hpa_config = {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': 'nino-medical-ner-hpa'
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': 'nino-medical-ner-api'
                },
                'minReplicas': 2,
                'maxReplicas': 20,
                'metrics': [
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'cpu',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': 70
                            }
                        }
                    },
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'memory',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': 80
                            }
                        }
                    }
                ],
                'behavior': {
                    'scaleUp': {
                        'stabilizationWindowSeconds': 300,
                        'policies': [{
                            'type': 'Percent',
                            'value': 100,
                            'periodSeconds': 15
                        }]
                    },
                    'scaleDown': {
                        'stabilizationWindowSeconds': 600,
                        'policies': [{
                            'type': 'Percent',
                            'value': 50,
                            'periodSeconds': 60
                        }]
                    }
                }
            }
        }
        
        return hpa_config
    
    def generate_prometheus_config(self) -> str:
        """Generate Prometheus configuration"""
        
        prometheus_config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'api-service'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'monitoring-dashboard'
    static_configs:
      - targets: ['monitoring:8501']
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']
"""
        return prometheus_config.strip()
    
    def generate_requirements_files(self) -> Dict[str, str]:
        """Generate requirements files for different components"""
        
        api_requirements = """
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pydantic==2.5.0
transformers==4.36.0
torch==2.1.1
spacy==3.7.2
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.24.4
sqlalchemy==2.0.23
asyncpg==0.29.0
redis==5.0.1
stripe==7.8.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
psutil==5.9.6
prometheus-client==0.19.0
python-dotenv==1.0.0
"""

        monitoring_requirements = """
streamlit==1.28.2
plotly==5.17.0
pandas==2.1.4
numpy==1.24.4
requests==2.31.0
psutil==5.9.6
sqlite3
"""

        return {
            'requirements.txt': api_requirements.strip(),
            'monitoring_requirements.txt': monitoring_requirements.strip()
        }
    
    def generate_deployment_scripts(self) -> Dict[str, str]:
        """Generate deployment scripts"""
        
        deploy_script = """#!/bin/bash
set -e

echo "🚀 Deploying Nino Medical AI API..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Build and start services
echo "📦 Building Docker images..."
docker-compose build

echo "🔄 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

# Run health checks
echo "🔍 Running health checks..."
curl -f http://localhost/health || exit 1

echo "✅ Deployment completed successfully!"
echo "🏥 API is available at: https://your-domain.com"
echo "📊 Monitoring dashboard: https://your-domain.com/monitoring"
echo "📈 Grafana: http://localhost:3000 (admin/admin123)"
"""

        backup_script = """#!/bin/bash
set -e

echo "💾 Starting backup process..."

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup database
echo "📂 Backing up database..."
docker-compose exec -T postgres pg_dump -U api_user nino_medical_ner > $BACKUP_DIR/database.sql

# Backup Redis data
echo "🔄 Backing up Redis data..."
docker-compose exec -T redis redis-cli BGSAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb $BACKUP_DIR/redis-dump.rdb

# Backup logs
echo "📝 Backing up logs..."
cp -r ./logs $BACKUP_DIR/

# Backup models
echo "🤖 Backing up models..."
cp -r ./models $BACKUP_DIR/

echo "✅ Backup completed: $BACKUP_DIR"
"""

        monitor_script = """#!/bin/bash

echo "👀 Monitoring system status..."

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Check API health
echo "🏥 Checking API health..."
curl -s http://localhost/health | jq .

# Check resource usage
echo "📊 Resource usage:"
docker stats --no-stream --format "table {{.Container}}\\t{{.CPUPerc}}\\t{{.MemUsage}}"

# Check logs for errors
echo "📝 Recent errors:"
docker-compose logs --tail=50 api | grep -i error || echo "No errors found"
"""

        return {
            'deploy.sh': deploy_script.strip(),
            'backup.sh': backup_script.strip(),
            'monitor.sh': monitor_script.strip()
        }
    
    def save_all_configs(self):
        """Save all configuration files"""
        
        configs = {
            'docker-compose.yml': self.generate_docker_compose(),
            'Dockerfile': self.generate_dockerfile(),
            'Dockerfile.monitoring': self.generate_monitoring_dockerfile(),
            'nginx.conf': self.generate_nginx_config(),
            'prometheus.yml': self.generate_prometheus_config(),
            'k8s-deployment.yaml': yaml.dump(self.generate_kubernetes_config()),
            'k8s-hpa.yaml': yaml.dump(self.generate_hpa_config())
        }
        
        # Save requirement files
        requirements = self.generate_requirements_files()
        configs.update(requirements)
        
        # Save deployment scripts
        scripts = self.generate_deployment_scripts()
        configs.update(scripts)
        
        # Create directories
        (self.project_root / "deployment").mkdir(exist_ok=True)
        (self.project_root / "k8s").mkdir(exist_ok=True)
        (self.project_root / "scripts").mkdir(exist_ok=True)
        
        # Save files
        for filename, content in configs.items():
            if filename.startswith('k8s-'):
                file_path = self.project_root / "k8s" / filename
            elif filename.endswith('.sh'):
                file_path = self.project_root / "scripts" / filename
                # Make scripts executable
                file_path.write_text(content)
                os.chmod(file_path, 0o755)
                continue
            else:
                file_path = self.project_root / filename
                
            file_path.write_text(content)
            
        print("✅ All deployment configurations generated successfully!")
        print(f"📁 Files saved in: {self.project_root}")
        
        # Generate .env template
        env_template = """
# Environment Configuration
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://api_user:secure_password@postgres:5432/nino_medical_ner

# Redis
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
EMAIL_PASSWORD=your_gmail_app_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Monitoring
MONITORING_EMAIL=nino58150@gmail.com
SLACK_WEBHOOK=https://hooks.slack.com/services/your/webhook/url

# SSL (for production)
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
"""
        
        (self.project_root / ".env.template").write_text(env_template.strip())
        
        print("📝 Don't forget to:")
        print("1. Copy .env.template to .env and update with your values")
        print("2. Set up SSL certificates in ./ssl/ directory")
        print("3. Update domain name in nginx.conf")
        print("4. Configure Stripe webhooks")
        print("5. Set up monitoring alerts")

if __name__ == "__main__":
    # Generate all deployment configurations
    deployment_manager = DeploymentManager()
    deployment_manager.save_all_configs()
    
    print("\n🎉 Deployment configuration complete!")
    print("📚 Quick start:")
    print("1. cp .env.template .env && nano .env")
    print("2. ./scripts/deploy.sh")
    print("3. Visit https://your-domain.com")
