# this is for local
import streamlit as st
import pandas as pd
import os
from googletrans import Translator
import pyttsx3
from io import StringIO, BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder
from gtts import gTTS
import base64
import string
import re

from eng2germ import english_to_german_translation, german_to_english_translation
from images3 import image_slideshow, image_slideshow2
from loaddata import load_data_s3, save_data_s3
from streamlit_carousel import carousel
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # for consistent results

# Initialize translator
translator = Translator()

def text_to_speech_url2(text: str) -> str:
    """gTTS to MP3 (file) and return as data URL."""
    tts = gTTS(text=text, lang='de')
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
    return f"data:audio/mp3;base64,{audio_base64}"

def text_to_speech_url(text: str) -> str:
    """gTTS to MP3 (in-memory) and return as data URL."""
    tts = gTTS(text=text, lang='de')
    audio_bytes_io = BytesIO()
    tts.write_to_fp(audio_bytes_io)
    audio_bytes_io.seek(0)
    audio_bytes = audio_bytes_io.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return f"data:audio/mp3;base64,{audio_base64}"

def pronounce_word(word: str, rate: int = 150):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.say(word)
    engine.runAndWait()

# Function to load dictionary from S3 and normalize to lowercase
def load_dictionary_s3_lower(bucket: str, filename: str) -> pd.DataFrame:
    df = load_data_s3(bucket, filename)
    if df is None or df.empty:
        df = pd.DataFrame(columns=['German', 'English'])
    # Normalize columns to lowercase strings
    if 'German' not in df.columns or 'English' not in df.columns:
        # Attempt to repair column names if possible
        cols_lower = {c.lower(): c for c in df.columns}
        german_col = cols_lower.get('german')
        english_col = cols_lower.get('english')
        if german_col and english_col:
            df = df.rename(columns={german_col: 'German', english_col: 'English'})
        else:
            df = pd.DataFrame(columns=['German', 'English'])
    df['German'] = df['German'].astype(str).str.strip().str.lower()
    df['English'] = df['English'].astype(str).str.strip().str.lower()
    # Drop exact duplicates post-normalization
    df = df.drop_duplicates(subset=['German', 'English']).reset_index(drop=True)
    return df

def save_dictionary_s3_lower(df: pd.DataFrame, bucket: str, filename: str):
    # Ensure lowercase before saving
    df = df.copy()
    df['German'] = df['German'].astype(str).str.strip().str.lower()
    df['English'] = df['English'].astype(str).str.strip().str.lower()
    df = df.drop_duplicates(subset=['German', 'English']).reset_index(drop=True)
    save_data_s3(df, bucket, filename)

# Sentence preprocessor (removes punctuation/digits, keeps umlauts, lowercase)
def preprocess_sentence(sentence: str):
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    sentence = re.sub(r'[^a-zA-ZäöüßÄÖÜ ]', '', sentence)
    sentence = sentence.lower()
    words = sentence.split()
    words = [w.strip() for w in words if len(w) >= 3]
    return words

# Auto-add: German -> English
def update_dictionary_auto(new_words, dictionary_df):
    added_words = []
    # Count English-like tokens to guard against wrong direction
    english_count = 0
    for word in new_words:
        try:
            lang = detect(word)
        except Exception:
            lang = 'unknown'
        if lang == 'en':
            english_count += 1

    # Safety: likely English sentence
    if english_count >= 50 or english_count == len(new_words):
        raise ValueError("The entered sentence appears to be English. Please enter a German sentence.")

    for word in new_words:
        try:
            lang = detect(word)
        except Exception:
            lang = 'unknown'
        # Skip words that are already English
        if lang == 'en':
            continue

        word_lower = word.strip().lower()
        # Skip if already exists
        if word_lower in dictionary_df['German'].str.lower().values:
            continue

        # Translate to English (lowercase)
        try:
            english_translation = translator.translate(word_lower, src='de', dest='en').text.lower().strip()
        except Exception:
            # If translation fails, skip
            continue

        # Skip if no real change
        if english_translation == word_lower:
            continue

        dictionary_df = pd.concat(
            [dictionary_df, pd.DataFrame({'English': [english_translation], 'German': [word_lower]})],
            ignore_index=True
        )
        added_words.append((word_lower, english_translation))

    return dictionary_df, added_words

