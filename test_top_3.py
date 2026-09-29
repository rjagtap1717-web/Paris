import sys
import os
import traceback

sys.path.insert(0, r"E:\Paris")

print("--- Testing Top 3 Paris Actions ---\n")

# 1. Open App
try:
    from actions.open_app import open_app
    print("[1] Testing open_app (notepad)...")
    res1 = open_app({"app_name": "notepad"})
    print(f"Result: {res1}")
except Exception as e:
    print(f"Error testing open_app: {e}")
    traceback.print_exc()

print()

# 2. Computer Settings
try:
    from actions.computer_settings import computer_settings
    print("[2] Testing computer_settings (volume_up)...")
    res2 = computer_settings({"action": "volume_up"})
    print(f"Result: {res2}")
except Exception as e:
    print(f"Error testing computer_settings: {e}")

print()

# 3. System Monitor
try:
    from actions.system_monitor import get_system_status
    print("[3] Testing system_monitor (get_system_status)...")
    res3 = get_system_status()
    print(f"Result: {res3}")
except Exception as e:
    print(f"Error testing system_monitor: {e}")

print("\n--- Done ---")
