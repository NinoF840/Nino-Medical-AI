"""
AssemblyAI + Italian Medical NER Integration Tests
Tests the combined functionality of speech-to-text and medical entity recognition
"""
import pytest
import assemblyai as aai
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_inference import EnhancedItalianMedicalNER
    from utils import MedicalPatterns, confidence_score, validate_entity
except ImportError:
    # Handle case where modules might not be available
    EnhancedItalianMedicalNER = None
    MedicalPatterns = None


class TestAssemblyAINERIntegration:
    """Test integration between AssemblyAI and Italian Medical NER"""
    
    def setup_method(self):
        """Set up test environment"""
        self.api_key = "987de64ccb5a4c098d90d42e50de8731"
        aai.settings.api_key = self.api_key
    
    @pytest.mark.unit
    @patch('assemblyai.Transcriber')
    def test_full_audio_to_ner_pipeline_mock(self, mock_transcriber):
        """Test complete pipeline from audio transcription to NER analysis (mocked)"""
        # Mock AssemblyAI transcription
        mock_instance = Mock()
        mock_transcript = Mock()
        mock_transcript.text = """
        Il paziente di 65 anni presenta dolori al petto e difficoltà respiratorie. 
        La diagnosi indica una possibile infezione polmonare che richiede antibiotici.
        È stata prescritta una radiografia del torace per confermare la diagnosi.
        """
        mock_transcript.status = "completed"
        mock_transcript.confidence = 0.92
        
        mock_instance.transcribe.return_value = mock_transcript
        mock_transcriber.return_value = mock_instance
        
        # Step 1: Transcribe audio (mocked)
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(language_code="it")
        transcript_result = transcriber.transcribe("mock_medical_audio.wav", config=config)
        
        # Step 2: Process transcript text for NER
        transcript_text = transcript_result.text.strip()
        
        # Step 3: Apply basic medical entity extraction (using patterns from your working utils)
        medical_entities = self._extract_medical_entities_basic(transcript_text)
        
        # Assertions
        assert transcript_result.status == "completed"
        assert transcript_result.confidence == 0.92
        assert len(transcript_text) > 0
        assert len(medical_entities) > 0
        
        # Check for expected medical entities
        entity_texts = [entity['text'] for entity in medical_entities]
        assert any('paziente' in text.lower() for text in entity_texts)
        assert any('dolori' in text.lower() for text in entity_texts)
        assert any('diagnosi' in text.lower() for text in entity_texts)
    
    @pytest.mark.unit
    def test_medical_entity_extraction_from_transcript(self):
        """Test medical entity extraction from transcript text"""
        transcript_text = """
        Il paziente presenta febbre alta, tosse persistente e mal di gola.
        La diagnosi preliminare suggerisce un'infezione delle vie respiratorie.
        È stata prescritta una terapia antibiotica con amoxicillina.
        """
        
        entities = self._extract_medical_entities_basic(transcript_text)
        
        assert len(entities) > 0
        
        # Check for medical terms
        entity_texts = [entity['text'].lower() for entity in entities]
        expected_terms = ['paziente', 'febbre', 'tosse', 'diagnosi', 'infezione', 'terapia', 'antibiotica']
        
        found_terms = []
        for term in expected_terms:
            if any(term in text for text in entity_texts):
                found_terms.append(term)
        
        assert len(found_terms) >= 3, f"Expected at least 3 medical terms, found: {found_terms}"
    
    @pytest.mark.unit
    @pytest.mark.skipif(EnhancedItalianMedicalNER is None, reason="EnhancedItalianMedicalNER not available")
    @patch('enhanced_inference.EnhancedItalianMedicalNER')
    def test_enhanced_ner_integration_mock(self, mock_ner_class):
        """Test integration with EnhancedItalianMedicalNER (mocked)"""
        # Mock the NER model
        mock_ner_instance = Mock()
        mock_ner_instance.predict.return_value = [
            {'text': 'paziente', 'label': 'PERSON', 'start': 3, 'end': 11, 'confidence': 0.95},
            {'text': 'dolori al petto', 'label': 'PROBLEM', 'start': 21, 'end': 36, 'confidence': 0.88},
            {'text': 'infezione polmonare', 'label': 'PROBLEM', 'start': 89, 'end': 108, 'confidence': 0.92},
            {'text': 'antibiotici', 'label': 'TREATMENT', 'start': 127, 'end': 138, 'confidence': 0.85}
        ]
        mock_ner_class.return_value = mock_ner_instance
        
        # Simulate transcript text
        transcript_text = "Il paziente presenta dolori al petto. La diagnosi indica una possibile infezione polmonare che richiede antibiotici."
        
        # Initialize NER model (mocked)
        ner_model = mock_ner_class()
        
        # Apply NER to transcript
        entities = ner_model.predict(transcript_text)
        
        # Verify results
        assert len(entities) == 4
        assert entities[0]['label'] == 'PERSON'
        assert entities[1]['label'] == 'PROBLEM'
        assert entities[2]['label'] == 'PROBLEM'
        assert entities[3]['label'] == 'TREATMENT'
        
        # Check confidence scores
        for entity in entities:
            assert entity['confidence'] > 0.8
    
    @pytest.mark.unit
    @patch('assemblyai.Transcriber')
    def test_multi_speaker_medical_conversation(self, mock_transcriber):
        """Test processing multi-speaker medical conversation"""
        mock_instance = Mock()
        mock_transcript = Mock()
        mock_transcript.text = """
        Dottore: Come si sente oggi, signor Rossi?
        Paziente: Ho ancora dolori al petto e difficoltà a respirare.
        Dottore: La radiografia mostra un'infiammazione polmonare. Prescriverò degli antibiotici.
        Paziente: Quanto tempo dovrò prendere la medicina?
        Dottore: La terapia durerà una settimana.
        """
        mock_transcript.speakers = [
            {"speaker": "A", "text": "Come si sente oggi, signor Rossi?"},
            {"speaker": "B", "text": "Ho ancora dolori al petto e difficoltà a respirare."},
            {"speaker": "A", "text": "La radiografia mostra un'infiammazione polmonare. Prescriverò degli antibiotici."},
            {"speaker": "B", "text": "Quanto tempo dovrò prendere la medicina?"},
            {"speaker": "A", "text": "La terapia durerà una settimana."}
        ]
        mock_transcript.status = "completed"
        
        mock_instance.transcribe.return_value = mock_transcript
        mock_transcriber.return_value = mock_instance
        
        # Transcribe with speaker separation
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(
            language_code="it",
            speaker_labels=True
        )
        result = transcriber.transcribe("doctor_patient_conversation.wav", config=config)
        
        # Process each speaker's text separately
        doctor_text = []
        patient_text = []
        
        for segment in result.speakers:
            if segment["speaker"] == "A":  # Assuming A is doctor
                doctor_text.append(segment["text"])
            else:  # B is patient
                patient_text.append(segment["text"])
        
        # Extract entities from each speaker
        doctor_entities = self._extract_medical_entities_basic(" ".join(doctor_text))
        patient_entities = self._extract_medical_entities_basic(" ".join(patient_text))
        
        # Verify extraction
        assert len(doctor_entities) > 0
        assert len(patient_entities) > 0
        
        # Doctor should mention medical terms like diagnosi, terapia
        doctor_terms = [e['text'].lower() for e in doctor_entities]
        assert any('radiografia' in term or 'antibiotici' in term or 'terapia' in term for term in doctor_terms)
        
        # Patient should mention symptoms
        patient_terms = [e['text'].lower() for e in patient_entities]
        assert any('dolori' in term or 'difficoltà' in term for term in patient_terms)
    
    @pytest.mark.unit
    def test_confidence_filtering_integration(self):
        """Test filtering low-confidence entities from transcript analysis"""
        transcript_text = "Il paziente ha la febbre e tosse. Possibile influenza."
        
        # Simulate entities with different confidence scores
        mock_entities = [
            {'text': 'paziente', 'label': 'PERSON', 'confidence': 0.95},
            {'text': 'febbre', 'label': 'PROBLEM', 'confidence': 0.88},
            {'text': 'tosse', 'label': 'PROBLEM', 'confidence': 0.92},
            {'text': 'influenza', 'label': 'PROBLEM', 'confidence': 0.65}  # Low confidence
        ]
        
        # Filter entities by confidence threshold
        high_confidence_entities = [e for e in mock_entities if e['confidence'] >= 0.8]
        
        assert len(high_confidence_entities) == 3
        assert all(e['confidence'] >= 0.8 for e in high_confidence_entities)
        
        # The low-confidence 'influenza' should be filtered out
        entity_texts = [e['text'] for e in high_confidence_entities]
        assert 'influenza' not in entity_texts
        assert 'paziente' in entity_texts
        assert 'febbre' in entity_texts
        assert 'tosse' in entity_texts
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires actual API call and audio file")
    def test_real_audio_to_ner_pipeline(self):
        """Test complete pipeline with real audio file - skipped by default"""
        # This would test the complete pipeline with a real audio file
        """
        # Step 1: Real transcription
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(language_code="it")
        result = transcriber.transcribe("path/to/real_italian_medical_audio.wav", config=config)
        
        # Step 2: Real NER processing
        if EnhancedItalianMedicalNER:
            ner_model = EnhancedItalianMedicalNER()
            entities = ner_model.predict(result.text)
            
            assert result.status == "completed"
            assert len(entities) > 0
        """
        pass
    
    def _extract_medical_entities_basic(self, text):
        """
        Basic medical entity extraction using pattern matching
        This is a simplified version that works without the full NER model
        """
        import re
        
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


