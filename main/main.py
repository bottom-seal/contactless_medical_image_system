from sklearn.cluster import KMeans
import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model
from Func import mediapipe_detection, draw_styled_landmarks, extract_keypoints, recognize_speech_from_mic, categorize_input
import threading
import queue
import speech_recognition as sr

#set up
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



cap = cv2.VideoCapture(0)
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
    cv2.imshow('OpenCV Feed', frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
            break
print(rgb_value)
rgb_image = np.uint8([[rgb_value[0]]])
hsv_value = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
hue = hsv_value[0][0][0]
print(hue)
if hue > 75 and hue < 110:
    render = 65
elif hue <=75:
    render = 0

with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        
        #render
        ret, frame = cap.read()
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h = hsv_image[:,:,0]
        s = hsv_image[:,:,1]
        v = hsv_image[:,:,2]
        hsv_image = cv2.add(h, render)
        hsv_image = cv2.merge([hsv_image,s,v])
        rendered_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        #detect on rendered image, shows retrieved
        rendered_image, results = mediapipe_detection(rendered_image, holistic)
        draw_styled_landmarks(frame, results)

        #detect with model
        ref, keypoints = extract_keypoints(ref, results)
        sequence.append(keypoints)
        sequence = sequence[-5:]
        
        if len(sequence) == 5:
            res = model.predict(np.expand_dims(sequence, axis=0))[0]
            command =  actions[np.argmax(res)]
            print(command)
            

    
        cv2.imshow('OpenCV Feed', frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break