from RPi import GPIO
import time
import cv2
import numpy as np
import torch  # For YOLOv8 model
import subprocess
from ultralytics import YOLO  # YOLOv8 from Ultralytics

# GPIO Setup
GPIO.setmode(GPIO.BCM)

# Define the IR sensor pin
IR_SENSOR_PIN = 7  
GPIO.setup(IR_SENSOR_PIN, GPIO.IN)

# Define Stepper Motor pins
MOTOR1_PINS = (5, 6, 13, 19)
MOTOR2_PINS = (12, 16, 20, 21)  
MOTOR3_PINS = (4, 17, 27, 22)  

# Initialize Stepper Motors GPIO Pins
for pin in MOTOR1_PINS + MOTOR2_PINS + MOTOR3_PINS:
    GPIO.setup(pin, GPIO.OUT)


STEP_SEQUENCE  = [
    [1, 0, 1, 0],  # Step 1: Coil A1 and Coil B1 energized
    [0, 1, 1, 0],  # Step 2: Coil A2 and Coil B1 energized
    [0, 1, 0, 1],  # Step 3: Coil A2 and Coil B2 energized
    [1, 0, 0, 1],  # Step 4: Coil A1 and Coil B2 energized
]

# Load YOLO pretrained model
model = YOLO('best.pt')  

def activate_motor(motor_pins):
    # Activate the motor by setting all pins to HIGH
    for pin in motor_pins:
        GPIO.output(pin, GPIO.HIGH)

def deactivate_motor(motor_pins):
    # Deactivate the motor by setting all pins to LOW
    for pin in motor_pins:
        GPIO.output(pin, GPIO.LOW)

# Camera setup using libcamera
def capture_image():
    # Capture image using libcamera
    image_filename = "/home/shree/Desktop/project/images/captured_image.jpg"
    
    # Use libcamera-still command to capture image
    subprocess.run(["libcamera-still", "-o", image_filename])
    
    return image_filename

def detect_objects(image_filename):
    # Read the image using OpenCV
    img = cv2.imread(image_filename)

    # Perform object detection using YOLO model
    results = model(img)  # Detect objects with YOLO
    
    return results

def get_detected_object_class(results):
    # Post-process results to get the highest confidence detected object class
    detected_classes = results[0].names  # Getting class names
    detections = results[0].boxes  # Bounding boxes for detected objects
    class_id = detections.cls.tolist()
    confidence = detections.conf.tolist()
    
    # Get the class with the highest confidence
    if len(class_id) > 0:
        # Getting the class with the highest confidence
        highest_confidence_index = np.argmax(confidence)  # The index of the highest confidence
        object_class = int(class_id[highest_confidence_index])  # The class of the object detected
        print("detected object Class: ", object_class)
        return object_class
    else:
        return None

def map_class_to_motor(object_class):
    if object_class == 6:  # compost
        return MOTOR1_PINS
    elif object_class == 5:  # trash
        return MOTOR2_PINS
    elif object_class in [0,1,2,3,4]:  # recycle
        return MOTOR3_PINS
    else:
        return None
    

def rotate_motor(motor_pins, steps):
    # Rotate the motor for a specific number of steps
    activate_motor(motor_pins)
    for _ in range(steps):
        for step in STEP_SEQUENCE:
            for pin, value in zip(motor_pins, step):
                GPIO.output(pin, value)
            time.sleep(0.003)  # Adjust sleep time for speed control
    deactivate_motor(motor_pins)

def main():
    try:
        while True:
            # Check if IR sensor is activated
            if not GPIO.input(IR_SENSOR_PIN):
                print("IR Sensor triggered!")
                
                # This one line code was removed in the demo since the dmo models belt was smaller and this step was not needed.
                # Motor 1 runs for a fixed number of steps when IR sensor is triggered
                rotate_motor(MOTOR1_PINS, 800)  
                
                # Capture image
                print("Capturing image...")
                image_filename = capture_image()
                
                # Detect objects in the image using YOLOv8
                results = detect_objects(image_filename)
                
                # Get the detected object class
                object_class = get_detected_object_class(results)
                if object_class is not None:
                    
                    # Map the detected object to a motor and rotate
                    motor_pins = map_class_to_motor(object_class)
                    if motor_pins:
                        rotate_motor(motor_pins, 550)  # Rotate the corresponding motor
                    else:
                        print("No motor assigned for the detected class.")
                else:
                    print("No object detected.")
                
                # Wait before next iteration
                time.sleep(1)
            else:
                print("Waiting for IR trigger...")
                time.sleep(1)
            time.sleep(10)
    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
