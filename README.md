---
license: apache-2.0
datasets:
- rigonsallauka/italian_ner_dataset
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
  - **Loss Function**: Focal Loss to handle class imbalance
- **Frameworks**: PyTorch, Hugging Face Transformers, SimpleTransformers

## How to Use
You can easily use this model with the Hugging Face `transformers` library. Here's an example of how to load and use the model for inference:

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

model_name = "rigonsallauka/italian_medical_ner"

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# Sample text for inference
text = "Il paziente ha lamentato forti mal di testa e nausea che persistevano da due giorni. Per alleviare i sintomi, gli è stato prescritto il paracetamolo e gli è stato consigliato di riposare e bere molti liquidi."

# Tokenize the input text
inputs = tokenizer(text, return_tensors="pt")