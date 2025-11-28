"""
Service Discovery Module
Allows machines to broadcast their names and be discovered on the local network
"""
import socket
import struct
import threading
import json
import time
from typing import Dict, Optional, Callable


class ServiceDiscovery:
    MULTICAST_GROUP = '239.255.77.77'
    MULTICAST_PORT = 5007
    BEACON_INTERVAL = 2  # seconds
    TIMEOUT = 6  # seconds (3 missed beacons)
    
    def __init__(self, machine_name: str, port: int, callback: Optional[Callable] = None):
        """
        Initialize service discovery
        
        Args:
            machine_name: Name to broadcast for this machine
            port: Port number where file transfer server is listening
            callback: Optional callback function when peers list changes
        """
        self.machine_name = machine_name
        self.port = port
        self.callback = callback
        self.running = False
        self.peers: Dict[str, dict] = {}  # {machine_name: {ip, port, last_seen}}
        self.local_ip = self._get_local_ip()  # CORREZIONE: nome del metodo corretto
        
        # Threading
        self.beacon_thread = None
        self.listen_thread = None
        self.cleanup_thread = None
        self.lock = threading.Lock()
        
    def start(self):
        """Start broadcasting and listening for peers"""
        if self.running:
            return
            
        self.running = True
        
        # Start beacon broadcaster
        self.beacon_thread = threading.Thread(target=self._broadcast_beacon, daemon=True)
        self.beacon_thread.start()
        
        # Start listener
        self.listen_thread = threading.Thread(target=self._listen_for_beacons, daemon=True)
        self.listen_thread.start()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_stale_peers, daemon=True)
        self.cleanup_thread.start()
        
    def stop(self):
        """Stop broadcasting and listening"""
        self.running = False
        if self.beacon_thread:
            self.beacon_thread.join(timeout=1)
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=1)
            
    def get_peers(self) -> Dict[str, dict]:
        """Get current list of discovered peers"""
        with self.lock:
            return {name: {'ip': info['ip'], 'port': info['port']} 
                   for name, info in self.peers.items()}
                   
    def get_peer_ip(self, machine_name: str) -> Optional[str]:
        """Get IP address for a specific machine name"""
        with self.lock:
            peer = self.peers.get(machine_name)
            return peer['ip'] if peer else None
            
    def _broadcast_beacon(self):
        """Broadcast this machine's presence"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        
        message = json.dumps({
            'name': self.machine_name,
            'ip': self.local_ip,
            'port': self.port,
            'timestamp': time.time()
        })
        
        try:
            while self.running:
                sock.sendto(message.encode('utf-8'), 
                          (self.MULTICAST_GROUP, self.MULTICAST_PORT))
                time.sleep(self.BEACON_INTERVAL)
        finally:
            sock.close()
            
    def _listen_for_beacons(self):
        """Listen for beacons from other machines"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind to the multicast port
        sock.bind(('', self.MULTICAST_PORT))
        
        # Join multicast group
        mreq = struct.pack('4sl', socket.inet_aton(self.MULTICAST_GROUP), 
                          socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.settimeout(1.0)
        
        try:
            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = json.loads(data.decode('utf-8'))
                    
                    # Don't add ourselves
                    if message['name'] == self.machine_name:
                        continue
                        
                    # Update peer information
                    with self.lock:
                        old_peers = set(self.peers.keys())
                        self.peers[message['name']] = {
                            'ip': message['ip'],
                            'port': message['port'],
                            'last_seen': time.time()
                        }
                        new_peers = set(self.peers.keys())
                        
                        # Trigger callback if peers changed
                        if old_peers != new_peers and self.callback:
                            self.callback()
                            
                except socket.timeout:
                    continue
                except (json.JSONDecodeError, KeyError):
                    continue
                    
        finally:
            sock.close()
            
    def _cleanup_stale_peers(self):
        """Remove peers that haven't been seen recently"""
        while self.running:
            time.sleep(self.BEACON_INTERVAL)
            current_time = time.time()
            
            with self.lock:
                old_peers = set(self.peers.keys())
                stale = [name for name, info in self.peers.items() 
                        if current_time - info['last_seen'] > self.TIMEOUT]
                
                for name in stale:
                    del self.peers[name]
                    
                new_peers = set(self.peers.keys())
                
                # Trigger callback if peers changed
                if old_peers != new_peers and self.callback:
                    self.callback()
                    
    def _get_local_ip(self) -> str:  # CORREZIONE: nome del metodo corretto
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"


# Command-line test
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python service_discovery.py <machine_name>")
        sys.exit(1)
        
    machine_name = sys.argv[1]
    
    def on_peers_changed():
        print(f"\nDiscovered peers: {discovery.get_peers()}")
        
    discovery = ServiceDiscovery(machine_name, 5000, callback=on_peers_changed)
    discovery.start()
    
    print(f"Broadcasting as '{machine_name}'...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        discovery.stop()