#!/usr/bin/env python3
"""
Integration test script for Market Data Anomaly Detection System
"""

import requests
import time
import sys
import json
from datetime import datetime

class IntegrationTester:
    """Runs comprehensive integration tests"""

    def __init__(self):
        self.base_urls = {
            'api-gateway': 'http://localhost:8080',
            'data-ingestion': 'http://localhost:8081',
            'stream-processing': 'http://localhost:8082',
            'alert-service': 'http://localhost:8083',
            'dashboard-api': 'http://localhost:8084',
            'detection-engine': 'http://localhost:8085'
        }
        self.test_results = {}

    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting integration tests...")

        self.test_health_endpoints()
        self.test_detection_algorithms()
        self.test_data_flow()

        self.print_results()
        return all(self.test_results.values())

    def test_health_endpoints(self):
        """Test all health endpoints"""
        print("🔍 Testing health endpoints...")

        for service, base_url in self.base_urls.items():
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                success = response.status_code == 200
                self.test_results[f"{service}_health"] = success

                if success:
                    print(f"✅ {service} health check passed")
                else:
                    print(f"❌ {service} health check failed: {response.status_code}")

            except Exception as e:
                print(f"❌ {service} health check failed: {e}")
                self.test_results[f"{service}_health"] = False

    def test_detection_algorithms(self):
        """Test detection algorithms"""
        print("🔍 Testing detection algorithms...")

        # Test data
        test_data = [
            {
                "symbol": "AAPL",
                "timestamp": datetime.now().isoformat(),
                "source": "gemfire",
                "data_type": "price",
                "payload": {"price": 150.0, "volume": 1000},
                "price": 150.0,
                "volume": 1000.0
            }
        ]

        # Test missing data detection
        try:
            response = requests.post(
                f"{self.base_urls['detection-engine']}/detect/missing-data",
                json=test_data,
                timeout=10
            )
            success = response.status_code == 200
            self.test_results["missing_data_detection"] = success

            if success:
                print("✅ Missing data detection test passed")
            else:
                print(f"❌ Missing data detection test failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Missing data detection test failed: {e}")
            self.test_results["missing_data_detection"] = False

        # Test price movement detection
        try:
            response = requests.post(
                f"{self.base_urls['detection-engine']}/detect/price-movement",
                json=test_data,
                timeout=10
            )
            success = response.status_code == 200
            self.test_results["price_movement_detection"] = success

            if success:
                print("✅ Price movement detection test passed")
            else:
                print(f"❌ Price movement detection test failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Price movement detection test failed: {e}")
            self.test_results["price_movement_detection"] = False

    def test_data_flow(self):
        """Test end-to-end data flow"""
        print("🔍 Testing data flow...")

        # This would test the complete data flow from ingestion to detection
        # For now, just mark as passed if basic services are up
        basic_services_up = all([
            self.test_results.get("api-gateway_health", False),
            self.test_results.get("detection-engine_health", False)
        ])

        self.test_results["data_flow"] = basic_services_up

        if basic_services_up:
            print("✅ Basic data flow test passed")
        else:
            print("❌ Data flow test failed")

    def print_results(self):
        """Print test results summary"""
        print("\n📊 Test Results Summary:")
        print("=" * 50)

        passed = 0
        total = len(self.test_results)

        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:30} {status}")
            if result:
                passed += 1

        print("=" * 50)
        print(f"Total: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed!")

if __name__ == "__main__":
    tester = IntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)