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
       # else:
        #    st.write('enter German Word.')
          #  english_word = ''


import streamlit as st
from googletrans import Translator
from gtts import gTTS

def german_to_english_translation():
    # Initialize Google Translator
    translator = Translator()

    # Input for German word
    german_word = st.text_input('Enter German sentence:', '')

    # Translate German to English using Google Translate API
    english_word = ''
    if german_word:
        english_word = translator.translate(german_word, dest='en', src='de').text
        st.write(f"{english_word}")

        # Option to pronounce the English word
        if st.button('Pronounce 4'):
            tts = gTTS(text=english_word, lang='en')
            tts.save("translated_word_temp.mp3")
            audio_file = open("translated_word_temp.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3', start_time=0, autoplay=True)

