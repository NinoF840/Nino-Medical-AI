#!/usr/bin/env python3
"""
Improved Italian Medical NER Inference Pipeline
Fixes tokenization issues and improves accuracy through better post-processing
"""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from collections import defaultdict
import re
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class ImprovedItalianMedicalNER:
    """
    Improved Italian Medical NER with better tokenization handling and post-processing
    """
    
    def __init__(self, model_path: str = "./", confidence_threshold: float = 0.6):
        """
        Initialize the improved NER model
        
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
        
        # Use pipeline for better entity aggregation
        self.pipeline = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="max",  # Use max aggregation for better results
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Entity labels
        self.id2label = self.model.config.id2label
        self.label2id = {v: k for k, v in self.id2label.items()}
        
        # Enhanced medical terminology patterns for Italian
        self.medical_patterns = self._load_enhanced_medical_patterns()
        
        # Common Italian medical entities that might be missed
        self.medical_dictionary = self._load_medical_dictionary()
    
    def _load_enhanced_medical_patterns(self) -> Dict[str, List[str]]:
        """
        Load comprehensive Italian medical terminology patterns
        """
        return {
            'PROBLEM_patterns': [
                # Symptoms and conditions
                r'\b(mal\s+di\s+testa|cefalea|emicrania|dolore\s+alla\s+testa)\b',
                r'\b(febbre|ipertermia|stato\s+febbrile|temperatura\s+elevata)\b',
                r'\b(nausea|vomito|conati|senso\s+di\s+nausea)\b',
                r'\b(diarrea|dissenteria|disturbi\s+intestinali)\b',
                r'\b(tosse|tossire|colpo\s+di\s+tosse)\b',
                r'\b(dolore|dolori|algia|dolenza|male)\b',
                r'\b(infezione|infiammazione|flogosi)\b',
                r'\b(diabete|glicemia\s+alta|iperglicemia)\b',
                r'\b(ipertensione|pressione\s+alta|ipotensione)\b',
                r'\b(allergia|reazione\s+allergica|intolleranza)\b',
                r'\b(tumore|neoplasia|cancro|carcinoma)\b',
                r'\b(ulcera|lesione|ferita)\b',
                r'\b(aritmia|tachicardia|bradicardia|palpitazioni)\b'
            ],
            'TREATMENT_patterns': [
                # Medications and treatments
                r'\b(paracetamolo|acetaminofene|tachipirina)\b',
                r'\b(ibuprofene|moment|brufen)\b',
                r'\b(aspirina|acido\s+acetilsalicilico|cardioaspirina)\b',
                r'\b(antibiotico|antibiotici|amoxicillina|azitromicina)\b',
                r'\b(antidolorifico|analgesico|antinfiammatorio)\b',
                r'\b(cortisone|corticosteroidi|prednisone)\b',
                r'\b(insulina|metformina|antidiabetico)\b',
                r'\b(terapia|trattamento|cura|medicazione)\b',
                r'\b(farmaco|medicina|medicinale|medicamento)\b',
                r'\b(intervento|operazione|chirurgia)\b',
                r'\b(fisioterapia|riabilitazione|ginnastica)\b',
                r'\b(chemioterapia|radioterapia|oncologia)\b'
            ],
            'TEST_patterns': [
                # Medical tests and examinations
                r'\b(esame\s+del\s+sangue|analisi\s+del\s+sangue|emocromo)\b',
                r'\b(radiografia|rx|raggi\s+x)\b',
                r'\b(ecografia|ultrasuoni|eco)\b',
                r'\b(tac|tomografia|risonanza\s+magnetica|rmn)\b',
                r'\b(elettrocardiogramma|ecg|ekg)\b',
                r'\b(biopsia|prelievo|campione)\b',
                r'\b(endoscopia|gastroscopia|colonscopia)\b',
                r'\b(spirometria|test\s+respiratorio)\b',
                r'\b(visita|controllo|consultazione)\b',
                r'\b(esame|test|analisi|screening)\b',
                r'\b(urine|feci|tampone|cultura)\b',
                r'\b(mammografia|pap\s+test|holter)\b'
            ]
        }
    
    def _load_medical_dictionary(self) -> Dict[str, str]:
        """
        Load dictionary of common Italian medical terms with their entity types
        """
        return {
            # Problems/Symptoms
            'cefalea': 'PROBLEM', 'emicrania': 'PROBLEM', 'nausea': 'PROBLEM',
            'febbre': 'PROBLEM', 'tosse': 'PROBLEM', 'dolore': 'PROBLEM',
            'diabete': 'PROBLEM', 'ipertensione': 'PROBLEM', 'ulcera': 'PROBLEM',
            'infezione': 'PROBLEM', 'allergia': 'PROBLEM', 'tumore': 'PROBLEM',
            'aritmia': 'PROBLEM', 'tachicardia': 'PROBLEM', 'bradicardia': 'PROBLEM',
            
            # Treatments
            'paracetamolo': 'TREATMENT', 'ibuprofene': 'TREATMENT', 'aspirina': 'TREATMENT',
            'antibiotico': 'TREATMENT', 'insulina': 'TREATMENT', 'cortisone': 'TREATMENT',
            'terapia': 'TREATMENT', 'trattamento': 'TREATMENT', 'farmaco': 'TREATMENT',
            'chirurgia': 'TREATMENT', 'fisioterapia': 'TREATMENT', 'chemioterapia': 'TREATMENT',
            
            # Tests
            'radiografia': 'TEST', 'ecografia': 'TEST', 'elettrocardiogramma': 'TEST',
            'biopsia': 'TEST', 'endoscopia': 'TEST', 'gastroscopia': 'TEST',
            'colonscopia': 'TEST', 'spirometria': 'TEST', 'mammografia': 'TEST',
            'esame': 'TEST', 'analisi': 'TEST', 'controllo': 'TEST', 'visita': 'TEST'
        }
    
    def _apply_pattern_enhancement(self, text: str, entities: List[Dict]) -> List[Dict]:
        """
        Apply pattern matching to find additional entities
        """
        enhanced_entities = entities.copy()
        found_spans = [(e['start'], e['end']) for e in entities]
        
        for entity_type, patterns in self.medical_patterns.items():
            entity_label = entity_type.split('_')[0]  # Extract PROBLEM, TREATMENT, TEST
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    start, end = match.span()
                    
                    # Check if this span overlaps with existing entities
                    overlaps = any(
                        (start < existing_end and end > existing_start)
                        for existing_start, existing_end in found_spans
                    )
                    
                    if not overlaps:
                        enhanced_entities.append({
                            'text': match.group(),
                            'label': entity_label,
                            'start': start,
                            'end': end,
                            'confidence': 0.8,  # Pattern-based confidence
                            'source': 'pattern'
                        })
                        found_spans.append((start, end))
        
        return enhanced_entities
    
    def _apply_dictionary_enhancement(self, text: str, entities: List[Dict]) -> List[Dict]:
        """
        Apply dictionary lookup to find additional entities
        """
        enhanced_entities = entities.copy()
        found_spans = [(e['start'], e['end']) for e in entities]
        
        # Split text into words and check each against dictionary
        words = re.findall(r'\b\w+\b', text.lower())
        word_positions = [(m.start(), m.end()) for m in re.finditer(r'\b\w+\b', text)]
        
        for word, (start, end) in zip(words, word_positions):
            if word in self.medical_dictionary:
                # Check if this span overlaps with existing entities
                overlaps = any(
                    (start < existing_end and end > existing_start)
                    for existing_start, existing_end in found_spans
                )
                
                if not overlaps:
                    enhanced_entities.append({
                        'text': text[start:end],
                        'label': self.medical_dictionary[word],
                        'start': start,
                        'end': end,
                        'confidence': 0.7,  # Dictionary-based confidence
                        'source': 'dictionary'
                    })
                    found_spans.append((start, end))
        
        return enhanced_entities
    
    def _filter_and_merge_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Filter entities by confidence and merge overlapping ones
        """
        # Filter by confidence threshold
        filtered_entities = [
            entity for entity in entities 
            if entity['confidence'] >= self.confidence_threshold
        ]
        
        # Sort by start position
        filtered_entities.sort(key=lambda x: x['start'])
        
        # Merge overlapping entities (keep the one with higher confidence)
        merged_entities = []
        for entity in filtered_entities:
            if not merged_entities:
                merged_entities.append(entity)
            else:
                last_entity = merged_entities[-1]
                
                # Check for overlap
                if (entity['start'] < last_entity['end'] and 
                    entity['end'] > last_entity['start']):
                    
                    # Keep entity with higher confidence
                    if entity['confidence'] > last_entity['confidence']:
                        merged_entities[-1] = entity
                    # If same confidence, prefer longer entity
                    elif (entity['confidence'] == last_entity['confidence'] and 
                          (entity['end'] - entity['start']) > (last_entity['end'] - last_entity['start'])):
                        merged_entities[-1] = entity
                else:
                    merged_entities.append(entity)
        
        return merged_entities
    
    def predict(self, text: str, apply_enhancement: bool = True) -> Dict:
        """
        Predict medical entities in Italian text with improved accuracy
        
        Args:
            text: Input Italian medical text
            apply_enhancement: Whether to apply post-processing enhancements
            
        Returns:
            Dictionary containing entities and metadata
        """
        # Use pipeline for basic entity detection
        pipeline_results = self.pipeline(text)
        
        # Convert pipeline results to standard format
        entities = []
        for result in pipeline_results:
            entities.append({
                'text': result['word'],
                'label': result['entity_group'],
                'start': result['start'],
                'end': result['end'],
                'confidence': result['score'],
                'source': 'model'
            })
        
        # Apply enhancements if requested
        if apply_enhancement:
            entities = self._apply_pattern_enhancement(text, entities)
            entities = self._apply_dictionary_enhancement(text, entities)
            entities = self._filter_and_merge_entities(entities)
        else:
            entities = self._filter_and_merge_entities(entities)
        
        # Calculate entity type counts
        entity_counts = defaultdict(int)
        for entity in entities:
            entity_counts[entity['label']] += 1
        
        return {
            'text': text,
            'entities': entities,
            'entity_counts': dict(entity_counts),
            'total_entities': len(entities),
            'confidence_threshold': self.confidence_threshold
        }
    
    def batch_predict(self, texts: List[str], apply_enhancement: bool = True) -> List[Dict]:
        """
        Predict entities for multiple texts
        """
        results = []
        for text in texts:
            result = self.predict(text, apply_enhancement)
            results.append(result)
        return results
    
    def get_entity_statistics(self, texts: List[str]) -> Dict:
        """
        Get statistics about entity detection across multiple texts
        """
        all_results = self.batch_predict(texts)
        
        total_entities = sum(result['total_entities'] for result in all_results)
        entity_type_counts = defaultdict(int)
        confidence_scores = []
        
        for result in all_results:
            for entity_type, count in result['entity_counts'].items():
                entity_type_counts[entity_type] += count
            
            confidence_scores.extend([e['confidence'] for e in result['entities']])
        
        return {
            'total_texts': len(texts),
            'total_entities': total_entities,
            'average_entities_per_text': total_entities / len(texts) if texts else 0,
            'entity_type_distribution': dict(entity_type_counts),
            'average_confidence': np.mean(confidence_scores) if confidence_scores else 0,
            'confidence_std': np.std(confidence_scores) if confidence_scores else 0,
            'min_confidence': min(confidence_scores) if confidence_scores else 0,
            'max_confidence': max(confidence_scores) if confidence_scores else 0
        }


