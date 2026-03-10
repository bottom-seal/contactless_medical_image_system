from sklearn.cluster import KMeans
import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model
from Func import mediapipe_detection, draw_styled_landmarks, extract_keypoints, recognize_speech_from_mic, categorize_input, dict_mode
import threading
import queue
import speech_recognition as sr
import pyautogui
import webbrowser
import ctypes
import time
#set up
pyautogui.FAILSAFE = False
actions = np.array(['1_up', '1_down', '1_left', '1_right', '2_up', '2_down', '3_up', '3_down', '3_left', '3_right', '4_up', '4_down', '5_up', '5_down', '5_left', '5_right', '6_up', '6_down', '6_left', '6_right'])
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils # Drawing utilities
model = load_model('main/model.h5')
sequence = []
sentence = []
predictions = []
threshold = 0.5
ref = [0,0,0]
lh = np.zeros(6*3)
recognizer = sr.Recognizer()
microphone = sr.Microphone(device_index=4)
result_queue = queue.Queue()
tags = ["平移", "縮放", "窗位", "旋轉", "選取", "放大鏡", "停止"]
stop_event = threading.Event()
mode = "none"
last_mode = "none"
command = "none"
valid_command = "none"
first_command = True
fix_x, fix_y = 1126, 600
mag_x, mag_y = 1126, 600
mag = False
#regarding window placement
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)
#initialize threading for voice recognition
speech_thread = threading.Thread(target=recognize_speech_from_mic, args=(recognizer, microphone, result_queue, stop_event))
speech_thread.daemon = True

webbrowser.open('https://www.dicomlibrary.com/meddream/?study=1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.79379639')

