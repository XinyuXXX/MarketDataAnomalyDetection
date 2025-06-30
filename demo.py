#!/usr/bin/env python3
"""
Demo script for Market Data Anomaly Detection System
Demonstrates the core detection algorithms without requiring Java/Maven
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the Python services to path
sys.path.append('python-services/detection-engine/src')

def demo_missing_data_detection():
    """Demonstrate missing data detection"""
    print("🔍 Demo: Missing Data Detection")
    print("-" * 40)
    
    from algorithms.missing_data_detector import MissingDataDetector
    
    # Create test data with missing data
    now = datetime.now()
    test_data = [
        {
            'symbol': 'AAPL',
            'timestamp': now.isoformat(),
            'price': 150.0
        },
        {
            'symbol': 'AAPL',
            'timestamp': (now - timedelta(hours=2)).isoformat(),  # 2 hour gap!
            'price': 149.0
        },
        {
            'symbol': 'GOOGL',
            'timestamp': now.isoformat(),
            'price': 2800.0
        },
        {
            'symbol': 'GOOGL',
            'timestamp': (now - timedelta(minutes=10)).isoformat(),  # Normal gap
            'price': 2799.0
        }
    ]
    
    # Run detection
    detector = MissingDataDetector(threshold_minutes=30)
    anomalies = detector.detect(test_data)
    
    print(f"📊 Processed {len(test_data)} data points")
    print(f"🚨 Found {len(anomalies)} missing data anomalies")
    
    for anomaly in anomalies:
        print(f"   • {anomaly['symbol']}: {anomaly['description']}")
        print(f"     Severity: {anomaly['severity']}")
        print(f"     Gap: {anomaly['details']['gap_minutes']:.1f} minutes")
    
    return anomalies

def demo_price_movement_detection():
    """Demonstrate price movement detection"""
    print("\n🔍 Demo: Price Movement Detection")
    print("-" * 40)
    
    from algorithms.price_movement_detector import PriceMovementDetector
    
    # Create test data with abnormal price movements
    now = datetime.now()
    test_data = [
        # Normal price movement
        {'symbol': 'AAPL', 'timestamp': (now - timedelta(minutes=30)).isoformat(), 'price': 150.0},
        {'symbol': 'AAPL', 'timestamp': (now - timedelta(minutes=20)).isoformat(), 'price': 151.0},  # 0.67% change
        
        # Abnormal price movement
        {'symbol': 'AAPL', 'timestamp': (now - timedelta(minutes=10)).isoformat(), 'price': 160.0},  # 6% jump!
        {'symbol': 'AAPL', 'timestamp': now.isoformat(), 'price': 145.0},  # 9.4% drop!
        
        # Another stock with extreme movement
        {'symbol': 'TSLA', 'timestamp': (now - timedelta(minutes=15)).isoformat(), 'price': 800.0},
        {'symbol': 'TSLA', 'timestamp': now.isoformat(), 'price': 900.0},  # 12.5% jump!
    ]
    
    # Run detection
    detector = PriceMovementDetector(threshold_percent=5.0)
    anomalies = detector.detect(test_data)
    
    print(f"📊 Processed {len(test_data)} data points")
    print(f"🚨 Found {len(anomalies)} price movement anomalies")
    
    for anomaly in anomalies:
        change = anomaly['details']['price_change_percent']
        print(f"   • {anomaly['symbol']}: {change:+.2f}% price change")
        print(f"     Severity: {anomaly['severity']}")
        print(f"     Current price: ${anomaly['details']['current_price']:.2f}")
    
    return anomalies

def demo_real_time_simulation():
    """Simulate real-time anomaly detection"""
    print("\n🔍 Demo: Real-time Simulation")
    print("-" * 40)
    
    import random
    import time
    
    from algorithms.missing_data_detector import MissingDataDetector
    from algorithms.price_movement_detector import PriceMovementDetector
    
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    base_prices = {'AAPL': 150.0, 'GOOGL': 2800.0, 'MSFT': 350.0, 'TSLA': 800.0}
    
    missing_detector = MissingDataDetector(threshold_minutes=2)
    movement_detector = PriceMovementDetector(threshold_percent=3.0)
    
    print("🚀 Starting real-time simulation (10 iterations)...")
    
    all_data = []
    total_anomalies = 0
    
    for i in range(10):
        print(f"\n⏰ Iteration {i+1}/10")
        
        # Generate some market data
        current_data = []
        for symbol in symbols:
            # Simulate price changes
            if random.random() < 0.8:  # 80% chance of normal data
                price_change = random.uniform(-2, 2)  # Normal ±2%
            else:  # 20% chance of abnormal movement
                price_change = random.uniform(-8, 8)  # Abnormal ±8%
            
            new_price = base_prices[symbol] * (1 + price_change / 100)
            base_prices[symbol] = new_price
            
            # Sometimes skip data to simulate missing data
            if random.random() > 0.1:  # 90% chance of data
                current_data.append({
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat(),
                    'price': new_price
                })
        
        all_data.extend(current_data)
        
        # Run detection on recent data
        recent_data = all_data[-20:] if len(all_data) > 20 else all_data
        
        missing_anomalies = missing_detector.detect(recent_data)
        movement_anomalies = movement_detector.detect(current_data)
        
        iteration_anomalies = len(missing_anomalies) + len(movement_anomalies)
        total_anomalies += iteration_anomalies
        
        if iteration_anomalies > 0:
            print(f"   🚨 {iteration_anomalies} anomalies detected")
            for anomaly in missing_anomalies:
                print(f"      Missing: {anomaly['symbol']}")
            for anomaly in movement_anomalies:
                change = anomaly['details']['price_change_percent']
                print(f"      Movement: {anomaly['symbol']} {change:+.1f}%")
        else:
            print(f"   ✅ No anomalies detected")
        
        time.sleep(0.5)  # Simulate real-time delay
    
    print(f"\n📈 Simulation Summary:")
    print(f"   Total data points: {len(all_data)}")
    print(f"   Total anomalies: {total_anomalies}")
    print(f"   Anomaly rate: {total_anomalies/len(all_data)*100:.1f}%")

def demo_api_simulation():
    """Simulate the FastAPI endpoints"""
    print("\n🔍 Demo: API Simulation")
    print("-" * 40)
    
    # Import the FastAPI models
    sys.path.append('python-services/detection-engine/src/api')
    
    try:
        # Simulate API calls
        from datetime import datetime
        
        # Sample data that would come from API
        api_data = [
            {
                "symbol": "AAPL",
                "timestamp": datetime.now().isoformat(),
                "source": "gemfire",
                "data_type": "price",
                "payload": {"price": 150.0, "volume": 1000},
                "price": 150.0,
                "volume": 1000.0
            },
            {
                "symbol": "AAPL", 
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "source": "gemfire",
                "data_type": "price", 
                "payload": {"price": 160.0, "volume": 1200},
                "price": 160.0,
                "volume": 1200.0
            }
        ]
        
        print("📡 Simulating API endpoints...")
        print(f"   Input: {len(api_data)} market data points")
        
        # Convert to format expected by detectors
        detector_data = [
            {
                'symbol': dp['symbol'],
                'timestamp': dp['timestamp'],
                'price': dp['price']
            }
            for dp in api_data
        ]
        
        # Run detections
        from algorithms.missing_data_detector import MissingDataDetector
        from algorithms.price_movement_detector import PriceMovementDetector
        
        missing_detector = MissingDataDetector()
        movement_detector = PriceMovementDetector()
        
        missing_results = missing_detector.detect(detector_data)
        movement_results = movement_detector.detect(detector_data)
        
        print(f"   Missing data anomalies: {len(missing_results)}")
        print(f"   Price movement anomalies: {len(movement_results)}")
        
        # Format results as API would return
        all_results = missing_results + movement_results
        
        print("📤 API Response simulation:")
        for result in all_results:
            print(f"   {json.dumps(result, indent=2, default=str)}")
        
        if not all_results:
            print("   ✅ No anomalies detected - system healthy")
            
    except Exception as e:
        print(f"❌ API simulation failed: {e}")

def main():
    """Run all demos"""
    print("🎯 Market Data Anomaly Detection System - Demo")
    print("=" * 60)
    print("This demo showcases the core detection algorithms")
    print("without requiring Java/Maven installation.")
    print("=" * 60)
    
    try:
        # Run all demos
        demo_missing_data_detection()
        demo_price_movement_detection()
        demo_real_time_simulation()
        demo_api_simulation()
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed successfully!")
        print("\n📋 What was demonstrated:")
        print("   ✅ Missing data detection algorithm")
        print("   ✅ Price movement detection algorithm") 
        print("   ✅ Real-time simulation")
        print("   ✅ API endpoint simulation")
        print("\n🚀 Next steps:")
        print("   • Install Java 17+ and Maven to build full system")
        print("   • Run './start-system.sh' for complete deployment")
        print("   • Access APIs at http://localhost:8080-8085")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
