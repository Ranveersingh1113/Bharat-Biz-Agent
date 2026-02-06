#!/usr/bin/env python3
"""
Webhook Diagnostic Tool for WhatsApp Business API

This script helps diagnose issues with webhook URL configuration.
It tests if your webhook endpoint is properly accessible and responds
correctly to Meta's verification requests.

Usage:
    python test_webhook.py <your-webhook-url> <verify-token>
    
Example:
    python test_webhook.py https://myapp.com/api/webhook my_verify_token_123
"""

import sys
import requests
import json
from urllib.parse import urljoin, urlparse

def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_url_format(url):
    """Test if URL format is valid"""
    print_section("Step 1: URL Format Validation")
    
    try:
        parsed = urlparse(url)
        
        # Check if URL has a scheme
        if not parsed.scheme:
            print_error("URL must include a scheme (http:// or https://)")
            return False
        
        # Check if HTTPS
        if parsed.scheme != 'https':
            print_warning("Meta requires HTTPS! Your URL uses http://")
            print_info("For production, you MUST use HTTPS")
            print_info("For testing, you can use ngrok to get HTTPS URL")
        else:
            print_success("URL uses HTTPS ✓")
        
        # Check if URL has a hostname
        if not parsed.netloc:
            print_error("URL must include a hostname (e.g., myapp.com)")
            return False
        else:
            print_success(f"Hostname: {parsed.netloc} ✓")
        
        # Check path
        if not parsed.path or parsed.path == '/':
            print_warning("URL should include the path /api/webhook")
            print_info(f"Did you mean: {url.rstrip('/')}/api/webhook ?")
        else:
            print_success(f"Path: {parsed.path} ✓")
        
        # Check for common issues
        if parsed.netloc == 'localhost' or parsed.netloc.startswith('127.0.0.1'):
            print_error("Cannot use localhost! Meta cannot reach localhost.")
            print_info("You need a public URL. Use ngrok for testing:")
            print_info("  ngrok http 8000")
            return False
        
        if parsed.netloc.startswith('192.168.') or parsed.netloc.startswith('10.'):
            print_error("Cannot use private IP addresses!")
            print_info("You need a public URL. Use ngrok for testing.")
            return False
        
        print_success("URL format looks good!")
        return True
        
    except Exception as e:
        print_error(f"Invalid URL format: {e}")
        return False

def test_url_accessibility(url):
    """Test if URL is accessible"""
    print_section("Step 2: URL Accessibility Test")
    
    try:
        print_info(f"Testing GET request to: {url}")
        response = requests.get(url, timeout=10)
        
        print_success(f"URL is accessible! Status code: {response.status_code}")
        return True
        
    except requests.exceptions.SSLError as e:
        print_error("SSL Certificate Error!")
        print_info("Your HTTPS certificate may be invalid or self-signed")
        print_info("Meta requires a valid SSL certificate")
        print_info(f"Error: {e}")
        return False
        
    except requests.exceptions.ConnectionError:
        print_error("Connection Error!")
        print_info("Cannot connect to the URL. Possible issues:")
        print_info("  - Server is not running")
        print_info("  - Firewall blocking connections")
        print_info("  - URL is incorrect")
        return False
        
    except requests.exceptions.Timeout:
        print_error("Connection Timeout!")
        print_info("Server took too long to respond")
        return False
        
    except Exception as e:
        print_error(f"Error accessing URL: {e}")
        return False

