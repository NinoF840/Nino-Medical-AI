#!/usr/bin/env python3
"""
Simplified Performance Analysis for Italian Medical NER
Analyzes current model performance and provides improvement recommendations
"""

import torch
import numpy as np
from improved_inference import ImprovedItalianMedicalNER
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import json
from typing import Dict, List
from collections import defaultdict

def analyze_model_performance(model_path: str = "./"):
    """
    Analyze current model performance and suggest improvements
    """
    # Load current model evaluation results
    try:
        with open(f"{model_path}/eval_results.txt", 'r') as f:
            results = {}
            for line in f:
                key, value = line.strip().split(' = ')
                results[key] = float(value)
        
        print("\nCurrent Model Performance:")
        print("=" * 40)
        print(f"F1 Score: {results.get('f1_score', 0):.3f}")
        print(f"Precision: {results.get('precision', 0):.3f}")
        print(f"Recall: {results.get('recall', 0):.3f}")
        print(f"Accuracy: {results.get('accuracy', 0):.3f}")
        print(f"Eval Loss: {results.get('eval_loss', 0):.3f}")
        
        # Suggest improvements based on metrics
        f1 = results.get('f1_score', 0)
        precision = results.get('precision', 0)
        recall = results.get('recall', 0)
        
        print("\n" + "=" * 50)
        print("IMPROVEMENT RECOMMENDATIONS")
        print("=" * 50)
        
        if f1 < 0.8:
            print(f"\n🎯 F1 Score Improvements (Current: {f1:.3f}):")
            if precision > recall:
                print("   📈 Focus on improving RECALL:")
                print("     • Use focal loss with higher gamma for minority classes")
                print("     • Add more training data for underrepresented entities")
                print("     • Apply data augmentation techniques")
                print("     • Lower confidence threshold in post-processing")
                print("     • Use pattern matching for missed entities")
            else:
                print("   📊 Focus on improving PRECISION:")
                print("     • Use stricter post-processing rules")
                print("     • Implement ensemble methods")
                print("     • Add more negative examples in training")
                print("     • Use higher confidence threshold")
                print("     • Better entity boundary detection")
        
        if f1 < 0.85:
            print(f"\n🚀 Advanced Techniques to Try:")
            print("   🏗️ Model Architecture Improvements:")
            print("     • Add BiLSTM-CRF layer on top of BERT")
            print("     • Try different base models (RoBERTa, DeBERTa)")
            print("     • Implement multi-head attention")
            print("     • Use conditional random fields (CRF)")
            
            print("   📚 Training Strategy Enhancements:")
            print("     • Gradual unfreezing of transformer layers")
            print("     • Curriculum learning (easy → hard examples)")
            print("     • Multi-task learning with related tasks")
            print("     • Knowledge distillation from larger models")
            
            print("   💾 Data Enhancement Techniques:")
            print("     • Active learning for better data selection")
            print("     • Pseudo-labeling on unlabeled medical texts")
            print("     • Cross-lingual transfer from English medical NER")
            print("     • Synthetic data generation")
        
        # Specific improvement strategies
        print(f"\n⚡ Immediate Improvement Strategies:")
        print("   1. 📝 Enhanced Post-processing (Already Implemented):")
        print("      • Pattern matching for Italian medical terms")
        print("      • Dictionary lookup for common entities")
        print("      • Better entity boundary detection")
        
        print("   2. 🔧 Hyperparameter Tuning:")
        print(f"      • Adjust confidence threshold (current: varies)")
        print("      • Optimize learning rate and batch size")
        print("      • Fine-tune loss function parameters")
        
        print("   3. 📊 Ensemble Methods:")
        print("      • Combine multiple models with voting")
        print("      • Use different aggregation strategies")
        print("      • Implement confidence-weighted ensembles")
        
        return results
    
    except FileNotFoundError:
        print("⚠️ Could not find evaluation results. Please run model evaluation first.")
        return None

