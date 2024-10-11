#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import re
import random
import json
import datetime
from pytz import timezone
#from collections import defaultdict

# Store words by sentence id
sentence_words = {}

# To maintain unique identifiers for anaphoras
anaphora_counter = 0
anaphora_map = {}  # Dictionary to map anaphoras to their identifiers
antecedent_map = {}  # Dictionary to map antecedents to their anaphoras' identifiers
antecedent_colors = {}  # Dictionary to store colors for antecedents
anaphora_colors = {}  # Dictionary to map anaphoras to their identifiers
color_word_map = {}  # Dictionary to map color codes to their corresponding words
tagged_word_id = 1  # Unique ID counter for all tagged words

def extract_elements(sentence):
    elements = {}
    lines = sentence.split('\n')

    current_element = {}
    current_chunk = []

    for line in lines:
        line = line.strip()

        if re.match(r'^\d+\s+\(\(', line):  # Start of a new element
            if current_chunk:
                elements[' '.join(current_chunk)] = current_element
            current_element = {}
            current_chunk = []
            element_id_match = re.search(r'^\d+', line)
            if element_id_match:
                current_element['element_id'] = element_id_match.group(0)
            name_match = re.search(r'name=(NP\d+)', line)
            if name_match:
                current_element['name'] = name_match.group(1)
            current_element['ref_sentence_id'] = None
            current_element['ref_name'] = None

        elif re.match(r'^\d+\.\d+\s+\S+', line):  # This line contains the actual word details or punctuation.
            word_match = re.match(r'^\d+\.\d+\s+(\S+)', line)
            if word_match:
                word = word_match.group(1)
                current_chunk.append(word)

            # Extract ref_sentence_id and REF if present
            ref_sentence_id_match = re.search(r'sentence\s?id\s?=\s?[\'"]?(\d+)[\'"]?', line)
            if ref_sentence_id_match:
                current_element['ref_sentence_id'] = ref_sentence_id_match.group(1)
            ref_name_match = re.search(r'REF=(NP\d+)', line)
            if ref_name_match:
                current_element['ref_name'] = ref_name_match.group(1)

        elif line == '))':  # End of a chunk
            current_element['combined_chunk'] = ' '.join(current_chunk)
            elements[' '.join(current_chunk)] = current_element
            current_element = {}
            current_chunk = []

    #print(elements)
    return elements


def generate_random_hex_color():
    letters = '89ABCDEF'
    hex_color = ''.join(random.choice(letters) for _ in range(6))
    return f"#{hex_color}"

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

def rgb_to_hex(rgb_string):
    rgb_values = rgb_string.strip('rgb()').split(',')  # Extract RGB values from string
    if len(rgb_values) == 3:
        r, g, b = [int(value.strip()) for value in rgb_values]
        return '#{:02X}{:02X}{:02X}'.format(r, g, b)
    else:
        return 'N/A'  # Handle cases where the RGB string is invalid

def generate_random_color():
    hex_color = generate_random_hex_color()
    return hex_to_rgb(hex_color)

count = 0

