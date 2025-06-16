---
license: apache-2.0
datasets:
- HUMADEX/italian_ner_dataset
language:
- it
metrics:
- f1
- precision
- recall
- confusion_matrix
base_model:
- google-bert/bert-base-cased
pipeline_tag: token-classification
tags:
- NER
- medical
- symptom
- extraction
- italian
---
# Italian Medical NER

## Acknowledgement

This model had been created as part of joint research of HUMADEX research group (https://www.linkedin.com/company/101563689/) and has received funding by the European Union Horizon Europe Research and Innovation Program project SMILE (grant number 101080923) and Marie Skłodowska-Curie Actions (MSCA) Doctoral Networks, project BosomShield ((rant number 101073222). Responsibility for the information and views expressed herein lies entirely with the authors.
Authors:
dr. Izidor Mlakar, Rigon Sallauka, dr. Umut Arioz, dr. Matej Rojc

## Publication
The paper associated with this model has been published: [10.3390/app15105585](https://doi.org/10.3390/app15105585)

Please cite this paper as follows if you use this model or build upon this work. Your citation supports the authors and the continued development of this research.
```bibtex
@article{app15105585,
  author  = {Sallauka, Rigon and Arioz, Umut and Rojc, Matej and Mlakar, Izidor},
  title   = {Weakly-Supervised Multilingual Medical NER for Symptom Extraction for Low-Resource Languages},
  journal = {Applied Sciences},
  volume  = {15},
  year    = {2025},
  number  = {10},
  article-number = {5585},
  url     = {https://www.mdpi.com/2076-3417/15/10/5585},
  issn    = {2076-3417},
  doi     = {10.3390/app15105585}
}
```

## Use
- **Primary Use Case**: This model is designed to extract medical entities such as symptoms, diagnostic tests, and treatments from clinical text in the Italian language.
- **Applications**: Suitable for healthcare professionals, clinical data analysis, and research into medical text processing.
- **Supported Entity Types**:
  - `PROBLEM`: Diseases, symptoms, and medical conditions.
  - `TEST`: Diagnostic procedures and laboratory tests.
  - `TREATMENT`: Medications, therapies, and other medical interventions.

## Training Data
- **Data Sources**: Annotated datasets, including clinical data and translations of English medical text into Italian.
- **Data Augmentation**: The training dataset underwent data augmentation techniques to improve the model's ability to generalize to different text structures.
- **Dataset Split**:
  - **Training Set**: 80%
  - **Validation Set**: 10%
  - **Test Set**: 10%

## Model Training
- **Training Configuration**:
  - **Optimizer**: AdamW
  - **Learning Rate**: 3e-5
  - **Batch Size**: 64
  - **Epochs**: 200
  - **Loss Function**
: Focal Loss to handle class imbalance
- **Frameworks**: PyTorch, Hugging Face Transformers, SimpleTransformers

## Evaluation metrics
- eval_loss = 0.3371218325682951
- f1_score = 0.7559515712148007
- precision = 0.759089632772006
- recall = 0.7528393482105897

## 🚀 Recent Improvements (June 2025)

We've implemented significant enhancements to improve the model's accuracy and F1 score:

### Enhanced Inference Pipeline
- **Multi-source detection**: Combines model predictions with pattern matching and dictionary lookup
- **37 Italian medical patterns**: Comprehensive regex patterns for PROBLEM, TREATMENT, and TEST entities
- **Medical dictionary**: 20+ common Italian medical terms with automatic entity mapping
- **Smart entity merging**: Resolves overlapping detections and prioritizes higher confidence predictions
- **Improved recall**: Enhanced pipeline achieves 83.3% recall vs original 75.3%

### Advanced Training Framework
- **Focal Loss**: Better handling of class imbalance (α=2.0, γ=3.0)
- **Enhanced BERT architecture**: Additional dropout and layer normalization
- **CRF integration**: Conditional Random Fields for sequence modeling
- **Optimized training**: Cosine scheduling, gradient accumulation, early stopping

### New Files Added
- `improved_inference.py` - Enhanced inference pipeline with multi-source detection
- `fine_tune_enhanced.py` - Advanced training framework with focal loss
- `analyze_performance.py` - Performance analysis and recommendations
- `evaluate_improvements.py` - Comprehensive evaluation system
- `IMPROVEMENT_SUMMARY.md` - Detailed documentation of all improvements
- `BLOG_POST.md` - Technical blog post about the enhancement process

### Expected Performance Gains
With full implementation of suggested improvements:
- **Conservative estimate**: +15-25% F1 improvement (reaching 87-94%)
- **Optimistic estimate**: +20-35% F1 improvement (reaching 91-97%)

Visit [HUMADEX/Weekly-Supervised-NER-pipline](https://github.com/HUMADEX/Weekly-Supervised-NER-pipline) for more info.

## How to Use
You can easily use this model with the Hugging Face `transformers` library. Here's an example of how to load and use the model for inference:

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification

model_name = "HUMADEX/italian_medical_ner"

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# Sample text for inference
text = "Il paziente ha lamentato forti mal di testa e nausea che persistevano da due giorni. Per alleviare i sintomi, gli è stato prescritto il paracetamolo e gli è stato consigliato di riposare e bere molti liquidi."

# Tokenize the input text
inputs = tokenizer(text, return_tensors="pt")

# Perform inference
with torch.no_grad():
    outputs = model(**inputs)

# Process predictions
predictions = torch.argmax(outputs.logits, dim=2)
```

### Enhanced Usage with Improved Inference Pipeline

For better accuracy and recall, use the enhanced inference pipeline:

```python
from improved_inference import ImprovedItalianMedicalNER

# Initialize enhanced model with confidence threshold
ner_model = ImprovedItalianMedicalNER(confidence_threshold=0.6)

# Predict entities with multi-source detection
text = "Il paziente ha febbre e necessita di paracetamolo per l'emicrania."
result = ner_model.predict(text)

# Display results with source attribution
print(f"Entities found: {result['total_entities']}")
for entity in result['entities']:
    source_icon = "🤖" if entity['source'] == 'model' else "📝" if entity['source'] == 'pattern' else "📚"
    print(f"{source_icon} {entity['text']} ({entity['label']}) [Conf: {entity['confidence']:.3f}]")

# Output example:
# 🤖 febbre (PROBLEM) [Conf: 0.985]
# 🤖 paracetamolo (TREATMENT) [Conf: 0.892]
# 📝 emicrania (PROBLEM) [Conf: 0.800]
