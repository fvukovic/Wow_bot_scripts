import pytesseract
import pyautogui
import mss 
import numpy
from PIL import Image
import cv2
import re

# Set the tesseract command path (if necessary)
# For Windows:
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Load the image using OpenCV or PIL
image_path = 'C:\\Users\\Lenovo\\Pictures\\Screenshots\\Snimka zaslona 2025-02-06 200337.png'  # Replace with your image path
image = cv2.imread(image_path)

# Convert the image to grayscale for better accuracy in OCR
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply thresholding to make the white text more prominent against the black background
_, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY_INV)

# Use pytesseract to extract text from the processed image
text = pytesseract.image_to_string(thresh_image)

# Regular expression pattern to match coordinates in the format xx.xx, yy.yy
coordinates_pattern = r'(\d+\.\d+),\s*(\d+\.\d+)'

# Find all matches in the extracted text
coordinates = re.findall(coordinates_pattern, text)

# Print the extracted coordinates
for coord in coordinates:
    print(f"Extracted coordinates: {coord[0]}, {coord[1]}")


w,h = pyautogui.size()
print("Screen res: W: " + str(w) + " h:" + str(h))
img = None
monitor = {"top": 1000, "left": 21, "width": 138, "height": 25}
with mss.mss() as sct:
    while True:
        img = sct.grab(monitor)
        img = numpy.array(img)

        cv2.imshow("Bla bla", img)
        
                # Convert the image to grayscale for better accuracy in OCR
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to make the white text more prominent against the black background
        _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY_INV)

        # Use pytesseract to extract text from the processed image
        text = pytesseract.image_to_string(thresh_image)

        # Regular expression pattern to match coordinates in the format xx.xx, yy.yy
        coordinates_pattern = r'(\d+\.\d+),\s*(\d+\.\d+)'

        # Find all matches in the extracted text
        coordinates = re.findall(coordinates_pattern, text)

        # Print the extracted coordinates
        for coord in coordinates:
            print(f"Extracted coordinates: {coord[0]}, {coord[1]}")
        
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

cv2.destroyAllWindows()