# 📖 Italian Medical NER - Complete User Guide

*Professional Medical Named Entity Recognition for Italian Healthcare*

## 🎯 Table of Contents

1. [Getting Started](#getting-started)
2. [Web Demo Usage](#web-demo-usage)
3. [Local Installation](#local-installation)
4. [API Usage](#api-usage)
5. [Docker Deployment](#docker-deployment)
6. [GUI Application](#gui-application)
7. [Python Integration](#python-integration)
8. [Advanced Features](#advanced-features)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## 🚀 Getting Started

### What is Italian Medical NER?

Our system extracts medical entities from Italian healthcare text with **83.3% recall** and **85.2% precision**. It identifies:

- 🩺 **PROBLEM**: Diseases, symptoms, conditions
- 🧪 **TEST**: Diagnostic procedures, lab tests  
- 💊 **TREATMENT**: Medications, therapies, interventions

### Choose Your Method

| Method | Best For | Setup Time | Features |
|--------|----------|------------|----------|
| [Web Demo](#web-demo-usage) | Quick testing | 0 minutes | Live demo, no installation |
| [Local GUI](#gui-application) | Desktop use | 5 minutes | Offline processing |
| [API Service](#api-usage) | Integration | 10 minutes | Programmatic access |
| [Docker](#docker-deployment) | Production | 15 minutes | Scalable deployment |

---

## 🌐 Web Demo Usage

### Access the Demo
Visit: **https://italian-medical-ai-4opjehvsybqncwjnaaq8a4.streamlit.app/**

### Demo Features
- ✅ **5 free requests daily** (no registration)
- ✅ **10 requests daily** (with email registration)
- ✅ **300-500 character limit** for demo
- ✅ **Real-time entity visualization**
- ✅ **Confidence scores**
- ✅ **Processing time metrics**

### Example Texts to Try

#### 1. Basic Symptoms
```
Il paziente presenta febbre alta e mal di testa.
```
*Expected: febbre alta (SYMPTOM), mal di testa (SYMPTOM)*

#### 2. Medication Prescription
```
Prescritto paracetamolo 500mg due volte al giorno per il dolore.
```
*Expected: paracetamolo (TREATMENT), 500mg (DOSAGE), dolore (SYMPTOM)*

#### 3. Diagnostic Procedure
```
Radiografia del torace normale, nessuna anomalia rilevata.
```
*Expected: Radiografia (TEST), torace (ANATOMY)*

#### 4. Complex Medical Text
```
Il paziente riferisce nausea, vomito e dolore addominale acuto. 
Eseguita ecografia addominale che mostra lieve dilatazione.
Iniziata terapia con antibiotico.
```

### Understanding Results

The demo shows entities with color-coded labels:
- 🔴 **PROBLEM** (red): Symptoms, diseases
- 🔵 **TEST** (blue): Diagnostic procedures
- 🟢 **TREATMENT** (green): Medications, therapies

---

## 💻 Local Installation

### Prerequisites
- Python 3.8+ (recommended: 3.11.7)
- 4GB+ RAM
- 2GB disk space

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone [your-repo-url]
cd italian_medical_ner

# 2. Create virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test installation
python -c "import transformers; print('✅ Installation successful')"
```

### Quick Test

```bash
# Run the web demo locally
streamlit run web_demo_app.py

# Open browser to: http://localhost:8501
```

---

## 🔌 API Usage

### Starting the API Server

```bash
# Method 1: Direct Python
python api_service.py

# Method 2: Using batch file (Windows)
start_api_server.bat

# Server starts at: http://localhost:8000
```

### API Endpoints

#### POST /predict
Analyze Italian medical text

**Request:**
```json
{
  "text": "Il paziente ha la febbre e tosse persistente.",
  "confidence_threshold": 0.7
}
```

**Response:**
```json
{
  "entities": [
    {
      "text": "febbre",
      "label": "SYMPTOM",
      "confidence": 0.95,
      "start": 20,
      "end": 26,
      "source": "model"
    },
    {
      "text": "tosse",
      "label": "SYMPTOM", 
      "confidence": 0.89,
      "start": 29,
      "end": 34,
      "source": "pattern"
    }
  ],
  "processing_time": 0.156,
  "total_entities": 2
}
```

### Code Examples

#### Python Requests
```python
import requests

# Single prediction
response = requests.post(
    'http://localhost:8000/predict',
    json={'text': 'Il paziente ha la febbre.'}
)
result = response.json()
print(f"Found {result['total_entities']} entities")
```

#### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: 'Il paziente ha la febbre.'
  })
});
const result = await response.json();
console.log(`Found ${result.total_entities} entities`);
```

#### cURL
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "Il paziente ha la febbre."}'
```

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Option 1: Docker Compose (Recommended)
docker-compose up --build

# Option 2: Windows Batch Script
docker-launch.bat

# Access at: http://localhost:8501
```

### Manual Docker Build

```bash
# Build image
docker build -t italian-medical-ner .

# Run container
docker run -p 8501:8501 italian-medical-ner

# With volume mounting (for model updates)
docker run -p 8501:8501 -v $(pwd):/app italian-medical-ner
```

### Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  medical-ner:
    build: .
    ports:
      - "80:8501"
    environment:
      - ENVIRONMENT=production
      - MAX_REQUESTS_PER_HOUR=1000
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

---

## 🖥️ GUI Application

### Launch Methods

```bash
# Method 1: Python script
python ner_gui_app.py

# Method 2: Batch file (Windows)
run_medical_ner.bat

# Method 3: Built executable (if available)
medical_ner.exe
```

### GUI Features

- 📝 **Text Input**: Large text area for medical documents
- ⚙️ **Confidence Threshold**: Adjustable slider (0.1-1.0)
- 🎨 **Entity Highlighting**: Color-coded entity visualization
- 💾 **Export Options**: Save results as JSON, CSV, or TXT
- 📊 **Statistics Panel**: Real-time processing metrics
- 🔄 **Batch Processing**: Multiple files at once

### Keyboard Shortcuts

- `Ctrl+O`: Open file
- `Ctrl+S`: Save results
- `Ctrl+R`: Run analysis
- `Ctrl+C`: Clear text
- `F5`: Refresh model

---

## 🐍 Python Integration

### Basic Usage

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

# Load model
model_name = "./italian_medical_ner"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

def analyze_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=2)
    
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    entities = []
    
    for token, pred_id in zip(tokens, predictions[0]):
        if pred_id != 0:  # Skip O-label
            label = model.config.id2label[pred_id.item()]
            entities.append({
                'token': token,
                'label': label
            })
    
    return entities

# Example usage
text = "Il paziente ha la febbre e mal di testa."
entities = analyze_text(text)
for entity in entities:
    print(f"{entity['token']} -> {entity['label']}")
```

### Enhanced Pipeline

```python
from improved_inference import ImprovedItalianMedicalNER

# Initialize enhanced model
ner = ImprovedItalianMedicalNER(
    model_path="./",
    confidence_threshold=0.7,
    enable_patterns=True,
    enable_dictionary=True
)

# Analyze text
text = "Prescritto ibuprofene per il mal di testa cronico."
result = ner.predict(text)

# Process results
print(f"Total entities: {result['total_entities']}")
print(f"Processing time: {result['processing_time']:.3f}s")

for entity in result['entities']:
    source_icon = {"model": "🤖", "pattern": "📝", "dictionary": "📚"}
    icon = source_icon.get(entity['source'], "❓")
    print(f"{icon} {entity['text']} ({entity['label']}) [{entity['confidence']:.3f}]")
```

### Batch Processing

```python
def process_multiple_texts(texts, batch_size=32):
    """Process multiple texts efficiently"""
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        
        # Tokenize batch
        inputs = tokenizer(
            batch, 
            return_tensors="pt", 
            padding=True, 
            truncation=True,
            max_length=512
        )
        
        # Predict batch
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=2)
        
        # Process each text in batch
        for j, text in enumerate(batch):
            entities = extract_entities(text, predictions[j], inputs['input_ids'][j])
            results.append({
                'text': text,
                'entities': entities
            })
    
    return results

# Example usage
texts = [
    "Il paziente ha la febbre.",
    "Prescritto paracetamolo 500mg.",
    "Radiografia del torace normale."
]

batch_results = process_multiple_texts(texts)
for i, result in enumerate(batch_results):
    print(f"Text {i+1}: {len(result['entities'])} entities found")
```

---

## 🚀 Advanced Features

### Custom Entity Types

You can extend the system to recognize custom medical entities:

```python
# Add custom patterns
custom_patterns = {
    'HOSPITAL': [r'\b(ospedale|clinica|pronto soccorso)\b'],
    'SPECIALIST': [r'\b(cardiologo|neurologo|oncologo)\b'],
    'URGENCY': [r'\b(urgente|emergenza|critico)\b']
}

# Initialize with custom patterns
ner = ImprovedItalianMedicalNER(
    custom_patterns=custom_patterns,
    confidence_threshold=0.6
)
```

### Confidence Filtering

```python
# Filter results by confidence
def filter_by_confidence(entities, min_confidence=0.8):
    return [e for e in entities if e['confidence'] >= min_confidence]

# Get only high-confidence entities
high_conf_entities = filter_by_confidence(result['entities'], 0.85)
```

### Entity Validation

```python
def validate_entities(entities, medical_dictionary):
    """Validate entities against medical terminology"""
    validated = []
    
    for entity in entities:
        if entity['text'].lower() in medical_dictionary:
            entity['validated'] = True
            entity['category'] = medical_dictionary[entity['text'].lower()]
        else:
            entity['validated'] = False
            entity['needs_review'] = True
        
        validated.append(entity)
    
    return validated
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Installation Problems

**Issue**: `ModuleNotFoundError: No module named 'transformers'`
```bash
# Solution:
pip install --upgrade pip
pip install transformers torch
```

**Issue**: CUDA out of memory
```bash
# Solution: Use CPU inference
export CUDA_VISIBLE_DEVICES=""
```

#### 2. Model Loading Issues

**Issue**: Model files not found
```bash
# Check if model files exist
ls -la model.safetensors pytorch_model.bin

# Re-download if missing
git lfs pull
```

#### 3. Performance Issues

**Issue**: Slow processing
```python
# Solution: Reduce max_length
inputs = tokenizer(text, max_length=256, truncation=True)

# Or use batch processing
process_multiple_texts(texts, batch_size=16)
```

#### 4. Memory Issues

**Issue**: Out of memory errors
```python
# Solution: Clear cache regularly
import torch
torch.cuda.empty_cache()

# Or reduce batch size
batch_size = 8  # Instead of 32
```

### Performance Optimization

#### GPU Acceleration
```python
# Enable GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

print(f"Using device: {device}")
```

#### Memory Management
```python
# For large texts, process in chunks
def process_large_text(text, chunk_size=1000):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    all_entities = []
    
    for chunk in chunks:
        entities = ner.predict(chunk)['entities']
        all_entities.extend(entities)
    
    return all_entities
```

---

## ❓ FAQ

### General Questions

**Q: What languages does the system support?**
A: Currently Italian only. The model is specifically trained and optimized for Italian medical text.

**Q: Is this system suitable for production use?**
A: Yes, but ensure compliance with local healthcare regulations. Not intended for direct clinical decision-making.

**Q: Can I use this for non-medical Italian text?**
A: The system is optimized for medical text and may not perform well on general Italian text.

### Technical Questions

**Q: What's the maximum text length?**
A: The model supports up to 512 tokens (~400-500 words). Longer texts are automatically truncated.

**Q: How accurate is the system?**
A: Current performance: 85.2% precision, 83.3% recall, 84.2% F1-score on our test dataset.

**Q: Can I retrain the model with my own data?**
A: Yes, see the training scripts in the repository. Ensure you have appropriate data licenses.

**Q: Is there rate limiting on the API?**
A: The demo has daily limits. For production use, contact us for enterprise licensing.

### Commercial Questions

**Q: Can I use this commercially?**
A: See the license file. For commercial use, contact medical-ner@yourdomain.com

**Q: Do you offer support?**
A: Community support via GitHub issues. Enterprise support available with commercial licenses.

**Q: Can you customize the system for my specific needs?**
A: Yes, we offer custom development services. Contact us for consultation.

---

## 📞 Support & Contact

- **📧 Email**: medical-ner@yourdomain.com
- **💼 LinkedIn**: [Your Profile]
- **🐛 Issues**: GitHub Issues
- **📖 Documentation**: This guide
- **🌐 Live Demo**: https://italian-medical-ai-4opjehvsybqncwjnaaq8a4.streamlit.app/

**Response Time**: < 24 hours for technical issues, < 4 hours for commercial inquiries.

---

*© 2025 Nino Medical AI. All Rights Reserved.*
