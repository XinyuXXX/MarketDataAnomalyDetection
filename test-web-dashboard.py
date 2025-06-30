#!/usr/bin/env python3
"""
Web Dashboard Structure Test
测试Web Dashboard的基本结构和文件完整性
"""

import os
import json
import sys
from pathlib import Path

def test_web_dashboard_structure():
    """测试Web Dashboard的目录结构和关键文件"""
    print("🧪 Testing Web Dashboard Structure...")
    
    # 检查基本目录结构
    required_dirs = [
        'web-dashboard',
        'web-dashboard/src',
        'web-dashboard/src/components',
        'web-dashboard/src/services',
        'web-dashboard/src/types',
        'web-dashboard/public'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("✅ All required directories exist")
    
    # 检查关键文件
    required_files = [
        'web-dashboard/package.json',
        'web-dashboard/tsconfig.json',
        'web-dashboard/src/index.tsx',
        'web-dashboard/src/App.tsx',
        'web-dashboard/src/index.css',
        'web-dashboard/src/types/index.ts',
        'web-dashboard/src/services/api.ts',
        'web-dashboard/src/components/Dashboard.tsx',
        'web-dashboard/src/components/Navigation.tsx',
        'web-dashboard/src/components/MetricsOverview.tsx',
        'web-dashboard/src/components/AnomalyChart.tsx',
        'web-dashboard/src/components/FilterPanel.tsx',
        'web-dashboard/src/components/AnomalyDetails.tsx',
        'web-dashboard/src/components/SystemHealth.tsx',
        'web-dashboard/public/index.html',
        'web-dashboard/Dockerfile',
        'web-dashboard/nginx.conf',
        'web-dashboard/README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
    
    # 检查package.json内容
    try:
        with open('web-dashboard/package.json', 'r') as f:
            package_json = json.load(f)
        
        required_deps = ['react', 'react-dom', 'typescript', 'antd', 'recharts', 'axios']
        missing_deps = []
        
        for dep in required_deps:
            if dep not in package_json.get('dependencies', {}):
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing dependencies in package.json: {missing_deps}")
            return False
        else:
            print("✅ All required dependencies found in package.json")
            
    except Exception as e:
        print(f"❌ Error reading package.json: {e}")
        return False
    
    # 检查TypeScript配置
    try:
        with open('web-dashboard/tsconfig.json', 'r') as f:
            tsconfig = json.load(f)
        
        if 'compilerOptions' in tsconfig and 'jsx' in tsconfig['compilerOptions']:
            print("✅ TypeScript configuration is valid")
        else:
            print("❌ Invalid TypeScript configuration")
            return False
            
    except Exception as e:
        print(f"❌ Error reading tsconfig.json: {e}")
        return False
    
    return True

def test_component_structure():
    """测试React组件的基本结构"""
    print("\n🧪 Testing React Components...")
    
    components = [
        'web-dashboard/src/App.tsx',
        'web-dashboard/src/components/Dashboard.tsx',
        'web-dashboard/src/components/Navigation.tsx',
        'web-dashboard/src/components/MetricsOverview.tsx',
        'web-dashboard/src/components/AnomalyChart.tsx'
    ]
    
    for component in components:
        try:
            with open(component, 'r') as f:
                content = f.read()
            
            # 检查基本React组件结构
            if 'import React' in content and 'export default' in content:
                print(f"✅ {component} has valid React component structure")
            else:
                print(f"❌ {component} missing React component structure")
                return False
                
        except Exception as e:
            print(f"❌ Error reading {component}: {e}")
            return False
    
    return True

def test_api_service():
    """测试API服务配置"""
    print("\n🧪 Testing API Service...")
    
    try:
        with open('web-dashboard/src/services/api.ts', 'r') as f:
            content = f.read()
        
        # 检查API服务的关键功能
        required_features = [
            'axios',
            'AnomalyAPI',
            'MockAPI',
            'getAnomalies',
            'getSystemMetrics',
            'getServiceHealth'
        ]
        
        missing_features = []
        for feature in required_features:
            if feature not in content:
                missing_features.append(feature)
        
        if missing_features:
            print(f"❌ Missing API features: {missing_features}")
            return False
        else:
            print("✅ API service has all required features")
            
    except Exception as e:
        print(f"❌ Error reading API service: {e}")
        return False
    
    return True

def test_docker_configuration():
    """测试Docker配置"""
    print("\n🧪 Testing Docker Configuration...")
    
    try:
        with open('web-dashboard/Dockerfile', 'r') as f:
            dockerfile_content = f.read()
        
        if 'FROM node:' in dockerfile_content and 'FROM nginx:' in dockerfile_content:
            print("✅ Dockerfile has multi-stage build configuration")
        else:
            print("❌ Dockerfile missing multi-stage build")
            return False
            
        with open('web-dashboard/nginx.conf', 'r') as f:
            nginx_content = f.read()
        
        if 'location /api/' in nginx_content and 'proxy_pass' in nginx_content:
            print("✅ Nginx configuration has API proxy setup")
        else:
            print("❌ Nginx configuration missing API proxy")
            return False
            
    except Exception as e:
        print(f"❌ Error reading Docker configuration: {e}")
        return False
    
    return True

def test_startup_scripts():
    """测试启动脚本"""
    print("\n🧪 Testing Startup Scripts...")
    
    startup_script = 'start-web-dashboard.sh'
    
    if not os.path.exists(startup_script):
        print(f"❌ Missing startup script: {startup_script}")
        return False
    
    # 检查脚本是否可执行
    if os.access(startup_script, os.X_OK):
        print("✅ Startup script is executable")
    else:
        print("❌ Startup script is not executable")
        return False
    
    try:
        with open(startup_script, 'r') as f:
            content = f.read()
        
        if 'npm install' in content and 'npm start' in content:
            print("✅ Startup script has required npm commands")
        else:
            print("❌ Startup script missing npm commands")
            return False
            
    except Exception as e:
        print(f"❌ Error reading startup script: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 Market Data Anomaly Detection - Web Dashboard Test")
    print("=" * 60)
    
    tests = [
        ("Web Dashboard Structure", test_web_dashboard_structure),
        ("React Components", test_component_structure),
        ("API Service", test_api_service),
        ("Docker Configuration", test_docker_configuration),
        ("Startup Scripts", test_startup_scripts)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Web Dashboard is ready!")
        print("\n📋 Next Steps:")
        print("1. Install dependencies: cd web-dashboard && npm install")
        print("2. Start development server: npm start")
        print("3. Or use the startup script: ./start-web-dashboard.sh")
        print("4. Access dashboard at: http://localhost:3000")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
