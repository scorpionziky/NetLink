"""
Transfer Server Module
Handles receiving files from clients
"""
import socket
import os
import struct
from pathlib import Path


class TransferServer:
    BUFFER_SIZE = 4096
    
    def __init__(self, port=5000, output_dir='.'):
        self.port = port
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def start(self):
        """Start the server and listen for incoming connections"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', self.port))
            server_socket.listen(1)
            
            print(f"Server listening on port {self.port}")
            print(f"Files will be saved to: {self.output_dir.absolute()}")
            print("Waiting for connections...")
            
            while True:
                try:
                    conn, addr = server_socket.accept()
                    print(f"\nConnection from {addr[0]}:{addr[1]}")
                    self._receive_file(conn)
                except Exception as e:
                    print(f"Error handling connection: {e}")
    
    def _receive_file(self, conn):
        """Receive a file from the connected client"""
        try:
            # Receive filename length (4 bytes)
            filename_len_data = self._recv_exact(conn, 4)
            if not filename_len_data:
                return
            filename_len = struct.unpack('!I', filename_len_data)[0]
            
            # Receive filename
            filename_data = self._recv_exact(conn, filename_len)
            if not filename_data:
                return
            filename = filename_data.decode('utf-8')
            
            # Receive file size (8 bytes)
            filesize_data = self._recv_exact(conn, 8)
            if not filesize_data:
                return
            filesize = struct.unpack('!Q', filesize_data)[0]
            
            print(f"Receiving: {filename} ({self._format_size(filesize)})")
            
            # Receive file content
            output_path = self.output_dir / filename
            received = 0
            
            with open(output_path, 'wb') as f:
                while received < filesize:
                    chunk_size = min(self.BUFFER_SIZE, filesize - received)
                    data = conn.recv(chunk_size)
                    if not data:
                        break
                    f.write(data)
                    received += len(data)
                    
                    # Progress indicator
                    progress = (received / filesize) * 100
                    print(f"\rProgress: {progress:.1f}% ({self._format_size(received)}/{self._format_size(filesize)})", end='')
            
            print(f"\n✓ File saved to: {output_path.absolute()}")
            
            # Send acknowledgment
            conn.sendall(b'OK')
            
        except Exception as e:
            print(f"\nError receiving file: {e}")
        finally:
            conn.close()
    
    def _recv_exact(self, conn, size):
        """Receive exact amount of bytes"""
        data = b''
        while len(data) < size:
            chunk = conn.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
