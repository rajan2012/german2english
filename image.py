import streamlit as st
import os
from PIL import Image

def image_slideshow(images_path):
    """
    Creates a slideshow of images in the specified directory.

    Parameters:
    images_path (str): The path to the directory containing images.
    """
    # Get a list of image files in the folder
    image_files = [f for f in os.listdir(images_path) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Sort the image files to ensure consistent order
    image_files.sort()

    # Initialize session state for the image index if not already set
    if 'image_index' not in st.session_state:
        st.session_state.image_index = 0

    # Define navigation buttons
    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        if st.button('Previous'):
            st.session_state.image_index = max(0, st.session_state.image_index - 1)

    with col3:
        if st.button('Next'):
            st.session_state.image_index = min(len(image_files) - 1, st.session_state.image_index + 1)

    # Load and display the selected image
    selected_image_path = os.path.join(images_path, image_files[st.session_state.image_index])
    image = Image.open(selected_image_path)
    st.image(image, caption=image_files[st.session_state.image_index], use_column_width=True)
