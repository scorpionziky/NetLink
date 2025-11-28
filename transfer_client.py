# ... existing code ...

class TransferClient:
    # ... existing code ...

    def send_file(self, filepath, progress_callback=None):
        """Send a file to the server"""
        # ... existing code ...

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # ... existing code ...

            # Send file content
            sent = 0
            with open(filepath, 'rb') as f:
                while sent < filesize:
                    data = f.read(self.BUFFER_SIZE)
                    if not data:
                        break
                    client_socket.sendall(data)
                    sent += len(data)
                    
                    # Progress indicator
                    progress = (sent / filesize) * 100
                    print(f"\rProgress: {progress:.1f}% ({self._format_size(sent)}/{self._format_size(filesize)})", end='')
                    if progress_callback:
                        progress_callback(progress)  # Call the progress callback

            # ... existing code ...

# ... existing code ...