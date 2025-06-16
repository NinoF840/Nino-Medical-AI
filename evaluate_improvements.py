#!/usr/bin/env python3
"""
Evaluation Script for Italian Medical NER Improvements
Compares original model performance with enhanced inference
"""

import torch
import time
from enhanced_inference import EnhancedItalianMedicalNER
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from typing import List, Dict
import json
from collections import defaultdict
import pandas as pd

class ModelEvaluator:
    """
    Evaluate and compare different NER approaches
    """
    
    def __init__(self, model_path: str = "./"):
        self.model_path = model_path
        
        # Load original model
        self.original_tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.original_model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.original_pipeline = pipeline(
            "ner", 
            model=self.original_model, 
            tokenizer=self.original_tokenizer,
            aggregation_strategy="simple"
        )
        
        # Load enhanced model
        self.enhanced_model = EnhancedItalianMedicalNER(model_path, confidence_threshold=0.7)
        
        # Test sentences
        self.test_sentences = [
            "Il paziente presenta forti mal di testa e nausea persistente da tre giorni.",
            "Per il trattamento dell'infezione è stato prescritto l'antibiotico amoxicillina.",
            "È necessario eseguire immediatamente un esame del sangue e una radiografia del torace.",
            "Il diabete del paziente è controllato con insulina e una dieta appropriata.",
            "La terapia fisioterapica ha migliorato notevolmente i dolori articolari.",
            "I risultati della biopsia hanno confermato la presenza di cellule tumorali.",
            "Il paracetamolo è efficace per ridurre la febbre e alleviare il dolore.",
            "La gastroscopia ha rivelato un'ulcera gastrica che richiede trattamento medico.",
            "Il paziente soffre di ipertensione e assume regolarmente farmaci antipertensivi.",
            "L'elettrocardiogramma mostra segni di aritmia cardiaca che necessita monitoraggio."
        ]
    
    def evaluate_original_model(self, text: str) -> Dict:
        """
        Evaluate using the original model
        """
        start_time = time.time()
        
        try:
            results = self.original_pipeline(text)
            entities = []
            
            for result in results:
                entities.append({
                    'text': result['word'],
                    'label': result['entity_group'],
                    'confidence': result['score'],
                    'start': result.get('start', 0),
                    'end': result.get('end', 0)
                })
            
            inference_time = time.time() - start_time
            
            return {
                'entities': entities,
                'inference_time': inference_time,
                'error': None
            }
        
        except Exception as e:
            return {
                'entities': [],
                'inference_time': time.time() - start_time,
                'error': str(e)
            }
    
    def evaluate_enhanced_model(self, text: str) -> Dict:
        """
        Evaluate using the enhanced model
        """
        start_time = time.time()
        
        try:
            result = self.enhanced_model.predict(text, apply_enhancement=True)
            inference_time = time.time() - start_time
            
            return {
                'entities': result['entities'],
                'inference_time': inference_time,
                'error': None,
                'tokens': result['tokens'],
                'predictions': result['predictions']
            }
        
        except Exception as e:
            return {
                'entities': [],
                'inference_time': time.time() - start_time,
                'error': str(e)
            }
    
    def compare_entity_detection(self, original_entities: List[Dict], 
                               enhanced_entities: List[Dict]) -> Dict:
        """
        Compare entity detection between models
        """
        # Group entities by type
        original_by_type = defaultdict(list)
        enhanced_by_type = defaultdict(list)
        
        for entity in original_entities:
            original_by_type[entity['label']].append(entity['text'].lower())
        
        for entity in enhanced_entities:
            enhanced_by_type[entity['label']].append(entity['text'].lower())
        
        comparison = {
            'total_original': len(original_entities),
            'total_enhanced': len(enhanced_entities),
            'by_type': {},
            'new_detections': [],
            'missed_detections': [],
            'confidence_improvement': 0
        }
        
        # Compare by entity type
        all_types = set(list(original_by_type.keys()) + list(enhanced_by_type.keys()))
        
        for entity_type in all_types:
            orig_count = len(original_by_type[entity_type])
            enh_count = len(enhanced_by_type[entity_type])
            
            comparison['by_type'][entity_type] = {
                'original_count': orig_count,
                'enhanced_count': enh_count,
                'difference': enh_count - orig_count
            }
        
        # Find new and missed detections
        original_texts = set([e['text'].lower() for e in original_entities])
        enhanced_texts = set([e['text'].lower() for e in enhanced_entities])
        
        comparison['new_detections'] = list(enhanced_texts - original_texts)
        comparison['missed_detections'] = list(original_texts - enhanced_texts)
        
        # Calculate average confidence improvement
        if enhanced_entities:
            avg_enhanced_conf = sum([e['confidence'] for e in enhanced_entities]) / len(enhanced_entities)
            if original_entities:
                avg_original_conf = sum([e['confidence'] for e in original_entities]) / len(original_entities)
                comparison['confidence_improvement'] = avg_enhanced_conf - avg_original_conf
            else:
                comparison['confidence_improvement'] = avg_enhanced_conf
        
        return comparison
    
    def run_comprehensive_evaluation(self) -> Dict:
        """
        Run comprehensive evaluation on test sentences
        """
        results = {
            'summary': {
                'total_sentences': len(self.test_sentences),
                'original_total_entities': 0,
                'enhanced_total_entities': 0,
                'average_original_time': 0,
                'average_enhanced_time': 0,
                'improvements_by_type': defaultdict(int),
                'new_detections_total': 0,
                'missed_detections_total': 0
            },
            'detailed_results': []
        }
        
        total_original_time = 0
        total_enhanced_time = 0
        
        print("Running comprehensive evaluation...")
        print("=" * 50)
        
        for i, sentence in enumerate(self.test_sentences, 1):
            print(f"\nEvaluating sentence {i}/{len(self.test_sentences)}")
            print(f"Text: {sentence[:60]}..." if len(sentence) > 60 else f"Text: {sentence}")
            
            # Evaluate with original model
            original_result = self.evaluate_original_model(sentence)
            
            # Evaluate with enhanced model
            enhanced_result = self.evaluate_enhanced_model(sentence)
            
            # Compare results
            comparison = self.compare_entity_detection(
                original_result['entities'], 
                enhanced_result['entities']
            )
            
            # Store detailed results
            detailed_result = {
                'sentence_id': i,
                'text': sentence,
                'original_result': original_result,
                'enhanced_result': enhanced_result,
                'comparison': comparison
            }
            
            results['detailed_results'].append(detailed_result)
            
            # Update summary statistics
            results['summary']['original_total_entities'] += comparison['total_original']
            results['summary']['enhanced_total_entities'] += comparison['total_enhanced']
            
            total_original_time += original_result['inference_time']
            total_enhanced_time += enhanced_result['inference_time']
            
            results['summary']['new_detections_total'] += len(comparison['new_detections'])
            results['summary']['missed_detections_total'] += len(comparison['missed_detections'])
            
            # Update improvements by type
            for entity_type, data in comparison['by_type'].items():
                results['summary']['improvements_by_type'][entity_type] += data['difference']
            
            # Print brief results
            print(f"  Original: {comparison['total_original']} entities")
            print(f"  Enhanced: {comparison['total_enhanced']} entities")
            if comparison['new_detections']:
                print(f"  New detections: {comparison['new_detections']}")
        
        # Calculate averages
        results['summary']['average_original_time'] = total_original_time / len(self.test_sentences)
        results['summary']['average_enhanced_time'] = total_enhanced_time / len(self.test_sentences)
        
        return results
    
    def print_summary_report(self, results: Dict):
        """
        Print a comprehensive summary report
        """
        summary = results['summary']
        
        print("\n" + "=" * 60)
        print("COMPREHENSIVE EVALUATION SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"  Total sentences evaluated: {summary['total_sentences']}")
        print(f"  Original model entities: {summary['original_total_entities']}")
        print(f"  Enhanced model entities: {summary['enhanced_total_entities']}")
        print(f"  Net improvement: {summary['enhanced_total_entities'] - summary['original_total_entities']} entities")
        
        improvement_percentage = ((summary['enhanced_total_entities'] - summary['original_total_entities']) / 
                                max(summary['original_total_entities'], 1)) * 100
        print(f"  Improvement percentage: {improvement_percentage:.1f}%")
        
        print(f"\n⏱️ PERFORMANCE TIMING:")
        print(f"  Average original inference time: {summary['average_original_time']:.3f}s")
        print(f"  Average enhanced inference time: {summary['average_enhanced_time']:.3f}s")
        
        speed_difference = summary['average_enhanced_time'] - summary['average_original_time']
        print(f"  Speed difference: {speed_difference:.3f}s ({'slower' if speed_difference > 0 else 'faster'})")
        
        print(f"\n🎯 ENTITY TYPE IMPROVEMENTS:")
        for entity_type, improvement in summary['improvements_by_type'].items():
            status = "⬆️" if improvement > 0 else "⬇️" if improvement < 0 else "➡️"
            print(f"  {entity_type}: {improvement:+d} entities {status}")
        
        print(f"\n🆕 DETECTION ANALYSIS:")
        print(f"  New detections: {summary['new_detections_total']}")
        print(f"  Missed detections: {summary['missed_detections_total']}")
        print(f"  Net detection improvement: {summary['new_detections_total'] - summary['missed_detections_total']}")
        
        # Calculate overall assessment
        total_improvements = sum([max(0, imp) for imp in summary['improvements_by_type'].values()])
        total_degradations = sum([abs(min(0, imp)) for imp in summary['improvements_by_type'].values()])
        
        print(f"\n🏆 OVERALL ASSESSMENT:")
        if improvement_percentage > 10:
            print("  ✅ SIGNIFICANT IMPROVEMENT - Enhanced model performs substantially better")
        elif improvement_percentage > 5:
            print("  ✅ MODERATE IMPROVEMENT - Enhanced model shows good gains")
        elif improvement_percentage > 0:
            print("  ✅ SLIGHT IMPROVEMENT - Enhanced model performs marginally better")
        elif improvement_percentage == 0:
            print("  ➡️ NO CHANGE - Both models perform equally")
        else:
            print("  ⚠️ DEGRADATION - Enhanced model performs worse")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if improvement_percentage < 5:
            print("  • Consider adjusting confidence threshold")
            print("  • Review medical terminology patterns")
            print("  • Fine-tune the model with additional data")
        
        if speed_difference > 0.1:
            print("  • Optimize post-processing for better speed")
            print("  • Consider using batch processing for multiple texts")
        
        if summary['missed_detections_total'] > summary['new_detections_total']:
            print("  • Review missed detections to improve recall")
            print("  • Lower confidence threshold or enhance pattern matching")

def main():
    """
    Main evaluation function
    """
    print("Italian Medical NER - Enhancement Evaluation")
    print("=" * 50)
    
    # Initialize evaluator
    evaluator = ModelEvaluator()
    
    # Run comprehensive evaluation
    results = evaluator.run_comprehensive_evaluation()
    
    # Print summary report
    evaluator.print_summary_report(results)
    
    # Optionally save results to file
    print("\n💾 Saving detailed results to 'evaluation_results.json'")
    with open('evaluation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n✓ Evaluation completed successfully!")
    print("\nTo further improve the model, consider:")
    print("1. Running the fine-tuning script (fine_tune_enhanced.py)")
    print("2. Adjusting confidence thresholds based on results")
    print("3. Adding more Italian medical terminology patterns")
    print("4. Implementing ensemble methods for even better accuracy")

if __name__ == "__main__":
    main()

