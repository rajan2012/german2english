#this is for local
import streamlit as st
import pandas as pd
import os
from googletrans import Translator
import pyttsx3
from io import StringIO
from st_aggrid import AgGrid, GridOptionsBuilder
from gtts import gTTS
import base64

from images3 import image_slideshow

# Initialize translator
translator = Translator()

# Filepath for the dictionary
filepath = r"C:\Users\User\Documents\msc\germansitegit\german2english\german_english_dictionary.csv"

def text_to_speech_url(text):
    tts = gTTS(text=text, lang='de')
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
    return f"data:audio/mp3;base64,{audio_base64}"

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
#dictionary_df = load_dictionary(filepath)



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

# Function to pronounce the word
def pronounce_word(word, rate=150):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)  # Adjust the rate of speech
    engine.say(word)
    engine.runAndWait()

# Streamlit app
st.title('Translation Dictionary')
# Combine search and pronunciation in one box
st.header('Search or Pronounce a German Word')
combined_input = st.text_input('Enter a German word to search or pronounce:', '')

col1, col2 = st.columns(2)

with col1:
    if st.button('Search'):
        if combined_input:
            search_result = dictionary_df[dictionary_df['German'].str.contains(combined_input, case=False, na=False)]
            if not search_result.empty:
                st.write('Search Results:')
                st.write(search_result)
            else:
                st.write('No results found.')
        else:
            st.write('Please enter a German word to search.')

with col2:
    if st.button('Pronounce'):
        if combined_input:
            tts = gTTS(text=combined_input, lang='de')
            tts.save("pronounce_temp.mp3")
            audio_file = open("pronounce_temp.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
        else:
            st.write('Please enter a German word to pronounce.')


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
            st.write(english_word)
            if st.button('Pronounce German Word22'):
                tts = gTTS(text=german_word, lang='de')
                tts.save("translated_word_temp3.mp3")
                audio_file = open("translated_word_temp3.mp3", "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3', start_time=0)
        except Exception as e:
            st.error(f"Error occurred during translation: {e}")

    st.write(english_word)

    if st.button('Add to Dictionary'):
        if german_word and english_word:
            existing_entry = dictionary_df[dictionary_df['German'] == german_word]
            if existing_entry.empty:
                # Add the translation to the DataFrame
                new_entry = pd.DataFrame({'German': [german_word], 'English': [english_word]})
                dictionary_df = pd.concat([dictionary_df, new_entry], ignore_index=True)

                # Save the updated dictionary
                save_dictionary(filepath, dictionary_df)

                st.write(f'Added: {german_word} -> {english_word}')
            else:
                existing_english_word = existing_entry['English'].values[0]
                st.write(f'The German word "{german_word}" already exists in the dictionary with the English translation: "{existing_english_word}".')
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
            st.write(german_word)
            if st.button('Pronounce Translated Word'):
                tts = gTTS(text=german_word, lang='de')
                tts.save("translated_word_temp.mp3")
                audio_file = open("translated_word_temp.mp3", "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3', start_time=0)
        except Exception as e:
            st.error(f"Error occurred during translation: {e}")

    if st.button('Add to Dictionary'):
        if english_word and german_word:
            if not any(dictionary_df['English'] == english_word):
                # Add the translation to the DataFrame
                new_entry = pd.DataFrame({'German': [german_word], 'English': [english_word]})
                dictionary_df = pd.concat([dictionary_df, new_entry], ignore_index=True)

                # Save the updated dictionary
                save_dictionary(filepath, dictionary_df)

                st.write(f'Added: {english_word} -> {german_word}')
            else:
                st.write(f'The English word "{english_word}" already exists in the dictionary.')
        else:
            st.write('Please enter both the English word and its German translation.')


# Display the current flashcard and pronounce the word
current_word = render_flashcard(st.session_state.current_index, st.session_state.flipped)

# Flashcard navigation
if st.button('Flip'):
    st.session_state.flipped = not st.session_state.flipped

if st.button('Next'):
    st.session_state.current_index = (st.session_state.current_index + 1) % len(dictionary_df)
    st.session_state.flipped = False

if st.button('Previous'):
    st.session_state.current_index = (st.session_state.current_index - 1) % len(dictionary_df)
    st.session_state.flipped = False

if current_word:
    if st.button('Pronounce2'):
        pronounce_word(current_word, rate=120)

# Define grid options
gb = GridOptionsBuilder.from_dataframe(dictionary_df)
gb.configure_default_column(width=200)  # Adjust width as needed
gridOptions = gb.build()


AgGrid(dictionary_df, gridOptions=gridOptions, height=400, theme='streamlit')


# JavaScript for flip functionality
st.markdown(
    """
    <script>
    function flipFlashcard() {
        window.parent.postMessage({
            isStreamlitMessage: true,
            type: "flip_flashcard"
        }, "*");
    }
    </script>
    """, unsafe_allow_html=True
)

# Add a hidden HTML element to listen for flip events
st.markdown(
    """
    <div id="flashcard-flip-listener"></div>
    <script>
    document.getElementById("flashcard-flip-listener").addEventListener("flip_flashcard", function() {
        window.location.href = window.location.href + '?flip_flashcard=true';
    });
    </script>
    """, unsafe_allow_html=True
)

# Check if the flip_flashcard event was triggered
if st.experimental_get_query_params().get('flip_flashcard'):
    st.session_state.flipped = not st.session_state.flipped
    # Remove the query parameter
    st.experimental_set_query_params()
