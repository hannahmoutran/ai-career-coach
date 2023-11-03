import re
import openai
from time import time, sleep
from halo import Halo
import textwrap
import yaml
import pyperclip
import os

def input_with_commands(prompt):
    """
    Get input from the user, with support for fetching content from the clipboard and loading from a file.
    """
    text = input(prompt).strip()

    if text == "help":
        print("Commands:")
        print("  Type:/paste, then press enter to paste in a text file, such as the job listing or your resume.")
        print("  Type:/load and type the name of your file to load content from a file that is saved in the same folder as this program")
        return input_with_commands(prompt)
    
    if text == "/paste":
        text = pyperclip.paste().strip()
        print(text)
        return text
    
    if text.startswith("/load "):
        filename = text.split(" ", 1)[1]
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read().strip()
                print(content)
                return content
        else:
            print(f"File '{filename}' not found.")
            return input_with_commands(prompt)
    
    return text


###     file operations


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


###     API functions


def chatbot(conversation, model="gpt-3.5-turbo-16k", temperature=0, max_tokens=8000):
    max_retry = 7
    retry = 0
    while True:
        try:
            spinner = Halo(text='Thinking...', spinner='dots')
            spinner.start()
            
            response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
            text = response['choices'][0]['message']['content']

            spinner.stop()
            
            return text, response['usage']['total_tokens']
        except Exception as oops:
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            exit(5)


def chat_print(text):
    formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in text.split('\n')]
    formatted_text = '\n'.join(formatted_lines)
    print('\n\n\nCHATBOT:\n\n%s' % formatted_text)


if __name__ == '__main__':
    openai.api_key = open_file('key_openai.txt').strip()
    
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_01_intake.md')})
    user_messages = list()
    all_messages = list()
    print('Talk about the job you are applying for. Type DONE when done.')
    
    ## INTAKE PORTION
    
    while True:
        # get user input
        text = input_with_commands('\n\nJob Seeker (to input long texts-job descriptions, etc, type help) : ').strip()
        if text == 'DONE':
            break
        user_messages.append(text)
        all_messages.append('Job Seeker : %s' % text)
        conversation.append({'role': 'user', 'content': text})
        response, tokens = chatbot(conversation)
        conversation.append({'role': 'assistant', 'content': response})
        all_messages.append('INTAKE: %s' % response)
        print('\n\nCareer Coach Extraordinaire:\n\n%s' % response)
    
    ## CHARTING NOTES
    
    print('\n\nGenerating Notes')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_02_prepare_notes.md')})
    text_block = '\n\n'.join(all_messages)
    chat_log = '<<BEGIN Job Seeker INTAKE CHAT>>\n\n%s\n\n<<END Job Seeker INTAKE CHAT>>' % text_block
    save_file('logs/log_%s_chat.txt' % time(), chat_log)
    conversation.append({'role': 'user', 'content': chat_log})
    notes, tokens = chatbot(conversation)
    print('\n\nNotes version of conversation:\n\n%s' % notes)
    save_file('logs/log_%s_notes.txt' % time(), notes)
    
    ## GENERATING REPORT

    print('\n\nGenerating Hypothesis Report')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_03_diagnosis.md')})
    conversation.append({'role': 'user', 'content': notes})
    report, tokens = chatbot(conversation)
    save_file('logs/log_%s_diagnosis.txt' % time(), report)
    print('\n\nHypothesis Report:\n\n%s' % report)

    ## CLINICAL EVALUATION

    print('\n\nPreparing for Clinical Evaluation')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_04_clinical.md')})
    conversation.append({'role': 'user', 'content': notes})
    clinical, tokens = chatbot(conversation)
    save_file('logs/log_%s_clinical.txt' % time(), clinical)
    print('\n\nClinical Evaluation:\n\n%s' % clinical)

    ## REFERRALS & TESTS

    print('\n\nGenerating Referrals and Tests')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_05_referrals.md')})
    conversation.append({'role': 'user', 'content': notes})
    referrals, tokens = chatbot(conversation)
    save_file('logs/log_%s_referrals.txt' % time(), referrals)
    print('\n\nReferrals and Tests:\n\n%s' % referrals)
