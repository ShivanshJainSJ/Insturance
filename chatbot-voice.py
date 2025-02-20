import os
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)


def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.pause_threshold = 1
        audio = r.listen(source,timeout=5, phrase_time_limit=5)

    try:
        print("Recognising...")
        query = r.recognize_google(audio,language='en-in')
        
        print(f'you said: {query}')
        
    except Exception as e:
        speak("Say it again i can't hear you")
        print("say that again")
        return ""
    return query.lower()

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice',voices[0].id)
engine.setProperty('rate',150)
def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def get_chatbot_response(user_input):
    response = genai.GenerativeModel('gemini-pro').generate_content(user_input)
    return response.text


def main():
    speak("Hello! I am your voice-enabled chatbot. How can I assist you today?")
    
    while True:
        command = take_command()
        if command:
            if 'exit' in command.lower():
                speak("Goodbye!")
                break
            else:
                # Get response from the chatbot
                response = get_chatbot_response(command)
                print(f"Chatbot: {response}")
                speak(response)

if __name__ == "__main__":
    main()