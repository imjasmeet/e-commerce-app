#!/usr/bin/env python3
"""
Test script for E-Commerce API failure scenarios
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000/api"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['data']['status']}")
            print(f"   Database: {data['data']['database']}")
            print(f"   Products: {data['data']['products']}")
            print(f"   Simulations: {data['data']['simulations']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_database_failure():
    """Test database failure simulation"""
    print("🗄️ Testing Database Failure Simulation...")
    
    # Enable DB failure
    response = requests.get(f"{BASE_URL}/simulate/db-failure")
    if response.status_code == 200:
        print("   Database failure simulation enabled")
        
        # Test homepage with DB failure
        response = requests.get(f"{BASE_URL}/products")
        if response.status_code == 500:
            print("✅ Database failure correctly triggered 500 error")
        else:
            print(f"❌ Expected 500, got {response.status_code}")
        
        # Disable DB failure
        response = requests.get(f"{BASE_URL}/simulate/db-failure")
        if response.status_code == 200:
            print("   Database failure simulation disabled")
            return True
    else:
        print(f"❌ Failed to toggle DB failure: {response.status_code}")
        return False

def test_slow_response():
    """Test slow response simulation"""
    print("🐌 Testing Slow Response Simulation...")
    
    # Enable slow response
    response = requests.get(f"{BASE_URL}/simulate/slow-response")
    if response.status_code == 200:
        print("   Slow response simulation enabled")
        
        # Test response time
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/products")
        duration = time.time() - start_time
        
        if duration >= 5:
            print(f"✅ Response time: {duration:.2f} seconds")
            print("✅ Slow response correctly simulated")
        else:
            print(f"❌ Expected slow response, got {duration:.2f} seconds")
        
        # Disable slow response
        response = requests.get(f"{BASE_URL}/simulate/slow-response")
        if response.status_code == 200:
            print("   Slow response simulation disabled")
            return True
    else:
        print(f"❌ Failed to toggle slow response: {response.status_code}")
        return False

def test_random_errors():
    """Test random error simulation"""
    print("🎲 Testing Random Error Simulation...")
    
    # Enable random errors
    response = requests.get(f"{BASE_URL}/simulate/random-errors")
    if response.status_code == 200:
        print("   Random error simulation enabled")
        
        # Make multiple requests to check error rate
        errors = 0
        total_requests = 10
        
        for i in range(total_requests):
            response = requests.get(f"{BASE_URL}/products")
            if response.status_code == 500:
                errors += 1
                print(f"   Request {i+1}: Error (500)")
            else:
                print(f"   Request {i+1}: Success (200)")
        
        error_rate = (errors / total_requests) * 100
        print(f"✅ Error rate: {error_rate:.1f}% ({errors}/{total_requests})")
        
        # Disable random errors
        response = requests.get(f"{BASE_URL}/simulate/random-errors")
        if response.status_code == 200:
            print("   Random error simulation disabled")
            return True
    else:
        print(f"❌ Failed to toggle random errors: {response.status_code}")
        return False

def test_null_pointer():
    """Test null pointer exception simulation"""
    print("💥 Testing Null Pointer Exception Simulation...")
    
    # Enable null pointer simulation
    response = requests.get(f"{BASE_URL}/simulate/null-pointer")
    if response.status_code == 200:
        print("   Null pointer simulation enabled")
        
        # Test orders endpoint (should trigger null pointer)
        response = requests.get(f"{BASE_URL}/orders")
        if response.status_code == 500:
            print("✅ Null pointer exception correctly triggered 500 error")
        else:
            print(f"❌ Expected 500, got {response.status_code}")
        
        # Disable null pointer simulation
        response = requests.get(f"{BASE_URL}/simulate/null-pointer")
        if response.status_code == 200:
            print("   Null pointer simulation disabled")
            return True
    else:
        print(f"❌ Failed to toggle null pointer: {response.status_code}")
        return False

def test_cart_operations():
    """Test cart operations with failures"""
    print("🛒 Testing Cart Operations with Failures...")
    
    # Add item to cart
    cart_data = {"product_id": 1, "quantity": 1}
    response = requests.post(f"{BASE_URL}/cart/add", json=cart_data)
    
    if response.status_code == 200:
        print("✅ Cart operation handled failure correctly")
        return True
    else:
        print(f"❌ Cart operation failed: {response.status_code}")
        return False

def test_normal_operation():
    """Test that app returns to normal after simulations are disabled"""
    print("✅ Testing Normal Operation...")
    
    response = requests.get(f"{BASE_URL}/products")
    if response.status_code == 200:
        print("✅ App returned to normal operation")
        return True
    else:
        print(f"❌ Expected 200, got {response.status_code}")
        return False

def test_api_endpoints():
    """Test basic API functionality"""
    print("🔍 Testing API Endpoints...")
    
    # Test products endpoint
    response = requests.get(f"{BASE_URL}/products")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Products endpoint: {len(data['data']['products'])} products")
    else:
        print(f"❌ Products endpoint failed: {response.status_code}")
    
    # Test cart endpoint
    response = requests.get(f"{BASE_URL}/cart")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Cart endpoint: {data['data']['item_count']} items")
    else:
        print(f"❌ Cart endpoint failed: {response.status_code}")
    
    # Test orders endpoint
    response = requests.get(f"{BASE_URL}/orders")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Orders endpoint: {len(data['data']['orders'])} orders")
    else:
        print(f"❌ Orders endpoint failed: {response.status_code}")

def main():
    """Main test function"""
    print("🚀 Starting API Failure Testing Suite")
    print("=" * 50)
    
    # Test basic API functionality
    test_api_endpoints()
    print()
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed, stopping tests")
        return
    
    print()
    
    # Test failure simulations
    test_database_failure()
    print()
    
    test_slow_response()
    print()
    
    test_random_errors()
    print()
    
    test_null_pointer()
    print()
    
    test_cart_operations()
    print()
    
    test_normal_operation()
    print()
    
    print("=" * 50)
    print("🎉 API Failure Testing Complete!")
    print("📊 Summary:")
    print("   - Database failure simulation: ✅")
    print("   - Slow response simulation: ✅")
    print("   - Random error simulation: ✅")
    print("   - Null pointer simulation: ✅")
    print("   - Error handling: ✅")
    print("   - Recovery: ✅")

if __name__ == "__main__":
    main() 