class TestAudioProcessingUtilities:
    """Test utilities for audio processing and preparation"""
    
    @pytest.mark.unit
    def test_supported_audio_formats(self):
        """Test checking supported audio formats for AssemblyAI"""
        supported_formats = ['.wav', '.mp3', '.mp4', '.m4a', '.flac', '.aac']
        
        test_files = [
            'audio.wav',
            'recording.mp3', 
            'interview.mp4',
            'conversation.m4a',
            'medical_record.flac',
            'voice_note.aac',
            'document.txt'  # Should not be supported
        ]
        
        def is_supported_audio_format(filename):
            import os
            _, ext = os.path.splitext(filename.lower())
            return ext in supported_formats
        
        supported_files = [f for f in test_files if is_supported_audio_format(f)]
        
        assert len(supported_files) == 6  # All except .txt
        assert 'document.txt' not in supported_files
        assert 'audio.wav' in supported_files
        assert 'recording.mp3' in supported_files
    
    @pytest.mark.unit
    def test_transcript_text_preprocessing(self):
        """Test preprocessing transcript text for better NER results"""
        raw_transcript = """
        ehm... il paziente, uh, presenta dolori al petto... e, uh, difficoltà respiratorie.
        La diagnosi... ehm... indica una possibile infezione polmonare.
        """
        
        def preprocess_transcript(text):
            import re
            # Remove filler words and hesitations
            text = re.sub(r'\b(ehm|uh|um|ah)\b', '', text, flags=re.IGNORECASE)
            # Clean up multiple dots
            text = re.sub(r'\.{2,}', '.', text)
            # Remove orphaned commas after filler word removal
            text = re.sub(r',\s*,', ',', text)
            text = re.sub(r'\s*,\s*([.!?])', r'\1', text)  # Remove commas before punctuation
            text = re.sub(r'^\s*,\s*', '', text)  # Remove leading commas
            text = re.sub(r'\s*,\s*$', '', text)  # Remove trailing commas
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        
        cleaned = preprocess_transcript(raw_transcript)
        
        assert 'ehm' not in cleaned.lower()
        assert 'uh' not in cleaned.lower()
        assert '...' not in cleaned
        assert 'il paziente presenta dolori al petto' in cleaned
        assert 'La diagnosi indica una possibile infezione polmonare' in cleaned
