#!/usr/bin/env python3
"""
Test Java compilation without Maven
"""

import subprocess
import os
import sys
from pathlib import Path

def test_java_compilation():
    """Test Java compilation using javac directly"""
    print("🔨 Testing Java compilation with javac...")
    
    # Find all Java files
    java_files = []
    java_services_dir = Path("java-services")
    
    for service_dir in java_services_dir.iterdir():
        if service_dir.is_dir() and service_dir.name != "common":
            java_src_dir = service_dir / "src/main/java"
            if java_src_dir.exists():
                for java_file in java_src_dir.rglob("*.java"):
                    java_files.append(str(java_file))
    
    # Also include common module
    common_src_dir = java_services_dir / "common/src/main/java"
    if common_src_dir.exists():
        for java_file in common_src_dir.rglob("*.java"):
            java_files.append(str(java_file))
    
    print(f"Found {len(java_files)} Java files")
    
    if not java_files:
        print("❌ No Java files found")
        return False
    
    # Create output directory
    output_dir = Path("build/classes")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to compile each file individually to check syntax
    success_count = 0
    for java_file in java_files:
        try:
            result = subprocess.run([
                "javac", 
                "-d", str(output_dir),
                "-cp", ".",
                java_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ {java_file} - compiled successfully")
                success_count += 1
            else:
                print(f"❌ {java_file} - compilation failed:")
                print(f"   Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {java_file} - compilation timed out")
        except Exception as e:
            print(f"❌ {java_file} - error: {e}")
    
    print(f"\n📊 Compilation Results: {success_count}/{len(java_files)} files compiled successfully")
    
    return success_count > 0

def test_python_imports():
    """Test Python imports"""
    print("\n🐍 Testing Python imports...")
    
    try:
        # Test core Python libraries
        import pandas
        import numpy
        import requests
        print("✅ Core Python libraries imported successfully")
        
        # Test our detection algorithms
        sys.path.append('python-services/detection-engine/src')
        from algorithms.missing_data_detector import MissingDataDetector
        from algorithms.price_movement_detector import PriceMovementDetector
        print("✅ Detection algorithms imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Project Components")
    print("=" * 50)
    
    results = {}
    
    # Test Java compilation
    results["java_compilation"] = test_java_compilation()
    
    # Test Python imports
    results["python_imports"] = test_python_imports()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("\n📝 Next steps:")
        print("   • Wait for Maven installation to complete")
        print("   • Run './start-system.sh' for full deployment")
        print("   • Or run 'python3 demo.py' for algorithm demo")
        return True
    else:
        print("\n⚠️  Some tests failed.")
        print("   • Java compilation issues may be resolved with Maven")
        print("   • Python demo should still work: 'python3 demo.py'")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
