import pyautogui
import time
import webbrowser
import keyboard
start_x, start_y = 1126, 600
mag_x, mag_y = 1126, 600
# Open the browser using webbrowser (this will open your default browser)
webbrowser.open('https://www.dicomlibrary.com/meddream/?study=1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.79379639')
while True:
    if keyboard.is_pressed("1"):
        pyautogui.click(x=636, y=145, button='left')
        mag = True
        mag_x = start_x
        mag_y = start_y
        pyautogui.moveTo(mag_x, mag_y+10)  # Drag to the target position
        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
    if keyboard.is_pressed('Up'):
        mag_y = mag_y - 10
        pyautogui.moveTo(mag_x, mag_y, duration=0.03)  # Drag to the target position
    if keyboard.is_pressed('Down'):
        mag_y = mag_y + 10
        pyautogui.moveTo(mag_x, mag_y, duration=0.03)  # Drag to the target position    
    if keyboard.is_pressed('Left'):
        mag_x = mag_x - 10
        pyautogui.moveTo(mag_x, mag_y, duration=0.03)  # Drag to the target position    
    if keyboard.is_pressed('Right'):
        mag_x = mag_x + 10
        pyautogui.moveTo(mag_x, mag_y, duration=0.03)  # Drag to the target position    
    