def tag_coreferences(all_elements):
    global sentence_words, anaphora_counter, tagged_word_id

    # New dictionary to store antecedent IDs and their corresponding words
    antecedent_id_map = {}

    # Iterate over each sentence in the input elements
    for i, elements in enumerate(all_elements):
        words = []

        # Process each word in the current sentence
        for word, word_info in elements.items():
            if word_info.get('ref_sentence_id'):
                # Increment the anaphora counter for each anaphora found
                anaphora_counter += 1
                
                # Create a superscript tag for the current anaphora
                anaphora_id = f"<sup> {anaphora_counter} </sup>"
                anaphora_map[anaphora_id] = word

                # Extract the referenced sentence index and name
                ref_sentence_index = int(word_info['ref_sentence_id']) - 1
                ref_name = word_info['ref_name']
                ref_sentence_id_key = f"Sentence {ref_sentence_index + 1}"

                # Retrieve the elements from the referenced sentence
                ref_elements = all_elements[ref_sentence_index]
                referenced_element_info = None
                
                # Find the referenced element's information
                for element_name, element_info in ref_elements.items():
                    if element_info['name'] == ref_name:
                        referenced_element_info = element_info
                        break

                # Get the combined chunk of the anaphora
                combined_chunk = word_info.get('combined_chunk', '')
                antecedent_word = referenced_element_info['combined_chunk'] if referenced_element_info else None

                # Determine the color for the anaphora
                if antecedent_word and antecedent_word in antecedent_colors:
                    color = antecedent_colors[antecedent_word]
                elif antecedent_word and antecedent_word in anaphora_colors:
                    color = anaphora_colors[antecedent_word]
                elif combined_chunk in anaphora_colors:
                    color = anaphora_colors[combined_chunk]
                elif combined_chunk in antecedent_colors:
                    color = antecedent_colors[combined_chunk]
                else:
                    # Generate a new random color if none is assigned
                    color = generate_random_color()
                    if antecedent_word:
                        antecedent_colors[antecedent_word] = color
                    anaphora_colors[combined_chunk] = color

                # Add to the color_word_map for tracking colors
                word_tag_id = f"{tagged_word_id}"
                id_anaphora = word_tag_id
                color_word_map[word_tag_id] = {'word': combined_chunk, 'color': color}
                tagged_word_id += 1

                # Append the anaphora HTML with its ID and style
                #words.append(f"<anaphora id=\"{id_anaphora}\" class=\"highlightAnnaphora\" ana_ref=\"TRUE\" ana_relid=\"None\" ana_rel_type=\"annaphora_c\" style=\"background-color: {color};\">{combined_chunk}{anaphora_id}</anaphora>")

                # Locate and tag the antecedent in the referenced sentence
                if ref_sentence_id_key in sentence_words:
                    ref_sentence_words = sentence_words[ref_sentence_id_key]

                    # Iterate through the referenced elements to find the correct antecedent
                    for ref_element in ref_elements.values():
                        if ref_element['name'] == word_info['ref_name']:
                            combined_chunk_ref = ref_element['combined_chunk']

                            # Store the antecedent ID and corresponding word in the new map
                            antecedent_id = f"{tagged_word_id}"  # Use the next available tagged_word_id as antecedent ID
                            antecedent_id_map[antecedent_id] = combined_chunk_ref  # Map ID to antecedent word

                            # Update the antecedent_map with the current anaphora ID wrapped in <sup> tags
                            if combined_chunk_ref not in antecedent_map:
                                antecedent_map[combined_chunk_ref] = []
                            # Append the current anaphora ID as a superscript tag
                            antecedent_map[combined_chunk_ref].append(anaphora_id)  # Store <sup> tags in the map

                            # Search through the referenced sentence words
                            for k, chunk_word_candidate in enumerate(ref_sentence_words):
                                if '<anaphora' in chunk_word_candidate:
                                    # Check if the word candidate matches the combined_chunk_ref
                                    match = re.search(r'<anaphora[^>]*>([^<]+)<', chunk_word_candidate)
                                    if match:
                                        actual_word = match.group(1)
                                        if actual_word.strip() == combined_chunk_ref.strip():
                                            existing_anaphora_tag = chunk_word_candidate
                                            word_tag_id = f"{tagged_word_id}"
                                            id_antecedent = word_tag_id
                                            tagged_word_id += 1

                                            # Create <sup> tags only if there are multiple anaphoras
                                            existing_anaphora_ids = ''.join(antecedent_map[combined_chunk_ref]) if len(antecedent_map[combined_chunk_ref]) > 1 else ""
                                            
                                            # Update the antecedent HTML with current anaphora
                                            ref_sentence_words[k] = f"<antecedent class=\"antecedent-border highlightAnnaphora\" id=\"{id_antecedent}\" style=\"background-color: {color}; font-weight: bold;\">{existing_anaphora_tag}{existing_anaphora_ids}</antecedent>"
                                            
                                            # Store the color and word in the map for antecedents
                                            color_word_map[antecedent_id] = {'word': combined_chunk_ref, 'color': color}
                                elif chunk_word_candidate.strip() == combined_chunk_ref.strip():
                                    existing_tag = ref_sentence_words[k]
                                    existing_anaphora_ids = ''.join(antecedent_map[combined_chunk_ref]) if len(antecedent_map[combined_chunk_ref]) > 1 else ""
                                    word_tag_id = f"{tagged_word_id}"
                                    id_antecedent = word_tag_id
                                    tagged_word_id += 1

                                    # Update the antecedent HTML accordingly
                                    ref_sentence_words[k] = f"<antecedent class=\"antecedent-border highlightAnnaphora\" id=\"{id_antecedent}\" style=\"background-color: {color}; font-weight: bold;\">{combined_chunk_ref}{existing_anaphora_ids}</antecedent>"
                                    
                                    # Store the color and word in the map for antecedents
                                    color_word_map[antecedent_id] = {'word': combined_chunk_ref, 'color': color}
                            break  # Exit the loop once the ref_word is found

                 # Append the anaphora HTML with its ID and style
                words.append(f"<anaphora id=\"{id_anaphora}\" class=\"highlightAnnaphora\" ana_ref=\"TRUE\" ana_relid=\"{id_antecedent}\" ana_rel_type=\"annaphora_c\" style=\"background-color: {color};\">{combined_chunk}{anaphora_id}</anaphora>")
            
            else:
                # If there is no reference, just append the word
                words.append(word)

        # Store the processed words for the current sentence in the sentence_words dictionary
        sentence_id = f"Sentence {i + 1}"
        sentence_words[sentence_id] = words

    # After processing all sentences, update the antecedents in sentence_words
    for antecedent_word, superscripts in antecedent_map.items():
        for sentence_id, sentence in sentence_words.items():
            for idx, word in enumerate(sentence):
                if f"{antecedent_word}" in word:
                     # Only append superscripts if the current word is an antecedent
                    if f"<antecedent" in word:
                        # Append the corresponding <sup> tags to the antecedent word before the closing tag
                        sentence[idx] = re.sub(r"(</antecedent>)", f"{''.join(superscripts)}\\1", word)



