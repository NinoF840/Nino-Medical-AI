"""
Standalone AssemblyAI Tests
Tests AssemblyAI functionality independently
"""
import pytest
import assemblyai as aai
from unittest.mock import Mock, patch
import json


class TestAssemblyAIStandalone:
    """Test AssemblyAI standalone functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        # Use your actual API key for real tests
        self.api_key = "987de64ccb5a4c098d90d42e50de8731"
        aai.settings.api_key = self.api_key
    
    @pytest.mark.unit
    def test_api_key_setting(self):
        """Test that API key is properly set"""
        aai.settings.api_key = self.api_key
        assert aai.settings.api_key == self.api_key
    
    @pytest.mark.unit
    @patch('assemblyai.Transcriber')
    def test_transcriber_initialization(self, mock_transcriber):
        """Test transcriber initialization"""
        mock_instance = Mock()
        mock_transcriber.return_value = mock_instance
        
        transcriber = aai.Transcriber()
        
        assert transcriber is not None
        mock_transcriber.assert_called_once()
    
    @pytest.mark.unit
    @patch('assemblyai.Transcriber')
    def test_transcribe_with_mock_audio(self, mock_transcriber):
        """Test transcription with mock audio file"""
        # Mock transcriber and transcript
        mock_instance = Mock()
        mock_transcript = Mock()
        mock_transcript.text = "Il paziente presenta dolori al petto e difficoltà respiratorie."
        mock_transcript.status = "completed"
        mock_transcript.id = "test_transcript_id"
        
        mock_instance.transcribe.return_value = mock_transcript
        mock_transcriber.return_value = mock_instance
        
        transcriber = aai.Transcriber()
        result = transcriber.transcribe("mock_audio_file.wav")
        
        assert result.text == "Il paziente presenta dolori al petto e difficoltà respiratorie."
        assert result.status == "completed"
        assert result.id == "test_transcript_id"
        mock_instance.transcribe.assert_called_once_with("mock_audio_file.wav")
    
    @pytest.mark.unit
    @patch('assemblyai.Transcriber')
    def test_transcribe_with_italian_medical_content(self, mock_transcriber):
        """Test transcription with Italian medical content"""
        mock_instance = Mock()
        mock_transcript = Mock()
        mock_transcript.text = """
        Il paziente di 65 anni presenta una storia clinica di diabete mellito di tipo 2, 
        ipertensione arteriosa e dislipidemia. Durante l'esame obiettivo si rileva 
        tachicardia e dispnea da sforzo. Gli esami di laboratorio mostrano 
        glicemia elevata e colesterolo alto.
        """
        mock_transcript.status = "completed"
        mock_transcript.confidence = 0.89
        
        mock_instance.transcribe.return_value = mock_transcript
        mock_transcriber.return_value = mock_instance
        
        transcriber = aai.Transcriber()
        result = transcriber.transcribe("italian_medical_audio.mp3")
        
        assert "diabete mellito" in result.text
        assert "ipertensione" in result.text
        assert "tachicardia" in result.text
        assert result.status == "completed"
        assert result.confidence == 0.89
    
    @pytest.mark.unit
    def test_transcription_config(self):
        """Test transcription configuration options"""
        config = aai.TranscriptionConfig(
            language_code="it",  # Italian
            punctuate=True,
            format_text=True,
            speaker_labels=True
        )
        
        assert config.language_code == "it"
        assert config.punctuate is True
        assert config.format_text is True
        assert config.speaker_labels is True
    
    @pytest.mark.unit
    @patch('assemblyai.Transcriber')
    def test_transcribe_with_config(self, mock_transcriber):
        """Test transcription with custom configuration"""
        mock_instance = Mock()
        mock_transcript = Mock()
        mock_transcript.text = "Il paziente ha la febbre alta."
        mock_transcript.speakers = [
            {"speaker": "A", "text": "Il paziente"},
            {"speaker": "B", "text": "ha la febbre alta"}
        ]
        
        mock_instance.transcribe.return_value = mock_transcript
        mock_transcriber.return_value = mock_instance
        
        config = aai.TranscriptionConfig(
            language_code="it",
            speaker_labels=True
        )
        
        transcriber = aai.Transcriber()
        result = transcriber.transcribe("audio.wav", config=config)
        
        assert result.text == "Il paziente ha la febbre alta."
        assert hasattr(result, 'speakers')
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires actual API call and audio file")
    def test_real_transcription(self):
        """Test real transcription - skipped by default"""
        # This test would require a real audio file and API call
        # Uncomment and provide a real audio file path to test
        """
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(language_code="it")
        
        # Replace with actual audio file path
        # result = transcriber.transcribe("path/to/italian_medical_audio.wav", config=config)
        # assert result.status == "completed"
        # assert len(result.text) > 0
        """
        pass
    
    @pytest.mark.unit
    def test_transcription_config_validation(self):
        """Test validation of transcription configuration"""
        # Test that TranscriptionConfig accepts valid parameters
        config = aai.TranscriptionConfig(
            language_code="it",
            punctuate=True,
            format_text=True,
            speaker_labels=False
        )
        
        # Verify the configuration was set correctly
        assert config.language_code == "it"
        assert config.punctuate is True
        assert config.format_text is True
        # speaker_labels=False sets it to None in AssemblyAI
        assert config.speaker_labels in [False, None]
        
        # Test with different settings
        config2 = aai.TranscriptionConfig(
            language_code="en",
            speaker_labels=True
        )
        
        assert config2.language_code == "en"
        assert config2.speaker_labels is True


class TestAssemblyAIUtilities:
    """Test utility functions for AssemblyAI integration"""
    
    @pytest.mark.unit
    def test_format_transcript_for_ner(self):
        """Test formatting transcript text for NER processing"""
        raw_transcript = """
        Il paziente, di 65 anni, presenta dolori al petto... 
        La diagnosi indica una possibile infezione polmonare.
        """
        
        # Simple text cleaning function
        def clean_transcript_text(text):
            # Remove extra whitespace and normalize
            import re
            text = re.sub(r'\s+', ' ', text.strip())
            text = re.sub(r'\.{3,}', '.', text)  # Replace ... with .
            return text
        
        cleaned = clean_transcript_text(raw_transcript)
        
        assert "Il paziente, di 65 anni, presenta dolori al petto." in cleaned
        assert "La diagnosi indica una possibile infezione polmonare." in cleaned
        assert "..." not in cleaned
    
    @pytest.mark.unit
    def test_extract_medical_segments(self):
        """Test extracting medical-relevant segments from transcript"""
        transcript_text = """
        Buongiorno dottore. Il paziente presenta dolori al petto e difficoltà respiratorie.
        Ieri ha mangiato una pizza. La diagnosi indica una possibile infezione polmonare.
        Che tempo fa oggi? È necessario prescrivere antibiotici.
        """
        
        # Simple medical keyword detection
        medical_keywords = [
            'paziente', 'dolori', 'petto', 'respiratorie', 'diagnosi', 
            'infezione', 'polmonare', 'antibiotici', 'sintomi', 'terapia'
        ]
        
        def extract_medical_sentences(text, keywords):
            sentences = text.split('.')
            medical_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if any(keyword in sentence.lower() for keyword in keywords):
                    medical_sentences.append(sentence)
            
            return medical_sentences
        
        medical_segments = extract_medical_sentences(transcript_text, medical_keywords)
        
        assert len(medical_segments) >= 3
        assert any("paziente" in segment.lower() for segment in medical_segments)
        assert any("diagnosi" in segment.lower() for segment in medical_segments)
        assert any("antibiotici" in segment.lower() for segment in medical_segments)
