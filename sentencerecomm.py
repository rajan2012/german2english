import streamlit as st
import requests


# Define a function to get example sentences from Reverso Context API
def get_example_sentences(word, language_pair="de-en"):
    url = f"https://api.reverso.net/translate/v1/examples?source_lang=de&target_lang=en&source_text={word}&page_size=5"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}  # Replace with your API key
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['examples']
    else:
        return []


# Title of the app
st.title('German Word Example Sentences')

# Input box for German word
german_word = st.text_input('Enter a German word:')

# Display example sentences if the word is provided
if german_word:
    example_sentences = get_example_sentences(german_word)
    if example_sentences:
        st.write(f'Example sentences for "{german_word}":')
        for example in example_sentences:
            german_sentence = example['source_text']
            english_translation = example['target_text']
            st.write(f'**{german_sentence}** - {english_translation}')
    else:
        st.write('No example sentences available for this word or there was an error fetching data.')

# Note: You need to handle cases where the API request might fail.
