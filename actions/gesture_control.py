import threading
import time
import os



_gesture_thread = None
_stop_gestures = False

def is_peace_sign(hand_landmarks):
    """Check if the hand is making a peace sign ✌️"""
    # Index and middle fingers extended (tips higher than lower joints)
    index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    middle_up = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
    # Ring and pinky fingers folded (tips lower than lower joints)
    ring_down = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y
    pinky_down = hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y
    
    return index_up and middle_up and ring_down and pinky_down

def is_open_palm(hand_landmarks):
    """Check if all fingers are extended ✋"""
    return (hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y and
            hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y and
            hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y and
            hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y)

def gesture_control(parameters: dict, player=None, speak=None, **kwargs) -> str:
    global _gesture_thread, _stop_gestures
    
    try:
        import cv2
        import numpy as np
        import pyautogui
        import mediapipe as mp
        from mediapipe.python.solutions import hands as mp_hands
    except ImportError:
        return "Error: The gesture control module requires mediapipe. Please run 'pip install mediapipe opencv-python pyautogui' first."
        
    action = parameters.get("action", "start")
    
    if action == "stop":
        _stop_gestures = True
        return "Gesture control deactivated. Camera released."
        
    if _gesture_thread and _gesture_thread.is_alive():
        return "Gesture control is already active and monitoring your hands."

    _stop_gestures = False
    
    def _worker():
        from actions.screen_processor import _get_camera_index, _cv2_backend
        
        index = _get_camera_index()
        backend = _cv2_backend()
        cap = cv2.VideoCapture(index, backend)
        
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        command_mode_active = False
        command_mode_end_time = 0
        last_action_time = 0
        
        # Used for swipe detection: deque stores (timestamp, x_coord) pairs
        from collections import deque
        position_history = deque(maxlen=10) # Track last ~300ms
        SWIPE_THRESHOLD = 0.25 # Normalized screen width displacement
        
        try:
            while not _stop_gestures:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                    
                # Mirror the frame so it feels natural, and convert color
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                results = hands.process(rgb_frame)
                
                current_time = time.time()
                
                # Check if command mode timed out
                if command_mode_active and current_time > command_mode_end_time:
                    command_mode_active = False
                    position_history.clear()
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    
                    # 1. Check for the Peace Sign Clutch
                    if not command_mode_active and is_peace_sign(hand_landmarks):
                        # Ensure we don't trigger too often
                        if current_time - last_action_time > 3.0:
                            command_mode_active = True
                            command_mode_end_time = current_time + 4.0 # 4 second window
                            if player: player.write_log("✌️ Gesture Clutch Activated! Ready for command.")
                            position_history.clear()
                            time.sleep(0.5) # debounce
                            continue
                            
                    # 2. If in Command Mode, look for actionable gestures
                    if command_mode_active and is_open_palm(hand_landmarks):
                        current_x = hand_landmarks.landmark[8].x # index finger tip X
                        position_history.append((current_time, current_x))
                        
                        if len(position_history) > 2 and (current_time - last_action_time > 2.0):
                            start_time, start_x = position_history[0]
                            # Only calculate if the window is within reasonable time limits (e.g. 0.5s)
                            if (current_time - start_time) < 0.5:
                                dx = current_x - start_x
                                
                                if abs(dx) > SWIPE_THRESHOLD:
                                    if dx > 0:
                                        print("[Gesture] ➡️ Swiped Right! Switching Window.")
                                        pyautogui.keyDown('alt')
                                        time.sleep(0.05)
                                        pyautogui.press('tab')
                                        time.sleep(0.05)
                                        pyautogui.keyUp('alt')
                                    else:
                                        print("[Gesture] ⬅️ Swiped Left! Opening Task View.")
                                        pyautogui.keyDown('win')
                                        time.sleep(0.05)
                                        pyautogui.press('tab')
                                        time.sleep(0.05)
                                        pyautogui.keyUp('win')
                                        
                                    last_action_time = current_time
                                    command_mode_active = False # Reset mode after action
                                    position_history.clear()
                                    if player: player.write_log("✋ Swipe gesture executed!")
                    else:
                        position_history.clear()
                else:
                    position_history.clear()
                    
                time.sleep(0.03) # Cap at ~30 FPS to save CPU
                
        except Exception as e:
            pass # Silent fail inside worker thread
        finally:
            cap.release()
            hands.close()
            
    _gesture_thread = threading.Thread(target=_worker, daemon=True)
    _gesture_thread.start()
    
    return "Gesture control activated! Hold up a Peace Sign ✌️ to engage command mode, then swipe your open palm ✋ to switch windows."

TOOL = {
    "name": "gesture_control",
    "scope": "exempt",
    "description": "Start or stop background hand gesture recognition via webcam. Use this when the user asks for gesture or hologram control.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "'start' or 'stop' gesture control."
            }
        },
        "required": ["action"]
    },
    "handler": gesture_control
}