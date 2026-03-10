from tensorflow.keras.models import load_model
import numpy as np
import mediapipe as mp
import cv2

def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
    image.flags.writeable = False                  # Image is no longer writeable
    results = model.process(image)                 # Make prediction
    image.flags.writeable = True                   # Image is now writeable 
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
    return image, results

def draw_styled_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                             mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                             ) 

def extract_keypoints(reference, results):
    global ref, lh
    if results.left_hand_landmarks:
        hand = results.left_hand_landmarks.landmark
        print(reference)
        if np.array_equal(reference, [0, 0, 0]):
            move_dist = [0,0,0]
        else:
            move_dist = [hand[0].x - reference[0], hand[0].y - reference[1], hand[0].z - reference[2]]
        ref = [hand[0].x, hand[0].y, hand[0].z]
        thumb_dist = [hand[4].x - hand[0].x, hand[4].y - hand[0].y, hand[4].z - hand[0].z]
        index_dist = [hand[8].x - hand[0].x, hand[8].y - hand[0].y, hand[8].z - hand[0].z]
        middle_dist = [hand[12].x - hand[0].x, hand[12].y - hand[0].y, hand[12].z - hand[0].z]
        ring_dist = [hand[16].x - hand[0].x, hand[16].y - hand[0].y, hand[16].z - hand[0].z]
        pinky_dist = [hand[20].x - hand[0].x, hand[20].y - hand[0].y, hand[20].z - hand[0].z]
        lh = np.array(move_dist + thumb_dist + index_dist + middle_dist + ring_dist + pinky_dist).flatten()
    else:
        lh =  np.zeros(6*3)
        ref = reference
    return ref, lh

actions = np.array(['1_up', '1_down', '1_left', '1_right', '2_up', '2_down', '3_up', '3_down', '3_left', '3_right', '4_up', '4_down', '5_up', '5_down', '5_left', '5_right', '6_up', '6_down', '6_left', '6_right'])
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils # Drawing utilities
model = load_model('main/model.h5')

# 1. New detection variables
sequence = []
sentence = []
predictions = []
threshold = 0.5
ref = [0,0,0]
lh = np.zeros(6*3)
cap = cv2.VideoCapture(0)
# Set mediapipe model 
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():

        # Read feed
        ret, frame = cap.read()

        # Make detections
        image, results = mediapipe_detection(frame, holistic)
        print(results)
        
        # Draw landmarks
        draw_styled_landmarks(image, results)
        
        # 2. Prediction logic
        ref, keypoints = extract_keypoints(ref, results)
        sequence.append(keypoints)
        sequence = sequence[-5:]
        
        if len(sequence) == 5:
            res = model.predict(np.expand_dims(sequence, axis=0))[0]
            print(actions[np.argmax(res)])
            predictions.append(np.argmax(res))

        #3. Viz logic
            if np.unique(predictions[-10:])[0]==np.argmax(res): 
                if res[np.argmax(res)] > threshold: 
                    
                    if len(sentence) > 0: 
                        if actions[np.argmax(res)] != sentence[-1]:
                            sentence.append(actions[np.argmax(res)])
                    else:
                        sentence.append(actions[np.argmax(res)])

            if len(sentence) > 5: 
                sentence = sentence[-5:]
                print(sentence)
            
        cv2.rectangle(image, (0,0), (640, 40), (245, 117, 16), -1)
        cv2.putText(image, ' '.join(sentence), (3,30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Show to screen
        cv2.imshow('OpenCV Feed', image)

        # Break gracefully
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()