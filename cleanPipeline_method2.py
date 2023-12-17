import csv
import PyPDF2
import pandas as pd
import re
import sys


def extract_text_from_pdf(pdf_file):
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text_list = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_list.append(page.extract_text())

        return text_list

def save_text_to_csv(text_list, csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for text in text_list:
            writer.writerow([text])


def clean_text(text):
    
    text = re.sub(r'\n©.*?permission', '', text)
    text = re.sub(r'©.*?Permission', '', text)
    text = re.sub(r'SOI.*?permission', '', text)
    text = re.sub(r'Steve.*?permission', '', text)
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\{.*?\}', '', text)
    text = text.replace('/', '')
    text = text.replace('"', '   ')
    text = text.replace('[', '   ')
    text = text.replace(']', '   ')
    text = text.replace('“', '   ')
    text = text.replace('”', '   ')
    
    text = re.sub(r'Growth Edge Coaching.*?permission', '', text)
    text = re.sub(r'Juanita Growth Edge Interview', '', text)
    text = re.sub(r'Transcript of Robert GEI', '', text)
    text = re.sub(r'GEI', '', text)
    text = re.sub('Transcript of Robert', '', text)
    
    return text


def separate_text(text):

    # separated_list = re.split(r'[.!?]', text)
    separated_list = re.split(r'[.!?]|\s{2,}', text)
    separated_list = [sentence.strip() for sentence in separated_list if sentence.strip()]
    return separated_list


def combine_consecutive_strings(lst):
    combined_strings = []
    current_combined = []

    for string in lst:
        # Check if the string is all capital letters
        is_all_caps = string.isupper()

        if current_combined:
            # If the current string has the same format as the previous one, combine them
            if (is_all_caps and current_combined[-1].isupper()) or (not is_all_caps and not current_combined[-1].isupper()):
                current_combined.append(string)
            else:
                # If the format changes, join the combined strings and reset
                combined_strings.append(' '.join(current_combined))
                current_combined = [string]
        else:
            current_combined.append(string)

    # Append the last set of combined strings
    if current_combined:
        combined_strings.append(' '.join(current_combined))

    return combined_strings


def identify_interviewer_interviewee(dialogue):
    result = []
    for sentence in dialogue:
        if sentence.isupper():
            result.append(['interviewer', sentence])
        else:
            result.append(['interviewee', sentence])
    return result


def create_conversations(sentence_list, name1, name2):
    
    conversations = []
    current_conversation = {}
    name1_said = None
    name2_said = None

    for name, sentence in sentence_list:
        if name == name1 and name1_said is None and name2_said is None:
            name1_said = sentence
        elif name == name2 and name2_said is None and name1_said is not None:
            name2_said = sentence

        if name1_said is not None and name2_said is not None:
            current_conversation[name1] = name1_said
            current_conversation[name2] = name2_said
            conversations.append(current_conversation)
            current_conversation = {}
            name1_said = None
            name2_said = None

    return conversations


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python script_name.py file_name name1 name2")
        sys.exit(1)

    file_name = sys.argv[1]

    pdf_file_name = 'pdfs/' + file_name + '.pdf'
    csv_file_name = 'text_original_csv/'+ file_name + '.csv'

    text_from_pdf = extract_text_from_pdf(pdf_file_name)
    save_text_to_csv(text_from_pdf, csv_file_name)

    df = pd.read_csv(csv_file_name, header=None)

    original_text = ''.join(df[0])
    formatted_text = clean_text(original_text)

    sentences = separate_text(formatted_text)
    sentences = combine_consecutive_strings(sentences)
    sentences = identify_interviewer_interviewee(sentences)

    conversation = create_conversations(sentences, "interviewer", "interviewee")

    df = pd.DataFrame(conversation)

    df['iterationID'] = range(1, len(df) + 1)
    df = df[['iterationID', 'interviewer', 'interviewee']]

    target_file_name = 'text_cleaned_csv/'+ file_name + '.csv'
    df.to_csv(target_file_name)