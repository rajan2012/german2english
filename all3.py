import streamlit as st
import pandas as pd
import os
from googletrans import Translator
import pyttsx3
from io import StringIO
from st_aggrid import AgGrid, GridOptionsBuilder
from gtts import gTTS
import base64
from io import BytesIO

from eng2germ import english_to_german_translation, german_to_english_translation
from images3 import image_slideshow,image_slideshow2
from loaddata import load_data_s3, save_data_s3

# Filepath for the dictionary
filepath = "german_english_dictionary.csv"
audio_folder = "audio_files"

# Create the audio folder if it doesn't exist
if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)


# Function to generate audio files for each German word
def generate_audio_files(df):
    engine = pyttsx3.init()
    engine.setProperty('rate', 120)
    for word in df['German']:
        audio_file_path = os.path.join(audio_folder, f"{word}.mp3")
        if not os.path.exists(audio_file_path):
            engine.save_to_file(word, audio_file_path)
    engine.runAndWait()


# Function to generate HTML with speaker icon
def generate_html(text):
    audio_file_path = os.path.join(audio_folder, f"{text}.mp3")
    if os.path.exists(audio_file_path):
        audio_url = f"/{audio_file_path}"
        return f"""
        <div style="display: flex; align-items: center;">
            <span>{text}</span>
            <a href="#" onclick="playAudio('{audio_url}')">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Speaker_Icon.svg/1200px-Speaker_Icon.svg.png" width="20" height="20">
            </a>
        </div>
        """
    return text


# Function to load dictionary from file
def load_dictionary(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=['German', 'English'])


# Function to save dictionary to file
def save_dictionary(file_path, df):
    df.to_csv(file_path, index=False)


# Load existing dictionary
dictionary_df = load_dictionary(filepath)

# Generate audio files for existing German words
if not dictionary_df.empty:
    generate_audio_files(dictionary_df)

# Initialize session state for the current index and flip state
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'flipped' not in st.session_state:
    st.session_state.flipped = False


# Function to render the flashcard
def render_flashcard(index, flipped):
    if not dictionary_df.empty:
        german_word = dictionary_df.iloc[index]['German']
        english_word = dictionary_df.iloc[index]['English']

        # Determine the word to be displayed based on flip state
        display_word = english_word if flipped else german_word

        # Define CSS styles for the flashcard
        card_style = """
            border: 2px solid #4CAF50;
            border-radius: 10px;
            background-color: #f9f9f9;
            width: 300px;
            height: 150px;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        """
        word_style = """
            color: #4CAF50;
            font-size: 24px;
        """

        # Render the flashcard
        st.markdown(
            f"""
            <div style="{card_style}" onclick="flipFlashcard()">
                <h3 style="{word_style}">{display_word}</h3>
            </div>
            """, unsafe_allow_html=True
        )
        return display_word


# Streamlit app
st.title('Translation Dictionary')

#search for german word and give english word when pressed button
german_word_search = st.text_input("Enter a German word:")

# If input is given, search for it
if german_word_search:
    # Case-insensitive search
    match = dictionary_df[dictionary_df['German'].str.lower() == german_word_search.lower()]

    if not match.empty:
        english_translation = match.iloc[0]['English']
        st.success(f"**English:** {english_translation}")
    else:
        st.warning("Word not found in the dictionary.")

# Choose translation direction
translation_direction = st.radio('Select translation direction:', ('German to English', 'English to German'))

if translation_direction == 'German to English':
    # Input for German word
    german_word = st.text_input('Enter a German word:', '')

    # Input for English translation using Google Translate API
    english_word = ''
    if german_word:
        try:
            english_word = translator.translate(german_word, dest='en', src='de').text
        except Exception as e:
            st.error(f"Error occurred during translation: {e}")

    st.write(english_word)

    if st.button('Add to Dictionary'):
        if german_word and english_word:
            # Add the translation to the DataFrame
            new_entry = pd.DataFrame({'German': [german_word], 'English': [english_word]})

            # Add pronunciation icon HTML to the new entry
            new_entry['German_HTML'] = new_entry['German'].apply(generate_html)

            # Concatenate the new entry with the existing dictionary
            dictionary_df = pd.concat([dictionary_df, new_entry], ignore_index=True)

            # Generate audio files for new German words
            generate_audio_files(new_entry)

            # Save the updated dictionary
            save_dictionary(filepath, dictionary_df)

            st.write(f'Added: {german_word} -> {english_word}')
        else:
            st.write('Please enter both the German word and its English translation.')

else:  # English to German
    # Input for English word
    english_word = st.text_input('Enter an English word:', '')

    # Input for German translation using Google Translate API
    german_word = ''
    if english_word:
        try:
            german_word = translator.translate(english_word, dest='de', src='en').text
        except Exception as e:
            st.error(f"Error occurred during translation: {e}")

    st.write(german_word)

    if st.button('Add to Dictionary'):
        if english_word and german_word:
            # Add the translation to the DataFrame
            new_entry = pd.DataFrame({'German': [german_word], 'English': [english_word]})

            # Add pronunciation icon HTML to the new entry
            new_entry['German_HTML'] = new_entry['German'].apply(generate_html)

            # Concatenate the new entry with the existing dictionary
            dictionary_df = pd.concat([dictionary_df, new_entry], ignore_index=True)

            # Generate audio files for new German words
            generate_audio_files(new_entry)

            # Save the updated dictionary
            save_dictionary(filepath, dictionary_df)

            st.write(f'Added: {english_word} -> {german_word}')
        else:
            st.write('Please enter both the English word and its German translation.')

# Add pronunciation icon HTML to the existing German words
if not dictionary_df.empty and 'German_HTML' not in dictionary_df.columns:
    dictionary_df['German_HTML'] = dictionary_df['German'].apply(generate_html)

# Define grid options
gb = GridOptionsBuilder.from_dataframe(dictionary_df)
gb.configure_column("German_HTML", header_name="German", wrapText=True, autoHeight=True)
gb.configure_column("English", header_name="English")
gb.configure_default_column(editable=False)
gridOptions = gb.build()



st.write(dictionary_df[['English', 'German_HTML'])

# Display the DataFrame using AgGrid
#'German_HTML', 'English'
AgGrid(dictionary_df[['English', 'German_HTML']], 
       gridOptions=gridOptions, 
       height=400, 
       theme='streamlit',
       allow_unsafe_jscode=True)


# Inject JavaScript for playing audio
st.markdown("""
<script>
function playAudio(url) {
    var audio = new Audio(url);
    audio.play();
}
</script>
""", unsafe_allow_html=True)
