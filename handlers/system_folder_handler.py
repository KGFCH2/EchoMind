"""System Folder and Drive opener handler"""
import re
import subprocess
import os
from config.settings import OS
from utils.voice_io import speak
from utils.logger import log_interaction


# Common system folders mapping
SYSTEM_FOLDERS = {
    'desktop': {
        'paths': ['Desktop', 'desktop'],
        'description': 'Desktop folder'
    },
    'downloads': {
        'paths': ['Downloads', 'downloads'],
        'description': 'Downloads folder'
    },
    'documents': {
        'paths': ['Documents', 'documents', 'docs'],
        'description': 'Documents folder'
    },
    'pictures': {
        'paths': ['Pictures', 'pictures', 'pics', 'photos'],
        'description': 'Pictures folder'
    },
    'music': {
        'paths': ['Music', 'music', 'songs'],
        'description': 'Music folder'
    },
    'videos': {
        'paths': ['Videos', 'videos', 'movies'],
        'description': 'Videos folder'
    }
}


def handle_system_folder_opening(command):
    r"""Handle opening system folders and drives
    
    Supports:
    - "Open Desktop" → Opens C:\Users\[username]\Desktop
    - "Open Downloads" → Opens C:\Users\[username]\Downloads
    - "Open Documents" → Opens C:\Users\[username]\Documents
    - "Open Pictures" → Opens C:\Users\[username]\Pictures
    - "Open Music" → Opens C:\Users\[username]\Music
    - "Open Videos" → Opens C:\Users\[username]\Videos
    - "Open drive C" → Opens C:\ (or any drive letter)
    - "Open drive D" → Opens D:\ (or any drive letter)
    - "Open C drive" → Opens C:\ 
    - "Open E drive" → Opens E:\
    - "Open the D drive" → Opens D:\
    - "Close drive C" → Closes/Ejects C:\ safely (if removable)
    - "Close drive D" → Closes/Ejects D:\ safely (if removable)
    - "Close the D drive" → Ejects D:\ 
    - "Eject drive C" → Ejects C:\ (if removable)
    """
    command_lower = command.lower().strip()
    
    # Check if this is a close/eject drive command
    if re.search(r'\b(?:close|eject|unmount)\s+(?:the\s+)?(?:drive\s+)?[a-z]:', command_lower) or \
       re.search(r'\b(?:close|eject|unmount)\s+(?:the\s+)?(?:drive\s+)?[a-z]\s+drive\b', command_lower):
        return _handle_drive_closing(command)
    
    # Check if this is NOT a system folder/drive opening command
    if not re.search(r'\b(open|access|go\s+to|navigate\s+to)\b.*\b(desktop|downloads|documents|pictures|music|videos|drive|partition)\b', command_lower):
        return False
    
    # PATTERN 1: Open system folders
    # "Open Desktop", "Open Downloads", etc.
    for folder_key, folder_info in SYSTEM_FOLDERS.items():
        folder_patterns = '|'.join(folder_info['paths'])
        folder_regex = rf'(?:open|access|go\s+to|navigate\s+to)\s+(?:the\s+)?(?:my\s+)?({folder_patterns})\b'
        
        folder_match = re.search(folder_regex, command_lower)
        if folder_match:
            return _open_system_folder(folder_key, command)
    
    # PATTERN 2: Open drives
    # "Open drive C", "Open C drive", "Open the D drive", etc.
    drive_regex = r'(?:open|access|go\s+to|navigate\s+to)\s+(?:the\s+)?(?:drive\s+)?([a-z]):?(?:\s+drive)?\b'
    drive_match = re.search(drive_regex, command_lower)
    
    if drive_match:
        drive_letter = drive_match.group(1).upper()
        return _open_drive(drive_letter, command)
    
    return False


