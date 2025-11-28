# Quick Start Guide

## Launch the GUI

```bash
python file_transfer_gui.py
```

## To Receive Files

1. Click the **"Receive Files"** tab
2. Give your machine a friendly name (default is your computer's hostname)
3. (Optional) Click **"Browse"** to choose where to save files
4. Click **"Start Receiver"**
5. Your machine will now be discoverable by others on the network
6. Wait for incoming files - they'll appear in the log when received

## To Send a File

1. Click the **"Send File"** tab
2. **Option A**: Select a machine from the "Discovered Machines" list (automatically filled)
   - **Option B**: Manually enter the receiver's IP address
3. Click **"Browse"** to select a file
4. Click **"Send File"**
5. Watch the progress bar and log for transfer status

## Tips

- Both computers must be on the same network for discovery to work
- Machines appear in the list within 2-3 seconds of starting their receiver
- If a machine doesn't appear, you can still enter its IP address manually
- Use the default port (5000) unless it's already in use
- Keep the receiver running while sending files
- Check firewall settings if connection or discovery fails
