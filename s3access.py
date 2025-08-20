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
from io import BytesIO
import string
import re

from eng2germ import english_to_german_translation, german_to_english_translation
from images3 import image_slideshow,image_slideshow2
from loaddata import load_data_s3, save_data_s3
from streamlit_carousel import carousel
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # for consistent results


# Initialize translator
translator = Translator()


def text_to_speech_url2(text):
    tts = gTTS(text=text, lang='de')
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()

    return f"data:audio/mp3;base64,{audio_base64}"


def text_to_speech_url(text):
    # Create the Text-to-Speech object
    tts = gTTS(text=text, lang='de')

    # Create an in-memory file-like object
    audio_bytes_io = BytesIO()

    # Save the audio data to the in-memory file-like object
    tts.write_to_fp(audio_bytes_io)

    # Get the audio data from the in-memory file-like object
    audio_bytes_io.seek(0)
    audio_bytes = audio_bytes_io.read()

    # Encode the audio data in Base64
    audio_base64 = base64.b64encode(audio_bytes).decode()

    # Construct the data URL
    data_url = f"data:audio/mp3;base64,{audio_base64}"

    return data_url

# Function to pronounce the word
def pronounce_word(word, rate=150):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)  # Adjust the rate of speech
    engine.say(word)
    engine.runAndWait()

# Function to load dictionary from file
def load_dictionary(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=['German', 'English'])

# Function to save dictionary to file
def save_dictionary(file_path, df):
    df.to_csv(file_path, index=False)


# Function to preprocess sentence
def preprocess_sentence(sentence):
    # Remove punctuation
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    # Remove digits and other non-alphabetic symbols
    sentence = re.sub(r'[^a-zA-ZäöüßÄÖÜ ]', '', sentence)  # keeps letters and spaces, including German umlauts
    # Convert to lowercase
    sentence = sentence.lower()
    # Split by space
    words = sentence.split()
    # Trim and keep words with length >= 3
    words = [word.strip() for word in words if len(word) >= 3]
    return words

# Function to automatically add new words with translation
from langdetect import detect

# Function to automatically add new words with translation
def update_dictionary_auto(new_words, dictionary_df):
    added_words = []
    # Robust English detection
    english_count = 0
    for word in new_words:
        try:
            lang = detect(word)
        except:
            lang = 'unknown'
        # Count as English if detected or contains only ASCII letters
        if lang == 'en':
            english_count += 1

    st.write("english_count", english_count)
    st.write("new_words", len(new_words))

    # Raise exception if sentence is mostly English
    if english_count >= 50 or english_count == len(new_words):
        raise ValueError("The entered sentence appears to be English. Please enter a German sentence.")

    for word in new_words:
        try:
            lang = detect(word)
        except:
            lang = 'unknown'

        # Skip words that are already English
        if lang == 'en':
            continue

        if word not in dictionary_df['German'].values:
            # Translate to English and convert to lowercase
            english_translation = translator.translate(word, src='de', dest='en').text.lower()
            dictionary_df = pd.concat(
                [dictionary_df, pd.DataFrame({'English': [english_translation], 'German': [word]})],
                ignore_index=True
            )
            added_words.append((word, english_translation))

    return dictionary_df, added_words


# Function to automatically add new words with translation
def update_dictionary_auto_eng2de(new_words, dictionary_df):
    added_words = []

    # Robust German detection
    german_count = 0
    for word in new_words:
        try:
            lang = detect(word)
        except:
            lang = 'unknown'
        # Count as German if detected or contains German special characters
        if lang == 'de' or any(c in word for c in 'äöüß'):
            german_count += 1

    #st.write("german_count", german_count)
    #st.write("new_words", len(new_words))

    # Raise exception if sentence is mostly German
    if german_count >= 50 or german_count == len(new_words):
        raise ValueError("Please enter an English sentence, not German.")

    for word in new_words:
        try:
            lang = detect(word)
        except:
            lang = 'unknown'

        # Skip words that are already German
        if lang == 'de' or any(c in word for c in 'äöüß'):
            continue

        if word not in dictionary_df['English'].values:
            # Translate to German and convert to lowercase
            german_translation = translator.translate(word, src='en', dest='de').text.lower()
            dictionary_df = pd.concat(
                [dictionary_df, pd.DataFrame({'English': [word], 'German': [german_translation]})],
                ignore_index=True
            )
            added_words.append((word, german_translation))

    return dictionary_df, added_words


bucket='test22-rajan'
filename='german_english_dictionary.csv'

# Set the path to your images folder
images_path = r"C:\Users\User\Documents\german\image"

#last_modified = 0  # Set initial last modified timestamp
dictionary_df = load_data_s3(bucket, filename)



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
# Input box for German word
german_word_s = st.text_input("Enter a German word for search:")

