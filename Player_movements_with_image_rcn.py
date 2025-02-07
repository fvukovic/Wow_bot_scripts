import pytesseract
import mss
import numpy
from PIL import Image
import cv2
import re
import time
import pydirectinput

# Postavljanje Tesseract OCR puta
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Lista koordinata koje bot treba slijediti
coordinates_data = [
    {"x": 55.17, "y": 37.45}
]

# Postavke ekrana za snimanje koordinata za Ficin laptop
monitor = {"top": 1500, "left": 67, "width": 207, "height": 35}

def extract_coordinates(img):
    """Ekstrahira koordinate iz slike koristeći OCR."""
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY_INV)
    text = pytesseract.image_to_string(thresh_image)
    coordinates_pattern = r'(\d+\.\d+),\s*(\d+\.\d+)'
    matches = re.findall(coordinates_pattern, text)
    
    if matches:
        return float(matches[0][0]), float(matches[0][1])
    return None

def is_moving_correctly(prev_x, prev_y, curr_x, curr_y, target_x, target_y):
    """Provjerava idemo li u pravom smjeru prema cilju."""
    moving_towards_x = (target_x - prev_x) * (curr_x - prev_x) > 0
    moving_towards_y = (target_y - prev_y) * (curr_y - prev_y) > 0
    return moving_towards_x and moving_towards_y

def move_to_target(target_x, target_y):
    """Kretanje prema ciljnim koordinatama uz pamćenje smjera."""

    # Drži W stalno pritisnut
    pydirectinput.keyDown("w")
    print("Držim W (kretanje naprijed)...")

    last_adjustment_time = time.time()  # Zadnji put kad smo prilagodili smjer
    last_x, last_y = None, None  # Posljednje koordinate za provjeru smjera

    with mss.mss() as sct:
        while True:
            img = numpy.array(sct.grab(monitor))
            cv2.imshow("Current Position", img)

            current_coords = extract_coordinates(img)
            if current_coords:
                current_x, current_y = current_coords
                print(f"Trenutne koordinate: {current_x}, {current_y}")

                # Ako smo dovoljno blizu cilju, prekini petlju
                if abs(current_x - target_x) < 1 and abs(current_y - target_y) < 1:
                    print(f"Dosegnuta ciljna točka: {target_x}, {target_y}")
                    pydirectinput.keyUp("w")
                    pydirectinput.keyUp("a")
                    pydirectinput.keyUp("d")
                    break

                # Svakih 5 sekundi provjeri smjer
                if time.time() - last_adjustment_time >= 1:
                    last_adjustment_time = time.time()  # Resetiraj timer

                    if last_x is not None and last_y is not None:
                        if is_moving_correctly(last_x, last_y, current_x, current_y, target_x, target_y):
                            print("✅ Smjer je dobar, ne diram A/D.")
                        else:
                            if current_x < target_x - 0.05:  # Treba skrenuti desno
                                print("⚠️ Skrećem desno (D)")
                                pydirectinput.keyDown("d")
                                time.sleep(0.1)
                                pydirectinput.keyUp("d")

                            elif current_x > target_x + 0.05:  # Treba skrenuti lijevo
                                print("⚠️ Skrećem lijevo (A)")
                                pydirectinput.keyDown("a")
                                time.sleep(0.1)
                                pydirectinput.keyUp("a")

                    # Ažuriraj zadnje koordinate za sljedeću provjeru
                    last_x, last_y = current_x, current_y

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            time.sleep(0.1)

    pydirectinput.keyUp("w")  # Pusti W nakon dolaska na cilj
    cv2.destroyAllWindows()

# Ovo sam stavio tek toliko da krene nakon 3 sekunde, da mogu prebacit prozor
time.sleep(3)

# Glavna petlja - prolazak kroz sve ciljne koordinate
for point in coordinates_data:
    move_to_target(point["x"], point["y"])
    time.sleep(1)
