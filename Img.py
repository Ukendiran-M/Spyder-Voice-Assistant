import os
import pyttsx3
import datetime
import speech_recognition as sr
import cv2
import requests

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

def analyze_image(image_path):
    """Upload an image to ImgBB API."""
    try:
        with open("imgbb_api_key.txt", "r") as file:
            imgbb_api_key = file.read().strip()
    except FileNotFoundError:
        print("API key file not found.")
        return "Error: API key file not found."

    url = "https://api.imgbb.com/1/upload"
    with open(image_path, "rb") as img_file:
        response = requests.post(
            url,
            files={"image": img_file},
            params={"key": imgbb_api_key}
        )
        
    if response.status_code == 200:
        results = response.json()
        if 'data' in results and 'url' in results['data']:
            image_url = results['data']['url']
            return image_url
        else:
            return "No image URL found in the response."
    else:
        return f"Error uploading image: {response.text}"

def search_similar_images_google(image_url):
    """Search for similar images on Google."""
    api_key = 'AIzaSyABoQxcXQamCQh40aynrQ3_l-MCvTI7chA'
    search_engine_id = '661fedf2855c14308'
    search_url = f'https://www.googleapis.com/customsearch/v1?q={image_url}&key={api_key}&cx={search_engine_id}&searchType=image'
    
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data:
                for item in data['items']:
                    speak(f"Similar image found: {item['link']}")
                    # You can do something with the links here
            else:
                speak("No similar images found on Google.")
        else:
            speak("Failed to search for similar images on Google.")
    except Exception as e:
        speak(f"An error occurred while searching for similar images on Google: {e}")

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
                image_url = analyze_image(image_path)
                speak(f"Image uploaded successfully. Image URL: {image_url}")
                speak("Searching for similar images on Google...")
                search_similar_images_google(image_url)

if __name__ == "__main__":
    main()
