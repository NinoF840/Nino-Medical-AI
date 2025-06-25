#!/usr/bin/env python3
"""
Pipeline Integration Adapter for Final Optimized Italian Medical NER
Seamlessly integrates the optimized model with existing API, web demo, and interfaces
while maintaining backward compatibility.

© 2025 Nino Medical AI. All Rights Reserved.
Author: NinoF840
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import time
import numpy as np

# Import the final optimized model
from final_optimized_ner import FinalOptimizedItalianMedicalNER

# Import existing interfaces for compatibility
try:
    from improved_inference import ImprovedItalianMedicalNER
except ImportError:
    ImprovedItalianMedicalNER = None

logger = logging.getLogger(__name__)

class ModelPerformanceLevel(Enum):
    """Performance levels available for the NER system"""
    BASIC = "basic"           # Original model, fast but lower accuracy
    ENHANCED = "enhanced"     # Improved model with moderate enhancements
    OPTIMIZED = "optimized"   # Final optimized model with maximum accuracy
    AUTO = "auto"            # Automatically select based on text complexity

@dataclass
class PipelineConfig:
    """Configuration for the integrated NER pipeline"""
    performance_level: ModelPerformanceLevel = ModelPerformanceLevel.OPTIMIZED
    confidence_threshold: float = 0.2
    enable_contextual_boosting: bool = True
    enable_morphological_analysis: bool = True
    enable_pattern_matching: bool = True
    enable_dictionary_lookup: bool = True
    max_text_length: int = 10000
    batch_size: int = 32
    timeout_seconds: int = 30

class IntegratedItalianMedicalNER:
    """
    Integrated Italian Medical NER Pipeline
    Provides seamless integration with existing APIs while using the optimized model
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the integrated NER pipeline
        
        Args:
            config: Pipeline configuration options
        """
        self.config = config or PipelineConfig()
        self.models = {}
        self.current_model = None
        self.model_performance_stats = {}
        
        # Initialize models based on configuration
        self._initialize_models()
        self._select_active_model()
        
        logger.info(f"Integrated NER pipeline initialized with {self.config.performance_level.value} performance level")
    
    def _initialize_models(self):
        """Initialize available models based on configuration"""
        try:
            # Always load the optimized model as the primary choice
            logger.info("Loading final optimized model...")
            self.models[ModelPerformanceLevel.OPTIMIZED] = FinalOptimizedItalianMedicalNER(
                confidence_threshold=self.config.confidence_threshold
            )
            logger.info("✅ Final optimized model loaded successfully")
            
            # Load enhanced model for fallback if available
            if ImprovedItalianMedicalNER is not None:
                try:
                    logger.info("Loading enhanced model as fallback...")
                    self.models[ModelPerformanceLevel.ENHANCED] = ImprovedItalianMedicalNER(
                        confidence_threshold=self.config.confidence_threshold
                    )
                    logger.info("✅ Enhanced model loaded successfully")
                except Exception as e:
                    logger.warning(f"Could not load enhanced model: {e}")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise RuntimeError(f"Model initialization failed: {e}")
    
    def _select_active_model(self):
        """Select the active model based on configuration and availability"""
        if self.config.performance_level == ModelPerformanceLevel.AUTO:
            # Use best available model
            if ModelPerformanceLevel.OPTIMIZED in self.models:
                self.current_model = self.models[ModelPerformanceLevel.OPTIMIZED]
                logger.info("Selected optimized model for AUTO mode")
            elif ModelPerformanceLevel.ENHANCED in self.models:
                self.current_model = self.models[ModelPerformanceLevel.ENHANCED]
                logger.info("Selected enhanced model for AUTO mode")
            else:
                raise RuntimeError("No suitable model available")
        else:
            # Use specifically requested model
            if self.config.performance_level in self.models:
                self.current_model = self.models[self.config.performance_level]
                logger.info(f"Selected {self.config.performance_level.value} model")
            else:
                # Fallback to best available
                if ModelPerformanceLevel.OPTIMIZED in self.models:
                    self.current_model = self.models[ModelPerformanceLevel.OPTIMIZED]
                    logger.warning(f"Requested {self.config.performance_level.value} model not available, using optimized")
                else:
                    raise RuntimeError(f"Requested model {self.config.performance_level.value} not available")
    
    def predict(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Predict medical entities with backward compatibility
        
        Args:
            text: Input Italian medical text
            **kwargs: Additional parameters for backward compatibility
            
        Returns:
            Dictionary with entities and metadata (compatible with existing API format)
        """
        if not text or not text.strip():
            return self._empty_result(text)
        
        # Validate input length
        if len(text) > self.config.max_text_length:
            raise ValueError(f"Text too long. Maximum {self.config.max_text_length} characters allowed.")
        
        # Extract parameters with backward compatibility
        confidence_threshold = kwargs.get('confidence_threshold', self.config.confidence_threshold)
        include_source = kwargs.get('include_source', True)
        apply_enhancement = kwargs.get('apply_enhancement', True)
        
        # Update model threshold if different
        if hasattr(self.current_model, 'confidence_threshold'):
            original_threshold = self.current_model.confidence_threshold
            self.current_model.confidence_threshold = confidence_threshold
        
        try:
            start_time = time.time()
            
            # Perform prediction with the active model
            if hasattr(self.current_model, 'predict'):
                result = self.current_model.predict(text, apply_enhancement=apply_enhancement)
            else:
                # Fallback for models with different interface
                result = self.current_model.predict(text)
            
            processing_time = time.time() - start_time
            
            # Format result for API compatibility
            formatted_result = self._format_api_response(
                result, text, processing_time, include_source
            )
            
            # Update performance statistics
            self._update_performance_stats(processing_time, len(result.get('entities', [])))
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}")
        
        finally:
            # Restore original threshold
            if hasattr(self.current_model, 'confidence_threshold'):
                self.current_model.confidence_threshold = original_threshold
    
    def batch_predict(self, texts: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Batch prediction with optimized processing
        
        Args:
            texts: List of Italian medical texts
            **kwargs: Additional parameters
            
        Returns:
            List of prediction results
        """
        if not texts:
            return []
        
        if len(texts) > 100:  # API limit
            raise ValueError("Maximum 100 texts per batch")
        
        results = []
        total_start_time = time.time()
        
        for i, text in enumerate(texts):
            try:
                result = self.predict(text, **kwargs)
                results.append(result)
                
                # Log progress for large batches
                if len(texts) > 10 and (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(texts)} texts")
                    
            except Exception as e:
                logger.error(f"Failed to process text {i + 1}: {e}")
                # Add error result to maintain batch consistency
                results.append({
                    'success': False,
                    'error': str(e),
                    'text': text,
                    'entities': [],
                    'total_entities': 0,
                    'processing_time': 0.0
                })
        
        total_time = time.time() - total_start_time
        logger.info(f"Batch processing completed: {len(texts)} texts in {total_time:.2f}s")
        
        return results
    
    def _format_api_response(self, result: Dict, original_text: str, 
                           processing_time: float, include_source: bool) -> Dict[str, Any]:
        """
        Format prediction result for API compatibility
        """
        # Handle both optimized model format and legacy formats
        entities = result.get('entities', [])
        
        # Ensure entities have required fields for API
        formatted_entities = []
        for entity in entities:
            formatted_entity = {
                'text': entity.get('text', ''),
                'label': entity.get('label', 'UNKNOWN'),
                'start': entity.get('start', 0),
                'end': entity.get('end', 0),
                'confidence': float(entity.get('confidence', 0.0))
            }
            
            # Add source information if requested and available
            if include_source and 'source' in entity:
                formatted_entity['source'] = entity['source']
            
            # Add contextual boost information if available
            if 'contextual_boost' in entity:
                formatted_entity['contextual_boost'] = entity['contextual_boost']
            
            formatted_entities.append(formatted_entity)
        
        # Calculate entity statistics
        entity_counts = {}
        for entity in formatted_entities:
            label = entity['label']
            entity_counts[label] = entity_counts.get(label, 0) + 1
        
        # Get model performance metrics
        performance_info = self._get_model_performance_info()
        
        return {
            'success': True,
            'text': original_text,
            'entities': formatted_entities,
            'total_entities': len(formatted_entities),
            'entity_counts': entity_counts,
            'processing_time': round(processing_time, 4),
            'model_version': self._get_model_version(),
            'performance_level': self.config.performance_level.value,
            'confidence_threshold': result.get('confidence_threshold', self.config.confidence_threshold),
            'enhancement_applied': result.get('enhancement_applied', True),
            'confidence_range_valid': result.get('confidence_range_valid', True),
            'performance_info': performance_info,
            'timestamp': time.time()
        }
    
    def _empty_result(self, text: str) -> Dict[str, Any]:
        """Return empty result for invalid input"""
        return {
            'success': True,
            'text': text,
            'entities': [],
            'total_entities': 0,
            'entity_counts': {},
            'processing_time': 0.0,
            'model_version': self._get_model_version(),
            'performance_level': self.config.performance_level.value,
            'timestamp': time.time()
        }
    
    def _get_model_version(self) -> str:
        """Get current model version string"""
        if self.config.performance_level == ModelPerformanceLevel.OPTIMIZED:
            return "nino_medical_final_optimized_v1.0"
        elif self.config.performance_level == ModelPerformanceLevel.ENHANCED:
            return "nino_medical_enhanced_v1.0"
        else:
            return "nino_medical_basic_v1.0"
    
    def _update_performance_stats(self, processing_time: float, entity_count: int):
        """Update performance statistics"""
        level = self.config.performance_level.value
        if level not in self.model_performance_stats:
            self.model_performance_stats[level] = {
                'total_predictions': 0,
                'total_processing_time': 0.0,
                'total_entities': 0,
                'avg_processing_time': 0.0,
                'avg_entities_per_text': 0.0
            }
        
        stats = self.model_performance_stats[level]
        stats['total_predictions'] += 1
        stats['total_processing_time'] += processing_time
        stats['total_entities'] += entity_count
        stats['avg_processing_time'] = stats['total_processing_time'] / stats['total_predictions']
        stats['avg_entities_per_text'] = stats['total_entities'] / stats['total_predictions']
    
    def _get_model_performance_info(self) -> Dict[str, Any]:
        """Get current model performance information"""
        level = self.config.performance_level.value
        stats = self.model_performance_stats.get(level, {})
        
        return {
            'model_type': level,
            'features_enabled': {
                'contextual_boosting': self.config.enable_contextual_boosting,
                'morphological_analysis': self.config.enable_morphological_analysis,
                'pattern_matching': self.config.enable_pattern_matching,
                'dictionary_lookup': self.config.enable_dictionary_lookup
            },
            'statistics': stats
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get pipeline health status"""
        return {
            'status': 'healthy' if self.current_model is not None else 'unhealthy',
            'active_model': self.config.performance_level.value,
            'models_available': list(self.models.keys()),
            'configuration': {
                'confidence_threshold': self.config.confidence_threshold,
                'max_text_length': self.config.max_text_length,
                'features_enabled': {
                    'contextual_boosting': self.config.enable_contextual_boosting,
                    'morphological_analysis': self.config.enable_morphological_analysis,
                    'pattern_matching': self.config.enable_pattern_matching,
                    'dictionary_lookup': self.config.enable_dictionary_lookup
                }
            },
            'performance_stats': self.model_performance_stats
        }
    
    def switch_performance_level(self, level: ModelPerformanceLevel) -> bool:
        """
        Switch to a different performance level
        
        Args:
            level: Target performance level
            
        Returns:
            True if switch was successful
        """
        if level in self.models:
            old_level = self.config.performance_level
            self.config.performance_level = level
            self._select_active_model()
            logger.info(f"Switched from {old_level.value} to {level.value}")
            return True
        else:
            logger.warning(f"Performance level {level.value} not available")
            return False
    
    # Backward compatibility methods
    @property
    def confidence_threshold(self) -> float:
        """Backward compatibility: get confidence threshold"""
        return self.config.confidence_threshold
    
    @confidence_threshold.setter
    def confidence_threshold(self, value: float):
        """Backward compatibility: set confidence threshold"""
        self.config.confidence_threshold = value
        if hasattr(self.current_model, 'confidence_threshold'):
            self.current_model.confidence_threshold = value


def create_integrated_ner(performance_level: str = "optimized", 
                         confidence_threshold: float = 0.2) -> IntegratedItalianMedicalNER:
    """
    Factory function to create integrated NER pipeline
    
    Args:
        performance_level: "basic", "enhanced", "optimized", or "auto"
        confidence_threshold: Confidence threshold for entity detection
        
    Returns:
        Configured IntegratedItalianMedicalNER instance
    """
    try:
        level = ModelPerformanceLevel(performance_level.lower())
    except ValueError:
        logger.warning(f"Invalid performance level '{performance_level}', using 'optimized'")
        level = ModelPerformanceLevel.OPTIMIZED
    
    config = PipelineConfig(
        performance_level=level,
        confidence_threshold=confidence_threshold
    )
    
    return IntegratedItalianMedicalNER(config)


# Compatibility aliases for existing code
def ImprovedItalianMedicalNERCompat(model_path: str = "./", confidence_threshold: float = 0.6):
    """
    Backward compatibility wrapper that provides the old interface
    but uses the new optimized model internally
    """
    class CompatWrapper:
        def __init__(self):
            self.ner_pipeline = create_integrated_ner("optimized", confidence_threshold)
        
        @property
        def confidence_threshold(self):
            return self.ner_pipeline.confidence_threshold
        
        @confidence_threshold.setter
        def confidence_threshold(self, value):
            self.ner_pipeline.confidence_threshold = value
        
        def predict(self, text: str):
            """Predict with old interface format"""
            result = self.ner_pipeline.predict(text)
            # Convert to old format if needed
            return {
                'entities': result['entities'],
                'total_entities': result['total_entities'],
                'confidence_threshold': result['confidence_threshold']
            }
    
    return CompatWrapper()


if __name__ == "__main__":
    """
    Test the integrated pipeline
    """
    import sys
    
    print("🚀 Testing Integrated Italian Medical NER Pipeline")
    print("=" * 60)
    
    # Test with different performance levels
    test_text = "Il paziente presenta forti mal di testa e nausea persistente da tre giorni."
    
    for level in ["optimized", "enhanced", "auto"]:
        try:
            print(f"\n📊 Testing {level.upper()} performance level:")
            ner = create_integrated_ner(level, confidence_threshold=0.2)
            
            result = ner.predict(test_text)
            print(f"  Model: {result['model_version']}")
            print(f"  Entities found: {result['total_entities']}")
            print(f"  Processing time: {result['processing_time']:.3f}s")
            print(f"  Confidence range valid: {result['confidence_range_valid']}")
            
            for entity in result['entities'][:3]:  # Show first 3
                print(f"    - {entity['text']} ({entity['label']}) [Conf: {entity['confidence']:.3f}]")
            
        except Exception as e:
            print(f"  ❌ Failed to test {level}: {e}")
    
    print(f"\n✅ Integration testing completed!")