# Auto-add: English -> German
def update_dictionary_auto_eng2de(new_words, dictionary_df):
    added_words = []

    german_count = 0
    for word in new_words:
        try:
            lang = detect(word)
        except Exception:
            lang = 'unknown'
        if lang == 'de' or any(c in word for c in 'äöüß'):
            german_count += 1

    # Safety: likely German sentence
    if german_count >= 50 or german_count == len(new_words):
        raise ValueError("Please enter an English sentence, not German.")

    for word in new_words:
        word_lower = word.strip().lower()
        try:
            lang = detect(word)
        except Exception:
            lang = 'unknown'

        # Skip words that are already German-ish
        if lang == 'de' or any(c in word for c in 'äöüß'):
            continue

        # Skip if already exists (case-insensitive)
        if word_lower in dictionary_df['English'].str.lower().values:
            continue

        # Translate to German (lowercase)
        try:
            german_translation = translator.translate(word_lower, src='en', dest='de').text.lower().strip()
        except Exception:
            continue

        if german_translation == word_lower:
            continue

        dictionary_df = pd.concat(
            [dictionary_df, pd.DataFrame({'English': [word_lower], 'German': [german_translation]})],
            ignore_index=True
        )
        added_words.append((word_lower, german_translation))

    return dictionary_df, added_words

# ----------------- App Constants -----------------
bucket = 'test22-rajan'
filename = 'german_english_dictionary.csv'
images_path = r"C:\Users\User\Documents\german\image"
bucket_name_images = 'image-rajan'

# ----------------- Load Dictionary -----------------
dictionary_df = load_dictionary_s3_lower(bucket, filename)

# ----------------- Session State -----------------
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'flipped' not in st.session_state:
    st.session_state.flipped = False

# ----------------- UI -----------------
st.title('Translation Dictionary')

# ---- Search exact German word (case-insensitive) ----
german_word_s = st.text_input("Enter a German word for search:").strip().lower()
if german_word_s:
    match = dictionary_df[dictionary_df['German'].str.lower() == german_word_s]
    if not match.empty:
        english_translation = match.iloc[0]['English']
        st.success(f"{english_translation}")
    else:
        st.warning("Word not found in the dictionary.")

# ---- German sentence -> auto add (de->en) ----
german_sentence = st.text_input("Enter a German sentence").strip().lower()
if german_sentence:
    words = preprocess_sentence(german_sentence)  # already lowercased
    st.write("Words extracted:", words)
    try:
        dictionary_df, new_words_added = update_dictionary_auto(words, dictionary_df)
        save_dictionary_s3_lower(dictionary_df, bucket, filename)
        if new_words_added:
            display_text = "\n".join([f"{de} → {en}" for de, en in new_words_added])
            st.text("New words added:\n" + display_text)
        else:
            st.info("All words already exist in dictionary.")
    except ValueError as e:
        st.error(str(e))

# ---- English sentence -> auto add (en->de) ----
english_sentence = st.text_input("Enter an English sentence").strip().lower()
if english_sentence:
    words = preprocess_sentence(english_sentence)  # already lowercased
    st.write("Words extracted:", words)
    try:
        dictionary_df, new_words_added = update_dictionary_auto_eng2de(words, dictionary_df)
        save_dictionary_s3_lower(dictionary_df, bucket, filename)
        if new_words_added:
            display_text = "\n".join([f"{en} → {de}" for en, de in new_words_added])
            st.text("New words added:\n" + display_text)
        else:
            st.info("All words already exist in dictionary.")
    except ValueError as e:
        st.error(str(e))

    if st.button("Pronounce15"):
        pronounce_word(english_sentence)

# Run the custom modules (unchanged)
english_to_german_translation()
german_to_english_translation()

# ---- Manual translation direction ----
translation_direction = st.radio('Select translation direction:', ('German to English', 'English to German'))

