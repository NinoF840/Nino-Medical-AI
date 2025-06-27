#!/usr/bin/env python3
"""
Nino's Italian Medical NER - Comprehensive Demo
===============================================

This demo showcases the core functionality of the Italian Medical NER system
without external dependencies like AssemblyAI. It demonstrates:

1. Enhanced Medical NER with pattern matching
2. Confidence scoring and filtering
3. Multi-text batch processing
4. Performance metrics
5. Entity validation and post-processing
"""

import time
import re
from typing import List, Dict, Tuple
from collections import Counter, defaultdict

# Try to import our enhanced models, with fallbacks
try:
    from enhanced_inference import EnhancedItalianMedicalNER
    ENHANCED_MODEL_AVAILABLE = True
except ImportError:
    ENHANCED_MODEL_AVAILABLE = False
    print("Enhanced model not available, using pattern-based fallback")

class MedicalPatternNER:
    """
    Fallback pattern-based medical NER for when models aren't available
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.medical_patterns = self._load_medical_patterns()
    
    def _load_medical_patterns(self) -> Dict[str, List[str]]:
        """Load comprehensive Italian medical patterns"""
        return {
            'PROBLEM': [
                r'\b(?:forti?\s+)?(?:mal\s+di\s+(?:testa|stomaco|schiena|gola|petto))\b',
                r'\b(?:dolore|dolori)\s+(?:al|alla|alle|ai|degli?|delle?)\s+\w+\b',
                r'\b(?:nausea|vomito)\s+(?:persistente|continua|ricorrente|improvvisa)\b',
                r'\b(?:febbre|temperatura)\s+(?:alta|elevata|superiore)\b',
                r'\b(?:dolore|dolori|mal|nausea|vomito|febbre|tosse)\b',
                r'\b(?:diabete|ipertensione|ipotensione|infezione|allergia)\b',
                r'\b(?:tumore|cancro|carcinoma|neoplasia)\b',
                r'\b(?:aritmia|tachicardia|bradicardia|angina|ictus|infarto)\b',
                r'\b(?:ulcera|gastrite|cistite|prostatite|sinusite|otite)\b',
                r'\b(?:artrite|artrosi|asma|bronchite|polmonite|anemia)\b',
                r'\b(?:sintomi?|manifestazioni?|segni)\s+(?:di\s+\w+)?\b',
                r'\b(?:difficoltà|problemi)\s+(?:respiratori?|respiratorie?)\b',
                r'\b(?:infezione|infiammazione)\s+(?:polmonare|respiratoria)\b'
            ],
            'TREATMENT': [
                r'\b(?:paracetamolo|acetaminofene|tachipirina|efferalgan)\b',
                r'\b(?:ibuprofene|moment|brufen|nurofen|arfen)\b',
                r'\b(?:aspirina|cardioaspirina|aspirinetta)\b',
                r'\b(?:antibiotico|antibiotici|amoxicillina|azitromicina)\b',
                r'\b(?:insulina|metformina|enalapril|amlodipina)\b',
                r'\b(?:cortisone|prednisone|betametasone|diclofenac)\b',
                r'\b(?:terapia|terapie|trattamento|trattamenti|cura|cure)\b',
                r'\b(?:farmaco|farmaci|medicina|medicine|medicinale)\b',
                r'\b(?:antidolorifico|analgesico|antinfiammatorio)\b',
                r'\b(?:fisioterapia|riabilitazione|fisioterapica)\b',
                r'\b(?:chemioterapia|radioterapia|immunoterapia)\b',
                r'\b(?:intervento|operazione|chirurgia|dialisi|trapianto)\b',
                r'\b(?:prescritto|somministrato|assunto|iniettato)\b',
                r'\b(?:efficace|migliorato|alleviare|ridurre|guarire)\b'
            ],
            'TEST': [
                r'\b(?:esame|analisi|controllo)\s+(?:del\s+)?(?:sangue|urine|feci)\b',
                r'\b(?:emocromo|emocromocitometrico|formula\s+leucocitaria)\b',
                r'\b(?:glicemia|colesterolo|trigliceridi|creatinina|urea)\b',
                r'\b(?:transaminasi|ALT|AST|gamma\s*GT|bilirubina)\b',
                r'\b(?:radiografia|RX|raggi\s+X|lastra)\s*(?:del\s+torace)?\b',
                r'\b(?:ecografia|ultrasuoni|eco|ecocardiografia)\b',
                r'\b(?:TAC|TC|tomografia\s+computerizzata)\b',
                r'\b(?:risonanza\s+magnetica|RM|RMN|risonanza)\b',
                r'\b(?:elettrocardiogramma|ECG|EKG|tracciato)\b',
                r'\b(?:ecocardiogramma|ecocardiografia)\b',
                r'\b(?:gastroscopia|EGDS|esofagogastroduodenoscopia)\b',
                r'\b(?:colonscopia|rettoscopia|sigmoidoscopia)\b',
                r'\b(?:biopsia|agoaspirato|prelievo|campione)\b',
                r'\b(?:esame|esami|test|analisi|controllo|controlli)\b',
                r'\b(?:visita|visite|consultazione|check\s*up)\b',
                r'\b(?:necessario|necessita|eseguire|immediatamente)\b',
                r'\b(?:mostra|rivela|evidenzia|conferma|confermato)\b'
            ],
            'PERSON': [
                r'\b(?:paziente|malato|cliente)\b',
                r'\bsignor[ea]?\s+[A-Z][a-z]+\b',
                r'\b(?:dottore|medico|specialista|cardiologo|neurologo)\b'
            ]
        }
    
    def predict(self, text: str) -> Dict:
        """Extract medical entities using pattern matching"""
        entities = []
        text_lower = text.lower()
        
        for label, patterns in self.medical_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Calculate confidence based on pattern specificity
                    confidence = 0.85 if len(match.group()) > 5 else 0.75
                    
                    entity = {
                        'text': match.group(),
                        'label': label,
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': confidence
                    }
                    entities.append(entity)
        
        # Remove duplicates and filter by confidence
        unique_entities = []
        seen = set()
        
        for entity in entities:
            key = (entity['text'].lower(), entity['label'], entity['start'])
            if key not in seen and entity['confidence'] >= self.confidence_threshold:
                unique_entities.append(entity)
                seen.add(key)
        
        return {
            'text': text,
            'entities': unique_entities,
            'entity_count': len(unique_entities)
        }

class MedicalNERDemo:
    """Comprehensive demo class for Italian Medical NER"""
    
    def __init__(self):
        print("🏥 Initializing Nino's Italian Medical NER Demo...")
        
        # Initialize the best available model
        if ENHANCED_MODEL_AVAILABLE:
            try:
                print("✅ Loading Enhanced Italian Medical NER model...")
                self.ner_model = EnhancedItalianMedicalNER(confidence_threshold=0.6)
                self.model_type = "Enhanced Model"
            except Exception as e:
                print(f"⚠️  Enhanced model failed to load: {e}")
                print("🔄 Falling back to pattern-based NER...")
                self.ner_model = MedicalPatternNER(confidence_threshold=0.7)
                self.model_type = "Pattern-Based Model"
        else:
            print("🔄 Using pattern-based NER...")
            self.ner_model = MedicalPatternNER(confidence_threshold=0.7)
            self.model_type = "Pattern-Based Model"
        
        print(f"✅ Model initialized: {self.model_type}")
    
    def demo_single_text(self, text: str) -> Dict:
        """Demo with a single medical text"""
        print(f"\n📝 Analyzing: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
        
        start_time = time.time()
        result = self.ner_model.predict(text)
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.3f} seconds")
        print(f"🔍 Found {len(result['entities'])} entities:")
        
        for i, entity in enumerate(result['entities'], 1):
            print(f"   {i}. '{entity['text']}' → {entity['label']} (confidence: {entity['confidence']:.2f})")
        
        return result
    
    def demo_batch_processing(self, texts: List[str]) -> List[Dict]:
        """Demo batch processing of multiple texts"""
        print(f"\n📚 Processing {len(texts)} texts in batch...")
        
        start_time = time.time()
        results = []
        
        for i, text in enumerate(texts, 1):
            print(f"   Processing text {i}/{len(texts)}...")
            result = self.ner_model.predict(text)
            results.append(result)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        total_entities = sum(len(r['entities']) for r in results)
        avg_entities = total_entities / len(texts) if texts else 0
        avg_time = total_time / len(texts) if texts else 0
        
        print(f"\n📊 Batch Processing Statistics:")
        print(f"   Total entities found: {total_entities}")
        print(f"   Average entities per text: {avg_entities:.1f}")
        print(f"   Total processing time: {total_time:.3f} seconds")
        print(f"   Average time per text: {avg_time:.3f} seconds")
        
        return results
    
    def demo_entity_analysis(self, results: List[Dict]) -> Dict:
        """Analyze entities across multiple results"""
        print(f"\n🔬 Entity Analysis across {len(results)} texts:")
        
        # Collect all entities
        all_entities = []
        for result in results:
            all_entities.extend(result['entities'])
        
        # Count by label
        label_counts = Counter(entity['label'] for entity in all_entities)
        
        # Find most common entities by text
        entity_texts = Counter(entity['text'].lower() for entity in all_entities)
        
        # Calculate confidence statistics
        confidences = [entity['confidence'] for entity in all_entities]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        min_confidence = min(confidences) if confidences else 0
        max_confidence = max(confidences) if confidences else 0
        
        print(f"   📈 Entity Types:")
        for label, count in label_counts.most_common():
            print(f"      {label}: {count} entities")
        
        print(f"   🎯 Most Common Terms:")
        for text, count in entity_texts.most_common(5):
            print(f"      '{text}': {count} occurrences")
        
        print(f"   📊 Confidence Statistics:")
        print(f"      Average: {avg_confidence:.3f}")
        print(f"      Range: {min_confidence:.3f} - {max_confidence:.3f}")
        
        return {
            'total_entities': len(all_entities),
            'label_counts': dict(label_counts),
            'entity_texts': dict(entity_texts),
            'avg_confidence': avg_confidence,
            'confidence_range': (min_confidence, max_confidence)
        }
    
    def run_comprehensive_demo(self):
        """Run the full comprehensive demo"""
        print("=" * 60)
        print("🏥 NINO'S ITALIAN MEDICAL NER - COMPREHENSIVE DEMO")
        print("=" * 60)
        
        # Sample Italian medical texts
        sample_texts = [
            "Il paziente di 65 anni presenta forti dolori al petto e difficoltà respiratorie acute.",
            "È stata prescritta una terapia con paracetamolo 1000mg tre volte al giorno per il mal di testa persistente.",
            "Necessari esami del sangue urgenti: emocromo completo, glicemia e creatinina.",
            "La radiografia del torace mostra un'infezione polmonare che richiede antibiotici.",
            "Il dottore ha programmato un elettrocardiogramma e un'ecografia cardiaca per valutare l'aritmia.",
            "La signora Rossi lamenta nausea e vomito dopo l'assunzione del nuovo farmaco antinfiammatorio.",
            "Intervento chirurgico necessario per rimuovere il tumore al fegato diagnosticato con la TAC.",
            "La fisioterapia post-operatoria ha mostrato risultati efficaci nella riabilitazione del paziente.",
            "Analisi delle urine positive per infezione delle vie urinarie, prescritti antibiotici specifici.",
            "Il controllo della glicemia evidenzia un peggioramento del diabete mellito di tipo 2."
        ]
        
        print(f"\n🎯 Model Type: {self.model_type}")
        
        # Demo 1: Single text analysis
        print("\n" + "="*50)
        print("DEMO 1: Single Text Analysis")
        print("="*50)
        
        sample_result = self.demo_single_text(sample_texts[0])
        
        # Demo 2: Batch processing
        print("\n" + "="*50)
        print("DEMO 2: Batch Processing")
        print("="*50)
        
        batch_results = self.demo_batch_processing(sample_texts[:5])
        
        # Demo 3: Entity analysis
        print("\n" + "="*50)
        print("DEMO 3: Entity Analysis")
        print("="*50)
        
        analysis = self.demo_entity_analysis(batch_results)
        
        # Demo 4: Performance test
        print("\n" + "="*50)
        print("DEMO 4: Performance Test")
        print("="*50)
        
        print(f"🚀 Processing all {len(sample_texts)} sample texts...")
        start_time = time.time()
        all_results = self.demo_batch_processing(sample_texts)
        total_time = time.time() - start_time
        
        final_analysis = self.demo_entity_analysis(all_results)
        
        print(f"\n🏆 FINAL RESULTS:")
        print(f"   ✅ Processed {len(sample_texts)} medical texts")
        print(f"   ✅ Extracted {final_analysis['total_entities']} medical entities")
        print(f"   ✅ Average confidence: {final_analysis['avg_confidence']:.3f}")
        print(f"   ✅ Total processing time: {total_time:.3f} seconds")
        print(f"   ✅ Throughput: {len(sample_texts)/total_time:.1f} texts/second")
        
        print("\n" + "="*60)
        print("🎉 Demo completed successfully! 🎉")
        print("="*60)
        
        return {
            'model_type': self.model_type,
            'total_texts': len(sample_texts),
            'total_entities': final_analysis['total_entities'],
            'processing_time': total_time,
            'analysis': final_analysis
        }

def main():
    """Main function to run the demo"""
    try:
        demo = MedicalNERDemo()
        results = demo.run_comprehensive_demo()
        
        # Optional: Save results to file
        import json
        with open('nino_medical_ner_demo_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to 'nino_medical_ner_demo_results.json'")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
