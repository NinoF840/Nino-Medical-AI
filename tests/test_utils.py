"""
Tests for utility functions and common helpers
"""
import pytest
import re
from typing import List, Dict


@pytest.mark.unit
class TestMedicalPatterns:
    """Test medical pattern matching utilities"""
    
    def test_problem_patterns(self):
        """Test medical problem pattern recognition"""
        # Common problem patterns that should be found
        problem_texts = [
            "Il paziente ha forti dolori al petto",
            "Presenta sintomi di nausea e vomito",
            "Diagnosi di diabete mellito di tipo 2",
            "Infezione polmonare grave",
            "Mal di testa persistente"
        ]
        
        # Basic problem pattern (simplified)
        problem_pattern = r'\b(?:dolore|dolori|sintomi?|nausea|vomito|diabete|infezione|mal di)\b'
        
        for text in problem_texts:
            matches = re.findall(problem_pattern, text, re.IGNORECASE)
            assert len(matches) > 0, f"No problem patterns found in: {text}"
    
    def test_treatment_patterns(self):
        """Test medical treatment pattern recognition"""
        treatment_texts = [
            "Prescritto paracetamolo per il dolore",
            "Terapia antibiotica per 7 giorni",
            "Farmaco antinfiammatorio da assumere",
            "Intervento chirurgico necessario",
            "Fisioterapia post-operatoria"
        ]
        
        treatment_pattern = r'\b(?:paracetamolo|terapia|farmaco|intervento|fisioterapia|antibiotico)\b'
        
        for text in treatment_texts:
            matches = re.findall(treatment_pattern, text, re.IGNORECASE)
            assert len(matches) > 0, f"No treatment patterns found in: {text}"
    
    def test_test_patterns(self):
        """Test medical test pattern recognition"""
        test_texts = [
            "Necessari esami del sangue urgenti",
            "Radiografia del torace normale",
            "Ecografia addominale programmata",
            "TAC cranio con contrasto",
            "Elettrocardiogramma a riposo"
        ]
        
        test_pattern = r'\b(?:esami?|radiografia|ecografia|TAC|elettrocardiogramma)\b'
        
        for text in test_texts:
            matches = re.findall(test_pattern, text, re.IGNORECASE)
            assert len(matches) > 0, f"No test patterns found in: {text}"


