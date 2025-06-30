#!/usr/bin/env python3
"""
Quick test script to verify the generated code works
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(cmd, cwd=None, timeout=60):
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_java_compilation():
    """Test Java code compilation"""
    print("🔨 Testing Java compilation...")
    
    # Test if Maven can compile the code
    success, stdout, stderr = run_command(
        "mvn clean compile -q", 
        cwd="java-services"
    )
    
    if success:
        print("✅ Java compilation successful")
        return True
    else:
        print("❌ Java compilation failed")
        print(f"Error: {stderr}")
        return False

def test_python_syntax():
    """Test Python code syntax"""
    print("🐍 Testing Python syntax...")
    
    python_files = [
        "python-services/detection-engine/src/api/main.py",
        "python-services/detection-engine/src/algorithms/missing_data_detector.py",
        "python-services/detection-engine/src/algorithms/price_movement_detector.py"
    ]
    
    all_good = True
    for file_path in python_files:
        if os.path.exists(file_path):
            success, _, stderr = run_command(f"python3 -m py_compile {file_path}")
            if success:
                print(f"✅ {file_path} - syntax OK")
            else:
                print(f"❌ {file_path} - syntax error: {stderr}")
                all_good = False
        else:
            print(f"⚠️  {file_path} - file not found")
            all_good = False
    
    return all_good

def test_docker_builds():
    """Test Docker builds"""
    print("🐳 Testing Docker builds...")
    
    # Test Python service Docker build
    print("Building Python detection engine...")
    success, stdout, stderr = run_command(
        "docker build -t detection-engine .", 
        cwd="python-services/detection-engine"
    )
    
    if success:
        print("✅ Python Docker build successful")
        python_build_ok = True
    else:
        print("❌ Python Docker build failed")
        print(f"Error: {stderr}")
        python_build_ok = False
    
    # Test Java service Docker build (just one service to save time)
    print("Building Java API Gateway...")
    success, stdout, stderr = run_command(
        "mvn package -DskipTests -q && docker build -t api-gateway .", 
        cwd="java-services/api-gateway"
    )
    
    if success:
        print("✅ Java Docker build successful")
        java_build_ok = True
    else:
        print("❌ Java Docker build failed")
        print(f"Error: {stderr}")
        java_build_ok = False
    
    return python_build_ok and java_build_ok

def test_python_algorithms():
    """Test Python detection algorithms"""
    print("🧪 Testing Python algorithms...")
    
    # Create a simple test
    test_script = """
import sys
sys.path.append('python-services/detection-engine/src')

from algorithms.missing_data_detector import MissingDataDetector
from algorithms.price_movement_detector import PriceMovementDetector
from datetime import datetime

# Test missing data detector
detector = MissingDataDetector()
test_data = [
    {'symbol': 'AAPL', 'timestamp': datetime.now().isoformat(), 'price': 150.0}
]
result = detector.detect(test_data)
print(f"Missing data detector: {len(result)} anomalies detected")

# Test price movement detector  
detector = PriceMovementDetector()
result = detector.detect(test_data)
print(f"Price movement detector: {len(result)} anomalies detected")

print("Algorithm tests completed successfully")
"""
    
    with open("temp_test.py", "w") as f:
        f.write(test_script)
    
    success, stdout, stderr = run_command("python3 temp_test.py")
    
    # Cleanup
    if os.path.exists("temp_test.py"):
        os.remove("temp_test.py")
    
    if success:
        print("✅ Python algorithms test successful")
        print(stdout)
        return True
    else:
        print("❌ Python algorithms test failed")
        print(f"Error: {stderr}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running quick tests for Market Data Anomaly Detection System")
    print("=" * 70)
    
    tests = [
        ("Java Compilation", test_java_compilation),
        ("Python Syntax", test_python_syntax),
        ("Python Algorithms", test_python_algorithms),
        ("Docker Builds", test_docker_builds)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print("=" * 70)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The system is ready.")
        print("\n🚀 To start the full system, run:")
        print("   ./start-system.sh")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
