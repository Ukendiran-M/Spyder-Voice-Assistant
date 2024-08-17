import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser as wb
import pyjokes
import os
import pyautogui
import wolframalpha
import requests
import time
import platform
import random
import threading
import cv2
import numpy as np
import matplotlib.pyplot as plt

def initialize_tts_engine():
    """Initialize the text-to-speech engine."""
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        print(f"Error initializing TTS engine: {e}")
        return None

engine = initialize_tts_engine()

def speak(audio):
    """Convert text to speech."""
    if engine:
        print(audio)  # Print the text
        engine.say(audio)
        engine.runAndWait()
    else:
        print("TTS engine is not initialized. Cannot speak.")

def get_current_time():
    """Get the current time."""
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    return current_time

def get_current_date():
    """Get the current date."""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    return current_date

def wish():
    """Wish the user based on the time."""
    speak("Welcome back!")
    current_hour = datetime.datetime.now().hour

    if 5 <= current_hour < 12:
        speak("Good morning")
    elif 12 <= current_hour < 18:
        speak("Good afternoon")
    elif 18 <= current_hour < 24:
        speak("Good evening")
    else:
        speak("Good night")

    speak("Spyder, Powerful Intelligence")

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
        speak("I didn't catch that. Please say that again.")
        return "None"
    except sr.RequestError as e:
        speak("Sorry, my speech service is down.")
        return "None"
def load_yolo():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    return net, classes, output_layers

