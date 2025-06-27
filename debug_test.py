import re
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _extract_medical_entities_basic(text):
    """
    Basic medical entity extraction using pattern matching
    This is a simplified version that works without the full NER model
    """
    # Medical patterns (simplified version of your working patterns)
    medical_patterns = {
        'PROBLEM': [
            r'\b(dolori?|dolore)\b.*?\b(al|alla|alle|agli|dei|delle|del)\b.*?\b(petto|torace|addome|testa|gola)\b',
            r'\b(febbre|tosse|nausea|vomito|diarrea|stitichezza)\b',
            r'\b(difficoltà|problemi)\b.*?\b(respiratorie?|respiratori?|respiro)\b',
            r'\b(infezione|infiammazione)\b.*?\b(polmonare|respiratoria|vie respiratorie)\b',
            r'\b(mal di)\b.*?\b(testa|gola|pancia|schiena)\b'
        ],
        'PERSON': [
            r'\b(paziente|malato|cliente)\b',
            r'\bsignor[ea]?\s+[A-Z][a-z]+\b'
        ],
        'TREATMENT': [
            r'\b(antibiotici?|medicina|farmaci?|medicinali?)\b',
            r'\b(terapia|cura|trattamento)\b',
            r'\b(prescriv\w+|somministr\w+)\b',
            r'\b(amoxicillina|paracetamolo|ibuprofene)\b'
        ],
        'TEST': [
            r'\b(radiografia|analisi|esame|test)\b',
            r'\b(laboratorio|clinico)\b'
        ],
        'DIAGNOSIS': [
            r'\b(diagnosi)\b'
        ]
    }
    
    entities = []
    text_lower = text.lower()
    
    for label, patterns in medical_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                entity = {
                    'text': text[match.start():match.end()],
                    'label': label,
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.85  # Default confidence for pattern matching
                }
                entities.append(entity)
    
    return entities

# Test text from the failing test
test_text = """
Il paziente di 65 anni presenta dolori al petto e difficoltà respiratorie. 
La diagnosi indica una possibile infezione polmonare che richiede antibiotici.
È stata prescritta una radiografia del torace per confermare la diagnosi.
"""

print("Test text:")
print(test_text)
print("\nExtracting entities...")

entities = _extract_medical_entities_basic(test_text)

print(f"\nFound {len(entities)} entities:")
for i, entity in enumerate(entities):
    print(f"{i+1}. Text: '{entity['text']}', Label: {entity['label']}, Start: {entity['start']}, End: {entity['end']}")

print("\nEntity texts for debugging:")
entity_texts = [entity['text'] for entity in entities]
for text in entity_texts:
    print(f"  - '{text}' (lower: '{text.lower()}')")

print("\nChecking for specific terms:")
print(f"Has 'paziente': {any('paziente' in text.lower() for text in entity_texts)}")
print(f"Has 'dolori': {any('dolori' in text.lower() for text in entity_texts)}")
print(f"Has 'diagnosi': {any('diagnosi' in text.lower() for text in entity_texts)}")