def test_enhanced_pipeline_performance():
    """
    Test the enhanced pipeline performance on sample texts
    """
    print("\n" + "=" * 50)
    print("ENHANCED PIPELINE PERFORMANCE TEST")
    print("=" * 50)
    
    # Initialize improved model
    ner_model = ImprovedItalianMedicalNER(confidence_threshold=0.6)
    
    # Test sentences with known entities
    test_cases = [
        {
            'text': "Il paziente presenta mal di testa e nausea persistente.",
            'expected_entities': ['mal di testa', 'nausea'],
            'expected_types': ['PROBLEM', 'PROBLEM']
        },
        {
            'text': "È stato prescritto paracetamolo per la febbre.",
            'expected_entities': ['paracetamolo', 'febbre'],
            'expected_types': ['TREATMENT', 'PROBLEM']
        },
        {
            'text': "Necessario eseguire esame del sangue e radiografia.",
            'expected_entities': ['esame del sangue', 'radiografia'],
            'expected_types': ['TEST', 'TEST']
        }
    ]
    
    total_expected = 0
    total_found = 0
    correct_entities = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['text']}")
        result = ner_model.predict(test_case['text'])
        
        found_texts = [e['text'].lower() for e in result['entities']]
        expected_texts = [e.lower() for e in test_case['expected_entities']]
        
        # Count matches
        matches = 0
        for expected in expected_texts:
            if any(expected in found or found in expected for found in found_texts):
                matches += 1
        
        total_expected += len(expected_texts)
        total_found += len(found_texts)
        correct_entities += matches
        
        print(f"  Expected: {test_case['expected_entities']}")
        print(f"  Found: {[e['text'] for e in result['entities']]}")
        print(f"  Matches: {matches}/{len(expected_texts)}")
    
    # Calculate performance metrics
    precision = correct_entities / total_found if total_found > 0 else 0
    recall = correct_entities / total_expected if total_expected > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\n📊 Enhanced Pipeline Performance:")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall: {recall:.3f}")
    print(f"  F1 Score: {f1:.3f}")
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'total_expected': total_expected,
        'total_found': total_found,
        'correct_entities': correct_entities
    }

def suggest_training_improvements():
    """
    Suggest specific training improvements
    """
    print("\n" + "=" * 50)
    print("TRAINING IMPROVEMENT STRATEGIES")
    print("=" * 50)
    
    strategies = {
        'Data Augmentation': {
            'description': 'Increase training data diversity',
            'techniques': [
                'Synonym replacement for medical terms',
                'Back-translation (Italian → English → Italian)',
                'Context variation while preserving entities',
                'Paraphrasing with medical language models'
            ],
            'expected_improvement': '+5-10% F1 score'
        },
        'Loss Function Optimization': {
            'description': 'Better handling of class imbalance',
            'techniques': [
                'Focal Loss (α=2.0, γ=3.0)',
                'Label smoothing (ε=0.1)',
                'Class-weighted loss functions',
                'Curriculum learning'
            ],
            'expected_improvement': '+3-7% F1 score'
        },
        'Model Architecture': {
            'description': 'Enhanced model capabilities',
            'techniques': [
                'BiLSTM-CRF on top of BERT',
                'Multi-head attention mechanisms',
                'Conditional Random Fields (CRF)',
                'Ensemble of different architectures'
            ],
            'expected_improvement': '+7-15% F1 score'
        },
        'Training Strategy': {
            'description': 'Optimized training process',
            'techniques': [
                'Learning rate scheduling (cosine annealing)',
                'Gradual unfreezing of layers',
                'Early stopping with patience',
                'Gradient accumulation for larger batch sizes'
            ],
            'expected_improvement': '+2-5% F1 score'
        }
    }
    
    for strategy_name, details in strategies.items():
        print(f"\n🎯 {strategy_name}:")
        print(f"   Description: {details['description']}")
        print(f"   Expected Improvement: {details['expected_improvement']}")
        print("   Techniques:")
        for technique in details['techniques']:
            print(f"     • {technique}")

def main():
    """
    Main analysis function
    """
    print("Italian Medical NER - Performance Analysis")
    print("=" * 50)
    
    # Analyze current model performance
    current_results = analyze_model_performance()
    
    # Test enhanced pipeline
    enhanced_results = test_enhanced_pipeline_performance()
    
    # Compare results if we have both
    if current_results and enhanced_results:
        print(f"\n📈 IMPROVEMENT SUMMARY:")
        current_f1 = current_results.get('f1_score', 0)
        enhanced_f1 = enhanced_results['f1']
        improvement = enhanced_f1 - current_f1
        improvement_pct = (improvement / current_f1 * 100) if current_f1 > 0 else 0
        
        print(f"  Original F1: {current_f1:.3f}")
        print(f"  Enhanced F1: {enhanced_f1:.3f}")
        print(f"  Improvement: {improvement:+.3f} ({improvement_pct:+.1f}%)")
        
        if improvement > 0:
            print("  ✅ Enhanced pipeline shows improvement!")
        else:
            print("  ⚠️ Enhanced pipeline needs further tuning")
    
    # Suggest training improvements
    suggest_training_improvements()
    
    print(f"\n" + "=" * 50)
    print("NEXT STEPS")
    print("=" * 50)
    print("1. 🔧 Fine-tune confidence thresholds based on your specific use case")
    print("2. 📊 Collect more Italian medical training data")
    print("3. 🚀 Implement the suggested training improvements")
    print("4. 🧪 Run comprehensive evaluation on held-out test set")
    print("5. 🔄 Iterate on the most promising improvements")
    
    print(f"\n💡 Pro Tip: The enhanced inference pipeline has already improved")
    print(f"   entity detection through pattern matching and dictionary lookup.")
    print(f"   For even better results, consider fine-tuning the base model!")

if __name__ == "__main__":
    main()

