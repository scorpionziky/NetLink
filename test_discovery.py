#!/usr/bin/env python3
"""
Test script for service discovery
Run multiple instances to see machines discover each other
"""
import sys
import time
from service_discovery import ServiceDiscovery


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_discovery.py <machine_name> [port]")
        print("\nExample:")
        print("  Terminal 1: python test_discovery.py MyLaptop")
        print("  Terminal 2: python test_discovery.py MyDesktop")
        sys.exit(1)
    
    machine_name = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    
    print(f"Starting service discovery as '{machine_name}' on port {port}")
    print("This will broadcast your presence and listen for other machines.")
    print("Press Ctrl+C to stop\n")
    
    def on_peers_changed():
        peers = discovery.get_peers()
        print(f"\n[{time.strftime('%H:%M:%S')}] Discovered machines:")
        if peers:
            for name, info in peers.items():
                print(f"  - {name}: {info['ip']}:{info['port']}")
        else:
            print("  (none yet)")
    
    discovery = ServiceDiscovery(machine_name, port, callback=on_peers_changed)
    discovery.start()
    
    print("Broadcasting started...\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        discovery.stop()
        print("Done!")


if __name__ == '__main__':
    main()
