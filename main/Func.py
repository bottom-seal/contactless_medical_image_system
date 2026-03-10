import numpy as np
import mediapipe as mp
import cv2
import threading
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils # Drawing utilities
stop_event = threading.Event()

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

import speech_recognition as sr
from fuzzywuzzy import process
from pypinyin import lazy_pinyin

def categorize_input(transcription, tags):
    """Find the closest tag for a given transcription using fuzzywuzzy."""
    if transcription:
        # Convert both transcription and tags to Pinyin
        transcription_pinyin = ' '.join(lazy_pinyin(transcription))  # Convert the transcription to Pinyin
        pinyin_tags = [' '.join(lazy_pinyin(tag)) for tag in tags]  # Convert tags to Pinyin
        
        # Use fuzzywuzzy's extractOne method to get the best match
        best_match = process.extractOne(transcription_pinyin, pinyin_tags)
        
        # If the match score is high enough, return the matched tag, otherwise return "none"
        if best_match and best_match[1] > 70:  # Adjust threshold to 70
            matched_tag = tags[pinyin_tags.index(best_match[0])]  # Get the original tag
            return matched_tag
        return "none"
    return "none"

def recognize_speech_from_mic(recognizer, microphone, result_queue, stop_event):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occurred, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")
    print("test")
    
    while not stop_event.is_set():
        print("test2")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        try:
            response["transcription"] = recognizer.recognize_google(audio, language='zh-tw')
        except sr.RequestError:
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            response["error"] = "Unable to recognize speech"

        # Add the response to the queue
        result_queue.put(response["transcription"])

    print("Exiting speech recognition loop...")

def dict_mode(value):
    case_dict = {
        "平移": "Pan",
        "縮放": "Zoom",
        "窗位": "Window",
        "旋轉": "Rotate",
        "選取": "Select",
        "放大鏡": "Magnifier",
        "停止": "stall"
    }
    return case_dict.get(value, "Unknown fruit.")
