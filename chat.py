import re

# Path to the exported WhatsApp chat text file
chat_file_path = r"C:\Users\User\Documents\project\dictionarymessage\german_english_dictionary.txt"

# Define the regex pattern to match the specific message format
pattern = r'\d{2}/\d{2}/\d{4}, \d{2}:\d{2} - .+?: (.+-.+)$'

# Initialize a list to store the matched messages
matched_words = []

# Read the chat file and extract matching messages
with open(chat_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        # Search for the pattern in each line
        match = re.search(pattern, line)
        if match:
            # Extract the part after the last colon and replace '-' with ','
            word_pair = match.group(1).replace('-', ',')
            matched_words.append(word_pair)

# Output the matched words
for words in matched_words:
    print(words)

# Optional: Save the matched words to a new file
output_file_path = r"C:\Users\User\Documents\project\dictionarymessage\output_file.txt"
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for words in matched_words:
        output_file.write(f"{words}\n")
