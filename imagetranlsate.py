import streamlit as st
import cv2
import numpy as np
import pytesseract
from googletrans import Translator


# Function to translate text using Google Translate
def translate_text(text, dest_lang='de'):
    translator = Translator()
    translation = translator.translate(text, dest=dest_lang)
    return translation.text


# Title of the app
st.title("Image to German Text Translator")

# File uploader for images
uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

# Initialize webcam capture
use_webcam = st.checkbox("Use webcam")

if use_webcam:
    picture = st.camera_input("Take a picture")

# Display the uploaded image or webcam picture
if uploaded_file or (use_webcam and picture):
    # Read the image
    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
    elif use_webcam and picture:
        file_bytes = np.asarray(bytearray(picture.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

    # Display the image
    st.image(img, caption='Uploaded Image', use_column_width=True)

    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to extract text
    extracted_text = pytesseract.image_to_string(gray)
    st.write("Extracted Text:", extracted_text)

    # Translate the text to German
    if extracted_text:
        translated_text = translate_text(extracted_text)
        st.write("Translated Text in German:", translated_text)
