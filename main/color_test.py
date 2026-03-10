from sklearn.cluster import KMeans
import cv2
import numpy as np
import mediapipe as mp

mp_holistic = mp.solutions.holistic # Holistic model
mp_drawing = mp.solutions.drawing_utils # Drawing utilities

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

        #draw ROI
        height, width = frame.shape[:2]
        print(height, width)
        x_bound = int((3/4)*width)
        cv2.line(frame, (x_bound, 0), (x_bound, height-1), (0, 255, 0), 3)
        cv2.line(frame, (x_bound, 0), (width-1, 0), (0, 255, 0), 3)
        cv2.line(frame, (x_bound, height-1), (width-1, height-1), (0, 255, 0), 3)
        cv2.line(frame, (width-1, 0), (width-1, height-1), (0, 255, 0), 3)
        ROI = frame[0:height-1, x_bound:width-1]

        #run K-means to find main color
        img = cv2.cvtColor(ROI, cv2.COLOR_BGR2RGB)
        img = img.reshape((img.shape[0] * img.shape[1], 3))
        kmeans = KMeans(n_clusters = 1)
        kmeans.fit(img)

        #getting hue for main color
        #clip color to have integer value for RGB
        rgb_value = np.clip(kmeans.cluster_centers_, 0, 255).astype(np.uint8)
        #rgb_image = np.uint8([[rgb_value]])
        #need to convert to 1x1x3 structure to use cv2 function
        rgb_image = np.uint8([[rgb_value[0]]])
        print(rgb_value)
        hsv_value = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
        hue = hsv_value[0][0][0]

        #render whole image based on hue value
        hue_shift = int(36 - hue)
        print(f"Hue Shift: {hue_shift}")

        print(hue)
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h = hsv_image[:,:,0]
        s = hsv_image[:,:,1]
        v = hsv_image[:,:,2]
        print(h)
        print(s)
        print(v)
        hsv_image = cv2.add(h, hue_shift)
        hsv_image = cv2.merge([hsv_image,s,v])

        #test if rendering gone right
        ROI = hsv_image[0:height-1, x_bound:width-1]
        img = cv2.cvtColor(ROI, cv2.COLOR_BGR2RGB)
        img = img.reshape((img.shape[0] * img.shape[1], 3))
        kmeans = KMeans(n_clusters = 1)
        kmeans.fit(img)
        rgb_value = np.clip(kmeans.cluster_centers_, 0, 255).astype(np.uint8)
        rgb_image = np.uint8([[rgb_value[0]]])
        hsv_value = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
        hue = hsv_value[0][0][0]
        print(hue)

        #test if mediapipe can capture hand
        display_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        image, results = mediapipe_detection(display_image, holistic)
        mp_drawing.draw_landmarks(display_image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        cv2.imshow('OpenCV Feed', display_image)
        # Break gracefully
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
            
