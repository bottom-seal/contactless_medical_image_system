from sklearn.cluster import KMeans
import cv2
import numpy as np
import mediapipe as mp

mp_holistic = mp.solutions.holistic # Holistic model
mp_drawing = mp.solutions.drawing_utils # Drawing utilities

#blue is - 90

def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
    image.flags.writeable = False                  # Image is no longer writeable
    results = model.process(image)                 # Make prediction
    image.flags.writeable = True                   # Image is now writeable 
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
    return image, results

cap = cv2.VideoCapture(0)


with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while True:
        ret, frame = cap.read()

        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h = hsv_image[:,:,0]
        s = hsv_image[:,:,1]
        v = hsv_image[:,:,2]
        print(h)
        print(s)
        print(v)
        hsv_image = cv2.add(h, -90)
        hsv_image = cv2.merge([hsv_image,s,v])

        #test if mediapipe can capture hand
        display_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        image, results = mediapipe_detection(display_image, holistic)
        mp_drawing.draw_landmarks(display_image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        cv2.imshow('OpenCV Feed', display_image)
        # Break gracefully
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
            
