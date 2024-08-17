import cv2
import numpy as np
import pyttsx3
import speech_recognition as sr
import os
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