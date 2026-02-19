"""USB Detection Handler - Monitors USB/Pendrive connections"""
import os
import threading
import time
from utils.voice_io import speak
from utils.logger import log_interaction
from config.settings import OS

# Track connected USB devices
connected_usbs = set()
monitoring = False


def get_connected_usbs_windows():
    """Get list of USB drives and connected mobile devices on Windows"""
    try:
        import subprocess
        drives = set()
        
        # Get all logical disks with drivetype
        result = subprocess.run(
            ["wmic", "logicaldisk", "get", "name,drivetype,description"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        lines = result.stdout.strip().split('\n')
        
        # Parse each line carefully
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip header line
            if 'DriveType' in line or 'Description' in line:
                continue
            
            parts = line.split()
            
            # The format is: [Description words...] DriveType Name
            # So we need to find the drive letter (X:) and work backwards
            # Look for a part that is a drive letter (single letter followed by colon)
            
            drive_name = None
            drive_type = None
            
            # Find the drive letter (X:) - it should be one of the last parts
            for part in parts:
                if len(part) == 2 and part[0].isalpha() and part[1] == ':':
                    drive_name = part
                    break
            
            if not drive_name:
                continue
            
            # Once we have drive_name, find drivetype which comes right before it
            drive_index = parts.index(drive_name)
            if drive_index > 0:
                try:
                    drive_type = int(parts[drive_index - 1])
                except (ValueError, IndexError):
                    continue
            else:
                continue
            
            # Now check the type and add if it's removable
            if drive_type == 2:
                # Type 2 = Removable (USB drives, pendrives)
                drives.add(drive_name)
            elif drive_type == 3 and "Removable" in line:
                # Type 3 with "Removable" in description
                drives.add(drive_name)
        
        return drives
    except Exception as e:
        return set()


def get_connected_usbs_linux():
    """Get list of USB drives on Linux"""
    try:
        import subprocess
        result = subprocess.run(
            ["lsblk", "-Jpl"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        drives = set()
        for line in result.stdout.split('\n'):
            if 'sr' in line or 'sd' in line and line.startswith('/dev/'):
                drives.add(line.split()[0])
        
        return drives
    except Exception:
        return set()


def get_connected_usbs_mac():
    """Get list of USB drives on macOS"""
    try:
        import subprocess
        result = subprocess.run(
            ["system_profiler", "SPUSBDataType"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        drives = set()
        # Parse the output to find USB devices
        if "Removable Media" in result.stdout:
            drives.add("USB Device Detected")
        
        return drives
    except Exception:
        return set()


def get_connected_usbs():
    """Get list of connected USB drives based on OS"""
    if OS == "windows":
        return get_connected_usbs_windows()
    elif OS == "darwin":
        return get_connected_usbs_mac()
    elif OS == "linux":
        return get_connected_usbs_linux()
    else:
        return set()


def monitor_usb_devices():
    """Background thread to monitor USB connections"""
    global connected_usbs, monitoring
    
    monitoring = True
    check_interval = 2  # Check every 2 seconds
    
    while monitoring:
        try:
            current_usbs = get_connected_usbs()
            
            # Check for newly connected USBs
            newly_connected = current_usbs - connected_usbs
            for usb in newly_connected:
                message = f"USB or Pendrive Injection Detected"
                speak(message)
                log_interaction("usb_detected", message, source="system")
            
            # Check for disconnected USBs
            disconnected = connected_usbs - current_usbs
            for usb in disconnected:
                message = f"Pendrive or USB Removed"
                speak(message)
                log_interaction("usb_removed", message, source="system")
            
            # Update the current state
            connected_usbs = current_usbs
            
            time.sleep(check_interval)
        
        except Exception as e:
            # Silent fail - don't interrupt the assistant
            time.sleep(check_interval)


def start_usb_monitoring():
    """Start USB monitoring in background thread"""
    global monitoring
    
    if not monitoring:
        # Initialize with current USB state
        global connected_usbs
        connected_usbs = get_connected_usbs()
        
        # Start monitoring thread
        usb_thread = threading.Thread(target=monitor_usb_devices, daemon=True)
        usb_thread.start()


def stop_usb_monitoring():
    """Stop USB monitoring"""
    global monitoring
    monitoring = False


def handle_usb_detection(command):
    """Handle USB detection queries"""
    command_lower = command.lower()
    
    # Keywords that indicate USB DETECTION (not definition/information queries)
    detection_keywords = [
        "detect", "connected", "any usb", "is there", "how many", "list",
        "available", "pendrive", "pen drive", "flash drive", "external drive",
        "removable", "storage device", "drives present"
    ]
    
    # Keywords that should NOT trigger USB detection (these are information queries)
    exclusion_keywords = [
        "full form", "meaning", "what is", "abbreviation", "definition",
        "stand for", "stands for"
    ]
    
    # Check if this is asking for USB information/definition (not detection)
    is_info_query = any(keyword in command_lower for keyword in exclusion_keywords)
    if is_info_query:
        return False
    
    # Check if this is a USB detection query
    is_usb_query = any(keyword in command_lower for keyword in detection_keywords)
    
    if not is_usb_query:
        return False
    
    # Get current USB devices
    current_usbs = get_connected_usbs()
    
    if current_usbs:
        # Found USB device(s)
        if len(current_usbs) == 1:
            usb_list = list(current_usbs)[0]
            response = f"USB device found: {usb_list}. You have 1 removable drive connected."
        else:
            usb_list = ", ".join(sorted(list(current_usbs)))
            response = f"USB devices found: {usb_list}. You have {len(current_usbs)} removable drives connected."
    else:
        response = "No USB device or Pendrive is currently connected to your device."
    
    print(response)
    speak(response)
    log_interaction(command, response, source="usb_detection")
    return True