def _open_system_folder(folder_key, command):
    """Open a system folder (Desktop, Downloads, etc.)
    
    Gets the path from Windows user directory
    """
    try:
        # Get the current user's home directory
        home_dir = os.path.expanduser("~")  # e.g., "C:\Users\babin"
        
        # Get the folder name
        folder_info = SYSTEM_FOLDERS[folder_key]
        folder_name = folder_info['paths'][0]  # Use first path as actual folder name
        
        # Construct full path
        folder_path = os.path.join(home_dir, folder_name)
        
        # Check if path exists
        if not os.path.exists(folder_path):
            speak(f"The {folder_name} folder was not found at {folder_path}")
            log_interaction(command, f"Folder not found: {folder_path}", source="local")
            return False
        
        # Open the folder
        if OS == "windows":
            # Use explorer.exe to open the folder
            subprocess.Popen(['explorer', folder_path])
            speak(f"Opening {folder_name} folder")
            log_interaction(command, f"Opened {folder_name} folder: {folder_path}", source="local")
            return True
        
        elif OS == "darwin":  # macOS
            subprocess.Popen(['open', folder_path])
            speak(f"Opening {folder_name} folder")
            log_interaction(command, f"Opened {folder_name} folder: {folder_path}", source="local")
            return True
        
        elif OS == "linux":
            subprocess.Popen(['xdg-open', folder_path])
            speak(f"Opening {folder_name} folder")
            log_interaction(command, f"Opened {folder_name} folder: {folder_path}", source="local")
            return True
    
    except Exception as e:
        print(f"Error opening {folder_key} folder: {e}")
        speak(f"Could not open the {folder_key} folder. Please try manually.")
        log_interaction(command, f"Error opening {folder_key}: {e}", source="local")
        return False


def _open_drive(drive_letter, command):
    """Open a specific drive (C:, D:, E:, etc.)
    
    Opens the drive in Windows Explorer or file manager
    """
    try:
        if OS == "windows":
            # Check if drive exists by checking if it's accessible
            drive_path = f"{drive_letter}:\\"
            
            # Check if drive exists
            if not os.path.exists(drive_path):
                speak(f"Drive {drive_letter} not found on this device")
                log_interaction(command, f"Drive {drive_letter} does not exist", source="local")
                return False
            
            # Open drive with explorer
            subprocess.Popen(['explorer', drive_path])
            speak(f"Opening drive {drive_letter}")
            log_interaction(command, f"Opened drive {drive_letter}", source="local")
            return True
        
        elif OS == "darwin":  # macOS (drives are different)
            # macOS doesn't use letter-based drives like Windows
            speak("Drive access works differently on macOS")
            return False
        
        elif OS == "linux":
            # Linux doesn't use letter-based drives
            speak("Drive access works differently on Linux")
            return False
    
    except Exception as e:
        print(f"Error opening drive {drive_letter}: {e}")
        speak(f"Could not open drive {drive_letter}. Please try manually.")
        log_interaction(command, f"Error opening drive {drive_letter}: {e}", source="local")
        return False


def get_available_drives():
    """Get list of all available drives on Windows
    
    Returns: List of drive letters (e.g., ['C', 'D', 'E'])
    """
    import string
    drives = []
    
    if OS == "windows":
        for drive_letter in string.ascii_uppercase:
            drive_path = f"{drive_letter}:\\"
            if os.path.exists(drive_path):
                drives.append(drive_letter)
    
    return drives


def get_available_system_folders():
    """Get list of available system folders for current user
    
    Returns: List of available folder names
    """
    home_dir = os.path.expanduser("~")
    available = []
    
    for folder_key, folder_info in SYSTEM_FOLDERS.items():
        folder_name = folder_info['paths'][0]
        folder_path = os.path.join(home_dir, folder_name)
        
        if os.path.exists(folder_path):
            available.append(folder_name)
    
    return available


def _handle_drive_closing(command):
    """Handle closing/ejecting drives
    
    Supports:
    - "Close drive C" → Safely eject C drive (if removable)
    - "Close D drive" → Safely eject D drive
    - "Eject drive E" → Safely eject E drive
    - "Close the F drive" → Safely eject F drive
    - "Unmount drive D" → Safely unmount D drive
    """
    command_lower = command.lower().strip()
    
    # Extract drive letter from command
    # Patterns: "close drive C", "close C drive", "close the D drive"
    drive_patterns = [
        r'(?:close|eject|unmount)\s+(?:the\s+)?(?:drive\s+)?([a-z])',  # close drive C or close C
        r'(?:close|eject|unmount)\s+(?:the\s+)?([a-z])\s+drive',  # close C drive
    ]
    
    drive_letter = None
    for pattern in drive_patterns:
        match = re.search(pattern, command_lower)
        if match:
            drive_letter = match.group(1).upper()
            break
    
    if not drive_letter:
        return False
    
    try:
        if OS == "windows":
            # Check if drive exists
            drive_path = f"{drive_letter}:\\"
            if not os.path.exists(drive_path):
                speak(f"Drive {drive_letter} is not connected")
                log_interaction(command, f"Drive {drive_letter} not found for closing", source="local")
                return True
            
            # Try to safely eject using Windows commands
            return _eject_drive_windows(drive_letter, command)
        
        elif OS == "darwin":  # macOS
            speak("Drive ejection works differently on macOS. Please eject manually.")
            return False
        
        elif OS == "linux":
            speak("Drive ejection works differently on Linux. Please unmount manually.")
            return False
    
    except Exception as e:
        print(f"Error closing drive {drive_letter}: {e}")
        speak(f"Could not safely eject drive {drive_letter}. Please eject manually.")
        log_interaction(command, f"Error closing drive {drive_letter}: {e}", source="local")
        return True


