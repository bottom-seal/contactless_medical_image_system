import pyautogui
import time
import webbrowser
from pynput.mouse import Listener

# Open the browser using webbrowser (this will open your default browser)
webbrowser.open('https://www.dicomlibrary.com/meddream/?study=1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.79379639')

# Wait for the page to load
time.sleep(5)

# Function to detect and print the mouse click position
def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse clicked at: x={x}, y={y}")

# Start listening to mouse clicks
with Listener(on_click=on_click) as listener:
    listener.join()

# Wait for user input to close the program
input("Press Enter to stop detecting clicks and close the program...")
