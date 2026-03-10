import pyautogui
import time
import webbrowser
import keyboard
start_x, start_y = 1126, 600

# Open the browser using webbrowser (this will open your default browser)
webbrowser.open('https://www.dicomlibrary.com/meddream/?study=1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.79379639')
time.sleep(15)
pyautogui.click(x=708, y=388)
time.sleep(0.1)
pyautogui.click(x=708, y=388)

while True:
    # Example: Perform an action when the "a" key is pressed
    if keyboard.is_pressed('1'):
        pyautogui.click(x=337, y=147, button='left')
    if keyboard.is_pressed('2'):
        pyautogui.click(x=413, y=136, button='left')
    if keyboard.is_pressed('3'):
        pyautogui.click(x=496, y=135, button='left')
    if keyboard.is_pressed('4'):
        pyautogui.click(x=560, y=143, button='left')
    if keyboard.is_pressed('5'):
        pyautogui.click(x=636, y=145, button='left')

    if keyboard.is_pressed('w'):
        print("Key 'w' pressed!")
        pyautogui.moveTo(start_x, start_y)  # Move to the starting position
        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
        pyautogui.moveTo(start_x, start_y-10, duration=0.033)  # Drag to the target position
        pyautogui.mouseUp(button='left')  # Release the left mouse button
    if keyboard.is_pressed('s'):
        print("Key 's' pressed!")
        pyautogui.moveTo(start_x, start_y)  # Move to the starting position
        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
        pyautogui.moveTo(start_x, start_y+10, duration=0.033)  # Drag to the target position
        pyautogui.mouseUp(button='left')  # Release the left mouse button
    if keyboard.is_pressed('a'):
        print("Key 'a' pressed!")
        pyautogui.moveTo(start_x, start_y)  # Move to the starting position
        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
        pyautogui.moveTo(start_x-10, start_y, duration=0.033)  # Drag to the target position
        pyautogui.mouseUp(button='left')  # Release the left mouse button
    if keyboard.is_pressed('d'):
        print("Key 'd' pressed!")
        pyautogui.moveTo(start_x, start_y)  # Move to the starting position
        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
        pyautogui.moveTo(start_x+10, start_y, duration=0.033)  # Drag to the target position
        pyautogui.mouseUp(button='left')  # Release the left mouse button        
    
# Wait for the page to load
time.sleep(5)

