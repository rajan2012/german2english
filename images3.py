import streamlit as st
import boto3
import os
from PIL import Image
from io import BytesIO

from loaddata import get_s3_images

import streamlit as st
import boto3
from PIL import Image
from io import BytesIO

def get_s3_images(bucket_name, prefix=''):
    """
    Fetch image files from an S3 bucket.

    Parameters:
    bucket_name (str): The name of the S3 bucket.
    prefix (str): The prefix for the files to fetch (default is '').

    Returns:
    list: A list of image file keys.
    """
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    image_files = [item['Key'] for item in response.get('Contents', []) if item['Key'].endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return image_files

def image_slideshow(bucket_name, prefix=''):
    """
    Creates a slideshow of images from an S3 bucket.

    Parameters:
    bucket_name (str): The name of the S3 bucket.
    prefix (str): The prefix for the files to fetch (default is '').
    """
    # Get a list of image files in the bucket
    image_files = get_s3_images(bucket_name, prefix)

    # Sort the image files to ensure consistent order
    image_files.sort()

    # Initialize session state for the image index if not already set
    if 'image_index' not in st.session_state:
        st.session_state.image_index = 0

    # Slider for navigation
    st.session_state.image_index = st.slider('Slide to select image', 0, len(image_files) - 1, st.session_state.image_index)

    # Load and display the selected image
    s3 = boto3.client('s3')
    selected_image_key = image_files[st.session_state.image_index]
    response = s3.get_object(Bucket=bucket_name, Key=selected_image_key)
    image_data = response['Body'].read()
    image = Image.open(BytesIO(image_data))
    st.image(image, caption=selected_image_key, use_column_width=True)



def image_slideshow2(bucket_name, prefix=''):
    """
    Fetches and sorts image URLs for a slideshow.

    Parameters:
    bucket_name (str): The name of the S3 bucket.
    prefix (str): The prefix for the files to fetch (default is '').

    Returns:
    list: A sorted list of image URLs in the required format.
    """
    # Get a list of image files in the bucket
    image_files = get_s3_images(bucket_name, prefix)

    # Sort the image files to ensure consistent order
    image_files.sort()

    # Construct URLs for each image
    base_url = "https://eu-north-1.console.aws.amazon.com/s3/object/image-rajan?region=eu-north-1&bucketType=general&prefix="
    image_urls = [f"{base_url}{imagename}" for imagename in image_files]

    return image_urls