def test_webhook_verification(url, verify_token):
    """Test webhook verification endpoint (simulating Meta's request)"""
    print_section("Step 3: Webhook Verification Test")
    
    # Simulate Meta's verification request
    test_challenge = "test_challenge_123456"
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": verify_token,
        "hub.challenge": test_challenge
    }
    
    try:
        print_info(f"Simulating Meta's verification request...")
        print_info(f"Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print_info(f"Response status code: {response.status_code}")
        print_info(f"Response content: {response.text}")
        
        # Check status code
        if response.status_code == 200:
            print_success("Status code is 200 ✓")
        else:
            print_error(f"Expected status code 200, got {response.status_code}")
            return False
        
        # Check if challenge is returned
        if response.text == test_challenge:
            print_success("Challenge returned correctly! ✓")
            print_success("Your webhook verification endpoint is working!")
            return True
        else:
            print_error("Challenge not returned correctly")
            print_info(f"Expected: {test_challenge}")
            print_info(f"Got: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Verification test failed: {e}")
        return False

def test_wrong_token(url, verify_token):
    """Test webhook with wrong token (should return 403)"""
    print_section("Step 4: Wrong Token Test")
    
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "wrong_token_12345",
        "hub.challenge": "test"
    }
    
    try:
        print_info("Testing with incorrect verify token (should fail)...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 403:
            print_success("Correctly rejects wrong token with 403 ✓")
            return True
        else:
            print_warning(f"Expected 403 for wrong token, got {response.status_code}")
            print_info("This might still work, but security could be improved")
            return True
            
    except Exception as e:
        print_error(f"Wrong token test failed: {e}")
        return False

def print_meta_configuration_guide(url, verify_token):
    """Print instructions for Meta configuration"""
    print_section("Meta Dashboard Configuration")
    
    print("\n📋 Copy these exact values into Meta Dashboard:\n")
    print(f"Callback URL:  {url}")
    print(f"Verify Token:  {verify_token}")
    
    print("\n⚠️  IMPORTANT:")
    print("1. The Callback URL must be EXACTLY as shown above")
    print("2. Include https:// at the beginning")
    print("3. Include /api/webhook at the end")
    print("4. No trailing slash")
    print("5. Verify Token is case-sensitive - copy exactly")
    
    print("\n📝 Steps in Meta Dashboard:")
    print("1. Go to your Meta App → WhatsApp → Configuration")
    print("2. Click 'Edit' next to Callback URL")
    print("3. Paste the Callback URL exactly as shown above")
    print("4. Paste the Verify Token exactly as shown above")
    print("5. Click 'Verify and Save'")
    print("6. Meta will send a verification request to your URL")
    print("7. If all tests above passed, it should work!")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("  WhatsApp Webhook Diagnostic Tool")
    print("="*70)
    
    # Check arguments
    if len(sys.argv) < 3:
        print("\n❌ Error: Missing required arguments\n")
        print("Usage:")
        print("  python test_webhook.py <webhook-url> <verify-token>")
        print("\nExample:")
        print("  python test_webhook.py https://myapp.com/api/webhook my_token_123")
        print("\nFor ngrok:")
        print("  python test_webhook.py https://abc123.ngrok.io/api/webhook my_token_123")
        sys.exit(1)
    
    webhook_url = sys.argv[1]
    verify_token = sys.argv[2]
    
    print(f"\n🔍 Testing webhook URL: {webhook_url}")
    print(f"🔐 Using verify token: {verify_token}")
    
    # Run tests
    all_passed = True
    
    # Test 1: URL Format
    if not test_url_format(webhook_url):
        all_passed = False
        print("\n❌ URL format test failed. Fix the URL format and try again.")
        sys.exit(1)
    
    # Test 2: URL Accessibility
    if not test_url_accessibility(webhook_url):
        all_passed = False
        print("\n❌ URL is not accessible. Make sure your server is running and accessible.")
        print("\nTroubleshooting:")
        print("- Is your server running? (python -m uvicorn server:app ...)")
        print("- If testing locally, are you using ngrok?")
        print("- Check firewall settings")
        sys.exit(1)
    
    # Test 3: Webhook Verification
    if not test_webhook_verification(webhook_url, verify_token):
        all_passed = False
        print("\n❌ Webhook verification failed.")
        print("\nTroubleshooting:")
        print("- Check that verify token in .env matches the token you're testing")
        print("- Restart your server after changing .env")
        print("- Check server logs for errors")
        sys.exit(1)
    
    # Test 4: Wrong Token
    test_wrong_token(webhook_url, verify_token)
    
    # Summary
    print_section("Summary")
    
    if all_passed:
        print_success("All tests passed! ✅")
        print_success("Your webhook is ready for Meta configuration!")
        print_meta_configuration_guide(webhook_url, verify_token)
    else:
        print_error("Some tests failed. Please fix the issues and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