# If input is given, search for it
if german_word_s:
    # Case-insensitive search
    match = dictionary_df[dictionary_df['German'].str.lower() == german_word_s.lower()]

    if not match.empty:
        english_translation = match.iloc[0]['English']
        st.success(f"{english_translation}")
    else:
        st.warning("Word not found in the dictionary.")

########enter sentence
german_sentence = st.text_input("Enter a German sentence")

if german_sentence:
    words = preprocess_sentence(german_sentence)
    st.write("Words extracted:", words)

    # Update dictionary automatically
    dictionary_df, new_words_added = update_dictionary_auto(words, dictionary_df)
    save_data_s3(dictionary_df, bucket, filename)

    if new_words_added:
        # Display each new word with its translation
        display_text = "\n".join([f"{de} → {en}" for de, en in new_words_added])
        st.text("New words added:\n" + display_text)
    else:
        st.info("All words already exist in dictionary.")



english_sentence = st.text_input("Enter a english sentence")

if english_sentence:
    words = preprocess_sentence(english_sentence)
    st.write("Words extracted:", words)

    # Update dictionary automatically
    dictionary_df, new_words_added = update_dictionary_auto_eng2de(words, dictionary_df)
    save_data_s3(dictionary_df, bucket, filename)

    if new_words_added:
        # Display each new word with its German translation
        display_text = "\n".join([f"{en} → {de}" for en, de in new_words_added])
        st.text("New words added:\n" + display_text)
    else:
        st.info("All words already exist in dictionary.")

    # Pronounce button
    if st.button("Pronounce15"):
        pronounce_word(english_sentence)

# Run the method
english_to_german_translation()
german_to_english_translation()


# Choose translation direction
translation_direction = st.radio('Select translation direction:', ('German to English', 'English to German'))

