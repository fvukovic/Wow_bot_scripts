import pytesseract
import mss
import numpy
import cv2
import re
import time
import pydirectinput
import math
import win32api
import win32con
import json
import os
import random  # Dodano za nasumične skokove

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

monitor_compass = {"top": 1500, "left": 67, "width": 207, "height": 35}
monitor_coordinates = {"top": 1444, "left": 100, "width": 207, "height": 35}
 
def load_coordinates_from_json():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "coordinates.json")
    try:
        with open(json_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return []

coordinates_data = load_coordinates_from_json()

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

def calculate_angle_to_target(x1, y1, x2, y2):
    delta_x = x2 - x1  
    delta_y = y2 - y1  
    angle = math.degrees(math.atan2(delta_x, -delta_y))  
    return (angle + 360) % 360  

def rotate_towards_target(current_angle, target_angle):
    angle_diff = abs(((target_angle - current_angle + 180) % 360) - 180)  
    rotation_time = angle_diff / 134.83  

    if ((target_angle - current_angle) % 360) < 180:  
        print(f"🔄 Skrećem desno (D) za {angle_diff:.1f}° ({rotation_time:.2f}s)")
        press_key("d", rotation_time)
    else:  
        print(f"🔄 Skrećem lijevo (A) za {angle_diff:.1f}° ({rotation_time:.2f}s)")
        press_key("a", rotation_time)

def press_key(key, duration):
    vk_code = win32con.VK_LEFT if key == "a" else win32con.VK_RIGHT  
    win32api.keybd_event(vk_code, 0, 0, 0)  
    time.sleep(duration)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  

def jump():
    """Simulira skok pritiskom na SPACE."""
    print("🦘 Skočim (SPACE)")
    pydirectinput.press("space")

def move_to_target(target_x, target_y):
    with mss.mss() as sct:
        img_coords = numpy.array(sct.grab(monitor_coordinates))
        img_compass = numpy.array(sct.grab(monitor_compass)) 
        current_coords = extract_coordinates(img_coords)
        current_angle = extract_direction(img_compass)

        if current_coords and current_angle is not None:
            current_x, current_y = current_coords
            print(f"📍 Trenutne koordinate: {current_x}, {current_y}, Orijentacija: {current_angle}°")
            print(f"🎯 Ciljne koordinate: {target_x}, {target_y}")

            target_angle = calculate_angle_to_target(current_x, current_y, target_x, target_y)
            win32api.keybd_event(win32con.VK_UP, 0, 0, 0)
            rotate_towards_target(current_angle, target_angle)
            
            print("🚀 Krećem naprijed (W)")

            prev_x, prev_y = current_x, current_y
            vrijeme_zadnje_provjere = time.time()
            failed_attempts = 0  # Broji koliko puta kalibracija nije pomogla

            while True:
                img_coords = numpy.array(sct.grab(monitor_coordinates))
                current_coords = extract_coordinates(img_coords)
                
                if current_coords:
                    current_x, current_y = current_coords
                    print(f"📍 Trenutne koordinate: {current_x}, {current_y}")

                    if abs(current_x - target_x) < 0.3 and abs(current_y - target_y) < 0.3:
                        print(f"✅ Dosegnuta ciljna točka: {target_x}, {target_y}")
                        break
                    
                    if time.time() - vrijeme_zadnje_provjere > 2:  
                        trenutna_udaljenost = math.sqrt((current_x - target_x) ** 2 + (current_y - target_y) ** 2)
                        prosla_udaljenost = math.sqrt((prev_x - target_x) ** 2 + (prev_y - target_y) ** 2)

                        if trenutna_udaljenost >= prosla_udaljenost:
                            print("⚠️ Ne približavam se cilju! Ponovno izračunavam smjer...")
                            img_compass = numpy.array(sct.grab(monitor_compass))
                            current_angle = extract_direction(img_compass)

                            if current_angle is not None:
                                target_angle = calculate_angle_to_target(current_x, current_y, target_x, target_y)
                                rotate_towards_target(current_angle, target_angle)
                                
                                #neka malo skoci heheh
                                jump()

                                failed_attempts += 1
                                if failed_attempts >= 2:  
                                    print("⛔ Zapelo! Radim zaokret od 90° i skačem...")
                                    target_angle = (target_angle + 90) % 360
                                    rotate_towards_target(current_angle, target_angle)
                                    jump()
                                    failed_attempts = 0  

                        else:
                            failed_attempts = 0  

                        prev_x, prev_y = current_x, current_y
                        vrijeme_zadnje_provjere = time.time()
                time.sleep(0.5)  # Pauza da ne skenira prečesto


            print("🎯 Cilj postignut, nastavljam dalje...")
            
time.sleep(3)

for point in coordinates_data:
    move_to_target(point["x"], point["y"])

win32api.keybd_event(win32con.VK_UP, 0, win32con.KEYEVENTF_KEYUP, 0)  
