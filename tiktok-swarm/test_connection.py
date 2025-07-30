"""Test if the API is running and accessible"""
import requests
import socket

def check_port(host, port):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

print("Testing API connectivity...\n")

# Check if port 8000 is open
if check_port("localhost", 8000):
    print("✓ Port 8000 is open")
    
    # Try to connect to the API
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✓ API is responding! Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API at http://localhost:8000")
    except Exception as e:
        print(f"✗ Error: {e}")
        
    # Try 127.0.0.1 instead of localhost
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"\n✓ API accessible via 127.0.0.1: {response.status_code}")
    except:
        print("\n✗ Cannot connect via 127.0.0.1")
        
else:
    print("✗ Port 8000 is not open. Is the server running?")
    print("\nTry running: python run_local.py")

# Also check common alternative ports
for port in [3000, 5000, 8080]:
    if check_port("localhost", port):
        print(f"\nNote: Port {port} is open - maybe the server is running there?")

print("\n\nIf the server is running but not accessible:")
print("1. Check Windows Firewall settings")
print("2. Try: http://127.0.0.1:8000 instead of localhost")
print("3. Make sure no other app is using port 8000")