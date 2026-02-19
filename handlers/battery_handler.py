"""Battery Monitoring Handler - Monitors device battery level"""
import os
import threading
import time
from utils.voice_io import speak
from utils.logger import log_interaction
from config.settings import OS

# Track battery state
current_battery_level = 100
is_charging = False
low_battery_announced = False
charging_announced = False
monitoring = False


def get_battery_info_windows():
    """Get battery info on Windows"""
    try:
        import subprocess
        result = subprocess.run(
            ["wmic", "path", "win32_battery", "get", "EstimatedChargeRemaining, BatteryStatus"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            data = lines[1].split()
            if len(data) >= 2:
                battery_level = int(data[0])
                battery_status = int(data[1])
                # Status: 1=discharging, 2=charging, 3=critical, 4=low, 5=high, 6=charging high, 7=charging low, 8=undefined, 9=partially charged
                is_charging = battery_status in [2, 6]
                return battery_level, is_charging
        
        # Fallback: use powercfg
        result = subprocess.run(
            ["powercfg", "/batteryreport", "/output", "battery_report.xml"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Try psutil as last resort
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                return int(battery.percent), battery.power_plugged
        except ImportError:
            pass
        
        return 100, False
    
    except Exception:
        # If we can't get battery info, assume it's OK
        return 100, False


def get_battery_info_linux():
    """Get battery info on Linux"""
    try:
        import subprocess
        
        # Try UPower first
        result = subprocess.run(
            ["upower", "-e"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        battery_level = 100
        is_charging = False
        
        for line in result.stdout.split('\n'):
            if 'percentage' in line:
                try:
                    battery_level = int(line.split()[-1].replace('%', ''))
                except:
                    pass
            if 'state' in line.lower() and 'charging' in line.lower():
                is_charging = True
        
        return battery_level, is_charging
    
    except Exception:
        return 100, False


def get_battery_info_mac():
    """Get battery info on macOS"""
    try:
        import subprocess
        result = subprocess.run(
            ["pmset", "-g", "batt"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        battery_level = 100
        is_charging = False
        
        for line in result.stdout.split('\n'):
            if '%' in line:
                try:
                    # Extract battery percentage
                    import re
                    match = re.search(r'(\d+)%', line)
                    if match:
                        battery_level = int(match.group(1))
                    
                    # Check if charging
                    if 'charging' in line.lower() or 'AC attached' in line:
                        is_charging = True
                except:
                    pass
        
        return battery_level, is_charging
    
    except Exception:
        return 100, False


def get_battery_info():
    """Get battery info based on OS"""
    if OS == "windows":
        return get_battery_info_windows()
    elif OS == "darwin":
        return get_battery_info_mac()
    elif OS == "linux":
        return get_battery_info_linux()
    else:
        return 100, False


def monitor_battery():
    """Background thread to monitor battery level"""
    global current_battery_level, is_charging, low_battery_announced, charging_announced, monitoring
    
    monitoring = True
    check_interval = 10  # Check every 10 seconds
    
    while monitoring:
        try:
            battery_level, charging_status = get_battery_info()
            current_battery_level = battery_level
            was_charging = is_charging
            is_charging = charging_status
            
            # Low battery alert (20%)
            if battery_level <= 20 and not low_battery_announced and not is_charging:
                message = "Put your device to charge"
                speak(message)
                log_interaction("low_battery", message, source="system")
                low_battery_announced = True
                charging_announced = False
            
            # Battery above 20% - reset low battery flag
            if battery_level > 20:
                low_battery_announced = False
            
            # Charging started
            if is_charging and not was_charging:
                message = "Charging in Progress"
                speak(message)
                log_interaction("charging_started", message, source="system")
                charging_announced = True
                low_battery_announced = False
            
            # Charging stopped - notify user charger is unplugged
            if not is_charging and was_charging:
                message = "Charger is plugged out"
                speak(message)
                log_interaction("charging_stopped", message, source="system")
                charging_announced = False
            
            time.sleep(check_interval)
        
        except Exception as e:
            # Silent fail - don't interrupt the assistant
            time.sleep(check_interval)


def start_battery_monitoring():
    """Start battery monitoring in background thread"""
    global monitoring
    
    if not monitoring:
        battery_thread = threading.Thread(target=monitor_battery, daemon=True)
        battery_thread.start()


def stop_battery_monitoring():
    """Stop battery monitoring"""
    global monitoring
    monitoring = False


def handle_battery_status(command):
    """Handle battery status queries"""
    if not any(word in command.lower() for word in ['battery', 'charge', 'charging']):
        return False
    
    battery_level, is_charging = get_battery_info()
    
    if is_charging:
        message = f"Battery is {battery_level} percent and currently charging"
    else:
        message = f"Battery is {battery_level} percent"
    
    speak(message)
    log_interaction(command, message, source="local")
    return True
