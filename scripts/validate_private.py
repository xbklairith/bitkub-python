#!/usr/bin/env python3
"""
Private API validation script to test authenticated Bitkub API endpoints.

This script tests private endpoints that require API key and secret authentication.
Set BITKUB_API_KEY and BITKUB_API_SECRET environment variables before running.
"""

import os
import sys
import time
from typing import Optional, Tuple

# Add the parent directory to the path so we can import bitkub
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bitkub import BitkubException, Client


def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Get API credentials from environment variables."""
    api_key = os.getenv("BITKUB_API_KEY")
    api_secret = os.getenv("BITKUB_API_SECRET")

    if not api_key or not api_secret:
        print("❌ Missing API credentials!")
        print("   Set BITKUB_API_KEY and BITKUB_API_SECRET environment variables")
        print("   Example: export BITKUB_API_KEY='your-api-key'")
        print("           export BITKUB_API_SECRET='your-api-secret'")
        return None, None

    return api_key, api_secret


def test_user_endpoints(client: Client) -> bool:
    """Test user information endpoints."""
    print("\n👤 Testing User Endpoints")
    print("-" * 30)

    tests_passed = 0
    total_tests = 2

    try:
        # Test 1: User Limits
        print("1. Testing User Limits...")
        try:
            limits = client.fetch_user_limits()
            if isinstance(limits, dict):
                result = limits.get("result", {})
                if result:
                    print("   ✅ User limits retrieved")
                    if "usage" in result:
                        usage = result["usage"]
                        print(
                            f"   ✅ API usage: {usage.get('used', 0)}/{usage.get('limit', 'N/A')}"
                        )
                else:
                    print("   ✅ User limits response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 2: Trading Credits
        print("2. Testing Trading Credits...")
        try:
            credits = client.fetch_user_trade_credit()
            if isinstance(credits, dict):
                result = credits.get("result")
                if result is not None:
                    print(f"   ✅ Trading credits retrieved: {result}")
                else:
                    print("   ✅ Trading credits response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    except Exception as e:
        print(f"❌ User endpoint tests failed: {e}")

    print(f"   📊 User tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests


def test_wallet_endpoints(client: Client) -> bool:
    """Test wallet and balance endpoints."""
    print("\n💰 Testing Wallet Endpoints")
    print("-" * 30)

    tests_passed = 0
    total_tests = 2

    try:
        # Test 1: Wallet Info
        print("1. Testing Wallet Info...")
        try:
            wallet = client.fetch_wallet()
            if isinstance(wallet, dict):
                result = wallet.get("result", {})
                if result:
                    print("   ✅ Wallet info retrieved")
                    # Show some wallet balances (non-zero ones)
                    for currency, balance in result.items():
                        if (
                            isinstance(balance, (int, float, str))
                            and float(balance) > 0
                        ):
                            print(f"   ✅ {currency}: {balance}")
                            break  # Just show one example
                else:
                    print("   ✅ Wallet response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 2: Market Balances
        print("2. Testing Market Balances...")
        try:
            balances = client.fetch_balances()
            if isinstance(balances, dict):
                result = balances.get("result", {})
                if result:
                    print("   ✅ Market balances retrieved")
                    # Show available and reserved balances
                    if "available" in result:
                        available = result["available"]
                        print(f"   ✅ Available balances: {len(available)} currencies")
                    if "reserved" in result:
                        reserved = result["reserved"]
                        print(f"   ✅ Reserved balances: {len(reserved)} currencies")
                else:
                    print("   ✅ Market balances response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    except Exception as e:
        print(f"❌ Wallet endpoint tests failed: {e}")

    print(f"   📊 Wallet tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests


def test_order_endpoints(client: Client) -> bool:
    """Test order-related endpoints (read-only)."""
    print("\n📋 Testing Order Endpoints")
    print("-" * 30)

    tests_passed = 0
    total_tests = 3

    try:
        # Test 1: Open Orders
        print("1. Testing Open Orders...")
        try:
            open_orders = client.fetch_open_orders("BTC_THB")
            if isinstance(open_orders, dict):
                result = open_orders.get("result", [])
                if isinstance(result, list):
                    print(f"   ✅ Open orders retrieved: {len(result)} orders")
                else:
                    print("   ✅ Open orders response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 2: Order History (limit to recent orders)
        print("2. Testing Order History...")
        try:
            order_history = client.fetch_order_history(
                symbol="BTC_THB", page=1, limit=5
            )
            if isinstance(order_history, dict):
                result = order_history.get("result", [])
                if isinstance(result, list):
                    print(f"   ✅ Order history retrieved: {len(result)} orders")
                    if result:
                        latest = result[0]
                        if isinstance(latest, dict):
                            side = latest.get("side", "N/A")
                            amount = latest.get("amount", "N/A")
                            rate = latest.get("rate", "N/A")
                            print(f"   ✅ Latest order: {side} {amount} @ {rate}")
                else:
                    print("   ✅ Order history response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 3: Order Info
        print("3. Testing Order Info...")
        try:
            # Test with a dummy order ID (will likely fail gracefully)
            order_info = client.fetch_order_info(
                symbol="BTC_THB", order_id="123456", side="buy"
            )
            if isinstance(order_info, dict):
                result = order_info.get("result")
                if result is not None:
                    print("   ✅ Order info retrieved")
                else:
                    print("   ✅ Order info response received (no order found)")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException:
            # Expected for dummy order ID
            print("   ✅ Order info API accessible (expected error for dummy ID)")
            tests_passed += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")

    except Exception as e:
        print(f"❌ Order endpoint tests failed: {e}")

    print(f"   📊 Order tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests


def test_crypto_endpoints(client: Client) -> bool:
    """Test crypto-related endpoints (read-only)."""
    print("\n₿ Testing Crypto Endpoints")
    print("-" * 30)

    tests_passed = 0
    total_tests = 3

    try:
        # Test 1: Crypto Addresses (V3)
        print("1. Testing Crypto Addresses (V3)...")
        try:
            addresses = client.fetch_addresses()
            if isinstance(addresses, dict):
                result = addresses.get("result", [])
                if isinstance(result, list):
                    print(f"   ✅ Crypto addresses retrieved: {len(result)} addresses")
                else:
                    print("   ✅ Crypto addresses response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 2: Deposit History (limit to recent)
        print("2. Testing Deposit History...")
        try:
            deposits = client.fetch_deposits(page=1, limit=5)
            if isinstance(deposits, dict):
                result = deposits.get("result", [])
                if isinstance(result, list):
                    print(f"   ✅ Deposit history retrieved: {len(result)} deposits")
                else:
                    print("   ✅ Deposit history response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 3: Withdraw History (limit to recent)
        print("3. Testing Withdraw History...")
        try:
            withdraws = client.fetch_withdrawals(page=1, limit=5)
            if isinstance(withdraws, dict):
                result = withdraws.get("result", [])
                if isinstance(result, list):
                    print(
                        f"   ✅ Withdraw history retrieved: {len(result)} withdrawals"
                    )
                else:
                    print("   ✅ Withdraw history response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    except Exception as e:
        print(f"❌ Crypto endpoint tests failed: {e}")

    print(f"   📊 Crypto tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests


def test_crypto_v4_endpoints(client: Client) -> bool:
    """Test crypto V4 endpoints."""
    print("\n₿ Testing Crypto V4 Endpoints")
    print("-" * 30)

    tests_passed = 0
    total_tests = 5

    try:
        # Test 1: Crypto Addresses V4
        print("1. Testing Crypto Addresses V4...")
        try:
            addresses_v4 = client.fetch_crypto_addresses_v4()
            if isinstance(addresses_v4, dict):
                result = addresses_v4.get("result", [])
                if isinstance(result, list):
                    print(
                        f"   ✅ Crypto addresses V4 retrieved: {len(result)} addresses"
                    )
                else:
                    print("   ✅ Crypto addresses V4 response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 2: Crypto Deposits V4
        print("2. Testing Crypto Deposits V4...")
        try:
            deposits_v4 = client.fetch_crypto_deposits_v4()
            if isinstance(deposits_v4, dict):
                result = deposits_v4.get("result", [])
                if isinstance(result, list):
                    print(f"   ✅ Crypto deposits V4 retrieved: {len(result)} deposits")
                else:
                    print("   ✅ Crypto deposits V4 response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 3: Crypto Withdraws V4
        print("3. Testing Crypto Withdraws V4...")
        try:
            withdraws_v4 = client.fetch_crypto_withdraws_v4()
            if isinstance(withdraws_v4, dict):
                result = withdraws_v4.get("result", [])
                if isinstance(result, list):
                    print(
                        f"   ✅ Crypto withdraws V4 retrieved: {len(result)} withdrawals"
                    )
                else:
                    print("   ✅ Crypto withdraws V4 response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 4: Crypto Coins V4
        print("4. Testing Crypto Coins V4...")
        try:
            coins_v4 = client.fetch_crypto_coins_v4()
            if isinstance(coins_v4, dict):
                result = coins_v4.get("result", [])
                if isinstance(result, list):
                    print(f"   ✅ Crypto coins V4 retrieved: {len(result)} coins")
                else:
                    print("   ✅ Crypto coins V4 response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 5: Crypto Compensations V4
        print("5. Testing Crypto Compensations V4...")
        try:
            compensations_v4 = client.fetch_crypto_compensations_v4()
            if isinstance(compensations_v4, dict):
                result = compensations_v4.get("result", [])
                if isinstance(result, list):
                    print(
                        f"   ✅ Crypto compensations V4 retrieved: {len(result)} compensations"
                    )
                else:
                    print("   ✅ Crypto compensations V4 response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    except Exception as e:
        print(f"❌ Crypto V4 endpoint tests failed: {e}")

    print(f"   📊 Crypto V4 tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests


def test_fiat_endpoints(client: Client) -> bool:
    """Test fiat-related endpoints."""
    print("\n💳 Testing Fiat Endpoints")
    print("-" * 30)

    tests_passed = 0
    total_tests = 3

    try:
        # Test 1: Fiat Accounts
        print("1. Testing Fiat Accounts...")
        try:
            fiat_accounts = client.fetch_fiat_accounts()
            if isinstance(fiat_accounts, dict):
                result = fiat_accounts.get("result", [])
                if isinstance(result, list):
                    print(f"   ✅ Fiat accounts retrieved: {len(result)} accounts")
                else:
                    print("   ✅ Fiat accounts response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 2: Fiat Deposit History
        print("2. Testing Fiat Deposit History...")
        try:
            fiat_deposits = client.fetch_fiat_deposits(page=1, limit=5)
            if isinstance(fiat_deposits, dict):
                result = fiat_deposits.get("result", [])
                if isinstance(result, list):
                    print(
                        f"   ✅ Fiat deposit history retrieved: {len(result)} deposits"
                    )
                else:
                    print("   ✅ Fiat deposit history response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 3: Fiat Withdraw History
        print("3. Testing Fiat Withdraw History...")
        try:
            fiat_withdraws = client.fetch_fiat_withdrawals(page=1, limit=5)
            if isinstance(fiat_withdraws, dict):
                result = fiat_withdraws.get("result", [])
                if isinstance(result, list):
                    print(
                        f"   ✅ Fiat withdraw history retrieved: {len(result)} withdrawals"
                    )
                else:
                    print("   ✅ Fiat withdraw history response received")
                tests_passed += 1
            else:
                print("   ❌ Unexpected response format")
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    except Exception as e:
        print(f"❌ Fiat endpoint tests failed: {e}")

    print(f"   📊 Fiat tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests


def test_websocket_token(client: Client) -> bool:
    """Test WebSocket token generation."""
    print("\n🔌 Testing WebSocket Token")
    print("-" * 30)

    try:
        print("1. Testing WebSocket Token Generation...")
        try:
            ws_token = client.create_websocket_token()
            if isinstance(ws_token, dict):
                result = ws_token.get("result", {})
                if result and "token" in result:
                    token = result["token"]
                    print(f"   ✅ WebSocket token generated: {token[:20]}...")
                    return True
                else:
                    print("   ✅ WebSocket token response received")
                    return True
            else:
                print("   ❌ Unexpected response format")
                return False
        except BitkubException as e:
            print(f"   ❌ API Error: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    except Exception as e:
        print(f"❌ WebSocket token test failed: {e}")
        return False


def main() -> None:
    """Run the private API validation."""
    print("🔐 Bitkub Private API Validation")
    print("=" * 40)

    # Get credentials
    api_key, api_secret = get_credentials()
    if not api_key or not api_secret:
        return

    print(f"🔑 Using API Key: {api_key[:8]}...{api_key[-4:]}")

    # Initialize client with credentials
    try:
        client = Client(api_key=api_key, api_secret=api_secret)
        print("✅ Client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return

    start_time = time.time()

    # Run test suites
    results = {
        "user": test_user_endpoints(client),
        "wallet": test_wallet_endpoints(client),
        "orders": test_order_endpoints(client),
        "crypto": test_crypto_endpoints(client),
        "crypto_v4": test_crypto_v4_endpoints(client),
        "fiat": test_fiat_endpoints(client),
        "websocket": test_websocket_token(client),
    }

    # Summary
    end_time = time.time()
    duration = end_time - start_time

    print("\n📊 Test Summary")
    print("=" * 40)

    passed_count = sum(1 for result in results.values() if result)
    total_count = len(results)

    for category, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{category.capitalize():12} {status}")

    print(f"\n⏱️ Test completed in {duration:.2f} seconds")
    print(f"📈 Overall result: {passed_count}/{total_count} test suites passed")

    if passed_count == total_count:
        print("\n🎉 All private API tests passed!")
        print("   Your API credentials are working correctly.")
    else:
        print(f"\n⚠️ {total_count - passed_count} test suite(s) failed.")
        print("   Check your API permissions or contact Bitkub support.")

    print("\n💡 Note: This script only tests read-only endpoints.")
    print("   Trading operations are not tested for safety.")


if __name__ == "__main__":
    main()
