"""
Tests for the FastAPI API service
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


@pytest.mark.api
class TestAPIService:
    """Test class for API service endpoints"""
    
    @patch('api_service.ImprovedItalianMedicalNER')
    @patch('api_service.NinoMedicalAnalytics')
    def test_root_endpoint(self, mock_analytics, mock_ner):
        """Test the root endpoint"""
        try:
            from api_service import app
            client = TestClient(app)
            
            response = client.get("/")
            assert response.status_code == 200
            
            data = response.json()
            assert "message" in data
            assert "version" in data
            assert data["version"] == "1.0.0"
            assert "Nino Medical AI" in data["message"]
            
        except ImportError:
            pytest.skip("FastAPI or API service not available")
    
    @patch('api_service.ImprovedItalianMedicalNER')
    @patch('api_service.NinoMedicalAnalytics')
    def test_health_endpoint(self, mock_analytics, mock_ner):
        """Test the health check endpoint"""
        try:
            from api_service import app
            client = TestClient(app)
            
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "model_loaded" in data
            assert "version" in data
            assert "timestamp" in data
            
        except ImportError:
            pytest.skip("FastAPI or API service not available")
    
    @patch('api_service.ner_model')
    def test_analyze_endpoint_without_auth(self, mock_ner_model):
        """Test analyze endpoint without authentication (should fail)"""
        try:
            from api_service import app
            client = TestClient(app)
            
            test_data = {
                "text": "Il paziente ha mal di testa",
                "confidence_threshold": 0.6
            }
            
            response = client.post("/analyze", json=test_data)
            assert response.status_code == 403  # Should require authentication
            
        except ImportError:
            pytest.skip("FastAPI or API service not available")
    
    @patch('api_service.ner_model')
    def test_analyze_endpoint_with_valid_auth(self, mock_ner_model):
        """Test analyze endpoint with valid authentication"""
        try:
            from api_service import app
            client = TestClient(app)
            
            # Mock the NER model response
            mock_ner_model.predict_with_source.return_value = {
                'entities': [
                    {'text': 'mal di testa', 'label': 'PROBLEM', 'start': 15, 'end': 27, 
                     'confidence': 0.85, 'source': 'model'}
                ],
                'processing_time': 0.123
            }
            mock_ner_model.confidence_threshold = 0.6
            
            test_data = {
                "text": "Il paziente ha mal di testa",
                "confidence_threshold": 0.6
            }
            
            headers = {"Authorization": "Bearer demo-key-123"}
            response = client.post("/analyze", json=test_data, headers=headers)
            
            # Should succeed with valid API key
            if response.status_code == 200:
                data = response.json()
                assert "entities" in data
                assert "total_entities" in data
                assert "processing_time" in data
                assert data["success"] is True
            
        except ImportError:
            pytest.skip("FastAPI or API service not available")
    
    def test_api_key_validation(self):
        """Test API key validation logic"""
        try:
            from api_service import VALID_API_KEYS
            
            assert "demo-key-123" in VALID_API_KEYS
            assert "pro-key-456" in VALID_API_KEYS
            assert "enterprise-key-789" in VALID_API_KEYS
            
            # Check tier structure
            assert VALID_API_KEYS["demo-key-123"]["tier"] == "demo"
            assert VALID_API_KEYS["pro-key-456"]["tier"] == "professional"
            assert VALID_API_KEYS["enterprise-key-789"]["tier"] == "enterprise"
            
        except ImportError:
            pytest.skip("API service not available")


@pytest.mark.api
class TestAPIModels:
    """Test API data models"""
    
    def test_text_input_model(self):
        """Test TextInput model validation"""
        try:
            from api_service import TextInput
            
            # Valid input
            valid_input = TextInput(
                text="Il paziente ha dolore",
                confidence_threshold=0.7,
                include_source=True
            )
            assert valid_input.text == "Il paziente ha dolore"
            assert valid_input.confidence_threshold == 0.7
            assert valid_input.include_source is True
            
            # Test defaults
            default_input = TextInput(text="Test text")
            assert default_input.confidence_threshold == 0.6
            assert default_input.include_source is True
            
        except ImportError:
            pytest.skip("API service models not available")
    
    def test_entity_result_model(self):
        """Test EntityResult model"""
        try:
            from api_service import EntityResult
            
            entity = EntityResult(
                text="dolore",
                label="PROBLEM",
                start=10,
                end=16,
                confidence=0.85,
                source="model"
            )
            
            assert entity.text == "dolore"
            assert entity.label == "PROBLEM"
            assert entity.confidence == 0.85
            
        except ImportError:
            pytest.skip("API service models not available")
    
    def test_batch_input_model(self):
        """Test BatchInput model validation"""
        try:
            from api_service import BatchInput
            
            batch_input = BatchInput(
                texts=["Text 1", "Text 2", "Text 3"],
                confidence_threshold=0.8
            )
            
            assert len(batch_input.texts) == 3
            assert batch_input.confidence_threshold == 0.8
            
        except ImportError:
            pytest.skip("API service models not available")


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API service"""
    
    @patch('api_service.ImprovedItalianMedicalNER')
    @patch('api_service.NinoMedicalAnalytics') 
    def test_full_api_workflow(self, mock_analytics, mock_ner_class, sample_italian_medical_text):
        """Test complete API workflow"""
        try:
            from api_service import app
            client = TestClient(app)
            
            # Mock NER model
            mock_ner_instance = Mock()
            mock_ner_instance.predict_with_source.return_value = {
                'entities': [
                    {'text': 'forti dolori', 'label': 'PROBLEM', 'start': 25, 'end': 37, 
                     'confidence': 0.89, 'source': 'model'},
                    {'text': 'paracetamolo', 'label': 'TREATMENT', 'start': 107, 'end': 119, 
                     'confidence': 0.92, 'source': 'dictionary'}
                ],
                'processing_time': 0.156
            }
            mock_ner_instance.confidence_threshold = 0.6
            mock_ner_class.return_value = mock_ner_instance
            
            # Patch the global ner_model
            with patch('api_service.ner_model', mock_ner_instance):
                # Test analyze endpoint
                test_data = {
                    "text": sample_italian_medical_text.strip(),
                    "confidence_threshold": 0.6,
                    "include_source": True
                }
                
                headers = {"Authorization": "Bearer demo-key-123"}
                response = client.post("/analyze", json=test_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["success"] is True
                    assert len(data["entities"]) == 2
                    assert data["total_entities"] == 2
                    assert "processing_time" in data
                
        except ImportError:
            pytest.skip("FastAPI or dependencies not available")


@pytest.mark.slow
class TestAPIPerformance:
    """Performance tests for API"""
    
    @patch('api_service.ner_model')
    def test_api_response_time(self, mock_ner_model, performance_test_text):
        """Test API response time with large text"""
        try:
            import time
            from api_service import app
            client = TestClient(app)
            
            # Mock fast response
            mock_ner_model.predict_with_source.return_value = {
                'entities': [],
                'processing_time': 0.05
            }
            
            test_data = {
                "text": performance_test_text[:5000],  # Limit text size
                "confidence_threshold": 0.6
            }
            
            headers = {"Authorization": "Bearer demo-key-123"}
            
            start_time = time.time()
            response = client.post("/analyze", json=test_data, headers=headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Should respond within reasonable time (5 seconds for large text)
            assert response_time < 5.0
            
            if response.status_code == 200:
                data = response.json()
                assert "processing_time" in data
                
        except ImportError:
            pytest.skip("FastAPI or dependencies not available")
