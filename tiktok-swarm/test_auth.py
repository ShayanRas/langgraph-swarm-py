#!/usr/bin/env python3
"""Test script for authentication flow"""
import requests
import json
import sys
from datetime import datetime

# Base URL - change this if running on a different host/port
BASE_URL = "http://localhost:8000"

def print_response(response, title="Response"):
    """Pretty print API response"""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body (text): {response.text}")
    print("-" * 50)

def test_health():
    """Test health endpoint (no auth required)"""
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/test/health")
    print_response(response, "Health Check")
    return response.status_code == 200

def test_signup(email, password, redirect_to=None):
    """Test signup endpoint"""
    print(f"\n2. Testing signup with email: {email}")
    data = {"email": email, "password": password}
    if redirect_to:
        data["redirect_to"] = redirect_to
    
    response = requests.post(
        f"{BASE_URL}/auth/signup",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "Signup")
    return response

def test_signin(email, password):
    """Test signin endpoint"""
    print(f"\n3. Testing signin with email: {email}")
    response = requests.post(
        f"{BASE_URL}/auth/signin",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "Signin")
    return response

def test_protected(token):
    """Test protected endpoint"""
    print("\n4. Testing protected endpoint with token...")
    response = requests.get(
        f"{BASE_URL}/test/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response, "Protected Endpoint")
    return response.status_code == 200

def test_me(token):
    """Test /auth/me endpoint"""
    print("\n5. Testing /auth/me endpoint...")
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response, "Get Current User")
    return response.status_code == 200

def test_resend_confirmation(email):
    """Test resend confirmation endpoint"""
    print(f"\n6. Testing resend confirmation for email: {email}")
    response = requests.post(
        f"{BASE_URL}/auth/resend-confirmation",
        json={"email": email, "password": "dummy"},
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "Resend Confirmation")
    return response

def main():
    """Run auth tests"""
    print("🧪 TikTok Swarm Auth Test Suite")
    print("================================")
    print(f"Testing against: {BASE_URL}")
    
    # Check if user wants to use existing credentials
    if len(sys.argv) > 2:
        test_email = sys.argv[1]
        test_password = sys.argv[2]
        print(f"\nUsing provided credentials:")
        print(f"Email: {test_email}")
        skip_signup = True
    else:
        # Test credentials - use a more realistic email
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        test_email = f"testuser{timestamp}@gmail.com"  # Use gmail.com instead of example.com
        test_password = "TestPassword123!"
        skip_signup = False
        
        print(f"\nTest credentials:")
        print(f"Email: {test_email}")
        print(f"Password: {test_password}")
        print("\nTip: To test with existing user, run:")
        print(f"  python {sys.argv[0]} <email> <password>")
    
    # 1. Test health (no auth)
    if not test_health():
        print("❌ Health check failed!")
        return
    
    # 2. Test signup (skip if using existing credentials)
    if not skip_signup:
        # Test with custom redirect URL
        custom_redirect = f"{BASE_URL}/auth/confirm"
        signup_response = test_signup(test_email, test_password, redirect_to=custom_redirect)
        
        if signup_response.status_code == 201:
            data = signup_response.json()
            if data.get("requires_email_confirmation"):
                print("\n📧 Email confirmation required!")
                print(f"✉️  A confirmation email has been sent to: {test_email}")
                print(f"📍 The confirmation link will redirect to: {custom_redirect}")
                print("\nWhat to do next:")
                print("1. Check your email for the confirmation link")
                print("2. Click the link to confirm your email")
                print("3. You'll be redirected to a success page")
                print("4. Then you can sign in with your credentials")
                
                # Test resend confirmation
                print("\n🔄 Testing resend confirmation endpoint...")
                resend_response = test_resend_confirmation(test_email)
                if resend_response.status_code == 200:
                    print("✅ Resend confirmation works!")
                
                print("\n💡 For development testing, you can:")
                print("1. Use the Supabase dashboard to manually confirm users")
                print("2. Or disable email confirmation in Auth > Settings")
                print("3. Or use an existing confirmed account")
                return
        
        if signup_response.status_code not in [200, 201]:
            print("❌ Signup failed!")
            print("\nPossible reasons:")
            print("1. Email domain might be restricted by Supabase")
            print("2. Password might not meet requirements (min 6 chars)")
            print("3. User might already exist")
            print("\nTrying signin instead...")
    
    # 3. Test signin
    signin_response = test_signin(test_email, test_password)
    
    if signin_response.status_code != 200:
        print("❌ Signin failed!")
        return
    
    # Extract token
    auth_data = signin_response.json()
    access_token = auth_data.get("access_token")
    
    if not access_token:
        print("❌ No access token received!")
        return
    
    print(f"\n✅ Got access token: {access_token[:50]}...")
    
    # 4. Test protected endpoint
    if not test_protected(access_token):
        print("❌ Protected endpoint test failed!")
        return
    
    # 5. Test /auth/me
    if not test_me(access_token):
        print("❌ Get current user test failed!")
        return
    
    print("\n✅ All tests passed!")
    print("\n📝 To use the API:")
    print(f"1. Include this header in your requests: Authorization: Bearer {access_token[:20]}...")
    print("2. Access tokens expire after 1 hour by default")
    print("3. Use the refresh token to get a new access token when needed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)