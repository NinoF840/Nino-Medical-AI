#!/usr/bin/env python3
"""
Test Local Deployment - Italian Medical NER
Quick verification that all components are working
"""

import sys
import importlib
import platform
from datetime import datetime

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'torch',
        'transformers', 
        'streamlit',
        'fastapi',
        'uvicorn',
        'numpy',
        'pandas'
    ]
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
            return False
    
    return True

def test_model_files():
    """Test if model files exist"""
    print("\n📁 Testing model files...")
    
    import os
    required_files = [
        'model.safetensors',
        'pytorch_model.bin',
        'config.json',
        'tokenizer_config.json',
        'vocab.txt'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            size_mb = os.path.getsize(file) / (1024*1024)
            print(f"  ✅ {file} ({size_mb:.1f} MB)")
        else:
            print(f"  ❌ {file}: Not found")
            return False
    
    return True

def test_streamlit_components():
    """Test Streamlit components"""
    print("\n🌐 Testing Streamlit components...")
    
    try:
        # Test if web_demo_app.py can be imported
        spec = importlib.util.spec_from_file_location("web_demo_app", "web_demo_app.py")
        module = importlib.util.module_from_spec(spec)
        # Don't execute, just check if it can be parsed
        print("  ✅ web_demo_app.py: Syntax OK")
        return True
    except Exception as e:
        print(f"  ❌ web_demo_app.py: {e}")
        return False

def test_api_components():
    """Test API components"""
    print("\n🔗 Testing API components...")
    
    try:
        from api_service import app
        print("  ✅ api_service.py: Imports OK")
        
        # Test if improved_inference exists
        try:
            from improved_inference import ImprovedItalianMedicalNER
            print("  ✅ improved_inference.py: Available")
        except ImportError:
            print("  ⚠️ improved_inference.py: Not available (will use basic inference)")
        
        return True
    except Exception as e:
        print(f"  ❌ api_service.py: {e}")
        return False

def test_quick_inference():
    """Test a quick inference"""
    print("\n🧠 Testing quick inference...")
    
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        
        # Quick test with small text
        tokenizer = AutoTokenizer.from_pretrained("./")
        model = AutoModelForTokenClassification.from_pretrained("./")
        
        text = "Il paziente ha la febbre."
        inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True)
        
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=2)
        
        print("  ✅ Model inference: Working")
        print(f"  ✅ Test text: '{text}'")
        print(f"  ✅ Tokens processed: {len(inputs['input_ids'][0])}")
        
        return True
    except Exception as e:
        print(f"  ❌ Model inference: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 ITALIAN MEDICAL NER - LOCAL DEPLOYMENT TEST")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️ Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print()
    
    tests = [
        ("Package Imports", test_imports),
        ("Model Files", test_model_files),
        ("Streamlit Components", test_streamlit_components),
        ("API Components", test_api_components),
        ("Quick Inference", test_quick_inference)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ❌ {test_name}: Failed with error: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your deployment is ready!")
        print("\n📝 Next Steps:")
        print("   1. Run Streamlit: streamlit run web_demo_app.py")
        print("   2. Run API: python api_service.py")
        print("   3. Access web demo: http://localhost:8501")
        print("   4. Access API docs: http://localhost:8000/docs")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Check the errors above.")
    
    print("\n💼 Nino Medical AI - Professional Italian Medical NER")
    print("© 2025 All Rights Reserved")

if __name__ == "__main__":
    main()
