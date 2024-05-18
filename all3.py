import streamlit as st
import pandas as pd
import os
from googletrans import Translator
import pyttsx3

# Initialize translator
translator = Translator()

# Filepath for the dictionary
filepath = r"C:\Users\User\Documents\msc\germansitegit\german2english\german_english_dictionary.csv"


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
        """
        word_style = """
            color: #4CAF50;
            font-size: 24px;
        """

        # Render the flashcard
        st.markdown(
            f"""
            <div style="{card_style}" onclick="this.style.transform='rotateY(180deg)'">
                <h3 style="{word_style}">{display_word}</h3>
            </div>
            """, unsafe_allow_html=True
        )
        return display_word


# Function to pronounce the word
def pronounce_word(word):
    engine = pyttsx3.init()
    engine.say(word)
    engine.runAndWait()


# Streamlit app
st.title('Translation Dictionary')

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
            dictionary_df = pd.concat([dictionary_df, new_entry], ignore_index=True)

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
            dictionary_df = pd.concat([dictionary_df, new_entry], ignore_index=True)

            # Save the updated dictionary
            save_dictionary(filepath, dictionary_df)

            st.write(f'Added: {english_word} -> {german_word}')
        else:
            st.write('Please enter both the English word and its German translation.')

# Flashcard navigation
if st.button('Flip'):
    st.session_state.flipped = not st.session_state.flipped

if st.button('Next'):
    st.session_state.current_index = (st.session_state.current_index + 1) % len(dictionary_df)
    st.session_state.flipped = False

if st.button('Previous'):
    st.session_state.current_index = (st.session_state.current_index - 1) % len(dictionary_df)
    st.session_state.flipped = False

# Display the current flashcard and pronounce the word
current_word = render_flashcard(st.session_state.current_index, st.session_state.flipped)
if current_word:
    if st.button('Pronounce'):
        pronounce_word(current_word)

# Display the stored dictionary in a table
#st.write('Translation Dictionary:')
#st.dataframe(dictionary_df)