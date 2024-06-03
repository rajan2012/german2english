import streamlit as st
from googletrans import Translator
from gtts import gTTS

def english_to_german_translation():
    # Initialize Google Translator
    translator = Translator()

    # Input for English word
    english_word = st.text_input('Enter an English word:', '')

    # Input for German translation using Google Translate API
    german_word = ''
    if english_word:
        german_word = translator.translate(english_word, dest='de', src='en').text
        st.write(f"{german_word}")

        if st.button('Pronounce 3'):
            tts = gTTS(text=german_word, lang='de')
            tts.save("translated_word_temp.mp3")
            audio_file = open("translated_word_temp.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3', start_time=0, autoplay=True)
        else:
            st.write('Please enter a German word to pronounce.')
            english_word = ''