if translation_direction == 'German to English':
    german_word = st.text_input('Enter a German word:', '').strip().lower()
    if german_word:
        try:
            english_word = translator.translate(german_word, dest='en', src='de').text.lower().strip()
            st.write(english_word)

            if st.button('Pronounce German Word22'):
                tts = gTTS(text=german_word, lang='de')
                tts.save("translated_word_temp3.mp3")
                with open("translated_word_temp3.mp3", "rb") as f:
                    st.audio(f.read(), format='audio/mp3', start_time=0, autoplay=True)

            # Case-insensitive existence check
            exists = dictionary_df['German'].str.lower() == german_word
            if not exists.any():
                new_entry = pd.DataFrame({'German': [german_word], 'English': [english_word]})
                dictionary_df = pd.concat([dictionary_df, new_entry], ignore_index=True)
                save_dictionary_s3_lower(dictionary_df, bucket, filename)
                st.write(f'Added: {german_word} -> {english_word}')
            else:
                existing_english_word = dictionary_df.loc[exists, 'English'].iloc[0]
                st.write(f'The German word "{german_word}" already exists with English: "{existing_english_word}".')
        except Exception as e:
            st.error(f"Error occurred during translation: {e}")

else:  # English to German
    english_word = st.text_input('Enter an English word2:', '').strip().lower()
    if english_word:
        try:
            german_word = translator.translate(english_word, dest='de', src='en').text.lower().strip()
            st.write(german_word)

            if st.button('Pronounce Translated Word'):
                tts = gTTS(text=german_word, lang='de')
                tts.save("translated_word_temp.mp3")
                with open("translated_word_temp.mp3", "rb") as f:
                    st.audio(f.read(), format='audio/mp3', start_time=0, autoplay=True)

            exists = dictionary_df['English'].str.lower() == english_word
            if not exists.any():
                new_entry = pd.DataFrame({'German': [german_word], 'English': [english_word]})
                dictionary_df = pd.concat([dictionary_df, new_entry], ignore_index=True)
                save_dictionary_s3_lower(dictionary_df, bucket, filename)
                st.write(f'Added: {english_word} -> {german_word}')
            else:
                existing_german_word = dictionary_df.loc[exists, 'German'].iloc[0]
                st.write(f'The English word "{english_word}" already exists with German: "{existing_german_word}".')
        except Exception as e:
            st.error(f"Error occurred during translation: {e}")

# ----------------- Table (latest first) -----------------
# Normalize again to be safe before display
dictionary_df['German'] = dictionary_df['German'].astype(str).str.strip().str.lower()
dictionary_df['English'] = dictionary_df['English'].astype(str).str.strip().str.lower()
dictionary_df = dictionary_df.drop_duplicates(subset=['German', 'English']).reset_index(drop=True)

# Reverse to show most recent additions first
display_df = dictionary_df.iloc[::-1][['English', 'German']]

st.write("German English Dictionary")
gb = GridOptionsBuilder.from_dataframe(display_df)
gb.configure_default_column(width=200)
gridOptions = gb.build()
AgGrid(display_df, gridOptions=gridOptions, height=400, theme='streamlit')

# ----------------- Flashcards -----------------
if 'current_index' not in st.session_state:
    st.session_state.current_index = len(display_df) - 1
if 'flipped' not in st.session_state:
    st.session_state.flipped = False

def render_flashcard(index, flipped):
    if index < 0 or index >= len(display_df):
        st.markdown("### (No words in dictionary yet)")
        return
    if flipped:
        st.markdown(f"### {display_df.iloc[index]['English']}")
    else:
        st.markdown(f"### {display_df.iloc[index]['German']}")

st.header("German-English Flashcards")
render_flashcard(st.session_state.current_index, st.session_state.flipped)

if st.button("Flip"):
    if not st.session_state.flipped:
        st.session_state.flipped = True
    else:
        st.session_state.current_index -= 1
        st.session_state.flipped = False
        if st.session_state.current_index < 0:
            st.session_state.current_index = len(display_df) - 1

if st.button("Previous"):
    st.session_state.current_index += 1
    st.session_state.flipped = False
    if st.session_state.current_index >= len(display_df):
        st.session_state.current_index = 0

# ----------------- Images from S3 -----------------
image_slideshow(bucket_name_images)

# ----------------- Footer -----------------
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
       z-index: 1000;
   }
   </style>
   <div class="footer">
       <p>&copy; 2024 rajan | <a href="mailto:rajansah8723@gmail.com">email</a> | 
       <a href="https://www.linkedin.com/in/rajan-sah-0a145495">LinkedIn</a></p>
   </div>
"""
st.markdown(footer, unsafe_allow_html=True)
