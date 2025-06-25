"""
Basic tests for FinalOptimizedItalianMedicalNER class
"""
import pytest
from final_optimized_ner import FinalOptimizedItalianMedicalNER

@pytest.mark.unit
class TestFinalOptimizedItalianMedicalNER:
    def test_initialization(self, mock_tokenizer, mock_model):
        """Test initialization with mock models"""
        ner_model = FinalOptimizedItalianMedicalNER()
        assert ner_model is not None

    def test_ner_pipelines(self, mock_tokenizer, mock_model):
        """Test NER pipelines creation"""
        ner_model = FinalOptimizedItalianMedicalNER()
        pipelines = ner_model._initialize_pipelines()
        assert 'simple' in pipelines
        assert 'max' in pipelines
        assert 'average' in pipelines
        assert 'first' in pipelines

    def test_comprehensive_patterns_loading(self):
        """Test loading comprehensive patterns"""
        ner_model = FinalOptimizedItalianMedicalNER()
        patterns = ner_model._load_comprehensive_patterns()
        assert 'PROBLEM_comprehensive' in patterns
        assert len(patterns['PROBLEM_comprehensive']) > 0

