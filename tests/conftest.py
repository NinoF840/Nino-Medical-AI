"""
Pytest configuration and fixtures for Italian Medical NER tests
"""
import pytest
import os
import sys
from unittest.mock import Mock, MagicMock
from typing import Dict, List

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_italian_medical_text():
    """Sample Italian medical text for testing"""
    return """
    Il paziente presenta forti dolori al petto e difficoltà respiratorie. 
    È stata prescritta una terapia con paracetamolo e sono stati effettuati 
    esami del sangue e una radiografia del torace. La diagnosi indica 
    una possibile infezione polmonare che richiede antibiotici.
    """

@pytest.fixture
def sample_entities():
    """Expected entities for the sample text"""
    return [
        {"text": "forti dolori", "label": "PROBLEM", "start": 25, "end": 37},
        {"text": "difficoltà respiratorie", "label": "PROBLEM", "start": 50, "end": 73},
        {"text": "terapia", "label": "TREATMENT", "start": 95, "end": 102},
        {"text": "paracetamolo", "label": "TREATMENT", "start": 107, "end": 119},
        {"text": "esami del sangue", "label": "TEST", "start": 140, "end": 156},
        {"text": "radiografia", "label": "TEST", "start": 163, "end": 174},
        {"text": "infezione polmonare", "label": "PROBLEM", "start": 215, "end": 234},
        {"text": "antibiotici", "label": "TREATMENT", "start": 248, "end": 259}
    ]

@pytest.fixture
def mock_tokenizer():
    """Mock tokenizer for testing"""
    tokenizer = Mock()
    tokenizer.convert_ids_to_tokens.return_value = [
        "[CLS]", "Il", "paziente", "presenta", "forti", "dolori", "[SEP]"
    ]
    tokenizer.return_value = {
        'input_ids': [[101, 1234, 5678, 9012, 3456, 7890, 102]],
        'attention_mask': [[1, 1, 1, 1, 1, 1, 1]]
    }
    return tokenizer

@pytest.fixture
def mock_model():
    """Mock model for testing"""
    model = Mock()
    model.config.id2label = {
        0: "O", 1: "B-PROBLEM", 2: "I-PROBLEM", 3: "E-PROBLEM", 4: "S-PROBLEM",
        5: "B-TREATMENT", 6: "I-TREATMENT", 7: "E-TREATMENT", 8: "S-TREATMENT",
        9: "B-TEST", 10: "I-TEST", 11: "E-TEST", 12: "S-TEST"
    }
    model.eval.return_value = None
    return model

@pytest.fixture
def confidence_threshold():
    """Default confidence threshold for testing"""
    return 0.6

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory with test data"""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    
    # Create sample model files
    (test_dir / "config.json").write_text('{"id2label": {"0": "O", "1": "B-PROBLEM"}}')
    (test_dir / "pytorch_model.bin").write_bytes(b"dummy model data")
    (test_dir / "tokenizer.json").write_text('{"model": {"vocab": {}}}')
    
    return str(test_dir)

@pytest.fixture
def api_test_client():
    """Test client for API testing"""
    from fastapi.testclient import TestClient
    try:
        from api_service import app
        return TestClient(app)
    except ImportError:
        # Return a mock client if FastAPI is not available
        return Mock()

@pytest.fixture
def sample_batch_texts():
    """Sample batch of Italian medical texts"""
    return [
        "Il paziente ha mal di testa persistente.",
        "Prescritto paracetamolo per il dolore.",
        "Necessari esami del sangue urgenti.",
        "Radiografia del torace mostra anomalie.",
        "Terapia antibiotica iniziata oggi."
    ]

@pytest.fixture
def performance_test_text():
    """Large text for performance testing"""
    base_text = """
    Il paziente di 65 anni presenta una storia clinica complessa con diabete mellito di tipo 2, 
    ipertensione arteriosa e cardiopatia ischemica. Durante l'ultimo ricovero ospedaliero, 
    sono stati effettuati numerosi esami diagnostici tra cui emocromo completo, elettrocardiogramma, 
    ecocardiografia e TAC torace-addome. La terapia farmacologica attuale include metformina per 
    il controllo glicemico, ACE-inibitori per l'ipertensione e antiaggreganti piastrinici per 
    la prevenzione cardiovascolare.
    """
    return base_text * 10  # Repeat to create larger text

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    os.environ['TESTING'] = 'true'
    yield
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
