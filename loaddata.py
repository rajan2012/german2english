import os
import boto3
import pandas as pd
from io import StringIO
import streamlit as st


#@st.cache_data
def load_data_s3(bucket_name, file_key):
    # Load AWS credentials from Streamlit secrets
    aws_default_region = st.secrets["aws"]["AWS_DEFAULT_REGION"]
    aws_access_key_id = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]

    # Set environment variables
    os.environ["AWS_DEFAULT_REGION"] = aws_default_region
    os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key

    # Create an S3 client
    s3_client = boto3.client('s3')

    # Get the object from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    # Read the CSV file from the response
    file = response["Body"]
    data = pd.read_csv(file)

    return data


def save_data_s3(df, bucket_name, file_key):
    # Convert DataFrame to CSV format
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # Load AWS credentials from Streamlit secrets
    aws_default_region = st.secrets["aws"]["AWS_DEFAULT_REGION"]
    aws_access_key_id = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]

    # Set environment variables
    os.environ["AWS_DEFAULT_REGION"] = aws_default_region
    os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key

    # Create an S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Upload the DataFrame as a CSV file to S3
    s3.put_object(Bucket=bucket_name, Key=file_key, Body=csv_buffer.getvalue())

    #st.write("CSV file saved and uploaded to S3 successfully!")

@st.cache_data
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