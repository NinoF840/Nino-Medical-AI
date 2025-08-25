# 🚀 Guida Completa al Deployment - Italian Medical NER

## 📋 Opzioni di Deployment Disponibili

### 1. **Streamlit Cloud** (Raccomandato) ⭐

#### Vantaggi:
- ✅ Gratuito per progetti pubblici
- ✅ Integrazione diretta con GitHub
- ✅ Auto-deployment su push
- ✅ Dominio personalizzato disponibile
- ✅ SSL automatico

#### Setup:
1. **Prepara Repository GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Streamlit Cloud deployment"
   git branch -M main
   git remote add origin https://github.com/NinoF840/italian-medical-ner.git
   git push -u origin main
   ```

2. **Vai su Streamlit Cloud**:
   - Visita: https://share.streamlit.io/
   - Login con GitHub
   - Clicca "New app"
   - Seleziona repository: `NinoF840/italian-medical-ner`
   - Main file path: `web_demo_app.py`
   - Deploy!

3. **URL Demo**: `https://ninof840-italian-medical-ner-web-demo-app-xyz123.streamlit.app/`

---

### 2. **Hugging Face Spaces** 🤗

#### Vantaggi:
- ✅ Gratuito con CPU
- ✅ Community ML-focused
- ✅ Facile condivisione
- ✅ GPU upgrade disponibile

#### Setup:
1. **Crea Space**:
   - Vai su: https://huggingface.co/new-space
   - Nome: `italian-medical-ner`
   - SDK: Streamlit
   - Pubblico

2. **Upload Files**:
   - `web_demo_app.py` (main app)
   - `requirements.txt`
   - `README_HF.md` (rinomina in README.md)
   - `.streamlit/config.toml`
   - Files del modello (se necessari)

3. **URL Demo**: `https://huggingface.co/spaces/NinoF840/italian-medical-ner`

---

### 3. **Render** 🔄

#### Setup:
1. Connetti GitHub a Render
2. Crea Web Service
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `streamlit run web_demo_app.py --server.port=$PORT --server.address=0.0.0.0`

---

### 4. **Railway** 🚆

#### Setup:
1. Aggiungi `Procfile`:
   ```
   web: streamlit run web_demo_app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Deploy da GitHub

---

## 📁 File Necessari per Deployment

### File Obbligatori:
- ✅ `web_demo_app.py` - App principale
- ✅ `requirements.txt` - Dipendenze
- ✅ `.streamlit/config.toml` - Configurazione Streamlit
- ✅ `README.md` - Documentazione

### File del Modello:
- `model.safetensors` / `pytorch_model.bin`
- `tokenizer_config.json`
- `vocab.txt`
- `config.json`

### File Opzionali ma Raccomandati:
- `.gitignore` - File da ignorare
- `LICENSE` - Licenza del progetto
- `app.py` - Entry point alternativo
- `Dockerfile` - Per deployment containerizzato

---

## ⚙️ Ottimizzazioni per Production

### 1. **Performance**:
```python
# Nel web_demo_app.py
@st.cache_resource
def load_model():
    # Carica modello una sola volta
    pass

@st.cache_data
def process_text(text):
    # Cache risultati elaborazione
    pass
```

### 2. **Memory Management**:
```python
# Limita dimensione cache
st.set_page_config(
    page_title="Italian Medical NER",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### 3. **Security**:
- Non includere API keys nel codice
- Usa `st.secrets` per configurazioni sensibili
- Valida input utente

---

## 🔧 Troubleshooting Comuni

### Problema: "Module not found"
**Soluzione**: Verifica che tutte le dipendenze siano in `requirements.txt`

### Problema: "Memory limit exceeded"
**Soluzione**: 
- Ottimizza caricamento modello
- Usa modelli più piccoli per demo
- Implementa lazy loading

### Problema: "App takes too long to load"
**Soluzione**:
- Aggiungi loading spinners
- Implementa caching
- Usa modelli pre-caricati

---

## 📊 Monitoraggio Post-Deployment

### Metriche da Monitorare:
- ⏱️ **Tempo di risposta**
- 👥 **Utenti attivi**
- 🐛 **Rate di errori**
- 💾 **Utilizzo memoria**
- 🔄 **Uptime**

### Tools Raccomandati:
- **Streamlit Analytics** - Metriche built-in
- **Google Analytics** - Traffico web
- **Sentry** - Error tracking
- **UptimeRobot** - Monitoring uptime

---

## 🚀 Deploy Commands Ready-to-Use

### Per GitHub:
```bash
# Setup iniziale
git init
git add .
git commit -m "🚀 Initial deployment setup"
git branch -M main
git remote add origin https://github.com/NinoF840/italian-medical-ner.git
git push -u origin main

# Updates futuri
git add .
git commit -m "📝 Update: [describe changes]"
git push
```

### Per Streamlit Cloud:
1. Vai su https://share.streamlit.io/
2. New app → GitHub → `NinoF840/italian-medical-ner`
3. Main file: `web_demo_app.py`
4. Deploy!

---

## 📞 Supporto e Contatti

**Nino** - Developer
- 📧 Email: nino58150@gmail.com
- 📱 Tel: 3936789529
- 🐙 GitHub: [@NinoF840](https://github.com/NinoF840)

---

## ✅ Checklist Pre-Deploy

- [ ] Repository GitHub creato e sincronizzato
- [ ] `requirements.txt` aggiornato
- [ ] `README.md` completo e professionale
- [ ] `.streamlit/config.toml` configurato
- [ ] App testata localmente
- [ ] File del modello inclusi (se necessari)
- [ ] `.gitignore` configurato
- [ ] Secrets/API keys rimossi dal codice
- [ ] Performance ottimizzate con caching

**🎉 Sei pronto per il deployment!**
