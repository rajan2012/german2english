import streamlit as st
import pandas as pd
import os
from googletrans import Translator


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

        if flipped:
            st.markdown(
                f"""
                <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9;">
                    <h3 style="color: #4CAF50;">{english_word}</h3>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9;">
                    <h3 style="color: #4CAF50;">{german_word}</h3>
                </div>
                """, unsafe_allow_html=True
            )


# Streamlit app
st.title('German to English Dictionary')

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

# Flashcard navigation
if st.button('Flip'):
    st.session_state.flipped = not st.session_state.flipped

if st.button('Next'):
    st.session_state.current_index = (st.session_state.current_index + 1) % len(dictionary_df)
    st.session_state.flipped = False

if st.button('Previous'):
    st.session_state.current_index = (st.session_state.current_index - 1) % len(dictionary_df)
    st.session_state.flipped = False

# Display the current flashcard
render_flashcard(st.session_state.current_index, st.session_state.flipped)

# Display the stored dictionary in a table
#st.write('German to English Dictionary:')
#st.table(dictionary_df)