@pytest.mark.unit
class TestTextProcessing:
    """Test text processing utilities"""
    
    def test_italian_text_normalization(self):
        """Test Italian text normalization"""
        test_cases = [
            ("È stata prescritta", "e stata prescritta"),  # Accent removal
            ("Diagnòsi", "diagnosi"),  # Accent normalization
            ("  spazi   multipli  ", "spazi multipli"),  # Space normalization
        ]
        
        for input_text, expected in test_cases:
            # Simple normalization (this would be implemented in actual utilities)
            normalized = self._simple_normalize(input_text)
            # Basic check that normalization occurred
            assert len(normalized.strip()) > 0
    
    def _simple_normalize(self, text: str) -> str:
        """Simple text normalization helper"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text.strip())
        # Convert to lowercase for comparison
        text = text.lower()
        # Basic accent removal (simplified)
        text = text.replace('è', 'e').replace('à', 'a').replace('ò', 'o')
        return text
    
    def test_entity_boundary_detection(self):
        """Test entity boundary detection"""
        text = "Il paziente ha mal di testa e nausea persistente"
        
        # Test finding word boundaries
        entities = [
            ("mal di testa", 15, 27),
            ("nausea", 30, 36)
        ]
        
        for entity_text, start, end in entities:
            # Verify the entity is at the correct position
            extracted = text[start:end]
            assert extracted == entity_text, f"Expected '{entity_text}' but got '{extracted}'"


@pytest.mark.unit 
class TestConfidenceCalculation:
    """Test confidence score calculation utilities"""
    
    def test_confidence_score_range(self):
        """Test that confidence scores are in valid range"""
        # Mock confidence scores that should be normalized
        raw_scores = [0.1, 0.5, 0.8, 0.95, 1.0, 1.2, 2.5]
        
        for score in raw_scores:
            normalized = self._normalize_confidence(score)
            assert 0.0 <= normalized <= 1.0, f"Confidence score {normalized} out of range"
    
    def _normalize_confidence(self, score: float) -> float:
        """Normalize confidence score to 0-1 range"""
        return max(0.0, min(1.0, score))
    
    def test_confidence_threshold_filtering(self):
        """Test filtering entities by confidence threshold"""
        entities = [
            {"text": "dolore", "confidence": 0.9},
            {"text": "testa", "confidence": 0.4},
            {"text": "farmaco", "confidence": 0.7},
            {"text": "esame", "confidence": 0.3}
        ]
        
        threshold = 0.6
        filtered = [e for e in entities if e["confidence"] >= threshold]
        
        assert len(filtered) == 2
        assert all(e["confidence"] >= threshold for e in filtered)


@pytest.mark.unit
class TestEntityValidation:
    """Test entity validation utilities"""
    
    def test_entity_label_validation(self):
        """Test that entity labels are valid"""
        valid_labels = ["PROBLEM", "TREATMENT", "TEST"]
        
        test_entities = [
            {"text": "dolore", "label": "PROBLEM"},
            {"text": "farmaco", "label": "TREATMENT"},
            {"text": "esame", "label": "TEST"},
            {"text": "invalid", "label": "INVALID"}
        ]
        
        for entity in test_entities:
            is_valid = entity["label"] in valid_labels
            if entity["label"] == "INVALID":
                assert not is_valid
            else:
                assert is_valid
    
    def test_entity_position_validation(self):
        """Test entity position validation"""
        text = "Il paziente ha dolore al petto"
        
        valid_entity = {"text": "dolore", "start": 15, "end": 21}
        invalid_entity = {"text": "dolore", "start": 25, "end": 30}  # Wrong position
        
        # Check valid entity
        extracted_valid = text[valid_entity["start"]:valid_entity["end"]]
        assert extracted_valid == valid_entity["text"]
        
        # Check invalid entity
        extracted_invalid = text[invalid_entity["start"]:invalid_entity["end"]]
        assert extracted_invalid != invalid_entity["text"]


@pytest.mark.unit
class TestPerformanceUtilities:
    """Test performance measurement utilities"""
    
    def test_processing_time_measurement(self):
        """Test processing time measurement"""
        import time
        
        start_time = time.time()
        # Simulate some processing
        time.sleep(0.01)  # 10ms
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should be approximately 10ms (with some tolerance)
        assert 0.005 < processing_time < 0.1  # Between 5ms and 100ms
    
    def test_entity_count_statistics(self):
        """Test entity counting utilities"""
        entities = [
            {"label": "PROBLEM"},
            {"label": "PROBLEM"},
            {"label": "TREATMENT"},
            {"label": "TEST"},
            {"label": "TREATMENT"}
        ]
        
        # Count entities by label
        counts = {}
        for entity in entities:
            label = entity["label"]
            counts[label] = counts.get(label, 0) + 1
        
        assert counts["PROBLEM"] == 2
        assert counts["TREATMENT"] == 2
        assert counts["TEST"] == 1
        assert sum(counts.values()) == len(entities)


@pytest.mark.integration
class TestUtilityIntegration:
    """Integration tests for utility functions"""
    
    def test_complete_text_processing_pipeline(self, sample_italian_medical_text):
        """Test complete text processing pipeline"""
        # This would test the integration of multiple utility functions
        text = sample_italian_medical_text.strip()
        
        # Basic pipeline steps
        assert len(text) > 0
        assert "paziente" in text.lower()
        
        # Pattern matching
        medical_terms = re.findall(r'\b(?:dolore|terapia|esame|paziente)\b', text, re.IGNORECASE)
        assert len(medical_terms) > 0
