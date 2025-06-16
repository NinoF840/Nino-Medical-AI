#!/usr/bin/env python3
"""
Enhanced Italian Medical NER Inference Pipeline
Features improved accuracy through post-processing techniques
"""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForTokenClassification
from collections import defaultdict
import re
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class EnhancedItalianMedicalNER:
    """
    Enhanced Italian Medical NER with post-processing improvements for better accuracy
    """
    
    def __init__(self, model_path: str = "./", confidence_threshold: float = 0.7):
        """
        Initialize the enhanced NER model
        
        Args:
            model_path: Path to the model directory
            confidence_threshold: Minimum confidence score for predictions
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.model.eval()
        
        # Entity labels
        self.id2label = self.model.config.id2label
        self.label2id = {v: k for k, v in self.id2label.items()}
        
        # Medical terminology patterns for post-processing
        self.medical_patterns = self._load_medical_patterns()
        
    def _load_medical_patterns(self) -> Dict[str, List[str]]:
        """
        Load Italian medical terminology patterns for better entity recognition
        """
        return {
            'PROBLEM_indicators': [
                r'\b(sintomo|sintomi|malattia|malattie|disturbo|disturbi|patologia|patologie)\b',
                r'\b(dolore|dolori|mal di|febbre|nausea|vomito|diarrea|tosse|raffreddore)\b',
                r'\b(infezione|infiammazione|allergia|allergie|tumore|tumori|cancro)\b',
                r'\b(diabete|ipertensione|ipotensione|tachicardia|bradicardia|aritmia)\b'
            ],
            'TREATMENT_indicators': [
                r'\b(farmaco|farmaci|medicina|medicine|terapia|terapie|trattamento|trattamenti)\b',
                r'\b(antibiotico|antibiotici|antidolorifico|antidolorifici|antinfiammatorio)\b',
                r'\b(paracetamolo|ibuprofene|aspirina|cortisone|insulina|eparina)\b',
                r'\b(intervento|operazione|chirurgia|fisioterapia|riabilitazione)\b'
            ],
            'TEST_indicators': [
                r'\b(esame|esami|test|analisi|controllo|controlli|visita|visite)\b',
                r'\b(radiografia|ecografia|tac|risonanza|elettrocardiogramma|ekg|ecg)\b',
                r'\b(biopsia|endoscopia|colonscopia|gastroscopia|spirometria)\b',
                r'\b(prelievo|sangue|urine|feci|tampone|cultura)\b'
            ]
        }
    
    def _get_confidence_scores(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Calculate confidence scores from model logits
        """
        probabilities = torch.softmax(logits, dim=-1)
        confidence_scores = torch.max(probabilities, dim=-1)[0]
        return confidence_scores
    
    def _apply_pattern_enhancement(self, tokens: List[str], predictions: List[str], 
                                 confidence_scores: List[float]) -> List[str]:
        """
        Apply medical pattern matching to enhance predictions
        """
        enhanced_predictions = predictions.copy()
        text = ' '.join(tokens)
        
        for entity_type, patterns in self.medical_patterns.items():
            entity_label = entity_type.split('_')[0]  # Extract PROBLEM, TREATMENT, TEST
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Find token positions for the match
                    start_pos = match.start()
                    end_pos = match.end()
                    
                    # Map character positions to token positions (simplified)
                    current_pos = 0
                    start_token_idx = None
                    end_token_idx = None
                    
                    for i, token in enumerate(tokens):
                        if current_pos <= start_pos < current_pos + len(token) + 1:
                            start_token_idx = i
                        if current_pos <= end_pos <= current_pos + len(token) + 1:
                            end_token_idx = i
                            break
                        current_pos += len(token) + 1
                    
                    # Apply BIOES tagging if pattern match found and confidence is low
                    if start_token_idx is not None and end_token_idx is not None:
                        for idx in range(start_token_idx, end_token_idx + 1):
                            if confidence_scores[idx] < self.confidence_threshold:
                                if start_token_idx == end_token_idx:
                                    enhanced_predictions[idx] = f'S-{entity_label}'
                                elif idx == start_token_idx:
                                    enhanced_predictions[idx] = f'B-{entity_label}'
                                elif idx == end_token_idx:
                                    enhanced_predictions[idx] = f'E-{entity_label}'
                                else:
                                    enhanced_predictions[idx] = f'I-{entity_label}'
        
        return enhanced_predictions
    
    def _post_process_bioes(self, predictions: List[str]) -> List[str]:
        """
        Post-process BIOES tags to ensure consistency
        """
        processed = []
        i = 0
        
        while i < len(predictions):
            current_pred = predictions[i]
            
            if current_pred.startswith('B-'):
                entity_type = current_pred[2:]
                sequence = [current_pred]
                i += 1
                
                # Look for continuation of the entity
                while i < len(predictions) and predictions[i].startswith(f'I-{entity_type}'):
                    sequence.append(predictions[i])
                    i += 1
                
                # Check for proper ending
                if i < len(predictions) and predictions[i].startswith(f'E-{entity_type}'):
                    sequence.append(predictions[i])
                    i += 1
                elif len(sequence) > 1:
                    # Fix missing E- tag
                    sequence[-1] = f'E-{entity_type}'
                
                processed.extend(sequence)
            
            elif current_pred.startswith('I-') or current_pred.startswith('E-'):
                # Orphaned I or E tag - convert to S if isolated or fix sequence
                entity_type = current_pred[2:]
                if not processed or not processed[-1].endswith(f'-{entity_type}'):
                    processed.append(f'S-{entity_type}')
                else:
                    processed.append(current_pred)
                i += 1
            
            else:
                processed.append(current_pred)
                i += 1
        
        return processed
    
    def predict(self, text: str, apply_enhancement: bool = True) -> Dict:
        """
        Predict medical entities in Italian text with enhanced accuracy
        
        Args:
            text: Input Italian medical text
            apply_enhancement: Whether to apply post-processing enhancements
            
        Returns:
            Dictionary containing entities, tokens, predictions, and confidence scores
        """
        # Tokenize input
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, 
                               padding=True, max_length=512)
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits[0]
            confidence_scores = self._get_confidence_scores(logits)
            
        # Convert logits to predictions
        predictions = torch.argmax(logits, dim=-1)
        predicted_labels = [self.id2label[pred.item()] for pred in predictions]
        confidence_list = confidence_scores.tolist()
        
        # Remove special tokens
        clean_tokens = []
        clean_predictions = []
        clean_confidence = []
        
        for i, (token, pred, conf) in enumerate(zip(tokens, predicted_labels, confidence_list)):
            if token not in ['[CLS]', '[SEP]', '[PAD]']:
                clean_tokens.append(token)
                clean_predictions.append(pred)
                clean_confidence.append(conf)
        
        # Apply enhancements if requested
        if apply_enhancement:
            clean_predictions = self._apply_pattern_enhancement(
                clean_tokens, clean_predictions, clean_confidence
            )
            clean_predictions = self._post_process_bioes(clean_predictions)
        
        # Extract entities
        entities = self._extract_entities(clean_tokens, clean_predictions, clean_confidence)
        
        return {
            'text': text,
            'tokens': clean_tokens,
            'predictions': clean_predictions,
            'confidence_scores': clean_confidence,
            'entities': entities
        }
    
    def _extract_entities(self, tokens: List[str], predictions: List[str], 
                         confidence_scores: List[float]) -> List[Dict]:
        """
        Extract entities from BIOES predictions
        """
        entities = []
        current_entity = None
        
        for i, (token, pred, conf) in enumerate(zip(tokens, predictions, confidence_scores)):
            if pred.startswith('B-') or pred.startswith('S-'):
                # Start of new entity
                if current_entity:
                    entities.append(current_entity)
                
                entity_type = pred[2:]
                current_entity = {
                    'text': token.replace('##', ''),
                    'label': entity_type,
                    'start_token': i,
                    'end_token': i,
                    'confidence': conf
                }
                
                if pred.startswith('S-'):
                    entities.append(current_entity)
                    current_entity = None
            
            elif pred.startswith('I-') and current_entity:
                # Continue current entity
                current_entity['text'] += token.replace('##', '')
                current_entity['end_token'] = i
                current_entity['confidence'] = min(current_entity['confidence'], conf)
            
            elif pred.startswith('E-') and current_entity:
                # End current entity
                current_entity['text'] += token.replace('##', '')
                current_entity['end_token'] = i
                current_entity['confidence'] = min(current_entity['confidence'], conf)
                entities.append(current_entity)
                current_entity = None
            
            elif current_entity and pred == 'O':
                # Entity interrupted by O tag
                entities.append(current_entity)
                current_entity = None
        
        # Add any remaining entity
        if current_entity:
            entities.append(current_entity)
        
        # Filter by confidence threshold
        filtered_entities = [
            entity for entity in entities 
            if entity['confidence'] >= self.confidence_threshold
        ]
        
        return filtered_entities
    
    def batch_predict(self, texts: List[str], apply_enhancement: bool = True) -> List[Dict]:
        """
        Predict entities for multiple texts
        """
        results = []
        for text in texts:
            result = self.predict(text, apply_enhancement)
            results.append(result)
        return results


def main():
    """
    Example usage of the enhanced Italian Medical NER
    """
    # Initialize enhanced model
    ner_model = EnhancedItalianMedicalNER()
    
    # Example Italian medical text
    sample_texts = [
        "Il paziente ha lamentato forti mal di testa e nausea che persistevano da due giorni.",
        "Per alleviare i sintomi, gli è stato prescritto il paracetamolo.",
        "È necessario eseguire un esame del sangue e una radiografia del torace.",
        "La terapia antibiotica è stata efficace nel trattamento dell'infezione."
    ]
    
    print("Enhanced Italian Medical NER Results:")
    print("=" * 50)
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\nExample {i}: {text}")
        result = ner_model.predict(text)
        
        print(f"Entities found: {len(result['entities'])}")
        for entity in result['entities']:
            print(f"  - {entity['text']} ({entity['label']}) [Confidence: {entity['confidence']:.3f}]")


if __name__ == "__main__":
    main()

