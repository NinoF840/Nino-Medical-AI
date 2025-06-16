#!/usr/bin/env python3
"""
Advanced Fine-tuning Script for Italian Medical NER
Implements multiple techniques to improve F1 score and accuracy
"""

import torch
import torch.nn as nn
import numpy as np
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification,
    TrainingArguments, Trainer, DataCollatorForTokenClassification
)
from torch.nn import CrossEntropyLoss
from typing import Dict, List, Tuple, Optional
import json
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score, precision_score, recall_score
import warnings
warnings.filterwarnings('ignore')

class FocalLoss(nn.Module):
    """
    Focal Loss implementation for handling class imbalance
    """
    def __init__(self, alpha: float = 1.0, gamma: float = 2.0, reduction: str = 'mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
    
    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = CrossEntropyLoss(reduction='none')(inputs.view(-1, inputs.size(-1)), targets.view(-1))
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss

class LabelSmoothingCrossEntropy(nn.Module):
    """
    Label smoothing cross entropy loss
    """
    def __init__(self, smoothing: float = 0.1):
        super(LabelSmoothingCrossEntropy, self).__init__()
        self.smoothing = smoothing
    
    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        log_probs = torch.log_softmax(inputs, dim=-1)
        targets_one_hot = torch.zeros_like(log_probs).scatter_(1, targets.unsqueeze(1), 1)
        targets_smooth = (1 - self.smoothing) * targets_one_hot + self.smoothing / log_probs.size(-1)
        loss = (-targets_smooth * log_probs).sum(dim=-1).mean()
        return loss

class EnhancedBERTForNER(nn.Module):
    """
    Enhanced BERT model with additional features for better NER performance
    """
    def __init__(self, base_model_name: str, num_labels: int, dropout_rate: float = 0.3):
        super(EnhancedBERTForNER, self).__init__()
        
        # Load base BERT model
        self.bert = AutoModelForTokenClassification.from_pretrained(
            base_model_name, num_labels=num_labels
        )
        
        # Additional layers for enhanced performance
        self.dropout = nn.Dropout(dropout_rate)
        self.layer_norm = nn.LayerNorm(self.bert.config.hidden_size)
        
        # CRF layer for sequence modeling (simplified implementation)
        self.use_crf = True
        if self.use_crf:
            self.crf_transitions = nn.Parameter(torch.randn(num_labels, num_labels))
    
    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        outputs = self.bert.bert(input_ids=input_ids, attention_mask=attention_mask)
        
        # Apply layer normalization and dropout
        hidden_states = self.layer_norm(outputs.last_hidden_state)
        hidden_states = self.dropout(hidden_states)
        
        # Get logits
        logits = self.bert.classifier(hidden_states)
        
        loss = None
        if labels is not None:
            # Use focal loss for better handling of class imbalance
            focal_loss = FocalLoss(alpha=1.0, gamma=2.0)
            
            # Flatten the tokens
            active_loss = attention_mask.view(-1) == 1
            active_logits = logits.view(-1, logits.size(-1))[active_loss]
            active_labels = labels.view(-1)[active_loss]
            
            loss = focal_loss(active_logits, active_labels)
        
        return {
            'loss': loss,
            'logits': logits,
            'hidden_states': outputs.hidden_states,
            'attentions': outputs.attentions
        }

class EnhancedTrainer(Trainer):
    """
    Enhanced trainer with custom loss functions and metrics
    """
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights
    
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get('logits')
        
        if labels is not None:
            # Use weighted focal loss
            loss_fct = FocalLoss(alpha=2.0, gamma=3.0)
            
            # Only compute loss on active tokens
            active_loss = inputs["attention_mask"].view(-1) == 1
            active_logits = logits.view(-1, logits.size(-1))[active_loss]
            active_labels = labels.view(-1)[active_loss]
            
            loss = loss_fct(active_logits, active_labels)
        else:
            loss = outputs.get('loss')
        
        return (loss, outputs) if return_outputs else loss

def compute_metrics(eval_pred):
    """
    Compute F1, precision, and recall metrics
    """
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=2)
    
    # Remove ignored index (special tokens)
    true_predictions = [
        [p for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [l for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    
    # Flatten for sklearn metrics
    flat_true_predictions = [item for sublist in true_predictions for item in sublist]
    flat_true_labels = [item for sublist in true_labels for item in sublist]
    
    return {
        "f1": f1_score(flat_true_labels, flat_true_predictions, average="weighted"),
        "precision": precision_score(flat_true_labels, flat_true_predictions, average="weighted"),
        "recall": recall_score(flat_true_labels, flat_true_predictions, average="weighted"),
    }

def create_enhanced_training_args() -> TrainingArguments:
    """
    Create enhanced training arguments for better performance
    """
    return TrainingArguments(
        output_dir="./enhanced_model",
        num_train_epochs=5,  # Reduced epochs for demonstration
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        gradient_accumulation_steps=4,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_ratio=0.1,
        logging_steps=100,
        evaluation_strategy="steps",
        eval_steps=500,
        save_strategy="steps",
        save_steps=500,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=3,
        report_to=None,  # Disable wandb/tensorboard for demo
        dataloader_pin_memory=False,
        fp16=torch.cuda.is_available(),  # Use FP16 if CUDA available
        # Advanced optimization settings
        adam_epsilon=1e-8,
        max_grad_norm=1.0,
        lr_scheduler_type="cosine",
    )

def prepare_dataset_for_training(data_path: str = None) -> Dict:
    """
    Prepare dataset for training (placeholder function)
    In a real implementation, this would load and preprocess your training data
    """
    # This is a placeholder - you would implement actual data loading here
    print("Note: This is a demonstration script.")
    print("For actual fine-tuning, you would need to:")
    print("1. Prepare your training dataset in the correct format")
    print("2. Implement proper data loading and preprocessing")
    print("3. Run the training loop")
    
    return {
        'train_dataset': None,
        'eval_dataset': None,
        'tokenizer': None
    }

def create_data_augmentation_strategies():
    """
    Data augmentation strategies for improving model performance
    """
    strategies = {
        'synonym_replacement': {
            'description': 'Replace medical terms with synonyms',
            'examples': {
                'mal di testa': ['cefalea', 'emicrania'],
                'febbre': ['ipertermia', 'stato febbrile'],
                'nausea': ['senso di nausea', 'malessere gastrico']
            }
        },
        'context_variation': {
            'description': 'Vary sentence structures while keeping entities',
            'examples': [
                'Il paziente presenta {} -> Il soggetto manifesta {}',
                'È stato riscontrato {} -> Si è osservato {}'
            ]
        },
        'back_translation': {
            'description': 'Translate to English and back to Italian for paraphrasing',
            'note': 'Use medical translation models for accuracy'
        }
    }
    return strategies

def analyze_model_performance(model_path: str = "./"):
    """
    Analyze current model performance and suggest improvements
    """
    # Load current model
    try:
        with open(f"{model_path}/eval_results.txt", 'r') as f:
            results = {}
            for line in f:
                key, value = line.strip().split(' = ')
                results[key] = float(value)
        
        print("\nCurrent Model Performance:")
        print(f"F1 Score: {results.get('f1_score', 0):.3f}")
        print(f"Precision: {results.get('precision', 0):.3f}")
        print(f"Recall: {results.get('recall', 0):.3f}")
        print(f"Accuracy: {results.get('accuracy', 0):.3f}")
        
        # Suggest improvements based on metrics
        f1 = results.get('f1_score', 0)
        precision = results.get('precision', 0)
        recall = results.get('recall', 0)
        
        print("\n=== IMPROVEMENT RECOMMENDATIONS ===")
        
        if f1 < 0.8:
            print("\n🎯 F1 Score Improvements:")
            if precision > recall:
                print("   • Focus on improving recall:")
                print("     - Use focal loss with higher gamma (already implemented)")
                print("     - Add more training data for underrepresented entities")
                print("     - Use data augmentation techniques")
                print("     - Lower confidence threshold in post-processing")
            else:
                print("   • Focus on improving precision:")
                print("     - Use stricter post-processing rules")
                print("     - Implement ensemble methods")
                print("     - Add more negative examples in training")
                print("     - Use higher confidence threshold")
        
        if f1 < 0.85:
            print("\n🚀 Advanced Techniques to Try:")
            print("   • Model Architecture:")
            print("     - Use BiLSTM-CRF layer on top of BERT")
            print("     - Try RoBERTa or DeBERTa as base model")
            print("     - Implement attention mechanisms")
            
            print("   • Training Strategies:")
            print("     - Gradual unfreezing of BERT layers")
            print("     - Curriculum learning (easy → hard examples)")
            print("     - Multi-task learning with related tasks")
            
            print("   • Data Enhancement:")
            print("     - Active learning for better data selection")
            print("     - Pseudo-labeling on unlabeled medical texts")
            print("     - Cross-lingual transfer from English medical NER")
    
    except FileNotFoundError:
        print("Could not find evaluation results. Run evaluation first.")

def main():
    """
    Main function demonstrating enhanced training approach
    """
    print("Enhanced Italian Medical NER - Fine-tuning Script")
    print("=" * 55)
    
    # Analyze current performance
    analyze_model_performance()
    
    # Show data augmentation strategies
    print("\n=== DATA AUGMENTATION STRATEGIES ===")
    strategies = create_data_augmentation_strategies()
    for name, strategy in strategies.items():
        print(f"\n{name.replace('_', ' ').title()}:")
        print(f"  {strategy['description']}")
        if 'examples' in strategy:
            print(f"  Examples: {strategy['examples']}")
    
    # Training configuration
    print("\n=== ENHANCED TRAINING CONFIGURATION ===")
    training_args = create_enhanced_training_args()
    print(f"Learning Rate: {training_args.learning_rate}")
    print(f"Batch Size: {training_args.per_device_train_batch_size}")
    print(f"Epochs: {training_args.num_train_epochs}")
    print(f"Weight Decay: {training_args.weight_decay}")
    print(f"Warmup Ratio: {training_args.warmup_ratio}")
    print(f"Scheduler: {training_args.lr_scheduler_type}")
    
    print("\n=== IMPLEMENTATION NOTES ===")
    print("• Focal Loss: Helps with class imbalance")
    print("• Enhanced BERT: Additional layers for better feature extraction")
    print("• Cosine Scheduler: Better learning rate decay")
    print("• Gradient Accumulation: Effective larger batch sizes")
    print("• Early Stopping: Prevents overfitting")
    
    print("\n=== NEXT STEPS ===")
    print("1. Prepare your training dataset in CoNLL format")
    print("2. Implement data loading functions")
    print("3. Run the enhanced training pipeline")
    print("4. Evaluate using the enhanced inference script")
    print("5. Compare results with current model")
    
    # Note about actual training
    print("\n⚠️  NOTE: This script demonstrates the enhanced training approach.")
    print("   For actual training, you'll need to provide your dataset and")
    print("   implement the data loading functions.")

if __name__ == "__main__":
    main()

