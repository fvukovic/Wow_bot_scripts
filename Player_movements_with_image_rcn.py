import pytesseract
import mss
import numpy
from PIL import Image
import cv2
import re
import time
import pydirectinput
import math

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

monitor_compass = {"top": 1500, "left": 67, "width": 207, "height": 35}
monitor_coordinates = {"top": 1444, "left": 100, "width": 207, "height": 35}

rotation_time_per_360 = 1.9  # Vrijeme potrebno za punu rotaciju (360°)

coordinates_data = [{"x": 26.00, "y": 50.00}]

def extract_coordinates(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    text = pytesseract.image_to_string(thresh)
    match = re.search(r'(\d+\.\d+)[^\d]+(\d+\.\d+)', text)
    return (float(match.group(1)), float(match.group(2))) if match else None

def extract_direction(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, numpy.ones((1, 1), numpy.uint8))
    text = pytesseract.image_to_string(processed, config='--psm 7')
    match = re.search(r'(\d+\.\d+|\d+)', text)  
 
    return float(match.group(1)) if match else None

def calculate_angle_to_target(lat1, lon1, lat2, lon2):

    print(lon1, lat1, lon2, lat2)
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lon = lon2 - lon1

    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    print((initial_bearing + 360) % 360)
    return (initial_bearing + 360) % 360  # Normalize to 0°–360°

def rotate_towards_target(current_angle, target_angle):
    """Okreće lika u pravom smjeru uzimajući u obzir WoW sustav."""
    angle_diff = ((target_angle - current_angle + 180) % 360) - 180  # Ispravljena formula

    print(f"🔍 Kutna razlika (nakon ispravke): {angle_diff}°")  # Debug ispis
    
    rotation_time = abs(angle_diff) / 360 * rotation_time_per_360

    if angle_diff < 2:  # Skretanje LIJEVO (A)
        print(f"🔄 Skrećem lijevo (A) za {angle_diff:.1f}° ({rotation_time:.2f}s)")
        pydirectinput.keyDown("a")
        time.sleep(rotation_time)
        pydirectinput.keyUp("a")
    elif angle_diff > -2:  # Skretanje DESNO (D)
        print(f"🔄 Skrećem desno (D) za {-angle_diff:.1f}° ({rotation_time:.2f}s)")
        pydirectinput.keyDown("d")
        time.sleep(rotation_time)
        pydirectinput.keyUp("d")

def move_to_target(target_x, target_y):
    """Okreće lika prema cilju i zatim se kreće naprijed."""
    with mss.mss() as sct:
        img_coords = numpy.array(sct.grab(monitor_coordinates))
        img_compass = numpy.array(sct.grab(monitor_compass)) 
        current_coords = extract_coordinates(img_coords)
        current_angle = extract_direction(img_compass)
        
        if current_coords and current_angle is not None:
            current_x, current_y = current_coords
            print(f"Trenutne koordinate: {current_x}, {current_y}, Orijentacija: {current_angle}°")
            
            target_angle = calculate_angle_to_target(current_y,current_x , target_y, target_x) 

            rotate_towards_target(current_angle, target_angle)
            
            print("🚀 Krećem naprijed (W)")
            #pydirectinput.keyDown("w")
            
            while True:
                img_coords = numpy.array(sct.grab(monitor_coordinates))
                current_coords = extract_coordinates(img_coords)
                
                if current_coords:
                    current_x, current_y = current_coords
                    print(f"📍 Koordinate: {current_x}, {current_y}")
                    
                    if abs(current_x - target_x) < 1 and abs(current_y - target_y) < 1:
                        print(f"🎯 Dosegnuta ciljna točka: {target_x}, {target_y}")
                        break
                
                time.sleep(0.2)
            
            pydirectinput.keyUp("w")

time.sleep(3)

for point in coordinates_data:
    move_to_target(point["x"], point["y"])
    time.sleep(1)
