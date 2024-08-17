import cv2
import numpy as np

def load_yolo():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    return net, classes, output_layers, colors

def detect_objects(img, net, output_layers):  
    height, width, channels = img.shape
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    return outs, width, height

def get_box_dimensions(outs, width, height):
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    return class_ids, confidences, boxes

def draw_labels(img, class_ids, confidences, boxes, classes, colors): 
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = colors[class_ids[i]]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y - 5), font, 1, color, 1)
    return img

def image_detection(image_path):  
    model, classes, output_layers, colors = load_yolo()
    image = cv2.imread(image_path)
    outs, width, height = detect_objects(image, model, output_layers)
    class_ids, confidences, boxes = get_box_dimensions(outs, width, height)
    img = draw_labels(image, class_ids, confidences, boxes, classes, colors)
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def webcam_detection():  
    model, classes, output_layers, colors = load_yolo()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        outs, width, height = detect_objects(frame, model, output_layers)
        class_ids, confidences, boxes = get_box_dimensions(outs, width, height)
        frame = draw_labels(frame, class_ids, confidences, boxes, classes, colors)
        
        cv2.imshow("Webcam", frame)
        if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
            break

    cap.release()
    cv2.destroyAllWindows()

# Uncomment one of the following lines to run the respective function:
# image_detection("your_image_path.jpg")
# webcam_detection()
