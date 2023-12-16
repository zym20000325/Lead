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


def extract_sentences(transcript, name1, name2):
    name_pattern = fr'({name1}|{name2}):'
    sentences = re.split(name_pattern, transcript)
    result = []
    
    speaker = None
    for sentence in sentences:
        if sentence == name1:
            speaker = name1
        elif sentence == name2:
            speaker = name2
        else:
            spoken_sentence = sentence.strip()
            if speaker:
                result.append([speaker, spoken_sentence])
    
    return result


def clean_sentences(sentences):

    for i in range(len(sentences)):

        substring_to_remove = r"This transcript was exported.*?\n"
        sentences[i][1] = re.sub(substring_to_remove, '', sentences[i][1])
        substring_to_remove = r"GEI .*?\n"
        sentences[i][1] = re.sub(substring_to_remove, '', sentences[i][1])
        substring_to_remove = r'Page\s\d+\s*of\s*\d+'
        sentences[i][1] = re.sub(substring_to_remove, '', sentences[i][1])
        substring_to_remove = r"Transcri pt by Rev.com"
        sentences[i][1] = re.sub(substring_to_remove, '', sentences[i][1])
        # substring_to_remove = r"Transcri pt.*?\n"
        # sentences[i][1] = re.sub(substring_to_remove, '', sentences[i][1])
        # substring_to_remove = r'Transcri pt.*?\d+'
        # sentences[i][1] = re.sub(substring_to_remove, '', sentences[i][1])
        substring_to_remove = r"\b\d+\s*\n"
        sentences[i][1] = re.sub(substring_to_remove, '', sentences[i][1])
        substring_to_remove = r"\[inaudible.*?\]"
        sentences[i][1] = re.sub(substring_to_remove, '', sentences[i][1])

        sentences[i][1] = sentences[i][1].replace('\n', '').replace(r'\ ', '').replace('\\', '')
        sentences[i][1] = re.sub(r'\s*\d+\s*$', '', sentences[i][1])

    return sentences


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


# Test data
# data = [['name1', 'sentence1'], ['name2', 'sentence2'], ['name1', 'sentence3'], ['name2', 'sentence4']]
# data = [['name1', 'sentence1'], ['name2', 'sentence2'], ['name1', 'sentence4'], ['name1', 'sentence5'], ['name2', 'sentence6']]
# data = [['name1', 'sentence1'], ['name2', 'sentence2'], ['name2', 'sentence3'], ['name1', 'sentence4'], ['name2', 'sentence6']]
# data = [['name1', 'sentence1'], ['name2', 'sentence2'], ['name2', 'sentence3'], ['name1', 'sentence4'], ['name1', 'sentence5'], ['name2', 'sentence6']]


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: python script_name.py file_name name1 name2")
        sys.exit(1)

    file_name = sys.argv[1]
    name1 = sys.argv[2]
    name2 = sys.argv[3]

    # file_name = 'Gideon-Patrice-GEI-Transcript'
    # name1 = "Patrice"
    # name2 = "Gideon"

    pdf_file_name = 'pdfs/' + file_name + '.pdf'
    csv_file_name = 'text_original_csv/'+ file_name + '.csv'

    text_from_pdf = extract_text_from_pdf(pdf_file_name)
    save_text_to_csv(text_from_pdf, csv_file_name)

    df = pd.read_csv(csv_file_name, header=None)

    original_text = ''.join(df[0])

    parts = original_text.split(':')
    formatted_parts = [part.strip() for part in parts]
    formatted_text = ':'.join(formatted_parts)

    sentences = extract_sentences(formatted_text, name1, name2)

    sentences = clean_sentences(sentences)
    conversation = create_conversations(sentences, name1, name2)

    df = pd.DataFrame(conversation)
    df.rename(columns={name1: 'interviewer', name2: 'interviewee'}, inplace=True)
    df['iterationID'] = range(1, len(df) + 1)
    df = df[['iterationID', 'interviewer', 'interviewee']]

    target_file_name = 'text_cleaned_csv/'+ file_name + '.csv'

    df.to_csv(target_file_name)