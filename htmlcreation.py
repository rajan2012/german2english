import streamlit as st
import pandas as pd
import os
from googletrans import Translator
from io import StringIO
from st_aggrid import AgGrid, GridOptionsBuilder
from gtts import gTTS
import base64


# Filepath for the dictionary
filepath = r"C:\Users\User\Documents\msc\germansitegit\german2english\text.csv"


# Function to create base64 encoded audio file URL
def text_to_speech_url(text):
    tts = gTTS(text=text, lang='de')
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
    os.remove("temp.mp3")
    return f"data:audio/mp3;base64,{audio_base64}"




# Function to create base64 encoded audio file URL
def text_to_speech_url(text):
    tts = gTTS(text=text, lang='de')
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
    os.remove("temp.mp3")
    return f"data:audio/mp3;base64,{audio_base64}"

# Function to generate HTML for the speaker icon with audio
def generate_html(text):
    url = text_to_speech_url(text)
    return f"""
    <div style="display: flex; align-items: center;">
        <span>{text}</span>
        <a href="#" onclick="playAudio('{url}')">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Speaker_Icon.svg/1200px-Speaker_Icon.svg.png" width="20" height="20">
        </a>
    </div>
    """

# Function to load dictionary from file
def load_dictionary(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.write("something")
        return pd.DataFrame(columns=['German', 'English'])

# Function to save dictionary to file
def save_dictionary(file_path, df):
    df.to_csv(file_path, index=False)



# Load existing dictionary
dictionary_df = load_dictionary(filepath)

st.write(dictionary_df)
# Add pronunciation icon HTML to the German column
dictionary_df['German_HTML'] = dictionary_df['German'].apply(generate_html)

save_dictionary(filepath, dictionary_df)


# Define grid options
gb = GridOptionsBuilder.from_dataframe(dictionary_df)
gb.configure_column("German_HTML", header_name="German", wrapText=True, autoHeight=True)
gb.configure_column("English", header_name="English")
gb.configure_default_column(editable=False)
gridOptions = gb.build()

# Display the DataFrame using AgGrid
AgGrid(dictionary_df[['German_HTML', 'English']], gridOptions=gridOptions, height=400, theme='streamlit', allow_unsafe_jscode=True)
