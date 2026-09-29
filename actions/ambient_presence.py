import threading
import time
import os
import cv2
import numpy as np

try:
    from actions.screen_processor import _capture_camera
except ImportError:
    pass

_presence_thread = None
_stop_presence = False

def ambient_presence(parameters: dict, player=None, speak=None, **kwargs) -> str:
    global _presence_thread, _stop_presence
    
    action = parameters.get("action", "start")
    
    if action == "stop":
        _stop_presence = True
        return "Ambient presence monitoring stopped."
        
    if _presence_thread and _presence_thread.is_alive():
        return "Ambient presence is already running."

    _stop_presence = False
    
    def _worker():
        # Load OpenCV's extremely lightweight, built-in face detection model
        cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        user_present = True  # Assume present at start
        last_seen = time.time()
        
        while not _stop_presence:
            try:
                # Use the robust capture logic we just built
                img_bytes, _ = _capture_camera()
                
                # Convert bytes back to CV2 format for the Haar Cascade
                nparr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    if len(faces) > 0:
                        last_seen = time.time()
                        if not user_present:
                            user_present = True
                            msg = "System Alert: The user has returned to the desk."
                            print(f"[Presence] {msg}")
                            if player: player.write_log(f"👤 {msg}")
                            if speak: speak(msg)
                    else:
                        if user_present and (time.time() - last_seen > 30):
                            user_present = False
                            msg = "System Alert: The user has stepped away from the desk."
                            print(f"[Presence] {msg}")
                            if player: player.write_log(f"👻 {msg}")
                            if speak: speak(msg)
                            
            except Exception as e:
                print(f"[Presence Monitor] Error: {e}")
                
            time.sleep(10) # Poll every 10 seconds to save CPU while still being responsive
            
    _presence_thread = threading.Thread(target=_worker, daemon=True)
    _presence_thread.start()
    
    return "Ambient presence monitoring started. I will now use facial detection in the background to alert you when the user leaves or returns."

TOOL = {
    "name": "ambient_presence",
    "scope": "exempt",
    "description": "Start or stop background facial recognition to detect if the user is currently at their desk.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "'start' or 'stop' monitoring."
            }
        },
        "required": ["action"]
    },
    "handler": ambient_presence
}
