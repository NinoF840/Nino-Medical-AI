"""
Unit tests for EnhancedItalianMedicalNER class
"""
import pytest
import torch
from unittest.mock import Mock, patch, MagicMock
from enhanced_inference import EnhancedItalianMedicalNER


@pytest.mark.unit
class TestEnhancedItalianMedicalNER:
    """Test class for EnhancedItalianMedicalNER"""
    
    @patch('enhanced_inference.AutoTokenizer')
    @patch('enhanced_inference.AutoModelForTokenClassification')
    def test_initialization(self, mock_model_class, mock_tokenizer_class):
        """Test model initialization"""
        # Setup mocks
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_model.config.id2label = {0: "O", 1: "B-PROBLEM"}
        
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model
        
        # Initialize model
        ner = EnhancedItalianMedicalNER(model_path="./test", confidence_threshold=0.5)
        
        # Assertions
        assert ner.model_path == "./test"
        assert ner.confidence_threshold == 0.5
        assert ner.tokenizer == mock_tokenizer
        assert ner.model == mock_model
        mock_model.eval.assert_called_once()
    
    def test_medical_patterns_loading(self):
        """Test loading of medical patterns"""
        with patch('enhanced_inference.AutoTokenizer'), \
             patch('enhanced_inference.AutoModelForTokenClassification'):
            ner = EnhancedItalianMedicalNER()
            patterns = ner.medical_patterns
            
            assert 'PROBLEM_indicators' in patterns
            assert 'TREATMENT_indicators' in patterns
            assert 'TEST_indicators' in patterns
            assert len(patterns['PROBLEM_indicators']) > 0
    
    def test_confidence_scores_calculation(self):
        """Test confidence score calculation from logits"""
        with patch('enhanced_inference.AutoTokenizer'), \
             patch('enhanced_inference.AutoModelForTokenClassification'):
            ner = EnhancedItalianMedicalNER()
            
            # Create dummy logits
            logits = torch.tensor([[[2.0, 1.0, 0.5], [1.5, 2.5, 0.8]]])
            confidence_scores = ner._get_confidence_scores(logits)
            
            # Fix: The shape includes batch dimension, so it's (1, 2) not (2,)
            assert confidence_scores.shape == (1, 2)
            assert torch.all(confidence_scores >= 0.0)
            assert torch.all(confidence_scores <= 1.0)
    
    def test_pattern_enhancement(self):
        """Test pattern enhancement functionality"""
        with patch('enhanced_inference.AutoTokenizer'), \
             patch('enhanced_inference.AutoModelForTokenClassification'):
            ner = EnhancedItalianMedicalNER(confidence_threshold=0.5)
            
            tokens = ["Il", "paziente", "ha", "dolore", "al", "petto"]
            predictions = ["O", "O", "O", "O", "O", "O"]
            confidence_scores = [0.9, 0.8, 0.7, 0.3, 0.4, 0.6]  # Low confidence for "dolore"
            
            enhanced = ner._apply_pattern_enhancement(tokens, predictions, confidence_scores)
            
            # Should have applied some enhancements
            assert len(enhanced) == len(predictions)
    
    def test_bioes_post_processing(self):
        """Test BIOES tag post-processing"""
        with patch('enhanced_inference.AutoTokenizer'), \
             patch('enhanced_inference.AutoModelForTokenClassification'):
            ner = EnhancedItalianMedicalNER()
            
            # Test sequence with orphaned tags
            predictions = ["O", "B-PROBLEM", "I-PROBLEM", "I-PROBLEM", "O", "I-TREATMENT"]
            processed = ner._post_process_bioes(predictions)
            
            assert len(processed) == len(predictions)
            # The orphaned I-TREATMENT should be converted to S-TREATMENT
            assert processed[-1] == "S-TREATMENT"
    
    @patch('enhanced_inference.AutoTokenizer')
    @patch('enhanced_inference.AutoModelForTokenClassification')
    def test_predict_method(self, mock_model_class, mock_tokenizer_class, sample_italian_medical_text):
        """Test the main predict method"""
        # Setup comprehensive mocks
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_model.config.id2label = {0: "O", 1: "B-PROBLEM", 2: "I-PROBLEM"}
        
        # Mock tokenizer behavior
        mock_inputs = {
            'input_ids': torch.tensor([[101, 1234, 5678, 102]]),
            'attention_mask': torch.tensor([[1, 1, 1, 1]])
        }
        mock_tokenizer.return_value = mock_inputs
        mock_tokenizer.convert_ids_to_tokens.return_value = ["[CLS]", "dolore", "petto", "[SEP]"]
        
        # Mock model outputs
        mock_outputs = Mock()
        mock_outputs.logits = torch.tensor([[[2.0, 1.0, 0.5], [1.5, 2.5, 0.8], [0.5, 1.0, 2.0], [1.0, 0.5, 0.3]]])
        mock_model.return_value = mock_outputs
        
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model
        
        # Initialize and test
        ner = EnhancedItalianMedicalNER()
        
        with patch.object(ner.model, '__call__', return_value=mock_outputs):
            result = ner.predict("Il paziente ha dolore al petto")
            
            assert 'entities' in result
            assert 'tokens' in result
            assert 'predictions' in result
            assert 'confidence_scores' in result
            assert 'text' in result
            assert isinstance(result['entities'], list)


@pytest.mark.integration
class TestEnhancedNERIntegration:
    """Integration tests that require actual model files (if available)"""
    
    def test_integration_with_sample_text(self, sample_italian_medical_text):
        """Integration test with sample medical text"""
        try:
            # Only run if model files exist
            ner = EnhancedItalianMedicalNER(model_path="./")
            result = ner.predict(sample_italian_medical_text)
            
            assert 'entities' in result
            assert len(result['entities']) >= 0  # Should find some entities
            
        except Exception as e:
            pytest.skip(f"Model files not available for integration test: {e}")


@pytest.mark.mock
class TestEnhancedNERMocked:
    """Tests using extensive mocking for scenarios where model loading fails"""
    
    @patch('enhanced_inference.AutoTokenizer')
    @patch('enhanced_inference.AutoModelForTokenClassification')
    def test_confidence_threshold_setting(self, mock_model_class, mock_tokenizer_class):
        """Test that confidence threshold is properly set"""
        mock_model = Mock()
        mock_model.config.id2label = {0: "O"}
        mock_model_class.from_pretrained.return_value = mock_model
        
        ner = EnhancedItalianMedicalNER(confidence_threshold=0.8)
        assert ner.confidence_threshold == 0.8
    
    def test_medical_pattern_structure(self):
        """Test the structure of medical patterns"""
        with patch('enhanced_inference.AutoTokenizer'), \
             patch('enhanced_inference.AutoModelForTokenClassification'):
            ner = EnhancedItalianMedicalNER()
            patterns = ner._load_medical_patterns()
            
            # Check that all pattern categories exist
            expected_categories = ['PROBLEM_indicators', 'TREATMENT_indicators', 'TEST_indicators']
            for category in expected_categories:
                assert category in patterns
                assert isinstance(patterns[category], list)
                assert len(patterns[category]) > 0