def main():
    """
    Example usage of the improved Italian Medical NER
    """
    # Initialize improved model
    ner_model = ImprovedItalianMedicalNER(confidence_threshold=0.6)
    
    # Example Italian medical text
    sample_texts = [
        "Il paziente ha lamentato forti mal di testa e nausea che persistevano da due giorni.",
        "Per alleviare i sintomi, gli è stato prescritto il paracetamolo e riposo.",
        "È necessario eseguire un esame del sangue e una radiografia del torace.",
        "La terapia antibiotica è stata efficace nel trattamento dell'infezione.",
        "Il diabete del paziente è controllato con insulina e dieta appropriata.",
        "La gastroscopia ha rivelato un'ulcera gastrica che richiede trattamento medico."
    ]
    
    print("Improved Italian Medical NER Results:")
    print("=" * 50)
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\nExample {i}: {text}")
        result = ner_model.predict(text)
        
        print(f"Entities found: {result['total_entities']}")
        for entity in result['entities']:
            source_icon = "🤖" if entity['source'] == 'model' else "📝" if entity['source'] == 'pattern' else "📚"
            print(f"  {source_icon} {entity['text']} ({entity['label']}) [Conf: {entity['confidence']:.3f}]")
        
        if result['entity_counts']:
            print(f"  Distribution: {result['entity_counts']}")
    
    # Get overall statistics
    print("\n" + "=" * 50)
    print("OVERALL STATISTICS")
    print("=" * 50)
    
    stats = ner_model.get_entity_statistics(sample_texts)
    print(f"Total texts processed: {stats['total_texts']}")
    print(f"Total entities found: {stats['total_entities']}")
    print(f"Average entities per text: {stats['average_entities_per_text']:.1f}")
    print(f"Average confidence: {stats['average_confidence']:.3f}")
    print(f"Entity type distribution: {stats['entity_type_distribution']}")


if __name__ == "__main__":
    main()