def extract_tags_and_colors(color_word_map):
    tags_info = []

    for tag_id, color_info in color_word_map.items():
        word = color_info.get('word', '')
        color = color_info.get('color', 'N/A')
        tags_info.append((word, color))

    # Convert the list of tuples into a dictionary with lists of colors
    final_tags_info = {}
    for word, color in tags_info:
        color = rgb_to_hex(color)
        if word in final_tags_info:
            if color not in final_tags_info[word]:  # Avoid duplicate colors
                final_tags_info[word].append(color)
        else:
            final_tags_info[word] = [color]

    # Convert lists to a single string for output, allowing duplicates
    final_tags_info = {key: ', '.join(colors) for key, colors in final_tags_info.items()}

    #print(type(final_tags_info))
    return final_tags_info



def main(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        sentences = file.read().split('\n\n')

    all_elements = [extract_elements(sentence) for sentence in sentences]
    tag_coreferences(all_elements)
    last_id = tagged_word_id  # Ensure you have the correct last ID

    # Create the output dictionary
    output_dict = {
        "text": "<document>\n<metadata last_id=\"{}\"></metadata>\n".format(last_id),
        "last_id": last_id,
        "colorMap": {},
        "anaphora_count": anaphora_counter
    }

    # Build the content for the document
    for sentence_id, words in sentence_words.items():
        output_dict["text"] += f"<paragraph>\n<p>{' '.join(words)}</p>\n</paragraph>\n\n<paragraph>\n<p> </p>\n</paragraph>\n\n"
    output_dict["text"] += '</document>\n'

    # Fill the color_map with extracted information
    tags_and_colors = extract_tags_and_colors(color_word_map)

    # Ensure to include unique keys for colorMap
    for tag, color in tags_and_colors.items():
        output_dict["colorMap"][tag] = color if color else "N/A"

    # Properly escape the HTML-like content in the 'text' field for valid JSON
    output_dict["text"] = output_dict["text"]

    # Convert to JSON
    json_output = json.dumps(output_dict, separators=(',', ':'))

    # Print the final JSON output
    #print(json_output)

    # Set the timezone to IST
    ist_timezone = timezone('Asia/Kolkata')
    # Get the current date and time
    now = datetime.datetime.now(ist_timezone)
    # Format the date and time (customize as needed)
    formatted_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Write the JSON output to a file in the specified location
    output_file_name = f'SSF_Conv_output_{formatted_datetime}.txt'
    output_file_full_path = f'{output_file_path}/{output_file_name}'
    with open(output_file_full_path, 'w', encoding='utf-8') as f:
        f.write(json_output)
        print(f'Output written to: {output_file_full_path}')

if __name__ == "__main__":
    input_file = input("Enter the absolute path of the input file: ")
    output_directory = input("Enter the absolute path of the output directory: ")

    # If the output directory is not provided, use the default "Downloads" directory
    if not output_directory:
        home_directory = os.path.expanduser("~")  # Get the home directory of the user
        output_directory = os.path.join(home_directory, "Downloads")

    print(f"Output will be saved to: {output_directory}")
    
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Your code to process the input file and save results in the output directory
    # For example, saving a file to the output directory
    output_file_path = os.path.join(output_directory, "output.txt")
    with open(output_file_path, "w") as output_file:
        output_file.write("This is a test output.")

    print(f"File saved to: {output_file_path}")

    main(input_file, output_directory)
#/home/alexander/Downloads/nenu_annotated.txt
#/home/alexander/Desktop/LTRC_IIIT_HYD/XML_frmt


# In[ ]:




