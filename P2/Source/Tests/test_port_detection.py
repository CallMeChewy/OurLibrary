#!/usr/bin/env python3
# File: test_port_detection.py
# Path: AndyGoogle/test_port_detection.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-12
# Last Modified: 2025-07-12  07:45PM
"""
Description: Test AndyGoogle's enhanced port detection capabilities
Demonstrates how the system handles busy ports and finds alternatives
"""

import socket
import time
from StartAndyGoogle import AndyGoogleStarter

def occupy_port(port, duration=2):
    """Temporarily occupy a port to simulate conflicts"""
    print(f"🔒 Temporarily occupying port {port} for {duration} seconds...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('127.0.0.1', port))
        sock.listen(1)
        time.sleep(duration)
    except Exception as e:
        print(f"   Could not occupy port {port}: {e}")
    finally:
        sock.close()
        print(f"🔓 Released port {port}")

def main():
    """Test port detection scenarios"""
    print("🧪 Testing AndyGoogle Port Detection")
    print("=" * 50)
    
    starter = AndyGoogleStarter()
    
    # Test 1: Normal operation (port 8000 available)
    print("\n📋 Test 1: Normal port detection")
    port = starter.find_available_port(8000)
    if port:
        print(f"✅ Found port: {port}")
    else:
        print("❌ No port found")
    
    # Test 2: Port 8000 busy (simulate HP printer conflict)
    print("\n📋 Test 2: Port 8000 busy (simulating HP printer)")
    import threading
    import time
    
    # Start a background thread to occupy port 8000
    def occupy_8000():
        occupy_port(8000, 3)
    
    thread = threading.Thread(target=occupy_8000, daemon=True)
    thread.start()
    
    time.sleep(0.5)  # Let the port get occupied
    
    port = starter.find_available_port(8000)
    if port:
        print(f"✅ Found alternative port: {port}")
    else:
        print("❌ No alternative port found")
    
    # Test 3: Multiple ports busy
    print("\n📋 Test 3: Multiple common ports busy")
    
    def occupy_multiple():
        sockets = []
        for test_port in [8000, 8001, 8002]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('127.0.0.1', test_port))
                sock.listen(1)
                sockets.append(sock)
                print(f"🔒 Occupied port {test_port}")
            except:
                pass
        
        time.sleep(2)
        
        for sock in sockets:
            sock.close()
        print("🔓 Released all test ports")
    
    thread2 = threading.Thread(target=occupy_multiple, daemon=True)
    thread2.start()
    
    time.sleep(0.5)
    
    port = starter.find_available_port(8000)
    if port:
        print(f"✅ Found available port despite conflicts: {port}")
    else:
        print("❌ Could not find any available port")
    
    # Test 4: Show current port usage
    print("\n📋 Test 4: Current port usage analysis")
    common_ports = [8000, 8001, 8080, 3000, 5000, 9000]
    
    for test_port in common_ports:
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind(('127.0.0.1', test_port))
            test_socket.close()
            print(f"✅ Port {test_port}: Available")
        except OSError:
            print(f"❌ Port {test_port}: Busy")
            starter.identify_port_user(test_port)
    
    print("\n🎉 Port detection testing completed!")
    print("\n💡 Usage examples:")
    print("   python StartAndyGoogle.py              # Auto-detect best port")
    print("   python StartAndyGoogle.py --port 8080  # Force specific port")
    print("   python StartAndyGoogle.py --port 3000  # Use development port")

if __name__ == "__main__":
    main()