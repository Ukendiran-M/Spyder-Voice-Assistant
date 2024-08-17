import os
import pyttsx3
import datetime
import speech_recognition as sr
import cv2
import webbrowser
import requests
from serpapi import GoogleSearch

# Initialize the text-to-speech engine
try:
    engine = pyttsx3.init()
except Exception as e:
    print(f"Error initializing TTS engine: {e}")
    engine = None

def speak(audio):
    """Convert text to speech."""
    if engine:
        print(audio)  # Print the text
        engine.say(audio)
        engine.runAndWait()
    else:
        print("TTS engine is not initialized. Cannot speak.")

def take_command():
    """Take command from the user through the microphone."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
    
    try:
        print("Recognizing....")
        query = recognizer.recognize_google(audio, language='en-US')
        print(f"You said: {query}")  # Print the recognized text
        return query.lower()
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        speak("I didn't catch that. Please say that again.")
        return "None"
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        speak("Sorry, my speech service is down.")
        return "None"

def capture_image():
    """Capture an image from the webcam."""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Could not open video device")
        ret, frame = cap.read()
        if ret:
            image_path = 'webcam_image.png'
            cv2.imwrite(image_path, frame)
            speak("Image captured successfully")
            cap.release()
            return image_path
        else:
            cap.release()
            speak("Failed to capture image")
            return None
    except Exception as e:
        print(f"Error capturing image: {e}")
        speak("Sorry, I could not capture the image.")
        return None

def search_similar_images_google(image_path):
    """Search for similar images using SERP API."""
    try:
        search = GoogleSearch({
            "api_key": "e9473f626cbac80ba7cb43e867924a36c0806a7acfe845db3b903e6ab5740548q",  # Replace with your actual SERP API key
            "engine": "google_reverse_image",
            "image_url": image_path,
            "tbm": "isch"
        })
        results = search.get_dict()

        if "images_results" in results:
            similar_images = results["images_results"]
            if similar_images:
                # Get the URL of the first similar image
                similar_image_url = similar_images[0]["original"]
                webbrowser.open(similar_image_url)
                speak("Opening Google search with similar images...")
            else:
                speak("No similar images found.")
        else:
            speak("No similar images found.")

    except Exception as e:
        speak(f"An error occurred while searching for similar images: {e}")

def main():
    """Main function to run the voice assistant."""
    speak("I am your voice assistant. How can I help you?")
    
    while True:
        query = take_command()
        if query == "None":
            continue
        
        if 'what can you do' in query:
            speak("I can take pictures and recognize objects in them, tell jokes, and more.")
        
        elif 'take image' in query:
            image_path = capture_image()
            if image_path:
                speak("Analyzing the image...")
                speak("Searching for similar images...")
                search_similar_images_google(image_path)  # Call the new function here

if __name__ == "__main__":
    main()