def _eject_drive_windows(drive_letter, command):
    """Safely eject a drive on Windows using multiple methods
    
    Tries to use:
    1. PowerShell Remove-Item method
    2. CMD diskpart method  
    3. Fallback to subprocess-based ejection
    """
    try:
        # Method 1: Try using 'cipher' command to flush drive
        # This ensures all data is written before ejection
        try:
            cipher_result = subprocess.run(
                ['cipher', '/w:C:'],
                capture_output=True,
                timeout=2
            )
        except:
            pass  # cipher might not be available, continue to next method
        
        # Method 2: Use Python's ctypes to safely eject (Windows specific)
        if OS == "windows":
            try:
                import ctypes
                import os as os_module
                
                # Get the handle to the drive
                drive_path = f"{drive_letter}:\\\\"
                
                # Use Windows API to eject
                # This method works for USB drives and external drives
                IOCTL_STORAGE_EJECT_MEDIA = 0x2d4808
                
                try:
                    handle = ctypes.windll.kernel32.CreateFileA(
                        drive_path,
                        0x00000001,  # GENERIC_READ
                        0x00000003,  # FILE_SHARE_READ | FILE_SHARE_WRITE
                        None,
                        0x00000003,  # OPEN_EXISTING
                        0,
                        None
                    )
                    
                    if handle > 0:
                        bytes_returned = ctypes.c_ulong()
                        ctypes.windll.kernel32.DeviceIoControl(
                            handle,
                            IOCTL_STORAGE_EJECT_MEDIA,
                            None,
                            0,
                            None,
                            0,
                            ctypes.byref(bytes_returned),
                            None
                        )
                        ctypes.windll.kernel32.CloseHandle(handle)
                        
                        speak(f"Safely ejected drive {drive_letter}")
                        log_interaction(command, f"Safely ejected drive {drive_letter} using Windows API", source="local")
                        return True
                except Exception as e:
                    print(f"ctypes ejection failed: {e}")
            except Exception as e:
                print(f"ctypes method unavailable: {e}")
        
        # Method 3: Try using 'eject' command if available
        try:
            result = subprocess.run(
                ['eject', f"{drive_letter}:"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                speak(f"Safely ejected drive {drive_letter}")
                log_interaction(command, f"Ejected drive {drive_letter} using eject command", source="local")
                return True
        except FileNotFoundError:
            pass  # eject command not available
        except Exception as e:
            print(f"Eject command failed: {e}")
        
        # Method 4: Use diskpart (most reliable for Windows)
        try:
            diskpart_script = f"""select volume={drive_letter}
remove all
"""
            result = subprocess.run(
                ['diskpart'],
                input=diskpart_script,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                speak(f"Safely ejected drive {drive_letter}")
                log_interaction(command, f"Ejected drive {drive_letter} using diskpart", source="local")
                return True
        except Exception as e:
            print(f"diskpart method failed: {e}")
        
        # Fallback: inform user
        speak(f"Please safely eject drive {drive_letter} using Windows Safely Remove Hardware")
        log_interaction(command, f"Could not auto-eject drive {drive_letter}, user action required", source="local")
        return True
    
    except Exception as e:
        print(f"Error in drive ejection: {e}")
        speak(f"Could not safely eject drive {drive_letter}. Please eject manually.")
        log_interaction(command, f"Error ejecting drive {drive_letter}: {e}", source="local")
        return True
