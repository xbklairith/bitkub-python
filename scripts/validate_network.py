#!/usr/bin/env python3
"""
Network connectivity and API endpoint test for Bitkub API.

Tests network connectivity, response times, and basic API functionality.
"""

import os
import sys
import time
from typing import Dict

import requests

# Add the parent directory to the path so we can import bitkub
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bitkub import Client


def test_network_connectivity() -> bool:
    """Test basic network connectivity to Bitkub API."""
    print("🌐 Testing Network Connectivity")
    print("-" * 40)

    base_url = "https://api.bitkub.com"

    try:
        # Test basic connectivity
        print("1. Testing basic connectivity...")
        start_time = time.time()
        response = requests.get(f"{base_url}/api/status", timeout=10)
        end_time = time.time()

        if response.status_code == 200:
            print(f"   ✅ Connected successfully ({end_time - start_time:.2f}s)")
        else:
            print(f"   ❌ HTTP {response.status_code}")
            return False

        # Test response format
        print("2. Testing response format...")
        try:
            response.json()
            print("   ✅ Valid JSON response")
        except Exception:
            print("   ❌ Invalid JSON response")
            return False

        return True

    except requests.exceptions.Timeout:
        print("   ❌ Connection timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def test_endpoint_response_times() -> Dict[str, float]:
    """Test response times for different endpoints."""
    print("\n⏱️ Testing Endpoint Response Times")
    print("-" * 40)

    client = Client()
    endpoints = [
        ("Status", lambda: client.fetch_status()),
        ("Server Time", lambda: client.fetch_server_time()),
        ("Symbols", lambda: client.fetch_symbols()),
        ("Ticker (All)", lambda: client.fetch_tickers()),
        (
            "Ticker (BTC)",
            lambda: client.fetch_tickers("BTC_THB"),
        ),  # Fixed symbol format
        ("Trades", lambda: client.fetch_trades("BTC_THB", 10)),  # Fixed symbol format
        ("Bids", lambda: client.fetch_bids("BTC_THB", 10)),  # Fixed symbol format
        ("Asks", lambda: client.fetch_asks("BTC_THB", 10)),  # Fixed symbol format
    ]

    times = {}

    for name, func in endpoints:
        try:
            start_time = time.time()
            func()
            end_time = time.time()

            duration = end_time - start_time
            times[name] = duration

            print(f"{name:15} {duration:6.3f}s ✅")

        except Exception as e:
            print(f"{name:15} FAILED ❌ - {e}")
            times[name] = -1

        time.sleep(0.2)  # Rate limiting

    return times


def test_rate_limiting() -> None:
    """Test API rate limiting behavior."""
    print("\n🚦 Testing Rate Limiting")
    print("-" * 40)

    client = Client()

    print("Making 5 rapid requests to test rate limiting...")

    success_count = 0
    for i in range(5):
        try:
            start_time = time.time()
            client.fetch_server_time()
            end_time = time.time()

            success_count += 1
            print(f"   Request {i + 1}: {end_time - start_time:.3f}s ✅")

        except Exception as e:
            print(f"   Request {i + 1}: FAILED ❌ - {e}")

    print(f"\nRate limiting test: {success_count}/5 requests succeeded")

    if success_count >= 4:
        print("✅ Rate limiting is reasonable")
    else:
        print("⚠️ Possible rate limiting issues")


def test_data_consistency() -> None:
    """Test data consistency across multiple requests."""
    print("\n🔄 Testing Data Consistency")
    print("-" * 40)

    client = Client()

    try:
        # Test server time consistency
        print("1. Testing server time consistency...")
        times = []
        for _ in range(3):
            response = client.fetch_server_time()
            # API returns integer timestamp, not dict with 'ts' key
            if isinstance(response, int):
                times.append(response)
            else:
                times.append(response.get("ts", response))
            time.sleep(1)

        # Check if times are increasing (within reason) - timestamps are in milliseconds
        time_diffs = [
            (times[i + 1] - times[i]) / 1000 for i in range(len(times) - 1)
        ]  # Convert to seconds
        if all(0 <= diff <= 5 for diff in time_diffs):
            print("   ✅ Server times are consistent")
        else:
            print(f"   ⚠️ Server time inconsistency: {time_diffs}")

        # Test symbol count consistency
        print("2. Testing symbol count consistency...")
        symbol_counts = []
        for _ in range(2):
            response = client.fetch_symbols()
            symbol_counts.append(len(response["result"]))
            time.sleep(0.5)

        if len(set(symbol_counts)) == 1:
            print(f"   ✅ Symbol count consistent: {symbol_counts[0]}")
        else:
            print(f"   ⚠️ Symbol count varies: {symbol_counts}")

    except Exception as e:
        print(f"   ❌ Consistency test failed: {e}")


def test_error_handling() -> None:
    """Test error handling with invalid requests."""
    print("\n🚨 Testing Error Handling")
    print("-" * 40)

    client = Client()

    # Test invalid symbol
    print("1. Testing invalid symbol...")
    try:
        response = client.fetch_tickers("INVALID_SYMBOL")
        if "INVALID_SYMBOL" not in response:
            print("   ✅ Invalid symbol handled correctly")
        else:
            print("   ⚠️ Invalid symbol returned data")
    except Exception as e:
        print(f"   ✅ Invalid symbol raised exception: {type(e).__name__}")

    # Test invalid parameters
    print("2. Testing invalid parameters...")
    try:
        response = client.fetch_trades("BTC_THB", limit=0)  # Fixed symbol format
        print("   ⚠️ Invalid limit parameter accepted")
    except Exception as e:
        print(f"   ✅ Invalid parameter raised exception: {type(e).__name__}")


def generate_summary_report(response_times: Dict[str, float]) -> None:
    """Generate a summary report."""
    print("\n📊 Summary Report")
    print("=" * 50)

    # Response time statistics
    valid_times = [t for t in response_times.values() if t > 0]
    if valid_times:
        avg_time = sum(valid_times) / len(valid_times)
        max_time = max(valid_times)
        min_time = min(valid_times)

        print("Response Time Statistics:")
        print(f"   Average: {avg_time:.3f}s")
        print(f"   Fastest: {min_time:.3f}s")
        print(f"   Slowest: {max_time:.3f}s")

        if avg_time < 1.0:
            print("   ✅ Response times are good")
        elif avg_time < 3.0:
            print("   ⚠️ Response times are acceptable")
        else:
            print("   ❌ Response times are slow")

    # Endpoint success rate
    successful_endpoints = sum(1 for t in response_times.values() if t > 0)
    total_endpoints = len(response_times)
    success_rate = successful_endpoints / total_endpoints * 100

    print(
        f"\nEndpoint Success Rate: {successful_endpoints}/{total_endpoints} ({success_rate:.1f}%)"
    )

    if success_rate >= 90:
        print("✅ Excellent API connectivity")
    elif success_rate >= 70:
        print("⚠️ Good API connectivity with some issues")
    else:
        print("❌ Poor API connectivity")


def main() -> None:
    """Run all network and connectivity tests."""
    print("🚀 Bitkub API Network & Connectivity Test")
    print("=" * 50)

    start_time = time.time()

    # Run tests
    network_ok = test_network_connectivity()

    if network_ok:
        response_times = test_endpoint_response_times()
        test_rate_limiting()
        test_data_consistency()
        test_error_handling()
        generate_summary_report(response_times)
    else:
        print("\n❌ Network connectivity failed. Cannot proceed with other tests.")
        return

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\n⏱️ Total test time: {total_time:.2f} seconds")
    print("🏁 Network test completed!")


if __name__ == "__main__":
    main()
