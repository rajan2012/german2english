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

from eng2germ import english_to_german_translation, german_to_english_translation
from images3 import image_slideshow,image_slideshow2
from loaddata import load_data_s3, save_data_s3
from streamlit_carousel import carousel


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
# Run the method
english_to_german_translation()
german_to_english_translation()

#########################################################################################################################################
# Combine search and pronunciation in one box
# st.header('Search or Pronounce a German Word')

# combined_input = st.text_input('Enter a German word to search or pronounce:', '')

# col1, col2 = st.columns(2)

# with col1:
#     if st.button('Search'):  # When the 'Search' button is clicked
#         if combined_input:  # Check if the user has entered a word
#             # Search for the entered word in the 'dictionary_df' DataFrame
#             search_result = dictionary_df[dictionary_df['German'].str.contains(combined_input, case=False, na=False)]
            
#             if not search_result.empty:  # If there are matching results
#                 st.write('Search Results:')
#                 st.write(search_result)  # Display the results
#             else:
#                 st.write('No results found.')  # If no matches found
#         else:
#             st.write('Please enter a German word to search.')  # Prompt for input if the field is empty

# with col2:
#     if st.button('Pronounce'):  # When the 'Pronounce' button is clicked
#         if combined_input:  # Check if the user has entered a word
#             # Use gTTS to generate an audio file for the entered word
#             tts = gTTS(text=combined_input, lang='de')
#             tts.save("pronounce_temp.mp3")  # Save the generated speech to a temporary file

#             # Open the saved audio file and read its content
#             audio_file = open("pronounce_temp.mp3", "rb")
#             audio_bytes = audio_file.read()

#             # Play the audio file in the Streamlit app
#             st.audio(audio_bytes, format='audio/mp3', start_time=0, autoplay=True)
#         else:
#             st.write('Please enter a German word to pronounce.')  # Prompt for input if the field is empty

##################################################################################################################################################
# Feature to delete a German word from the dictionary
#st.header('Delete a German Word')
#delete_input = st.text_input('Enter a German word to delete:', '')

#if st.button('Delete'):
 #   if delete_input:
  #      if delete_input in dictionary_df['German'].str.lower().values:
   #         dictionary_df = dictionary_df[dictionary_df['German'] != delete_input]
    #        save_data_s3(dictionary_df, bucket, filename)  # Save the updated DataFrame to S3
     #       st.write(f'The word "{delete_input}" has been deleted from the dictionary.')
      #  else:
       #     st.write(f'The word "{delete_input}" was not found in the dictionary.')
    #else:
     #   st.write('Please enter a German word to delete.')


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
            german_word = translator.translate(english_word, dest='de', src='en').text
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
dictionary_df = dictionary_df.iloc[::-1]

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
#image_slideshow(bucket_name)

# Title for Streamlit App
st.title("S3 Image Carousel Example")

# Fetch image URLs
image_urls = image_slideshow2(bucket_name)

# If images are found, display the carousel
if image_urls:
    carousel(image_urls, height=400)
else:
    st.write("No images found in the specified S3 folder.")


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
