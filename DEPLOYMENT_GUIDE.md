# 🚀 Deployment Guide - Italian Medical NER

*Professional deployment options for Italian Medical AI platform*

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Docker](#production-docker)
5. [Cloud Deployment](#cloud-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

---

## 🏃 Quick Start

### Using the Deployment Script (Windows)

```bash
# Run the interactive deployment script
./deploy.bat

# Choose option 1 for local development
# Choose option 2 for Docker development
# Choose option 3 for production deployment
```

### Manual Quick Start

```bash
# 1. Clone and navigate
git clone [your-repo]
cd italian_medical_ner

# 2. Install dependencies
pip install -r requirements.txt -r web_demo_requirements.txt

# 3. Run Streamlit demo
streamlit run web_demo_app.py
```

---

## 🏠 Local Development

### Prerequisites

- **Python 3.11.7** (recommended) or 3.8+
- **4GB+ RAM**
- **2GB disk space**
- **Git** (for version control)

### Installation Steps

1. **Setup Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r web_demo_requirements.txt
   pip install -r api_requirements.txt
   ```

3. **Verify Installation**
   ```bash
   python -c "import transformers; print('✅ Setup complete')"
   ```

### Running Services

#### Streamlit Web Demo
```bash
streamlit run web_demo_app.py --server.port=8501
# Access: http://localhost:8501
```

#### FastAPI Service
```bash
python api_service.py
# Access: http://localhost:8000
# Docs: http://localhost:8000/docs
```

#### GUI Application
```bash
python ner_gui_app.py
# Or use: run_medical_ner.bat (Windows)
```

---

## 🐳 Docker Deployment

### Development Docker

Perfect for local development with containerization benefits.

#### Quick Start
```bash
# Start services
docker-compose up --build

# Background mode
docker-compose up --build -d

# View logs
docker-compose logs -f
```

#### Services Available
- **Streamlit Demo**: http://localhost:8501
- **FastAPI Service**: http://localhost:8000

#### Docker Commands
```bash
# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache

# View container status
docker-compose ps

# Access container shell
docker-compose exec nino-medical-web bash
```

### Custom Docker Build

```bash
# Build custom image
docker build -t italian-medical-ner .

# Run with custom settings
docker run -p 8501:8501 \
  -e ENVIRONMENT=development \
  italian-medical-ner

# Run API service
docker run -p 8000:8000 \
  italian-medical-ner \
  uvicorn api_service:app --host 0.0.0.0 --port 8000
```

---

## 🌐 Production Docker

Full production setup with monitoring, load balancing, and security.

### Production Features

- **Load Balancing** with Traefik
- **SSL/HTTPS** automatic certificates
- **Monitoring** with Prometheus & Grafana
- **Caching** with Redis
- **Database** with PostgreSQL
- **Health Checks** and auto-restart
- **Resource Limits** and scaling

### Quick Production Start

```bash
# Deploy production stack
docker-compose -f docker-compose.production.yml up --build -d

# Monitor deployment
docker-compose -f docker-compose.production.yml logs -f
```

### Production Services

| Service | URL | Purpose |
|---------|-----|---------|
| Web App | http://localhost | Main application |
| API | http://localhost:8000 | API endpoints |
| Traefik | http://localhost:8080 | Load balancer dashboard |
| Grafana | http://localhost:3000 | Monitoring dashboard |
| Prometheus | http://localhost:9090 | Metrics collection |

### Production Configuration

#### 1. Update Domain Names
Edit `docker-compose.production.yml`:
```yaml
labels:
  - "traefik.http.routers.nino-web.rule=Host(`your-domain.com`)"
  - "traefik.http.routers.nino-api.rule=Host(`api.your-domain.com`)"
```

#### 2. Change Default Passwords
```yaml
# PostgreSQL
- POSTGRES_PASSWORD=your_secure_password

# Grafana  
- GF_SECURITY_ADMIN_PASSWORD=your_grafana_password
```

#### 3. Configure SSL Certificates
```yaml
# Traefik ACME settings
- "--certificatesresolvers.myresolver.acme.email=your-email@domain.com"
```

#### 4. Set Resource Limits
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 2G
      cpus: '1.0'
```

---

## ☁️ Cloud Deployment

### Streamlit Cloud (FREE)

**Best for**: Demos, prototypes, small-scale usage

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Streamlit Cloud"
   git push origin main
   ```

2. **Deploy**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect GitHub repository
   - Set main file: `web_demo_app.py`
   - Deploy automatically!

3. **Configuration**
   Create `.streamlit/config.toml`:
   ```toml
   [general]
   dataFrameSerialization = "legacy"
   
   [server]
   headless = true
   enableCORS = false
   enableXsrfProtection = true
   ```

### AWS Deployment

**Best for**: Scalable production deployments

#### AWS Elastic Beanstalk

1. **Install AWS CLI**
   ```bash
   pip install awsebcli
   aws configure
   ```

2. **Initialize Application**
   ```bash
   eb init italian-medical-ner
   eb create production
   ```

3. **Deploy Updates**
   ```bash
   eb deploy
   ```

#### AWS ECS (Elastic Container Service)

1. **Create Task Definition**
   ```json
   {
     "family": "italian-medical-ner",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "containerDefinitions": [
       {
         "name": "web-app",
         "image": "your-account.dkr.ecr.region.amazonaws.com/italian-medical-ner",
         "portMappings": [
           {
             "containerPort": 8501,
             "protocol": "tcp"
           }
         ]
       }
     ]
   }
   ```

2. **Deploy with CDK/CloudFormation**
   ```bash
   aws ecs create-service \
     --cluster your-cluster \
     --service-name italian-medical-ner \
     --task-definition italian-medical-ner:1 \
     --desired-count 2
   ```

### Azure Deployment

**Best for**: Enterprise integration with Microsoft ecosystem

#### Azure Container Instances

1. **Install Azure CLI**
   ```bash
   # Download from: https://aka.ms/installazurecliwindows
   az login
   ```

2. **Create Resource Group**
   ```bash
   az group create \
     --name nino-medical-rg \
     --location eastus
   ```

3. **Deploy Container**
   ```bash
   az container create \
     --resource-group nino-medical-rg \
     --name italian-medical-ner \
     --image italian-medical-ner:latest \
     --cpu 2 --memory 4 \
     --ports 8501 8000 \
     --dns-name-label nino-medical-ai
   ```

#### Azure App Service

1. **Create Web App**
   ```bash
   az webapp create \
     --resource-group nino-medical-rg \
     --plan your-app-plan \
     --name italian-medical-ner \
     --deployment-container-image-name italian-medical-ner:latest
   ```

### Google Cloud Platform

**Best for**: AI/ML workloads, serverless architecture

#### Cloud Run

1. **Install gcloud CLI**
   ```bash
   # Download from: https://cloud.google.com/sdk/docs/install
   gcloud auth login
   gcloud config set project your-project-id
   ```

2. **Enable APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

3. **Deploy**
   ```bash
   gcloud run deploy italian-medical-ner \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

#### Cloud Build Pipeline

Create `cloudbuild.yaml`:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/italian-medical-ner', '.']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/italian-medical-ner']
  
  - name: 'gcr.io/cloud-builders/gcloud'
    args: 
      - 'run'
      - 'deploy' 
      - 'italian-medical-ner'
      - '--image'
      - 'gcr.io/$PROJECT_ID/italian-medical-ner'
      - '--platform'
      - 'managed'
      - '--region'
      - 'us-central1'
      - '--allow-unauthenticated'
```

### DigitalOcean App Platform

**Best for**: Simple, cost-effective deployment

1. **Create App Spec**
   ```yaml
   name: italian-medical-ner
   services:
   - name: web
     source_dir: /
     github:
       repo: your-username/italian-medical-ner
       branch: main
     run_command: streamlit run web_demo_app.py --server.port=8080
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     routes:
     - path: /
   ```

2. **Deploy via CLI**
   ```bash
   doctl apps create --spec app.yaml
   ```

---

## 📊 Monitoring & Maintenance

### Health Checks

#### Built-in Health Endpoints

```bash
# Streamlit health check
curl http://localhost:8501/_stcore/health

# FastAPI health check  
curl http://localhost:8000/health

# Docker health check
docker ps --format "table {{.Names}}\t{{.Status}}"
```

#### Custom Health Monitoring

Create `health_check.py`:
```python
import requests
import time
import logging

def check_service_health():
    services = {
        'streamlit': 'http://localhost:8501/_stcore/health',
        'api': 'http://localhost:8000/health'
    }
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
            else:
                print(f"⚠️ {name}: Unhealthy (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Failed ({str(e)})")

if __name__ == "__main__":
    check_service_health()
```

### Monitoring with Prometheus & Grafana

#### Prometheus Configuration

Create `monitoring/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'italian-medical-ner'
    static_configs:
      - targets: ['nino-medical-web:8501', 'nino-medical-api:8000']
  
  - job_name: 'docker'
    static_configs:
      - targets: ['host.docker.internal:9323']
```

#### Grafana Dashboards

Key metrics to monitor:
- **Request Rate**: Requests per second
- **Response Time**: Average response latency  
- **Error Rate**: 4xx/5xx error percentage
- **Resource Usage**: CPU, Memory, Disk
- **Model Performance**: Prediction accuracy, processing time

### Log Management

#### Centralized Logging

```bash
# View all container logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f nino-medical-web

# Save logs to file
docker-compose logs > deployment.log
```

#### Log Rotation

Create `logging.conf`:
```ini
[loggers]
keys=root

[handlers]
keys=rotatingFileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=rotatingFileHandler

[handler_rotatingFileHandler]
class=handlers.RotatingFileHandler
level=INFO
formatter=simpleFormatter
args=('logs/app.log', 'a', 10485760, 5)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Backup & Recovery

#### Data Backup

```bash
# Backup PostgreSQL data
docker-compose exec postgres pg_dump -U nino_user nino_medical_analytics > backup.sql

# Backup application data
docker run --rm -v italian_medical_ner_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Backup configuration
tar czf config_backup.tar.gz docker-compose*.yml monitoring/ ssl/
```

#### Recovery Procedures

```bash
# Restore PostgreSQL
docker-compose exec postgres psql -U nino_user nino_medical_analytics < backup.sql

# Restore data volume
docker run --rm -v italian_medical_ner_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

---

## 🔒 Security Considerations

### Production Security Checklist

#### Container Security

- [ ] **Non-root user**: All containers run as non-root
- [ ] **Resource limits**: CPU/Memory limits configured
- [ ] **Read-only filesystem**: Where possible
- [ ] **No secrets in images**: Use environment variables
- [ ] **Regular updates**: Keep base images updated

#### Network Security

- [ ] **HTTPS only**: Force SSL/TLS encryption
- [ ] **Rate limiting**: Prevent abuse
- [ ] **CORS configuration**: Restrict origins
- [ ] **API authentication**: Protect API endpoints
- [ ] **Firewall rules**: Limit exposed ports

#### Application Security

- [ ] **Input validation**: Sanitize all inputs
- [ ] **CSRF protection**: Enable XSRF protection
- [ ] **Secure headers**: Set security headers
- [ ] **Error handling**: Don't expose sensitive info
- [ ] **Logging**: Log security events

### Environment Variables

Create `.env` file for sensitive configuration:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password
POSTGRES_USER=nino_user
POSTGRES_DB=nino_medical_analytics

# API Security  
API_SECRET_KEY=your_jwt_secret_key
API_RATE_LIMIT=100

# SSL/TLS
SSL_CERT_PATH=/app/ssl/cert.pem
SSL_KEY_PATH=/app/ssl/key.pem

# Monitoring
GRAFANA_ADMIN_PASSWORD=your_grafana_password

# External Services
SENTRY_DSN=your_sentry_dsn
ANALYTICS_TOKEN=your_analytics_token
```

### SSL Certificate Setup

#### Let's Encrypt (Automatic)

Traefik handles this automatically in production configuration.

#### Manual Certificate

```bash
# Generate self-signed certificate (development only)
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Update docker-compose to mount certificates
volumes:
  - ./ssl:/app/ssl
```

---

## 🔧 Troubleshooting

### Common Issues

#### Docker Issues

**Problem**: `docker-compose up` fails
```bash
# Solution: Check Docker Desktop is running
docker info

# Clean and rebuild
docker-compose down --volumes
docker-compose up --build --force-recreate
```

**Problem**: Port already in use
```bash
# Find process using port
netstat -ano | find ":8501"

# Kill process (Windows)
taskkill /PID <PID> /F

# Kill process (macOS/Linux)  
kill -9 <PID>
```

#### Memory Issues

**Problem**: Out of memory errors
```bash
# Increase Docker memory limits
# Docker Desktop > Settings > Resources > Memory > 8GB

# Or reduce batch size in code
BATCH_SIZE = 8  # Instead of 32
```

#### Model Loading Issues

**Problem**: Model files not found
```bash
# Check model files exist
ls -la model.safetensors pytorch_model.bin

# Re-download if using Git LFS
git lfs pull

# Verify file integrity
python -c "
import torch
model = torch.load('pytorch_model.bin', map_location='cpu')
print('✅ Model loads successfully')
"
```

#### Performance Issues

**Problem**: Slow response times
```bash
# Check system resources
docker stats

# Enable GPU if available
# Add to docker-compose.yml:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### Debug Mode

Enable debug logging:

```python
# Add to app startup
import logging
logging.basicConfig(level=logging.DEBUG)

# Streamlit debug
streamlit run web_demo_app.py --logger.level=debug

# FastAPI debug  
uvicorn api_service:app --log-level debug
```

### Support Resources

- **Documentation**: This guide and USER_GUIDE.md
- **Live Demo**: https://italian-medical-ai-4opjehvsybqncwjnaaq8a4.streamlit.app/
- **GitHub Issues**: Report bugs and request features
- **Email Support**: medical-ner@yourdomain.com

---

## 📈 Performance Optimization

### Production Optimizations

#### Gunicorn Configuration

```bash
# Production WSGI server
gunicorn api_service:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

#### Nginx Reverse Proxy

Create `nginx.conf`:
```nginx
upstream italian_medical_ner {
    server web1:8501;
    server web2:8501;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://italian_medical_ner;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Caching Strategy

```python
# Redis caching for API responses
import redis
import json
import hashlib

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache_prediction(text, result, ttl=3600):
    """Cache prediction result"""
    cache_key = hashlib.md5(text.encode()).hexdigest()
    redis_client.setex(cache_key, ttl, json.dumps(result))

def get_cached_prediction(text):
    """Retrieve cached prediction"""
    cache_key = hashlib.md5(text.encode()).hexdigest()
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None
```

---

*© 2025 Nino Medical AI. All Rights Reserved.*

Need help? Contact us at medical-ner@yourdomain.com or visit our [live demo](https://italian-medical-ai-4opjehvsybqncwjnaaq8a4.streamlit.app/).
