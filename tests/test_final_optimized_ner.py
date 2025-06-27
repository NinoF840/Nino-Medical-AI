"""
Basic tests for FinalOptimizedItalianMedicalNER class
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from final_optimized_ner import FinalOptimizedItalianMedicalNER

@pytest.mark.unit
class TestFinalOptimizedItalianMedicalNER:
    
    @patch('final_optimized_ner.AutoTokenizer.from_pretrained')
    @patch('final_optimized_ner.AutoModelForTokenClassification.from_pretrained')
    @patch('final_optimized_ner.pipeline')
    def test_initialization(self, mock_pipeline, mock_model_cls, mock_tokenizer_cls):
        """Test initialization with mock models"""
        # Setup mocks
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_model.config.id2label = {0: "O", 1: "B-PROBLEM", 2: "I-PROBLEM"}
        mock_model.eval.return_value = None
        
        mock_tokenizer_cls.return_value = mock_tokenizer
        mock_model_cls.return_value = mock_model
        mock_pipeline.return_value = Mock()
        
        ner_model = FinalOptimizedItalianMedicalNER()
        assert ner_model is not None
        assert ner_model.confidence_threshold == 0.2

    @patch('final_optimized_ner.AutoTokenizer.from_pretrained')
    @patch('final_optimized_ner.AutoModelForTokenClassification.from_pretrained')
    @patch('final_optimized_ner.pipeline')
    def test_ner_pipelines(self, mock_pipeline, mock_model_cls, mock_tokenizer_cls):
        """Test NER pipelines creation"""
        # Setup mocks
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_model.config.id2label = {0: "O", 1: "B-PROBLEM"}
        mock_model.eval.return_value = None
        
        mock_tokenizer_cls.return_value = mock_tokenizer
        mock_model_cls.return_value = mock_model
        mock_pipeline.return_value = Mock()
        
        ner_model = FinalOptimizedItalianMedicalNER()
        pipelines = ner_model.pipelines
        
        assert 'simple' in pipelines
        assert 'max' in pipelines
        assert 'average' in pipelines
        assert 'first' in pipelines

    def test_comprehensive_patterns_loading(self):
        """Test loading comprehensive patterns without model initialization"""
        # Test the pattern loading method independently
        ner_instance = FinalOptimizedItalianMedicalNER.__new__(FinalOptimizedItalianMedicalNER)
        patterns = ner_instance._load_comprehensive_patterns()
        
        assert 'PROBLEM_comprehensive' in patterns
        assert 'TREATMENT_comprehensive' in patterns
        assert 'TEST_comprehensive' in patterns
        assert len(patterns['PROBLEM_comprehensive']) > 0
        assert len(patterns['TREATMENT_comprehensive']) > 0
        assert len(patterns['TEST_comprehensive']) > 0