if translation_direction == 'German to English':
    # Input for German word
    german_word = st.text_input('Enter a German word:', '')

    # Input for English translation using Google Translate API
    english_word = ''
    if german_word:
        try:
            english_word = translator.translate(german_word, dest='en', src='de').text.lower()
            st.write(english_word)
            if st.button('Pronounce German Word22'):
                tts = gTTS(text=german_word, lang='de')
                tts.save("translated_word_temp3.mp3")
                audio_file = open("translated_word_temp3.mp3", "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3', start_time=0, autoplay=True)
            # Check if the word is already in the dictionary
            existing_entry = dictionary_df[dictionary_df['German'] == german_word]
            if existing_entry.empty:
                # Add the translation to the DataFrame
                new_entry = pd.DataFrame({'German': [german_word], 'English': [english_word]})
                dictionary_df = pd.concat([dictionary_df, new_entry], ignore_index=True)

                # Save the updated dictionary
                save_data_s3(dictionary_df, bucket, filename)

                st.write(f'Added: {german_word} -> {english_word}')
            else:
                existing_english_word = existing_entry['English'].values[0]
                st.write(f'The German word "{german_word}" already exists in the dictionary with the English translation: "{existing_english_word}".')
        except Exception as e:
            st.error(f"Error occurred during translation: {e}")

else:  # English to German
    # Input for English word
    english_word = st.text_input('Enter an English word2:', '')

    # Input for German translation using Google Translate API
    german_word = ''
    if english_word:
        try:
            german_word = translator.translate(english_word, dest='de', src='en').text.lower()
            st.write(german_word)
            if st.button('Pronounce Translated Word'):
                tts = gTTS(text=german_word, lang='de')
                tts.save("translated_word_temp.mp3")
                audio_file = open("translated_word_temp.mp3", "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3', start_time=0, autoplay=True)
            # Check if the word is already in the dictionary
            existing_entry = dictionary_df[dictionary_df['English'] == english_word]
            if existing_entry.empty:
                # Add the translation to the DataFrame
                new_entry = pd.DataFrame({'German': [german_word], 'English': [english_word]})
                dictionary_df = pd.concat([dictionary_df, new_entry], ignore_index=True)

                # Save the updated dictionary
                save_data_s3(dictionary_df, bucket, filename)

                st.write(f'Added: {english_word} -> {german_word}')
            else:
                existing_german_word = existing_entry['German'].values[0]
                st.write(f'The English word "{english_word}" already exists in the dictionary with the German translation: "{existing_german_word}".')
        except Exception as e:
            st.error(f"Error occurred during translation: {e}")

# if current_word:
#     if st.button('Pronounce2'):
#         pronounce_word(current_word, rate=120)

# Define grid options
# Reverse the DataFrame to display the last row first
dictionary_df = dictionary_df.iloc[::-1][['English', 'German']]

# Streamlit UI
st.write("German English Dictionary")
gb = GridOptionsBuilder.from_dataframe(dictionary_df)
gb.configure_default_column(width=200)  # Adjust width as needed
gridOptions = gb.build()

AgGrid(dictionary_df, gridOptions=gridOptions, height=400, theme='streamlit')

##############################################################################################################################
# # Display the current flashcard and pronounce the word
# current_word = render_flashcard(st.session_state.current_index, st.session_state.flipped)

# # Flashcard navigation
# if st.button('Flip'):
#     st.session_state.flipped = not st.session_state.flipped

# if st.button('Next'):
#     st.session_state.current_index = (st.session_state.current_index + 1) % len(dictionary_df)
#     st.session_state.flipped = False

# if st.button('Previous'):
#     st.session_state.current_index = (st.session_state.current_index - 1) % len(dictionary_df)
#     st.session_state.flipped = False

# if current_word:
#     if st.button('Pronounce2'):
#         pronounce_word(current_word, rate=120)

# # Define grid options
# gb = GridOptionsBuilder.from_dataframe(dictionary_df)
# gb.configure_default_column(width=200)  # Adjust width as needed
# gridOptions = gb.build()

# AgGrid(dictionary_df, gridOptions=gridOptions, height=400, theme='streamlit')

# # JavaScript for flip functionality
# st.markdown(
#     """
#     <script>
#     function flipFlashcard() {
#         window.parent.postMessage({
#             isStreamlitMessage: true,
#             type: "flip_flashcard"
#         }, "*");
#     }
#     </script>
#     """, unsafe_allow_html=True
# )

# # Add a hidden HTML element to listen for flip events
# st.markdown(
#     """
#     <div id="flashcard-flip-listener"></div>
#     <script>
#     document.getElementById("flashcard-flip-listener").addEventListener("flip_flashcard", function() {
#         window.location.href = window.location.href + '?flip_flashcard=true';
#     });
#     </script>
#     """, unsafe_allow_html=True
# )

# # Check if the flip_flashcard event was triggered
# if st.experimental_get_query_params().get('flip_flashcard'):
#     st.session_state.flipped = not st.session_state.flipped
#     # Remove the query parameter
#     st.experimental_set_query_params()


###########################################################################################################################################

# Session state initialization
if 'current_index' not in st.session_state:
    st.session_state.current_index = len(dictionary_df) - 1  # Start from the last row
if 'flipped' not in st.session_state:
    st.session_state.flipped = False

# Function to render the flashcard
def render_flashcard(index, flipped):
    if flipped:
        st.markdown(f"### {dictionary_df.loc[index, 'English']}")
    else:
        st.markdown(f"### {dictionary_df.loc[index, 'German']}")

# Display the flashcard
st.header("German-English Flashcards")
render_flashcard(st.session_state.current_index, st.session_state.flipped)

# Flip button
if st.button("Flip"):
    if not st.session_state.flipped:
        # Show English translation
        st.session_state.flipped = True
    else:
        # Automatically move one row above and reset flip state
        st.session_state.current_index -= 1
        st.session_state.flipped = False

        # Wrap around to the last word if we go past the first row
        if st.session_state.current_index < 0:
            st.session_state.current_index = len(dictionary_df) - 1
            
# Button to move to the previous row (move down)####################################
if st.button("Previous"):
    st.session_state.current_index += 1
    st.session_state.flipped = False

    # Wrap around to the first row if moving past the last row
    if st.session_state.current_index >= len(dictionary_df):
        st.session_state.current_index = 0

# Set the name of your S3 bucket
bucket_name = 'image-rajan'  # Replace with your actual bucket name

# Call the function to create the slideshow
##############################################################################################################################
image_slideshow(bucket_name)

# Title for Streamlit App
#st.title("S3 Image Carousel Example")

# Fetch image URLs
#image_urls = image_slideshow2(bucket_name)

# Debugging step: Display the fetched image URLs
#st.write("Fetched image URLs:", image_urls)

# If images are found, display the carousel
#if image_urls:
    # Create a list of dictionaries where each dictionary contains 'img' and 'title' keys
   # images_for_carousel = [{'img': url, 'title': f"Image {i+1}"} for i, url in enumerate(image_urls)]
    
    # Show the carousel with the formatted image URLs and titles
  #  carousel(images_for_carousel)
#else:
  #  st.write("No images found in the specified S3 folder.")

#, height=400
###############################################################################################################
    

# Adding the footer with transparent background
footer = """
   <style>
   .footer {
       position: fixed;
       left: 0;
       bottom: 0;
       width: 100%;
       background-color: transparent;
       text-align: center;
       padding: 10px;
   }
   </style>
   <div class="footer">
       <p>&copy; 2024 rajan | <a href="mailto:rajansah8723@gmail.com">email</a> | 
       <a href="https://www.linkedin.com/in/rajan-sah-0a145495">LinkedIn</a></p>
   </div>
   """
st.markdown(footer, unsafe_allow_html=True)
