import torch
import cv2
import pyttsx3
import speech_recognition as sr
import matplotlib.pyplot as plt

# Initialize the text-to-speech engine
def init_tts_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        print(f"Error initializing TTS engine: {e}")
        return None

engine = init_tts_engine()

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
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    results = model(image_path)

    results.print()  # Print results to the console

    # Display the image using matplotlib
    img = results.render()[0]
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.axis('off')  # Hide the axis
    plt.show()

    # Speak detected objects
    labels = results.names
    for *box, conf, cls in results.xyxy[0]:
        speak(f"Detected {labels[int(cls)]} with confidence {conf:.2f}")

def main():
    """Main function to run the voice assistant."""
    speak("I am your voice assistant. How can I help you?")
    
    while True:
        speak("Please give a command.")
        query = take_command()
        if query == "None":
            continue
        
        if 'what can you do' in query:
            speak("I can take pictures and recognize objects in them, tell jokes, and more.")
        
        elif 'capture' in query or 'take image' in query:
            try:
                image_path = capture_image()
                speak("Image captured successfully. Analyzing the image...")
                detect_objects(image_path)
            except Exception as e:
                speak(f"An error occurred: {e}")
        
        elif 'exit' in query or 'quit' in query:
            speak("Goodbye!")
            break

if __name__ == "__main__":
    main()
