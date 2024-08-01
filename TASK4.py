from transformers import MarianMTModel, MarianTokenizer
import speech_recognition as sr
from datetime import datetime
import streamlit as st

model_name_hi = 'Helsinki-NLP/opus-mt-en-hi'
model_en_hi = MarianMTModel.from_pretrained(model_name_hi)
tokenizer_en_hi = MarianTokenizer.from_pretrained(model_name_hi)

#Speech Recognize from mic
def recognize_speech_from_mic(recognizer):
    mic_list = sr.Microphone.list_microphone_names()
    headset_index = None
    for i, mic_name in enumerate(mic_list):
        if 'headset' in mic_name.lower():
            headset_index = i
            break

    if headset_index is not None:
        st.write("Using headset microphone:", mic_list[headset_index])
        mic_index = headset_index
    else:
        st.write("Headset microphone not found, switching to main microphone.")
        mic_index = None

    with sr.Microphone(device_index=mic_index) as source:
        recognizer.adjust_for_ambient_noise(source)
        st.write("Listening...")
        audio = recognizer.listen(source)
    try:
        response = recognizer.recognize_google(audio)
    except sr.RequestError:
        response = "API unavailable"
    except sr.UnknownValueError:
        response = "Unable to recognize speech"
    except OSError:
        st.write("Error accessing microphone. Retrying...")
        response = None
    
    return response


def translate_audio_to_hindi(recognizer, model, tokenizer):
    current_time = datetime.now().time()

    if not (current_time >= datetime.strptime("18:00", "%H:%M").time() or 
            current_time <= datetime.strptime("06:00", "%H:%M").time()):
        return "Please try after 6 PM IST."

    english_text = recognize_speech_from_mic(recognizer)

    if english_text in ["API unavailable", "Unable to recognize speech"]:
        return "Please repeat the audio."

    if english_text[0].lower() in ['m', 'o']:
        return "Words starting with 'M' or 'O' cannot be translated."

    encoded_text = tokenizer(english_text, return_tensors='pt')
    translated_tokens = model.generate(**encoded_text)
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

    return translated_text

def main():
    recognizer = sr.Recognizer()
    while True:
        st.write("Speak a word in English:")
        translation = translate_audio_to_hindi(recognizer, model_en_hi, tokenizer_en_hi)
        st.write("Translation:",translation)
        if translation == "Please try after 6 PM IST.":
            break

if __name__ == "__main__":
    main()