try:
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('Glove Color Detection', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Glove Color Detection', cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow('Glove Color Detection', 640, 480)

    fps = cap.get(cv2.CAP_PROP_FPS)
    print("FPS:", fps)
    counter = 10
    #10 seconds to capture glove color
    for frame_iter in range(300):
        ret, frame = cap.read()

        #draw ROI
        height, width = frame.shape[:2]
        x_bound = int((5/11)*width)
        x_bound = int((4/9)*height)
        #left
        cv2.line(frame, (int((5/11)*width), int((4/9)*height)), (int((5/11)*width), int((5/9)*height)), (0, 255, 0), 3)
        #up
        cv2.line(frame, (int((5/11)*width), int((4/9)*height)), (int((6/11)*width), int((4/9)*height)), (0, 255, 0), 3)
        #bottom
        cv2.line(frame, (int((5/11)*width), int((5/9)*height)), (int((6/11)*width), int((5/9)*height)), (0, 255, 0), 3)
        #right
        cv2.line(frame, (int((6/11)*width), int((4/9)*height)), (int((6/11)*width), int((5/9)*height)), (0, 255, 0), 3)

        if frame_iter == 299:
            ROI = frame[int((5/11)*width):int((6/11)*width), int((4/9)*height):int((5/9)*height)]
            img = cv2.cvtColor(ROI, cv2.COLOR_BGR2RGB)
            img = img.reshape((img.shape[0] * img.shape[1], 3))
            kmeans = KMeans(n_clusters = 1)
            kmeans.fit(img)
            rgb_value = np.clip(kmeans.cluster_centers_, 0, 255).astype(np.uint8)

        cv2.putText(frame, "Detecting glove color in " + str(counter), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Please cover block with your hand", (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if frame_iter % 30 == 0:
            counter = counter - 1
        x_pos = screen_width - width
        y_pos = screen_height - height
        cv2.moveWindow('Glove Color Detection', x_pos, y_pos-10)
        cv2.imshow('Glove Color Detection', frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
                break
    cv2.destroyWindow("Glove Color Detection")
    print(rgb_value)
    rgb_image = np.uint8([[rgb_value[0]]])
    hsv_value = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
    hue = hsv_value[0][0][0]
    print(hue)
    if hue > 75 and hue < 110:
        render = -90
    elif hue <=75:
        render = -10
    
    #time.sleep(10)
    pyautogui.click(x=708, y=388)
    time.sleep(0.1)
    pyautogui.click(x=708, y=388)
    stop_event.clear()
    speech_thread.start()
    cv2.namedWindow('UI', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('UI', 640, 480)
    cv2.setWindowProperty('UI', cv2.WND_PROP_TOPMOST, 1)
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            #deal with voice recognition
            if not result_queue.empty():
                transcription = result_queue.get()
                print(f"Recognized: {transcription}")
                if transcription != "Unable to recognize speech" and transcription != "API unavailable":
                    category = categorize_input(transcription, tags)
                    if category != "none":
                        print(f"Categorized as: {category}")
                        last_mode = mode
                        mode = dict_mode(category)
                        if mode == "Pan" and last_mode != "Pan" and first_command != True:
                            #x=413, y=136
                            pyautogui.click(x=413, y=136, button='left')
                            if mag == True:
                                mag = False
                                pyautogui.mouseUp(button='left')  # Press and hold the left mouse button

                        elif mode == "Zoom" and last_mode != "Zoom":
                            #x=496, y=135
                            pyautogui.click(x=496, y=135, button='left')
                            if mag == True:
                                mag = False
                                pyautogui.mouseUp(button='left')  # Press and hold the left mouse button

                        elif mode == "Window" and last_mode != "Window":
                            #x=337, y=147,
                            pyautogui.click(x=337, y=147, button='left')
                            if mag == True:
                                mag = False
                                pyautogui.mouseUp(button='left')  # Press and hold the left mouse button

                        elif mode == "Rotate" and last_mode != "Rotate":
                            pyautogui.click(x=560, y=143, button='left')
                            if mag == True:
                                mag = False
                                pyautogui.mouseUp(button='left')  # Press and hold the left mouse button

                        elif mode == "Magnifier" and last_mode != "Magnifier":
                            pyautogui.click(x=636, y=145, button='left')
                            mag = True
                            mag_x = fix_x
                            mag_y = fix_y
                            pyautogui.moveTo(mag_x, mag_y+10)  # Drag to the target position
                            pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        elif mode == "Select":
                            if mag == True:
                                mag = False
                                pyautogui.mouseUp(button='left')  # Press and hold the left mouse button


                        if first_command == True:
                            first_command = False
                    else:
                        print("Could not match input to a category.")
                else:
                    print(transcription)
            #render
            ret, frame = cap.read()
            hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            h = hsv_image[:,:,0]
            s = hsv_image[:,:,1]
            v = hsv_image[:,:,2]
            hsv_image = cv2.add(h, render)
            hsv_image = cv2.merge([hsv_image,s,v])
            rendered_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
            height, width = rendered_image.shape[:2]
            recog_image = rendered_image[0:height-1, x_bound:width-1]
            #detect on rendered image, shows retrieved
            rendered_image, results = mediapipe_detection(recog_image, holistic)
            #draw_styled_landmarks(frame, results)

            #detect with model
            ref, keypoints = extract_keypoints(ref, results)
            sequence.append(keypoints)
            sequence = sequence[-5:]
            
            if len(sequence) == 5 and not np.array_equal(sequence, np.zeros(16*5)):
                res = model.predict(np.expand_dims(sequence, axis=0))[0]
                command =  actions[np.argmax(res)]
                #print(command)
                #handle commands
                if mode == "Pan":
                    if command == "1_up":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x, fix_y-10)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                    elif command == "1_down":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x, fix_y+10)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                    elif command == "1_left":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x-10, fix_y)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                    elif command == "1_right":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x+10, fix_y)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                elif mode == "Zoom":
                    if command == "2_up":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x, fix_y-10)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                    elif command == "2_down":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x, fix_y+10)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                elif mode == "Window":
                    if command == "3_up":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x, fix_y-10)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                    elif command == "3_down":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x, fix_y+10)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                    elif command == "3_left":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x-10, fix_y)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                    elif command == "3_right":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x+10, fix_y)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                elif mode == "Rotate":
                    if command == "4_up":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x, fix_y-10)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                    elif command == "4_down":
                        valid_command = command
                        pyautogui.moveTo(fix_x, fix_y)  # Move to the starting position
                        pyautogui.mouseDown(button='left')  # Press and hold the left mouse button
                        pyautogui.moveTo(fix_x, fix_y+10)  # Drag to the target position
                        pyautogui.mouseUp(button='left')  # Release the left mouse button
                elif mode == "Select":
                    if command == "5_up":
                        valid_command = command
                        pyautogui.press('up')
                    elif command == "5_down":
                        valid_command = command
                        pyautogui.press('down')
                    elif command == "5_left":
                        valid_command = command
                        pyautogui.press('left')
                    elif command == "5_right":
                        valid_command = command
                        pyautogui.press('right')

                elif mode == "Magnifier":
                    if command == "6_up":
                        valid_command = command
                        mag_y = mag_y - 10
                        pyautogui.moveTo(mag_x, mag_y, duration=0.5)  # Drag to the target position
                    elif command == "6_down":
                        valid_command = command
                        mag_y = mag_y + 10
                        pyautogui.moveTo(mag_x, mag_y, duration=0.5)  # Drag to the target position
                    elif command == "6_left":
                        valid_command = command
                        mag_x = mag_x - 10
                        pyautogui.moveTo(mag_x, mag_y, duration=0.5)  # Drag to the target position
                    elif command == "6_right":
                        valid_command = command
                        mag_x = mag_x + 10
                        pyautogui.moveTo(mag_x, mag_y, duration=0.5)  # Drag to the target position
                    command = "none"
            print(mode)
            print(valid_command)
            cv2.putText(frame, "current mode " + mode, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "current command " + valid_command, (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.moveWindow('UI', x_pos, y_pos-10)
            cv2.imshow('UI', frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                stop_event.set()  # Signal the thread to stop
                speech_thread.join()  # Wait for the thread to finish
                break
except KeyboardInterrupt:
    print("\nStopping speech recognition thread...")
    stop_event.set()  # Signal the thread to stop
    speech_thread.join()  # Wait for the thread to finish
    print("Speech recognition thread has stopped.")