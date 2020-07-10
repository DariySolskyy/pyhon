# Using Using Tesseract OCR with Python to define images of Nutritional tables from list of images
# Scrypt is written based on Adrian Rosebrock's post https://www.pyimagesearch.com/2017/07/10/using-tesseract-ocr-python/

from PIL import Image
import pytesseract
import argparse
import cv2
import os
import urllib
import requests

def ocr(img_file):
    method = 'thresh'

    # load the example image and convert it to grayscale
    image = cv2.imread(img_file)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # check to see if we should apply thresholding to preprocess theimage
    if method == "thresh":
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # make a check to see if median blurring should be done to remove noise
    elif method == "blur":
        gray = cv2.medianBlur(gray, 3)

    # write the grayscale image to disk as a temporary file so we can apply OCR to it
    file_grey = "ocr_3_gr.jpg".format(os.getpid())
    cv2.imwrite(file_grey, gray)

    # load the image as a PIL/Pillow image, apply OCR, and then delete the temporary file
    img_text = pytesseract.image_to_string(Image.open(file_grey))
    os.remove(file_grey)

    return img_text

img_url_list = ['https://images-na.ssl-images-amazon.com/images/I/91FYCc3%2BByL._SL1500_.jpg',
 'https://images-na.ssl-images-amazon.com/images/I/91cDzIam8JL._SL1500_.jpg',
 'https://images-na.ssl-images-amazon.com/images/I/81fsdNTVOsL._SL1500_.jpg',
 'https://images-na.ssl-images-amazon.com/images/I/81h4VTXRXpL._SL1500_.jpg',
 'https://images-na.ssl-images-amazon.com/images/I/91WCaDlq9tL._SL1500_.jpg',
 'https://images-na.ssl-images-amazon.com/images/I/710YG9oqE3L._SL1500_.jpg',
 'https://images-na.ssl-images-amazon.com/images/I/81zCHfi70AL._SL1500_.jpg',
 'https://images-na.ssl-images-amazon.com/images/I/71yR9JkxBuL._SL1000_.jpg',
 'https://images-na.ssl-images-amazon.com/images/I/81cpY7e6mqL._SL1500_.jpg',
 'https://images-na.ssl-images-amazon.com/images/I/81j6PKAV6PL._SL1500_.jpg']

nutr_img_list = []

for image in img_url_list:
    img_file = str(image.split('/')[-1])
    urllib.request.urlretrieve(image, img_file)

    try:
        check = "Nutrition" in ocr(img_file)
    except SimulationException as sim_exc:
        print("error", sim_exc)
    else:
        if check:
            nutr_img_list.append(image)
    
    os.remove(img_file)
print(nutr_img_list)