def capture_image():
    """Capture an image from the webcam."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Could not open video device")
    
    # Allow the camera to warm up
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise Exception("Failed to capture image")
    
    image_path = 'webcam_image.png'
    cv2.imwrite(image_path, frame)
    cap.release()
    return image_path

def detect_objects(image_path):
    net, classes, output_layers = load_yolo()
    image = cv2.imread(image_path)
    height, width, channels = image.shape

    # Prepare the image for YOLO
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Analyze the output
    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            speak(f"Detected {label}")
            color = (0, 255, 0)
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(image, label, (x, y + 30), font, 2, color, 2)

    # Display the image using matplotlib
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')  # Hide the axis
    plt.show()

def get_wikipedia_summary(query):
    """Get summary from Wikipedia."""
    try:
        speak("Searching Wikipedia...")
        query = query.replace('wikipedia', '')
        result = wikipedia.summary(query, sentences=2)
        speak(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("Multiple results found. Please specify your search.")
    except wikipedia.exceptions.PageError:
        speak("No information found.")

brave_path = "C://Program Files//BraveSoftware//Brave-Browser//Application//brave.exe"

wb.register('brave', None, wb.BackgroundBrowser(brave_path))

def search(query, search_engine):
    speak(f"What should I search in {search_engine}?")
    search_term = take_command()
    if search_term != "None":
        speak("Searching...")
        try:
            wb.get("brave").open_new_tab(f"https://www.{search_engine}.com/search?q={search_term}")
            print(f"Opened Brave browser for searching {search_term} on {search_engine}")
        except Exception as e:
            print(f"Failed to open Brave browser: {e}")

def tell_joke():
    """Tell a joke."""
    speak(pyjokes.get_joke())

def control_volume(action):
    """Control the system volume."""
    if action == "mute":
        pyautogui.press("volumemute")
        speak("Volume muted.")
    elif action == "increase":
        pyautogui.press("volumeup", presses=5)
        speak("Volume increased.")
    elif action == "decrease":
        pyautogui.press("volumedown", presses=5)
        speak("Volume decreased.")

def take_screenshot():
    """Take a screenshot."""
    try:
        img = pyautogui.screenshot()
        img.save('screenshot.png')
        speak("Screenshot taken and saved as screenshot.png")
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        speak("Sorry, I could not take the screenshot.")

def get_weather(city):
    """Get weather information for a city."""
    api_key = "fd36ce5a74d7bf6ddc1fc354db3f8d07"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "q=" + city + "&appid=" + api_key + "&units=metric"
    
    try:
        response = requests.get(complete_url)
        data = response.json()
        if data["cod"] != "404":
            weather = data["main"]
            temperature = weather["temp"]
            pressure = weather["pressure"]
            humidity = weather["humidity"]
            weather_desc = data["weather"][0]["description"]
            weather_report = (f"Temperature: {temperature}°C\n"
                              f"Pressure: {pressure} hPa\n"
                              f"Humidity: {humidity}%\n"
                              f"Weather description: {weather_desc}")
            speak(weather_report)
        else:
            speak("City not found.")
    except Exception as e:
        print(f"Error retrieving weather data: {e}")
        speak("Sorry, I couldn't retrieve the weather information.")

def play_music():
    """Play music from a specified directory."""
    music_dir = 'path_to_your_music_directory'  # Update the path
    songs = os.listdir(music_dir)
    song = random.choice(songs)
    os.startfile(os.path.join(music_dir, song))
    speak("Playing music")

def get_news():
    """Get the latest news headlines."""
    api_key = "bda4525fb5ae4fd29ca703e1c368d517"
    base_url = "https://newsapi.org/v2/top-headlines?"
    country = "us"
    complete_url = base_url + f"country={country}&apiKey={api_key}"
    
    try:
        response = requests.get(complete_url)
        data = response.json()
        articles = data["articles"]
        headlines = [article["title"] for article in articles[:5]]  # Get top 5 headlines
        news_report = "\n".join(headlines)
        speak("Here are the top news headlines:")
        speak(news_report)
    except Exception as e:
        print(f"Error retrieving news: {e}")
        speak("Sorry, I couldn't retrieve the news.")

def set_alarm(alarm_time):
    """Set an alarm."""
    def alarm_thread():
        speak(f"Alarm set for {alarm_time}")
        while True:
            current_time = datetime.datetime.now().strftime("%H:%M")
            if current_time == alarm_time:
                speak("Wake up! It's time!")
                break
            time.sleep(30)
    thread = threading.Thread(target=alarm_thread)
    thread.start()


def set_reminder(reminder_text):
    """Set a reminder."""
    with open('reminders.txt', 'a') as file:
        file.write(reminder_text + "\n")
    speak("Reminder set.")

def show_reminders():
    """Show all reminders."""
    try:
        with open('reminders.txt', 'r') as file:
            reminders = file.read()
            if reminders:
                speak("Here are your reminders:")
                print(reminders)
                speak(reminders)
            else:
                speak("You have no reminders.")
    except FileNotFoundError:
        speak("You have no reminders.")

def get_system_info():
    """Get system information."""
    system_info = platform.uname()
    info = (f"System: {system_info.system}\n"
            f"Node Name: {system_info.node}\n"
            f"Release: {system_info.release}\n"
            f"Version: {system_info.version}\n"
            f"Machine: {system_info.machine}\n"
            f"Processor: {system_info.processor}")
    print(info)
    speak(info)

def main():
    """Main function to run the voice assistant."""
    wish()

    while True:
        query = take_command()
        if query == "None":
            continue
        
        if 'what can you do' in query:
            speak("I can open apps, search and answer any question, take notes, calculate, tell jokes, take screenshots, control volume, and more.")

        elif 'who are you' in query:
            speak('I am Spyder AI,your voice assistant')

        elif 'capture' in query or 'take image' in query:
            try:
                image_path = capture_image()
                speak("Image captured successfully. Analyzing the image...")
                detect_objects(image_path)
            except Exception as e:
                speak(f"An error occurred: {e}")

        elif 'initialise spider' in query:
            speak('How can I help you?')

        elif 'time' in query:
            speak("The current time is " + get_current_time())

        elif 'date' in query:
            speak("The current date is " + get_current_date())

        elif 'tell me' in query:
            get_wikipedia_summary(query)

        elif 'search in youtube' in query:
            search(query, "youtube")

        elif 'search in google' in query:
            search(query, "google")

        elif any(word in query for word in ['what', 'which', 'who']):
            query = query.replace("what is", "").replace("which is", "").replace("who is", "")
            speak(f"You asked me about {query}")
            wb.open_new_tab(f"https://www.google.com/search?q={query}")

        elif 'joke' in query:
            tell_joke()

        elif 'go offline' in query:
            speak("Going offline")
            quit()  

        elif 'screenshot' in query:
            take_screenshot()

        elif 'remember' in query:
            speak("What should I remember?")
            memory = take_command()
            if memory != "None":
                speak("You asked me to remember that " + memory)
                with open('memory.txt', 'w') as file:
                    file.write(memory)

        elif 'what you remember' in query:
            try:
                with open('memory.txt', 'r') as file:
                    memory = file.read()
                    speak("You asked me to remember that " + memory)
            except FileNotFoundError:
                speak("You have not asked me to remember anything yet.")

        elif 'where' in query:
            query = query.replace("where is", "")
            location = query
            speak(f"You asked to locate {location}")
            wb.open_new_tab(f"https://www.google.com/maps/place/{location}")

        elif 'calculate' in query:
            client = wolframalpha.Client('T2LXW8-HTUJGP2G48')
            query = query.replace("calculate", "")
            res = client.query(query)
            try:
                answer = next(res.results).text
                speak('The answer is ' + answer)
            except StopIteration:
                speak("Sorry, I could not find an answer.")

        elif 'open steam' in query:
            speak("Opening Steam")
            steam = r'C:\Users\Public\Desktop\Steam.lnk'  # Update the path
            os.startfile(steam)

        elif 'write a note' in query:
            speak("What should I write?")
            notes = take_command()
            if notes != "None":
                with open('note.txt', 'w') as file:
                    file.write(notes)
                speak("Note saved successfully")

        elif 'show note' in query:
            speak('Showing notes')
            try:
                with open('note.txt', 'r') as file:
                    notes = file.read()
                    print(notes)
                    speak(notes)
            except FileNotFoundError:
                speak("No notes found.")

        elif 'mute volume' in query:
            control_volume("mute")

        elif 'increase volume' in query:    
            control_volume("increase")

        elif 'decrease volume' in query:
            control_volume("decrease")

        elif 'weather' in query:
            speak("Which city's weather would you like to know?")
            city = take_command()
            if city != "None":
                get_weather(city)

        elif 'play music' in query:
            play_music()

        elif 'news' in query:
            get_news()

        elif 'set alarm' in query:
            speak("Please tell me the time to set the alarm. For example, say 07:30 AM.")
            alarm_time = take_command()
            if alarm_time != "None":
                set_alarm(alarm_time)

        elif 'set reminder' in query:
            speak("What should I remind you about?")
            reminder = take_command()
            if reminder != "None":
                set_reminder(reminder)

        elif 'show reminders' in query:
            show_reminders()

        elif 'system information' in query:
            get_system_info()

        elif 'sign out' in query:
            os.system("shutdown -l") 
        elif 'restart' in query:
            os.system("shutdown /r /t 1")
        elif 'shutdown' in query:
            os.system("shutdown /s /t 1")
        elif 'sleep' in query:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif 'exit' in query or 'quit' in query:
            speak("Goodbye!")
            break

if __name__ == "__main__":
    main()