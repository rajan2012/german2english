#for webiste
import pyttsx3
import streamlit as st
import pandas as pd
import os
from googletrans import Translator
import requests
from io import StringIO
from github import Github

# Initialize translator
translator = Translator()

# Function to load dictionary from file
def load_dictionary(file_url):
    response = requests.get(file_url)
    if response.status_code == 200:
        csv_content = response.text
        return pd.read_csv(StringIO(csv_content))
    else:
        return pd.DataFrame(columns=['German', 'English'])


# GitHub raw URL for the dictionary CSV file
github_csv_url = "https://raw.githubusercontent.com/rajan2012/german2english/main/german_english_dictionary.csv"


# Function to save dictionary to file
# Function to save dictionary to file in GitHub repository
def save_dictionary_to_github(file_url, df):
    csv_content = df.to_csv(index=False)
    response = requests.put(file_url, data=csv_content)
    if response.status_code == 200:
        st.success("Dictionary updated successfully on GitHub.")
    else:
        st.error("Failed to update dictionary on GitHub.")

# Load existing dictionary
dictionary_df = load_dictionary(github_csv_url)

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
            save_dictionary_to_github(github_csv_url, dictionary_df)

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
            save_dictionary_to_github(github_csv_url, dictionary_df)

            st.write(f'Added: {english_word} -> {german_word}')
        else:
            st.write('Please enter both the English word and its German translation.')


# Display the current flashcard and pronounce the word
current_word = render_flashcard(st.session_state.current_index, st.session_state.flipped)

# Flashcard navigation buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Flip'):
        st.session_state.flipped = not st.session_state.flipped
with col3:
    if st.button('Previous'):
        st.session_state.current_index = (st.session_state.current_index - 1) % len(dictionary_df)
        st.session_state.flipped = False

with col2:
    if st.button('Next'):
        st.session_state.current_index = (st.session_state.current_index + 1) % len(dictionary_df)
        st.session_state.flipped = False

    
#, rate=150
def pronounce_word(word):
    engine = pyttsx3.init()
    #engine.setProperty('rate', rate)  # Adjust the rate of speech
    engine.say(word)
    engine.runAndWait()

if current_word:
    if st.button('Pronounce'):
        #,rate=120
        pronounce_word(current_word)

# Display the stored dictionary in a table
st.write('Translation Dictionary:')
st.dataframe(dictionary_df)
