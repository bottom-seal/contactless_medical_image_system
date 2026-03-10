import speech_recognition as sr
from fuzzywuzzy import process
from pypinyin import lazy_pinyin  # Convert Chinese characters to Pinyin

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

def recognize_speech_from_mic(recognizer, microphone):
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
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio, language='zh-tw')
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

r = sr.Recognizer()
mic = sr.Microphone(device_index=4)
tags = ["平移", "縮放", "窗位", "旋轉", "選取", "放大鏡", "停止"]

while True:
    print("1")
    guess = recognize_speech_from_mic(r, mic)
    if guess["success"] and guess["transcription"]:
        print(f"Recognized: {guess['transcription']}")
        category = categorize_input(guess["transcription"], tags)
        if category != "none":
            print(f"Categorized as: {category}")
        else:
            print("Could not match input to a category.")
    elif guess["error"]:
        print(f"Error: {guess['error']}")
