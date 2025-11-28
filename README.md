# File Transfer App

A simple, cross-platform command-line application for transferring files between computers over a local network.

## Features

- ✅ Cross-platform support (Windows, Linux, macOS)
- ✅ No external dependencies (uses Python standard library only)
- ✅ Graphical user interface (GUI) and command-line interface (CLI)
- ✅ **Service discovery**: Find machines by name instead of IP address
- ✅ Progress indicator during transfer
- ✅ TCP socket-based transfer for reliability
- ✅ Human-readable file size display

## Requirements

- Python 3.6 or higher (no additional packages required)

## Installation

1. Clone or download this repository
2. No additional installation required - uses only Python standard library

## Usage

### GUI Mode (Recommended)

For a user-friendly graphical interface:

```bash
python file_transfer_gui.py
```

The GUI provides:
- **Send File tab**: 
  - Automatically discover machines on your network by name
  - Or manually enter receiver's IP address
  - Select a file and send with visual progress
- **Receive Files tab**: 
  - Give your machine a friendly name for others to find
  - Start/stop the receiver
  - Choose output directory
  - See your IP address
- Real-time transfer logs
- Progress indicators
- Easy file and directory browsing

### Command-Line Mode

#### Receiving Files

On the computer that will receive the file, start the server:

```bash
python file_transfer.py receive --port 5000
```

Optional arguments:
- `--port`: Port to listen on (default: 5000)
- `--output-dir`: Directory to save received files (default: current directory)

Example with custom output directory:
```bash
python file_transfer.py receive --port 5000 --output-dir ./received_files
```

#### Sending Files

On the computer that will send the file:

```bash
python file_transfer.py send --host 192.168.1.100 --port 5000 --file document.pdf
```

Required arguments:
- `--host`: IP address or hostname of the receiving computer
- `--file`: Path to the file you want to send

Optional arguments:
- `--port`: Port of the receiver (default: 5000)

## How It Works

1. The receiving computer starts a server that listens for incoming connections
2. The sending computer connects to the server and transmits the file
3. The transfer includes:
   - Filename
   - File size
   - File contents
   - Progress indicator
   - Acknowledgment upon completion

## Finding Your IP Address

### Windows
```powershell
ipconfig
```
Look for "IPv4 Address"

### Linux/macOS
```bash
ip addr show    # Linux
ifconfig        # macOS/Linux
```
Look for "inet" address (usually 192.168.x.x or 10.x.x.x for local networks)

## Network Configuration

- Ensure both computers are on the same network (or have network connectivity)
- If you have a firewall enabled, you may need to allow incoming connections on the chosen port
- For security reasons, this application is designed for trusted local networks only

## Security Notes

⚠️ **Important**: This is a basic file transfer tool designed for use on trusted local networks. It does not include:
- Encryption
- Authentication
- Authorization

Do not use this over untrusted networks or the internet without additional security measures.

## Examples

### Example 1: Transfer a document to another computer on your home network

**Computer A (Receiver - IP: 192.168.1.100):**
```bash
python file_transfer.py receive --port 5000
```

**Computer B (Sender):**
```bash
python file_transfer.py send --host 192.168.1.100 --port 5000 --file report.pdf
```

### Example 2: Organize received files in a specific folder

**Receiver:**
```bash
python file_transfer.py receive --port 8080 --output-dir ~/Downloads/transfers
```

**Sender:**
```bash
python file_transfer.py send --host 192.168.1.100 --port 8080 --file vacation_photos.zip
```

## Troubleshooting

**Connection refused:**
- Ensure the receiver is running before attempting to send
- Verify the IP address is correct
- Check firewall settings on both computers
- Ensure both computers are on the same network

**File not found:**
- Verify the file path is correct
- Use absolute paths if relative paths aren't working

**Permission denied:**
- Ensure you have read permissions for the file you're sending
- Ensure you have write permissions in the output directory

## License

This project is open source and available for personal and commercial use.
## Author

Created by: Scorpionziky89

for any issues If you encounter any problems,bugs or have any questions, 
please contact me at scorpionziky89@gmail.com 